from concurrent.futures import ThreadPoolExecutor

import pytest
from django.db import connection
from django.urls import reverse

from apps.claims.models import Claim


@pytest.mark.django_db(transaction=True)
def test_concurrent_claim_only_one_success(staff_user, participant, event_config):
    if "postgresql" not in connection.vendor:
        pytest.skip("Concurrency uniqueness test requires PostgreSQL")

    from django.test import Client

    c = Client()
    c.force_login(staff_user)
    scan = c.post(reverse("scanner:scan_api"), {"token": participant._raw_token}).json()

    def do_claim():
        client = Client()
        client.force_login(staff_user)
        return client.post(reverse("scanner:claim_api"), {"signed_ref": scan["signed_ref"]}).status_code

    with ThreadPoolExecutor(max_workers=2) as ex:
        codes = list(ex.map(lambda _: do_claim(), [1, 2]))

    assert sorted(codes) == [200, 409]
    assert Claim.objects.count() == 1
