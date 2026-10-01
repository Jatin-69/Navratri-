from django.contrib.auth.decorators import login_required
from django.core import signing
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from apps.claims.models import Claim
from apps.claims.services import create_claim
from apps.core import dates
from apps.core.decorators import role_required
from apps.events.models import EventConfig
from apps.participants.models import Participant
from apps.qr.services import extract_token, hash_token


def _role_allowed(user):
    return user.is_authenticated and (user.role in ["ADMIN", "STAFF"] or user.is_superuser)


@login_required
def scanner_page(request):
    if not _role_allowed(request.user):
        return JsonResponse({"code": "FORBIDDEN"}, status=403)
    return render(request, "scanner/scanner.html")


@require_POST
@login_required
@ratelimit(key="user_or_ip", rate="120/m", block=False)
def scan_api(request):
    if not _role_allowed(request.user):
        return JsonResponse({"code": "FORBIDDEN"}, status=403)

    token = extract_token(request.POST.get("token", ""))
    if not token:
        return JsonResponse({"code": "INVALID_QR", "message": "Invalid QR code."}, status=400)

    token_hash = hash_token(token)
    participant = Participant.objects.filter(qr_token_hash=token_hash, qr_active=True).first()
    if not participant:
        return JsonResponse({"code": "INVALID_QR", "message": "This QR is not registered."}, status=404)

    event = EventConfig.get_solo()
    if not event:
        return JsonResponse({"code": "EVENT_NOT_CONFIGURED", "message": "Event is not configured."}, status=400)

    status = dates.get_distribution_status(event)
    if status.code == dates.NOT_STARTED:
        return JsonResponse({"code": "NOT_STARTED", "message": "Distribution has not started yet."}, status=400)
    if status.code == dates.ENDED:
        return JsonResponse({"code": "ENDED", "message": "Distribution has ended."}, status=400)

    navratri_day = dates.get_navratri_day(status.today, event.start_date)
    existing = Claim.objects.filter(participant=participant, distribution_date=status.today).select_related(
        "claimed_by"
    ).first()
    signed_ref = signing.dumps({"participant_id": participant.id}, salt="scan-ref")

    if existing:
        return JsonResponse(
            {
                "code": "ALREADY_CLAIMED",
                "message": "Already collected today",
                "participant": {
                    "id": participant.id,
                    "name": participant.name,
                    "participant_code": participant.participant_code,
                    "photo": participant.photo.url if participant.photo else "",
                },
                "day": navratri_day,
                "claimed_at": existing.claimed_at.isoformat(),
                "claimed_by": existing.claimed_by.get_username(),
                "signed_ref": signed_ref,
            }
        )

    return JsonResponse(
        {
            "code": "NOT_COLLECTED",
            "participant": {
                "id": participant.id,
                "name": participant.name,
                "participant_code": participant.participant_code,
                "photo": participant.photo.url if participant.photo else "",
            },
            "day": navratri_day,
            "signed_ref": signed_ref,
        }
    )


@require_POST
@login_required
@ratelimit(key="user_or_ip", rate="120/m", block=False)
def claim_api(request):
    if not _role_allowed(request.user):
        return JsonResponse({"code": "FORBIDDEN"}, status=403)

    signed_ref = request.POST.get("signed_ref", "")
    try:
        payload = signing.loads(signed_ref, salt="scan-ref", max_age=120)
    except signing.BadSignature:
        return JsonResponse({"code": "INVALID_REQUEST", "message": "Invalid request."}, status=400)

    participant = Participant.objects.filter(id=payload.get("participant_id"), qr_active=True).first()
    if not participant:
        return JsonResponse({"code": "INVALID_QR", "message": "This QR is not registered."}, status=404)

    result = create_claim(participant, request.user)
    if result.code == "OK":
        return JsonResponse(
            {
                "code": "OK",
                "message": "Prop distributed successfully",
                "participant": participant.name,
                "day": result.claim.navratri_day,
                "claimed_at": result.claim.claimed_at.isoformat(),
            }
        )
    if result.code == "ALREADY_CLAIMED":
        return JsonResponse(
            {"code": "ALREADY_CLAIMED", "message": "This participant has already collected today's prop."},
            status=409,
        )
    if result.code == dates.NOT_STARTED:
        return JsonResponse({"code": "NOT_STARTED", "message": "Distribution has not started yet."}, status=400)
    if result.code == dates.ENDED:
        return JsonResponse({"code": "ENDED", "message": "Distribution has ended."}, status=400)
    return JsonResponse({"code": "EVENT_NOT_CONFIGURED", "message": "Event is not configured."}, status=400)
