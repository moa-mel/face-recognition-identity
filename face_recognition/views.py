import logging
from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status

from face_recognition.embeddings import get_face_service

from rest_framework.parsers import MultiPartParser

from face_recognition.models import FaceEmbedding
from user.models import User

logger = logging.getLogger(__name__)


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
            # Expected validation problems: no face, multiple faces, bad image.
            return Response(
                {"message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            # Unexpected: model download/load failure, corrupt image decode...
            logger.exception("Face embedding extraction failed")
            return Response(
                {"message": "Face processing failed on the server."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        FaceEmbedding.objects.update_or_create(
            user=user,
            defaults={
                "embedding": embedding,
                "model_name": "opencv",
                "model_version": "sface_2021dec",
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