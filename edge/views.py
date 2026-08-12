from django.shortcuts import render

# Create your views here.
from rest_framework.parsers import MultiPartParser
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from face_recognition.verification import verify_face
from user.models import User

from .models import EdgeUser
from .permissions import HasEdgeToken


class EdgeUserListView(GenericAPIView):
    """
    Central-side endpoint: serves the list of fully-enrolled users
    (face embedding + e-ID) that edge nodes pull down to populate
    their local on-prem database.
    """
    permission_classes = [HasEdgeToken]

    def get(self, request):
        users = User.objects.select_related(
            "face_embedding", "eid_card"
        ).filter(
            face_embedding__isnull=False,
            face_embedding__is_active=True,
            eid_card__isnull=False,
            eid_card__is_active=True,
        )

        data = [
            {
                "id": str(user.id),
                "firstName": user.firstName,
                "lastName": user.lastName,
                "artisan_type": user.artisan_type,
                "face_embedding": user.face_embedding.embedding,
                "qr_token": user.eid_card.qr_token,
            }
            for user in users
        ]

        return Response(data, status=status.HTTP_200_OK)


class EdgeVerifyView(GenericAPIView):
    """
    Verify a user's identity using the e-ID QR code
    and facial recognition against the local edge database.
    """
    parser_classes = [MultiPartParser]
    def post(self, request):
        qr_token = request.data.get('qr_token')
        face_file = request.FILES.get('face')

        if not qr_token or not face_file:
            return Response({"verified": False, "message": "QR token and face image are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            user = EdgeUser.objects.get(
                qr_token=qr_token,
                is_active=True
            )
        except EdgeUser.DoesNotExist:
            return Response({"verified": False, "message": "User is not available on this edge server."},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            result = verify_face(
                stored_embedding=user.face_embedding,
                image_bytes=face_file.read()
            )
        except ValueError as exc:
            return Response(
                {"verified": False, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not result["matched"]:
            return Response({"verified": False, "message": "Face verification failed."},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(
            {
                "verified": True,
                "message": "Identity verified.",
                "user": {
                    "id": str(user.id),
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "artisan_type": user.artisan_type,
                }
            }
        )