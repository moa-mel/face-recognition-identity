import os

import numpy as np

from .embeddings import get_face_service

# SFace: cosine similarity >= 0.363 => same identity (OpenCV's recommended
# default). Tune via env if needed.
_MATCH_THRESHOLD = float(os.environ.get("FACE_MATCH_THRESHOLD", "0.363"))


def cosine_similarity(a, b):
    """
    calculate the cosine similarity between two vectors a and b
    """
    a = np.array(a)
    b = np.array(b)

    denominator = (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b) / denominator
    )


def verify_face(
    stored_embedding,
    image_bytes,
    threshold=_MATCH_THRESHOLD
):

    new_embedding = get_face_service().get_embedding(
        image_bytes
    )

    similarity = cosine_similarity(
        stored_embedding,
        new_embedding
    )

    return {
        "matched": similarity >= threshold,
        "similarity": similarity,
        "threshold": threshold,
    }