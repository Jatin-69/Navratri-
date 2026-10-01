from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAFF)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"
