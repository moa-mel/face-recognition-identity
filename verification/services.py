from face_recognition.models import FaceEmbedding
from face_recognition.verification import verify_face
from .models import VerificationLog


def verify_user(user,face_image,device_id,location):
    """
    Verify the identity of a user using their face
    """
    try:
        face_embedding = FaceEmbedding.objects.get(
            user=user,
            is_active=True
        )

    except FaceEmbedding.DoesNotExist:
        return {
            "verified": False,
            "message": "No face enrollment found."
        }

    result = verify_face(
        stored_embedding=face_embedding.embedding,
        image_bytes=face_image
    )
    VerificationLog.objects.create(
        user=user,
        device_id=device_id or "",
        location=location or "",
        result=(
            "SUCCESS"
            if result["matched"]
            else "FAILED"
        ),

        similarity=result["similarity"]
    )

    return {
        "verified": result["matched"],
        "similarity": result["similarity"]
    }