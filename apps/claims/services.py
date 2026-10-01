from __future__ import annotations

from django.db import IntegrityError, transaction

from apps.claims.models import Claim
from apps.core import dates
from apps.events.models import EventConfig


class ClaimResult:
    def __init__(self, code, claim=None):
        self.code = code
        self.claim = claim


def create_claim(participant, staff_user):
    event = EventConfig.get_solo()
    if not event:
        return ClaimResult("EVENT_NOT_CONFIGURED")

    status = dates.get_distribution_status(event)
    if status.code != dates.ACTIVE:
        return ClaimResult(status.code)

    navratri_day = dates.get_navratri_day(status.today, event.start_date)

    try:
        with transaction.atomic():
            claim = Claim.objects.create(
                participant=participant,
                distribution_date=status.today,
                navratri_day=navratri_day,
                claimed_by=staff_user,
            )
    except IntegrityError:
        return ClaimResult("ALREADY_CLAIMED")

    return ClaimResult("OK", claim=claim)
