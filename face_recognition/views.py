from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status

from face_recognition.embeddings import get_face_service
from face_recognition.models import FaceEnrollment

from rest_framework.parsers import MultiPartParser


class FaceEnrollmentView(GenericAPIView):
    parser_classes = [MultiPartParser]
    def post(self, request):
        face = request.FILES.get("face")
        if not face:
            return Response(
                {"message": "Face image is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            embedding = get_face_service().get_embedding(
                face.read()
            )
            
        except ValueError as exc:
            return Response(
                {"message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
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