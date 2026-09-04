from django.shortcuts import render

# Create your views here.
import requests
from rest_framework.parsers import MultiPartParser
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from edge.sync import sync_users
from eid.models import EIDCard
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
    # permission_classes = [HasEdgeToken]

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

class EdgeSyncUsersView(GenericAPIView):
    """
    Sync enrolled users from the central API
    into the local edge database.
    """

    def post(self, request):
        try:
            count = sync_users()

            return Response(
                {
                    "success": True,
                    "message": "Users synchronized successfully.",
                    "synced_users": count,
                },
                status=status.HTTP_200_OK
            )

        except requests.RequestException as exc:
            return Response(
                {
                    "success": False,
                    "message": f"Failed to sync users: {str(exc)}",
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
            
class EdgeVerifyView(GenericAPIView):
    """
    Verify a user's identity using the e-ID QR code
    and facial recognition against the local edge database.
    """

    parser_classes = [MultiPartParser]

    @staticmethod
    def _resolve_identity(qr_token):
        """
        Look up the identity behind a scanned QR token.

        Prefers the locally synced ``EdgeUser`` replica, and falls back to the
        central ``EIDCard`` / ``FaceEmbedding`` tables so verification also works
        on a single-node deployment (or before the first edge sync has run).

        Returns ``(stored_embedding, user_payload)`` or ``None`` when no active
        e-ID with an active face embedding matches the token.
        """
        try:
            edge_user = EdgeUser.objects.get(
                qr_token=qr_token,
                is_active=True,
            )
            return edge_user.face_embedding, {
                "id": str(edge_user.id),
                "firstName": edge_user.firstName,
                "lastName": edge_user.lastName,
                "artisan_type": edge_user.artisan_type,
            }
        except EdgeUser.DoesNotExist:
            pass

        try:
            card = EIDCard.objects.select_related(
                "user", "user__face_embedding"
            ).get(
                qr_token=qr_token,
                is_active=True,
            )
        except EIDCard.DoesNotExist:
            return None

        face_embedding = getattr(card.user, "face_embedding", None)

        if face_embedding is None or not face_embedding.is_active:
            return None

        return face_embedding.embedding, {
            "id": str(card.user.id),
            "firstName": card.user.firstName,
            "lastName": card.user.lastName,
            "artisan_type": card.user.artisan_type,
        }

    def post(self, request):
        qr_token = request.data.get("qr_token")
        face = request.FILES.get("face")

        if isinstance(qr_token, str):
            qr_token = qr_token.strip()

        print("QR TOKEN RECEIVED:", repr(qr_token))

        if not qr_token or not face:
            return Response(
                {
                    "verified": False,
                    "message": "QR token and face image are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        identity = self._resolve_identity(qr_token)

        if identity is None:
            return Response(
                {
                    "verified": False,
                    "message": "Invalid or inactive e-ID."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        stored_embedding, user_payload = identity

        try:
            result = verify_face(
                stored_embedding=stored_embedding,
                image_bytes=face.read()
            )
        except ValueError as exc:
            return Response(
                {
                    "verified": False,
                    "message": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not result["matched"]:
            return Response(
                {
                    "verified": False,
                    "message": "Face verification failed."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                "verified": True,
                "message": "Identity verified.",
                "user": user_payload,
            },
            status=status.HTTP_200_OK
        )