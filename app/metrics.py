from prometheus_client import Counter, Gauge, Histogram

COMMENTS_CLASSIFIED = Counter(
    "comments_classified_total", "Number of classified comments"
)
COMMENTS_BY_LABEL = Counter(
    "comments_classified_by_label_total", "Classified comments per predicted label", ["label"]
)
BATCHES_PROCESSED = Counter(
    "batches_processed_total", "Number of processed microbatches"
)
BATCH_SIZE = Histogram(
    "batch_size", "Number of comments per processed batch", buckets=[1, 2, 4, 8, 16]
)
BATCH_INFERENCE_DURATION = Histogram(
    "batch_inference_duration_seconds", "Model inference duration per batch"
)
BATCH_WAIT_TIME = Histogram(
    "batch_wait_time_seconds", "Time a comment waits in the queue until its batch starts"
)
QUEUE_SIZE = Gauge(
    "microbatch_queue_size", "Number of comments currently waiting in the queue"
)
