from rest_framework import serializers

from .models import EIDCard


class EIDCardSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = EIDCard
        fields = ["id", "card_number", "qr_token", "issued_at", "is_active"]