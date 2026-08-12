import requests

from django.conf import settings

from .models import EdgeUser


def sync_users():
    """
    Sync users from the central API to the local database.
    """
    response = requests.get(
        f"{settings.CENTRAL_API_URL}/api/edge/users/",
        headers={
            "Authorization":
            f"Bearer {settings.EDGE_API_TOKEN}"
        },
        timeout=30
    )

    response.raise_for_status()

    users = response.json()

    for data in users:

        EdgeUser.objects.update_or_create(

            id=data["id"],

            defaults={
                "firstName": data["firstName"],
                "lastName": data["lastName"],
                "artisan_type": data["artisan_type"],
                "face_embedding": data["face_embedding"],
                "qr_token": data["qr_token"],
                "is_active": data["is_active"],
            }
        )