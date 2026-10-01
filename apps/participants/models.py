import re

from django.db import models


class Participant(models.Model):
    participant_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120, db_index=True)
    phone = models.CharField(max_length=15, db_index=True)
    phone_normalized = models.CharField(max_length=10, db_index=True)
    photo = models.ImageField(upload_to="participants/")
    extra_identifier = models.CharField(max_length=60, blank=True)
    qr_token_hash = models.CharField(max_length=64, unique=True)
    qr_token_encrypted = models.BinaryField(null=True, blank=True)
    qr_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def normalize_phone(phone: str) -> str:
        digits = re.sub(r"\D", "", phone or "")
        return digits[-10:]

    def save(self, *args, **kwargs):
        self.phone_normalized = self.normalize_phone(self.phone)
        super().save(*args, **kwargs)

    def masked_phone(self):
        if len(self.phone) <= 4:
            return self.phone
        return f"{'X' * (len(self.phone) - 4)}{self.phone[-4:]}"

    def __str__(self):
        return f"{self.participant_code} - {self.name}"
