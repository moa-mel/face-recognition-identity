from uuid import uuid4
from django.db import models

from user.models import User

# Create your models here.
class EIDCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="eid_card")
    card_number = models.CharField(max_length=100, unique=True)
    qr_token = models.CharField(max_length=500, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.card_number