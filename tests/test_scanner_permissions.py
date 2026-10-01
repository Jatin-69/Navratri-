import json

import pytest
import time_machine
from django.urls import reverse

from apps.claims.models import Claim


@pytest.mark.django_db
def test_scan_does_not_create_claim(client, staff_user, event_config, participant):
    client.force_login(staff_user)
    with time_machine.travel("2026-10-02 09:00:00+05:30"):
        res = client.post(
            reverse("scanner:scan_api"),
            data=json.dumps({"token": participant._raw_token}),
            content_type="application/json",
        )
    assert res.status_code == 200
    assert res.json()["code"] == "NOT_COLLECTED"
    assert Claim.objects.count() == 0


@pytest.mark.django_db
def test_claim_requires_staff_auth(client, event_config, participant):
    res = client.post(reverse("scanner:claim_api"), data="{}", content_type="application/json")
    assert res.status_code in {302, 403}


@pytest.mark.django_db
def test_staff_forbidden_from_admin_event_config(client, staff_user):
    client.force_login(staff_user)
    res = client.get(reverse("events:config"))
    assert res.status_code == 403
