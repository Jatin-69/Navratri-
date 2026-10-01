from datetime import date

import time_machine

from apps.core import dates
from apps.events.models import EventConfig


def test_navratri_day_mapping():
    assert dates.get_navratri_day(date(2026, 10, 1), date(2026, 10, 1)) == 1
    assert dates.get_navratri_day(date(2026, 10, 9), date(2026, 10, 1)) == 9


def test_distribution_status_windows(db):
    event = EventConfig.objects.create(start_date=date(2026, 10, 1), end_date=date(2026, 10, 9))
    assert dates.get_distribution_status(event, date(2026, 9, 30)).code == dates.NOT_STARTED
    assert dates.get_distribution_status(event, date(2026, 10, 1)).code == dates.ACTIVE
    assert dates.get_distribution_status(event, date(2026, 10, 9)).code == dates.ACTIVE
    assert dates.get_distribution_status(event, date(2026, 10, 10)).code == dates.ENDED


def test_ist_business_date_from_utc_boundary():
    with time_machine.travel("2026-09-30 20:00:00+00:00"):
        assert dates.get_current_india_date() == date(2026, 10, 1)
