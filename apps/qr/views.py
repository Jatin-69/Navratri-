import base64

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.core.decorators import role_required
from apps.participants.models import Participant

from .services import create_qr_png, decrypt_token


@role_required("ADMIN")
def print_cards(request):
    participants = Participant.objects.filter(qr_active=True).order_by("participant_code")
    ids = request.GET.getlist("ids")
    if ids:
        participants = participants.filter(id__in=ids)

    cards = []
    for p in participants:
        token = decrypt_token(p.qr_token_encrypted)
        cards.append(
            {
                "participant": p,
                "qr_data_url": "data:image/png;base64," + base64.b64encode(create_qr_png(token)).decode(),
            }
        )

    return render(request, "qr/print_cards.html", {"cards": cards})


@role_required("ADMIN")
def qr_preview(request, pk):
    participant = get_object_or_404(Participant, pk=pk, qr_active=True)
    token = decrypt_token(participant.qr_token_encrypted)
    image = create_qr_png(token)
    return HttpResponse(image, content_type="image/png")
