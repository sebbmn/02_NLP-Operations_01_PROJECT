from transformers import pipeline

from app.labels import CANDIDATE_LABELS, HYPOTHESIS_TEMPLATE

MODEL_NAME = "facebook/bart-large-mnli"

# Loaded once when the module is imported (downloads the model on first run).
_pipeline = pipeline("zero-shot-classification", model=MODEL_NAME)


def classify_batch(comments: list[str]) -> list[dict]:
    """Classify several comments in one model call, return the best label per comment."""
    results = _pipeline(
        comments,
        candidate_labels=CANDIDATE_LABELS,
        hypothesis_template=HYPOTHESIS_TEMPLATE,
        batch_size=len(comments),
    )
    # The pipeline returns a single dict instead of a list when given one comment.
    if isinstance(results, dict):
        results = [results]

    # Labels are sorted by score, so index 0 is the best match.
    return [
        {"label": result["labels"][0], "score": round(result["scores"][0], 4)}
        for result in results
    ]
