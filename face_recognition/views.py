from datetime import timedelta, timezone
from requests import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status

from face_recognition.embeddings import FaceEmbeddingService
from face_recognition.models import FaceEnrollment

from rest_framework.parsers import MultiPartParser

face_service = FaceEmbeddingService()

class FaceEnrollmentView(GenericAPIView):
    parser_classes = [MultiPartParser]
    def post(self, request):
        face = request.FILES.get("face")
        if not face:
            return Response(
                {"message": "Face image is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        embedding = face_service.get_embedding(
            face.read()
        )

        enrollment = FaceEnrollment.objects.create(
            embedding=embedding,
            model_name="insightface",
            model_version="buffalo_l",
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        return Response(
            {
                "message": "Face enrolled successfully.",
                "enrollment_id": str(enrollment.id)
            },
            status=status.HTTP_201_CREATED
        )