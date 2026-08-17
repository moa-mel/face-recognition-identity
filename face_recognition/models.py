from django.db import models
from user.models import User
from uuid import uuid4

# Create your models here.
from uuid import uuid4

from django.db import models

    
class FaceEmbedding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField("user.User", on_delete=models.CASCADE, related_name="face_embedding")
    embedding = models.JSONField()
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)