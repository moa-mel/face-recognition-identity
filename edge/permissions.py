from django.conf import settings
from rest_framework.permissions import BasePermission


class HasEdgeToken(BasePermission):
    """
    Grants access to edge nodes that present the shared EDGE_API_TOKEN
    as a Bearer token, used when an edge node pulls the user/embedding
    sync feed from the central server.
    """

    def has_permission(self, request, view):
        if not settings.EDGE_API_TOKEN:
            return False

        auth_header = request.headers.get("Authorization", "")

        return auth_header == f"Bearer {settings.EDGE_API_TOKEN}"
