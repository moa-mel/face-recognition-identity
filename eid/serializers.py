from rest_framework import serializers

from .models import EIDCard
from user.models import User


class _UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "firstName", "lastName", "email"]


class EIDCardSerializer(
    serializers.ModelSerializer
):
    user = _UserSerializer(read_only=True)

    class Meta:
        model = EIDCard
        fields = [
            "id", "user", "card_number", "qr_token",
            "issued_at", "is_active"
        ]