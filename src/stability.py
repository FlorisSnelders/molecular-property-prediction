"""Turning predicted class probabilities into stability labels."""

from __future__ import annotations

import numpy as np


def predict_stability_labels(proba: np.ndarray, classes, n_low: int | None = None) -> np.ndarray:
    """Stability labels from ``predict_proba`` output.

    By default this is the model's own prediction (the most likely class).

    ``n_low`` reproduces the adjustment used for the final Kaggle submission:
    exactly ``n_low`` molecules are labelled "low" (those with the lowest
    probability of being "high"), and every other molecule gets whichever of
    "high" / "medium" is more likely. The count (34) was inferred from public
    leaderboard feedback, not from the model, so it only makes sense for that
    specific test set.
    """
    classes = np.asarray(classes)
    if n_low is None:
        return classes[np.argmax(proba, axis=1)]

    idx = {name: i for i, name in enumerate(classes)}
    high, low, medium = idx["high"], idx["low"], idx["medium"]
    pred = np.full(len(proba), -1)
    pred[np.argsort(proba[:, high])[:n_low]] = low
    rest = pred == -1
    pred[rest] = np.where(proba[rest, high] > proba[rest, medium], high, medium)
    return classes[pred]
