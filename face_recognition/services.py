from .embeddings import FaceEmbeddingService
from .models import FaceEmbedding


face_service = FaceEmbeddingService()


def enroll_face(user, image_bytes):

    embedding = face_service.get_embedding(
        image_bytes
    )

    face_embedding, created = FaceEmbedding.objects.update_or_create(
        user=user,
        defaults={
            "embedding": embedding,
            "model_name": "insightface",
            "model_version": "buffalo_l",
        }
    )

    return face_embedding