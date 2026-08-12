from django.shortcuts import render

# Create your views here.
from uuid import uuid4

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from user.models import User

from .models import EIDCard
from .serializers import EIDCardSerializer


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
        return Response(
            {
                "message": "E-ID generated successfully",

                "card": EIDCardSerializer(
                    card
                ).data
            },
            status=status.HTTP_201_CREATED
        )
        