from .embeddings import get_face_service
from .models import FaceEmbedding


def enroll_face(user, image_bytes):

    embedding = get_face_service().get_embedding(
        image_bytes
    )

    face_embedding, created = FaceEmbedding.objects.update_or_create(
        user=user,
        defaults={
            "embedding": embedding,
            "model_name": "opencv",
            "model_version": "sface_2021dec",
        }
    )

    return face_embedding