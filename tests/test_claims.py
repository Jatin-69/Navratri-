from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
import time_machine
from django.conf import settings

from apps.claims.models import Claim
from apps.claims.services import ClaimResultCode, create_claim
from apps.participants.models import Participant


@pytest.mark.django_db
def test_first_claim_succeeds_second_rejected(event_config, participant, staff_user):
    with time_machine.travel("2026-10-02 08:00:00+05:30"):
        code, claim = create_claim(participant, staff_user)
        assert code == ClaimResultCode.OK
        assert claim.navratri_day == 2

        code2, _ = create_claim(participant, staff_user)
        assert code2 == ClaimResultCode.ALREADY_CLAIMED


@pytest.mark.django_db
def test_next_day_claim_allowed(event_config, participant, staff_user):
    with time_machine.travel("2026-10-01 10:00:00+05:30"):
        assert create_claim(participant, staff_user)[0] == ClaimResultCode.OK
    with time_machine.travel("2026-10-02 10:00:00+05:30"):
        assert create_claim(participant, staff_user)[0] == ClaimResultCode.OK


@pytest.mark.django_db(transaction=True)
def test_concurrent_claims_only_one_succeeds(event_config, staff_user, photo_file):
    if "postgresql" not in settings.DATABASES["default"]["ENGINE"]:
        pytest.skip("Concurrency assertion is meaningful on PostgreSQL")

    participant, _ = Participant.create_with_new_token(
        name="Concurrent",
        phone="9999999999",
        photo=photo_file,
        extra_identifier="",
    )

    with time_machine.travel("2026-10-03 09:00:00+05:30"):
        def claim_once():
            return create_claim(participant, staff_user)[0]

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: claim_once(), [1, 2]))

    assert results.count(ClaimResultCode.OK) == 1
    assert results.count(ClaimResultCode.ALREADY_CLAIMED) == 1
    assert Claim.objects.filter(participant=participant, distribution_date=date(2026, 10, 3)).count() == 1
