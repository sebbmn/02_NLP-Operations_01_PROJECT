import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from app.batcher import MicroBatcher

batcher = MicroBatcher()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the batch worker together with the server and stop it on shutdown.
    worker = asyncio.create_task(batcher.run())
    yield
    worker.cancel()


app = FastAPI(title="30Sekunden Comment Classifier", lifespan=lifespan)


class ClassifyRequest(BaseModel):
    comment: str


class ClassifyResponse(BaseModel):
    comment: str
    label: str
    score: float


@app.post("/classify", response_model=ClassifyResponse)
async def classify(request: ClassifyRequest) -> ClassifyResponse:
    result = await batcher.classify(request.comment)
    return ClassifyResponse(comment=request.comment, **result)
