from datetime import datetime

import time_machine
from django.urls import reverse

from apps.claims.models import Claim


def test_scan_never_creates_claim(client, staff_user, participant, event_config):
    with time_machine.travel("2026-10-03 09:30:00+05:30"):
        client.force_login(staff_user)
        res = client.post(reverse("scanner:scan_api"), {"token": participant._raw_token})
    assert res.status_code == 200
    assert Claim.objects.count() == 0


def test_first_claim_succeeds_second_rejected(client, staff_user, participant, event_config):
    with time_machine.travel("2026-10-03 10:00:00+05:30"):
        client.force_login(staff_user)
        scan = client.post(reverse("scanner:scan_api"), {"token": participant._raw_token}).json()
        ok = client.post(reverse("scanner:claim_api"), {"signed_ref": scan["signed_ref"]})
        duplicate = client.post(reverse("scanner:claim_api"), {"signed_ref": scan["signed_ref"]})
    assert ok.status_code == 200
    assert ok.json()["code"] == "OK"
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "ALREADY_CLAIMED"


def test_next_day_claim_allowed(client, staff_user, participant, event_config):
    with time_machine.travel("2026-10-03 10:00:00+05:30"):
        client.force_login(staff_user)
        scan = client.post(reverse("scanner:scan_api"), {"token": participant._raw_token}).json()
        client.post(reverse("scanner:claim_api"), {"signed_ref": scan["signed_ref"]})
    with time_machine.travel("2026-10-04 10:00:00+05:30"):
        client.force_login(staff_user)
        scan2 = client.post(reverse("scanner:scan_api"), {"token": participant._raw_token}).json()
        next_day = client.post(reverse("scanner:claim_api"), {"signed_ref": scan2["signed_ref"]})
    assert next_day.status_code == 200
    assert Claim.objects.count() == 2
