from rest_framework import serializers

from user.models import User

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "firstName",
            "lastName",
            "email",
            "NIN",
            "artisan_type",
        ]

    def validate_email(self, value):

        if User.objects.filter(
            email__iexact=value
        ).exists():

            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value.lower()

    def validate_NIN(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                "NIN must contain only numbers."
            )

        if len(value) != 11:
            raise serializers.ValidationError(
                "NIN must be exactly 11 digits."
            )

        if User.objects.filter(
            NIN=value
        ).exists():

            raise serializers.ValidationError(
                "A user with this NIN already exists."
            )

        return value

    def create(self, validated_data):

        user = User.objects.create(
            **validated_data
        )

        return user