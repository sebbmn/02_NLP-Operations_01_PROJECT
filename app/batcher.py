import asyncio
import os
import time

from app.classifier import classify_batch
from app.metrics import (
    BATCH_INFERENCE_DURATION,
    BATCH_SIZE,
    BATCH_WAIT_TIME,
    BATCHES_PROCESSED,
    COMMENTS_BY_LABEL,
    COMMENTS_CLASSIFIED,
    QUEUE_SIZE,
)

BATCH_WINDOW_SECONDS = float(os.getenv("BATCH_WINDOW_MS", "200")) / 1000
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "8"))


class MicroBatcher:
    """Collects incoming comments and classifies them together in small batches.

    A batch is processed as soon as the batch window has expired
    or the maximum batch size is reached, whichever comes first.
    """

    def __init__(self):
        self.queue = asyncio.Queue()
        # The gauge reads the current queue length whenever Prometheus scrapes.
        QUEUE_SIZE.set_function(self.queue.qsize)

    async def classify(self, comment: str) -> dict:
        """Put a comment in the queue and wait until its batch has been classified."""
        future = asyncio.get_running_loop().create_future()
        await self.queue.put((comment, future, time.monotonic()))
        return await future

    async def run(self):
        """Worker loop: collect a batch, classify it, hand each result back to its request."""
        while True:
            batch = await self._collect_batch()
            comments = [comment for comment, _, _ in batch]
            print(f"Classifying batch of {len(batch)} comments", flush=True)

            batch_start = time.monotonic()
            for _, _, enqueued_at in batch:
                BATCH_WAIT_TIME.observe(batch_start - enqueued_at)

            try:
                # Run the model in a thread so the server keeps accepting requests meanwhile.
                with BATCH_INFERENCE_DURATION.time():
                    results = await asyncio.to_thread(classify_batch, comments)
            except Exception as error:
                for _, future, _ in batch:
                    if not future.done():
                        future.set_exception(error)
                continue

            BATCHES_PROCESSED.inc()
            BATCH_SIZE.observe(len(batch))
            COMMENTS_CLASSIFIED.inc(len(batch))
            for result in results:
                COMMENTS_BY_LABEL.labels(label=result["label"]).inc()

            for (_, future, _), result in zip(batch, results):
                # A future is already done if its client disconnected.
                if not future.done():
                    future.set_result(result)

    async def _collect_batch(self) -> list:
        # Wait for the first comment, its arrival starts the batch window.
        batch = [await self.queue.get()]
        deadline = time.monotonic() + BATCH_WINDOW_SECONDS

        while len(batch) < MAX_BATCH_SIZE:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                batch.append(await asyncio.wait_for(self.queue.get(), timeout=remaining))
            except asyncio.TimeoutError:
                break

        return batch
