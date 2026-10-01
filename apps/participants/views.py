from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.claims.models import Claim, QRRegenerationLog
from apps.core.decorators import role_required
from apps.qr.services import create_qr_png, decrypt_token, encrypt_token, generate_token, hash_token

from .forms import ParticipantForm
from .models import Participant


def _next_participant_code():
    latest = Participant.objects.order_by("-id").first()
    if not latest:
        return "NAV-001"
    try:
        number = int(latest.participant_code.split("-")[-1]) + 1
    except (ValueError, IndexError):
        number = latest.id + 1
    return f"NAV-{number:03d}"


@role_required("ADMIN")
def participant_list(request):
    query = request.GET.get("q", "").strip()
    participants = Participant.objects.all().order_by("participant_code")
    if query:
        participants = participants.filter(name__icontains=query) | participants.filter(
            phone__icontains=query
        ) | participants.filter(participant_code__icontains=query)
    paginator = Paginator(participants, 50)
    page = request.GET.get("page")
    return render(
        request,
        "participants/list.html",
        {"page_obj": paginator.get_page(page), "query": query},
    )


@role_required("ADMIN")
def participant_create(request):
    if request.method == "POST":
        form = ParticipantForm(request.POST, request.FILES)
        if form.is_valid():
            participant = form.save(commit=False)
            participant.participant_code = _next_participant_code()
            token = generate_token()
            participant.qr_token_hash = hash_token(token)
            participant.qr_token_encrypted = encrypt_token(token)
            participant.save()
            messages.success(request, "Participant registered")
            return redirect("participants:detail", pk=participant.pk)
    else:
        form = ParticipantForm()
    return render(request, "participants/form.html", {"form": form, "is_create": True})


@role_required("ADMIN")
def participant_update(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == "POST":
        form = ParticipantForm(request.POST, request.FILES, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant updated")
            return redirect("participants:detail", pk=participant.pk)
    else:
        form = ParticipantForm(instance=participant)
    return render(request, "participants/form.html", {"form": form, "participant": participant})


@role_required("ADMIN")
def participant_detail(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    claims = Claim.objects.filter(participant=participant).order_by("distribution_date")
    claim_days = {c.navratri_day for c in claims}
    day_grid = [{"day": i, "claimed": i in claim_days} for i in range(1, 10)]
    return render(
        request,
        "participants/detail.html",
        {"participant": participant, "claims": claims, "day_grid": day_grid},
    )


@role_required("ADMIN")
def participant_qr(request, pk):
    participant = get_object_or_404(Participant, pk=pk, qr_active=True)
    token = decrypt_token(participant.qr_token_encrypted)
    qr_data = create_qr_png(token)
    response = HttpResponse(qr_data, content_type="image/png")
    response["Content-Disposition"] = (
        f'inline; filename="{participant.participant_code}-qr.png"'
    )
    return response


@role_required("ADMIN")
def participant_qr_download(request, pk):
    response = participant_qr(request, pk)
    response["Content-Disposition"] = response["Content-Disposition"].replace("inline", "attachment")
    return response


@role_required("ADMIN")
def participant_regenerate_qr(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    token = generate_token()
    participant.qr_token_hash = hash_token(token)
    participant.qr_token_encrypted = encrypt_token(token)
    participant.save(update_fields=["qr_token_hash", "qr_token_encrypted", "updated_at"])
    QRRegenerationLog.objects.create(participant=participant, regenerated_by=request.user)
    messages.success(request, "QR token regenerated")
    return redirect("participants:detail", pk=participant.pk)


@login_required
def public_qr_landing(request, token):
    return render(request, "scanner/public_qr_notice.html", {"token": token})
