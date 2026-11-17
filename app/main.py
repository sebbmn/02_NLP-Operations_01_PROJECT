from fastapi import FastAPI
from pydantic import BaseModel

from app.classifier import classify_batch

app = FastAPI(title="30Sekunden Comment Classifier")


class ClassifyRequest(BaseModel):
    comment: str


class ClassifyResponse(BaseModel):
    comment: str
    label: str
    score: float


@app.post("/classify", response_model=ClassifyResponse)
def classify(request: ClassifyRequest) -> ClassifyResponse:
    result = classify_batch([request.comment])[0]
    return ClassifyResponse(comment=request.comment, **result)
