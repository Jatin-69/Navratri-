from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render

from apps.claims.models import Claim
from apps.core import dates
from apps.core.decorators import role_required
from apps.events.models import EventConfig
from apps.participants.models import Participant


@login_required
def home(request):
    if request.user.role == "ADMIN" or request.user.is_superuser:
        return redirect("dashboard:admin_dashboard")
    return redirect("dashboard:staff_dashboard")


@role_required("ADMIN")
def admin_dashboard(request):
    event = EventConfig.get_solo()
    total_participants = Participant.objects.count()
    status = dates.get_distribution_status(event) if event else None
    today = status.today if status else None
    today_claims = Claim.objects.filter(distribution_date=today).count() if today else 0
    collection_rate = (today_claims / total_participants * 100) if total_participants else 0
    day_stats = (
        Claim.objects.values("navratri_day")
        .annotate(total=Count("id"))
        .order_by("navratri_day")
    )
    return render(
        request,
        "dashboard/admin.html",
        {
            "event": event,
            "today": today,
            "today_claims": today_claims,
            "total_participants": total_participants,
            "pending": max(total_participants - today_claims, 0),
            "collection_rate": collection_rate,
            "day_stats": day_stats,
            "day_number": dates.get_navratri_day(today, event.start_date)
            if event and today and status.code == dates.ACTIVE
            else None,
        },
    )


@role_required("ADMIN", "STAFF")
def staff_dashboard(request):
    event = EventConfig.get_solo()
    status = dates.get_distribution_status(event) if event else None
    today = status.today if status else None
    collected = Claim.objects.filter(distribution_date=today).count() if today else 0
    day_number = (
        dates.get_navratri_day(today, event.start_date)
        if event and today and status.code == dates.ACTIVE
        else None
    )
    return render(
        request,
        "dashboard/staff.html",
        {"event": event, "collected": collected, "day_number": day_number},
    )
