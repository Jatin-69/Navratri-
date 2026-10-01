import io
from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import User
from apps.events.models import EventConfig
from apps.participants.models import Participant


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        username="admin",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="staff",
        role=User.Role.STAFF,
    )


@pytest.fixture
def event_config(db):
    return EventConfig.objects.create(start_date=date(2026, 10, 1), end_date=date(2026, 10, 9))


@pytest.fixture
def photo_file():
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buffer, format="PNG")
    return SimpleUploadedFile("photo.png", buffer.getvalue(), content_type="image/png")


@pytest.fixture
def participant(db, photo_file):
    participant, token = Participant.create_with_new_token(
        name="Priya",
        phone="9876543210",
        photo=photo_file,
        extra_identifier="",
    )
    participant._raw_token = token
    return participant
