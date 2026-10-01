from datetime import date, datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


class DistributionStatus:
    NOT_STARTED = "NOT_STARTED"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


def get_current_india_datetime() -> datetime:
    return datetime.now(IST)


def get_current_india_date() -> date:
    return get_current_india_datetime().date()


def get_navratri_day(today: date, start_date: date) -> int:
    return (today - start_date).days + 1


def get_distribution_status(today: date, start_date: date, end_date: date) -> str:
    if today < start_date:
        return DistributionStatus.NOT_STARTED
    if today > end_date:
        return DistributionStatus.ENDED
    return DistributionStatus.ACTIVE


def is_distribution_active(today: date, start_date: date, end_date: date) -> bool:
    return get_distribution_status(today, start_date, end_date) == DistributionStatus.ACTIVE
