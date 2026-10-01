from datetime import date

import time_machine

from apps.core.dates import (
    DistributionStatus,
    get_current_india_date,
    get_distribution_status,
    get_navratri_day,
)


def test_navratri_day_calculation():
    assert get_navratri_day(date(2026, 10, 1), date(2026, 10, 1)) == 1
    assert get_navratri_day(date(2026, 10, 9), date(2026, 10, 1)) == 9


def test_distribution_status_values():
    start = date(2026, 10, 1)
    end = date(2026, 10, 9)
    assert get_distribution_status(date(2026, 9, 30), start, end) == DistributionStatus.NOT_STARTED
    assert get_distribution_status(date(2026, 10, 1), start, end) == DistributionStatus.ACTIVE
    assert get_distribution_status(date(2026, 10, 10), start, end) == DistributionStatus.ENDED


def test_ist_date_is_used_even_if_utc_previous_day():
    with time_machine.travel("2026-09-30 20:00:00+00:00"):
        assert get_current_india_date().isoformat() == "2026-10-01"
