from uuid import uuid4
from django.db import models

from user.choices import RESULT_CHOICES

# Create your models here.
class VerificationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey("user.User", on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    similarity = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True
                                      )