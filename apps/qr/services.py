import base64
import hashlib
import hmac
import secrets
from io import BytesIO
from urllib.parse import urlparse

import segno
from cryptography.fernet import Fernet
from django.conf import settings


def generate_qr_token() -> str:
    return secrets.token_urlsafe(32)


def get_hash_key() -> bytes:
    return settings.QR_HASH_KEY.encode("utf-8")


def token_hash(token: str) -> str:
    return hmac.new(get_hash_key(), token.encode("utf-8"), hashlib.sha256).hexdigest()


def maybe_extract_token(raw_value: str) -> str:
    value = raw_value.strip()
    if "/q/" in value or value.startswith("http"):
        parsed = urlparse(value)
        segments = [segment for segment in parsed.path.split("/") if segment]
        if segments:
            return segments[-1]
    return value


def get_fernet():
    if not settings.FERNET_KEY:
        return None
    return Fernet(settings.FERNET_KEY)


def encrypt_token(token: str) -> bytes | None:
    fernet = get_fernet()
    if not fernet:
        return None
    return fernet.encrypt(token.encode("utf-8"))


def decrypt_token(token_encrypted: bytes | None) -> str | None:
    if not token_encrypted:
        return None
    fernet = get_fernet()
    if not fernet:
        return None
    return fernet.decrypt(token_encrypted).decode("utf-8")


def render_qr_png_base64(payload: str) -> str:
    qr = segno.make(payload, error="m")
    buffer = BytesIO()
    qr.save(buffer, kind="png", scale=8, border=2)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
