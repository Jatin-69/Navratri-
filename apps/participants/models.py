import re

from django.db import models

from apps.qr.services import encrypt_token, generate_qr_token, token_hash


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    return digits[-10:] if len(digits) >= 10 else digits


class Participant(models.Model):
    participant_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120, db_index=True)
    phone = models.CharField(max_length=15, db_index=True)
    photo = models.ImageField(upload_to="participants/")
    extra_identifier = models.CharField(max_length=60, blank=True)
    qr_token_hash = models.CharField(max_length=64, unique=True)
    qr_token_encrypted = models.BinaryField(null=True, blank=True)
    qr_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def next_code() -> str:
        last = Participant.objects.order_by("-id").first()
        if not last:
            return "NAV-001"
        try:
            number = int(last.participant_code.split("-")[-1]) + 1
        except (ValueError, IndexError):
            number = last.id + 1
        return f"NAV-{number:03d}"

    @classmethod
    def create_with_new_token(cls, **kwargs):
        token = generate_qr_token()
        participant = cls.objects.create(
            qr_token_hash=token_hash(token),
            qr_token_encrypted=encrypt_token(token),
            participant_code=cls.next_code(),
            **kwargs,
        )
        return participant, token

    def regenerate_qr(self):
        token = generate_qr_token()
        self.qr_token_hash = token_hash(token)
        self.qr_token_encrypted = encrypt_token(token)
        self.qr_active = True
        self.save(update_fields=["qr_token_hash", "qr_token_encrypted", "qr_active", "updated_at"])
        return token

    @property
    def normalized_phone(self) -> str:
        return normalize_phone(self.phone)

    def __str__(self) -> str:
        return f"{self.participant_code} - {self.name}"
