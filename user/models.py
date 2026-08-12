from uuid import uuid4
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

from user.choices import ARTISAN_TYPE
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from user.managers import UserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    NIN = models.CharField(max_length=11, unique=True)
    artisan_type = models.CharField(max_length=50, choices=ARTISAN_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = "user"