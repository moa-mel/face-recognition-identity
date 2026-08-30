from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status

from face_recognition.embeddings import get_face_service

from rest_framework.parsers import MultiPartParser

from face_recognition.models import FaceEmbedding
from user.models import User


class FaceEnrollmentView(GenericAPIView):
    parser_classes = [MultiPartParser]

    def post(self, request, user_id):
        
        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            return Response(
                {
                    "message": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        face = request.FILES.get("face")

        if not face:
            return Response(
                {
                    "message": "face image are required."
                },
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

        FaceEmbedding.objects.update_or_create(
            user=user,
            defaults={
                "embedding": embedding,
                "model_name": "insightface",
                "model_version": "buffalo_l",
                "is_active": True,
            }
        )

        return Response(
            {
                "message": "Face enrolled successfully.",
                "enrollment_id": str(user.face_embedding.id)
            },
            status=status.HTTP_201_CREATED
        )