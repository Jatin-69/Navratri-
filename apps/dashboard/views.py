from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from apps.claims.models import Claim
from apps.core.dates import get_current_india_date, get_navratri_day
from apps.events.models import EventConfig
from apps.participants.models import Participant


@login_required
def home(request):
    config = EventConfig.get_solo()
    today = get_current_india_date()
    total = Participant.objects.count()
    collected_today = Claim.objects.filter(distribution_date=today).count()
    day_number = get_navratri_day(today, config.start_date) if config and config.start_date <= today <= config.end_date else None
    daywise = Claim.objects.values("navratri_day").annotate(total=Count("id")).order_by("navratri_day")

    context = {
        "config": config,
        "today": today,
        "day_number": day_number,
        "total": total,
        "collected_today": collected_today,
        "pending_today": max(total - collected_today, 0),
        "collection_rate": (collected_today / total * 100) if total else 0,
        "daywise": daywise,
    }

    if request.user.role == "STAFF":
        return render(request, "dashboard/staff_home.html", context)
    return render(request, "dashboard/admin_home.html", context)
