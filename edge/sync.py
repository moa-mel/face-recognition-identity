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

    synced_ids = []

    for data in users:

        EdgeUser.objects.update_or_create(

            id=data["id"],

            defaults={
                "firstName": data["firstName"],
                "lastName": data["lastName"],
                "artisan_type": data["artisan_type"],
                "face_embedding": data["face_embedding"],
                "qr_token": data["qr_token"],
            }
        )

        synced_ids.append(data["id"])

    # Users no longer present on the central server are deactivated
    # locally rather than deleted, so a stale edge device fails closed.
    EdgeUser.objects.exclude(id__in=synced_ids).update(is_active=False)

    return len(synced_ids)