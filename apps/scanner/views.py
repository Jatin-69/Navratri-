import json

from django.core import signing
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import localtime
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from apps.claims.models import Claim
from apps.claims.services import ClaimResultCode, create_claim
from apps.core.dates import (
    DistributionStatus,
    get_current_india_date,
    get_distribution_status,
    get_navratri_day,
)
from apps.core.decorators import role_required
from apps.events.models import EventConfig
from apps.participants.models import Participant
from apps.qr.services import maybe_extract_token, token_hash

SIGNER = signing.TimestampSigner(salt="claim-ref")


@role_required("ADMIN", "STAFF")
def scanner_page(request):
    return render(request, "scanner/page.html")


def _json_error(code, message, status=400, **extra):
    payload = {"code": code, "message": message}
    payload.update(extra)
    return JsonResponse(payload, status=status)


@require_POST
@role_required("ADMIN", "STAFF")
@ratelimit(key="user", rate="60/m", method="POST", block=True)
def scan_api(request):
    data = json.loads(request.body.decode("utf-8") or "{}")
    raw_token = data.get("token", "")
    token = maybe_extract_token(raw_token)
    if not token:
        return _json_error("INVALID_QR", "Invalid QR code.")

    participant = Participant.objects.filter(qr_token_hash=token_hash(token), qr_active=True).first()
    if not participant:
        return _json_error("INVALID_QR", "This QR is not registered.")

    config = EventConfig.get_solo()
    if not config:
        return _json_error("EVENT_NOT_CONFIGURED", "Event dates are not configured.", 503)

    today = get_current_india_date()
    status = get_distribution_status(today, config.start_date, config.end_date)
    if status == DistributionStatus.NOT_STARTED:
        return _json_error("NOT_STARTED", "Distribution has not started yet.")
    if status == DistributionStatus.ENDED:
        return _json_error("ENDED", "Distribution has ended.")

    navratri_day = get_navratri_day(today, config.start_date)
    claim = Claim.objects.select_related("claimed_by").filter(participant=participant, distribution_date=today).first()

    if claim:
        return JsonResponse(
            {
                "code": "ALREADY_CLAIMED",
                "message": "This participant has already collected today's prop.",
                "participant": {
                    "id": participant.id,
                    "name": participant.name,
                    "participant_code": participant.participant_code,
                    "photo_url": participant.photo.url if participant.photo else "",
                },
                "navratri_day": navratri_day,
                "claimed_at": localtime(claim.claimed_at).isoformat(),
                "claimed_by": claim.claimed_by.get_full_name() or claim.claimed_by.username,
            }
        )

    claim_ref = SIGNER.sign(str(participant.id))
    return JsonResponse(
        {
            "code": "NOT_COLLECTED",
            "message": "Participant verified.",
            "participant": {
                "id": participant.id,
                "name": participant.name,
                "participant_code": participant.participant_code,
                "photo_url": participant.photo.url if participant.photo else "",
            },
            "navratri_day": navratri_day,
            "claim_ref": claim_ref,
        }
    )


@require_POST
@role_required("ADMIN", "STAFF")
@ratelimit(key="user", rate="60/m", method="POST", block=True)
def claim_api(request):
    data = json.loads(request.body.decode("utf-8") or "{}")
    claim_ref = data.get("claim_ref", "")
    if not claim_ref:
        return _json_error("INVALID_REQUEST", "Missing claim reference.")

    try:
        participant_id = int(SIGNER.unsign(claim_ref, max_age=300))
    except signing.BadSignature:
        return _json_error("INVALID_REQUEST", "Invalid or expired claim reference.")

    participant = Participant.objects.filter(id=participant_id, qr_active=True).first()
    if not participant:
        return _json_error("INVALID_QR", "Invalid QR code.")

    code, claim = create_claim(participant, request.user)
    if code == ClaimResultCode.OK:
        return JsonResponse(
            {
                "code": "OK",
                "message": "Prop distributed successfully.",
                "participant_name": participant.name,
                "navratri_day": claim.navratri_day,
                "claimed_at": localtime(claim.claimed_at).isoformat(),
            }
        )
    if code == ClaimResultCode.ALREADY_CLAIMED:
        return _json_error(
            "ALREADY_CLAIMED",
            "This participant has already collected today's prop.",
            claimed_by=claim.claimed_by.username,
            claimed_at=localtime(claim.claimed_at).isoformat(),
        )
    if code == ClaimResultCode.NOT_STARTED:
        return _json_error("NOT_STARTED", "Distribution has not started yet.")
    if code == ClaimResultCode.ENDED:
        return _json_error("ENDED", "Distribution has ended.")
    return _json_error("EVENT_NOT_CONFIGURED", "Event dates are not configured.", status=503)
