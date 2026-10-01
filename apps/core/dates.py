from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from apps.events.models import EventConfig

IST = ZoneInfo("Asia/Kolkata")

NOT_STARTED = "NOT_STARTED"
ACTIVE = "ACTIVE"
ENDED = "ENDED"


@dataclass(frozen=True)
class DistributionStatus:
    code: str
    today: datetime.date


def get_current_india_datetime() -> datetime:
    return datetime.now(IST)


def get_current_india_date():
    return get_current_india_datetime().date()


def get_navratri_day(today, start_date) -> int:
    return (today - start_date).days + 1


def get_distribution_status(event: EventConfig, today=None) -> DistributionStatus:
    business_date = today or get_current_india_date()
    if business_date < event.start_date:
        return DistributionStatus(code=NOT_STARTED, today=business_date)
    if business_date > event.end_date:
        return DistributionStatus(code=ENDED, today=business_date)
    return DistributionStatus(code=ACTIVE, today=business_date)


def is_distribution_active(event: EventConfig, today=None) -> bool:
    return get_distribution_status(event, today).code == ACTIVE
