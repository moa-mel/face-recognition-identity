
# Create your models here.
from uuid import uuid4

from django.db import models


class EdgeUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    artisan_type = models.CharField(max_length=50)
    face_embedding = models.JSONField()
    qr_token = models.CharField(max_length=500, unique=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)