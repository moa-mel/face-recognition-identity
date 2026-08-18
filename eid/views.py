from django.shortcuts import render

# Create your views here.
from io import BytesIO
from uuid import uuid4

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

from user.models import User

from .models import EIDCard
from .serializers import EIDCardSerializer
from .qr import generate_qr


class GenerateEIDView(GenericAPIView):
    """
    Generate a new e-ID for a user.
    """
    def post(self, request, user_id):
        try:
            user = User.objects.get(
                id=user_id
            )

        except User.DoesNotExist:
            return Response(
                {
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if hasattr(user, "eid_card"):
            card = user.eid_card
        else:
            card = EIDCard.objects.create(
                user=user,
                card_number=f"EID-{uuid4().hex[:12].upper()}",
                qr_token=str(uuid4())
            )
        
        # Generate the QR code image from the qr_token
        qr_image = generate_qr(card.qr_token)
        
        # Save the image to a byte stream
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        buffer.seek(0)
        print(f"Generated QR code for user {user.firstName} with token {card.qr_token}")
        
        # Return the image in the response
        return HttpResponse(buffer, content_type="image/png")


class VerifyEIDView(GenericAPIView):
    """
    Verify an E-ID using the scanned QR token.
    """
    serializer_class = EIDCardSerializer

    def get(self, request, qr_token):
        try:
            card = EIDCard.objects.select_related('user').get(
                qr_token=qr_token,
                is_active=True
            )
        except EIDCard.DoesNotExist:
            return Response(
                {"message": "E-ID card not found or is inactive"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            "verified": True,
            "message": "E-ID verified successfully",
            "eid_id": str(card.id),
            "card_number": card.card_number,
        })

