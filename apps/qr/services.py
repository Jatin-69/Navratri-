from __future__ import annotations

import base64
import hashlib
import hmac
import io
import secrets
from urllib.parse import urlparse

import segno
from cryptography.fernet import Fernet
from django.conf import settings


def generate_token() -> str:
    return secrets.token_urlsafe(32)


def token_hmac_key() -> bytes:
    return hashlib.sha256(f"{settings.SECRET_KEY}:qr-token".encode()).digest()


def hash_token(token: str) -> str:
    return hmac.new(token_hmac_key(), token.encode(), hashlib.sha256).hexdigest()


def _get_fernet() -> Fernet:
    key = getattr(settings, "FERNET_KEY", "")
    if not key:
        seed = hashlib.sha256(f"{settings.SECRET_KEY}:fernet".encode()).digest()
        key = base64.urlsafe_b64encode(seed).decode()
    return Fernet(key.encode())


def encrypt_token(token: str) -> bytes:
    return _get_fernet().encrypt(token.encode())


def decrypt_token(token_bytes: bytes) -> str:
    return _get_fernet().decrypt(token_bytes).decode()


def create_qr_png(value: str) -> bytes:
    qr = segno.make(value, error="m")
    buffer = io.BytesIO()
    qr.save(buffer, kind="png", scale=8, border=2)
    return buffer.getvalue()


def extract_token(raw_scan_value: str) -> str:
    value = (raw_scan_value or "").strip()
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        return parsed.path.rstrip("/").split("/")[-1]
    return value
