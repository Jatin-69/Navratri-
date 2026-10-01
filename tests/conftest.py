from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import User
from apps.events.models import EventConfig
from apps.participants.models import Participant
from apps.qr.services import encrypt_token, generate_token, hash_token


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(username="admin", role=User.Role.ADMIN)


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username="staff", role=User.Role.STAFF)


@pytest.fixture
def event_config(db):
    return EventConfig.objects.create(
        start_date=date(2026, 10, 1), end_date=date(2026, 10, 9), timezone="Asia/Kolkata"
    )


@pytest.fixture
def participant(db):
    token = generate_token()
    p = Participant.objects.create(
        participant_code="NAV-001",
        name="Priya",
        phone="9876543210",
        phone_normalized="9876543210",
        photo=SimpleUploadedFile("a.jpg", b"filecontent", content_type="image/jpeg"),
        qr_token_hash=hash_token(token),
        qr_token_encrypted=encrypt_token(token),
        qr_active=True,
    )
    p._raw_token = token
    return p
