from django.utils import timezone
from rest_framework import serializers

from face_recognition.models import FaceEmbedding, FaceEnrollment
from face_recognition.services import enroll_face
from user.models import User

class RegisterSerializer(serializers.ModelSerializer):

    enrollment_id = serializers.UUIDField(
        write_only=True
    )

    class Meta:

        model = User

        fields = [
            "firstName",
            "lastName",
            "email",
            "NIN",
            "artisan_type",
            "enrollment_id",
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

        enrollment_id = validated_data.pop(
            "enrollment_id"
        )

        try:

            enrollment = FaceEnrollment.objects.get(
                id=enrollment_id,
                status="COMPLETED"
            )

        except FaceEnrollment.DoesNotExist:

            raise serializers.ValidationError({
                "enrollment_id":
                "Invalid or expired face enrollment."
            })

        if enrollment.expires_at < timezone.now():

            raise serializers.ValidationError({
                "enrollment_id":
                "Invalid or expired face enrollment."
            })

        user = User.objects.create(
            **validated_data
        )

        FaceEmbedding.objects.create(
            user=user,
            embedding=enrollment.embedding,
            model_name=enrollment.model_name,
            model_version=enrollment.model_version
        )

        enrollment.status = "USED"
        enrollment.used_at = timezone.now()
        enrollment.save(
            update_fields=[
                "status",
                "used_at"
            ]
        )

        return user