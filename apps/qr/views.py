from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import smart_str

from apps.core.decorators import role_required
from apps.participants.models import Participant

from .models import QRRegenerationLog
from .services import decrypt_token, render_qr_png_base64


@role_required("ADMIN")
def view_qr(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    token = decrypt_token(participant.qr_token_encrypted)
    if not token:
        raise Http404("QR token not available. Regenerate QR.")
    qr_image = render_qr_png_base64(token)
    return render(request, "qr/view.html", {"participant": participant, "qr_image": qr_image})


@role_required("ADMIN")
def download_qr(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    token = decrypt_token(participant.qr_token_encrypted)
    if not token:
        raise Http404("QR token not available. Regenerate QR.")
    import base64

    content = base64.b64decode(render_qr_png_base64(token))
    response = HttpResponse(content, content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="{smart_str(participant.participant_code)}.png"'
    return response


@role_required("ADMIN")
def regenerate_qr(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    if request.method == "POST":
        participant.regenerate_qr()
        QRRegenerationLog.objects.create(participant=participant, regenerated_by=request.user)
    return redirect("participants:detail", pk=participant.id)


def qr_public_landing(request, token):
    return render(
        request,
        "qr/public_landing.html",
        {"message": "Please show this QR at the distribution counter."},
    )
