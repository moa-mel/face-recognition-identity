from django.shortcuts import render

# Create your views here.
from rest_framework.parsers import MultiPartParser
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from eid.models import EIDCard

from .services import verify_user


class VerifyIdentityView(GenericAPIView):
    """
    Verify the identity of a user using the qr code and face
    """
    parser_classes = [MultiPartParser]
    def post(self, request):
        qr_token = request.data.get("qr_token")
        face = request.FILES.get("face")
        device_id = request.data.get("device_id")
        location = request.data.get("location")

        if not qr_token or not face:
            return Response(
                {
                    "message": "QR token and face are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:

            card = EIDCard.objects.select_related(
                "user"
            ).get(
                qr_token=qr_token,
                is_active=True,
            )

        except EIDCard.DoesNotExist:

            return Response(
                {
                    "verified": False,
                    "message": "Invalid e-ID."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            result = verify_user(
                user=card.user,
                face_image=face.read(),
                device_id=device_id,
                location=location
            )
        except ValueError as exc:
            return Response(
                {
                    "verified": False,
                    "message": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not result["verified"]:

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
                "user": {
                    "id": str(card.user.id),
                    "firstName": card.user.firstName,
                    "lastName": card.user.lastName,
                    "artisan_type": card.user.artisan_type,
                }
            },
            status=status.HTTP_200_OK
        )