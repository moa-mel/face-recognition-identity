import numpy as np

from .embeddings import FaceEmbeddingService


face_service = FaceEmbeddingService()


def cosine_similarity(a, b):
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
    threshold=0.5
):

    new_embedding = face_service.get_embedding(
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