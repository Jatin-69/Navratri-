from django.db import IntegrityError, transaction

from apps.core.dates import (
    DistributionStatus,
    get_current_india_date,
    get_distribution_status,
    get_navratri_day,
)
from apps.events.models import EventConfig

from .models import Claim


class ClaimResultCode:
    OK = "OK"
    NOT_STARTED = "NOT_STARTED"
    ENDED = "ENDED"
    ALREADY_CLAIMED = "ALREADY_CLAIMED"
    EVENT_NOT_CONFIGURED = "EVENT_NOT_CONFIGURED"


def create_claim(participant, staff_user):
    config = EventConfig.get_solo()
    if not config:
        return ClaimResultCode.EVENT_NOT_CONFIGURED, None

    today = get_current_india_date()
    status = get_distribution_status(today, config.start_date, config.end_date)
    if status == DistributionStatus.NOT_STARTED:
        return ClaimResultCode.NOT_STARTED, None
    if status == DistributionStatus.ENDED:
        return ClaimResultCode.ENDED, None

    navratri_day = get_navratri_day(today, config.start_date)

    try:
        with transaction.atomic():
            claim = Claim.objects.create(
                participant=participant,
                distribution_date=today,
                navratri_day=navratri_day,
                claimed_by=staff_user,
            )
            return ClaimResultCode.OK, claim
    except IntegrityError:
        existing = Claim.objects.select_related("claimed_by").get(participant=participant, distribution_date=today)
        return ClaimResultCode.ALREADY_CLAIMED, existing
