import csv

from django.http import StreamingHttpResponse
from django.utils import timezone
from zoneinfo import ZoneInfo

from apps.claims.models import Claim
from apps.core.decorators import role_required
from apps.participants.models import Participant

IST = ZoneInfo("Asia/Kolkata")


class Echo:
    def write(self, value):
        return value


def sanitize_csv_cell(value):
    text = str(value)
    if text.startswith(("=", "+", "-", "@")):
        return f"'{text}"
    return text


@role_required("ADMIN")
def participant_report_csv(request):
    rows = Participant.objects.order_by("participant_code").values_list(
        "participant_code", "name", "phone", "created_at", "qr_active"
    )

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    def stream():
        yield writer.writerow(["Participant Code", "Name", "Phone", "Registration Date", "QR Active"])
        for row in rows.iterator():
            yield writer.writerow([sanitize_csv_cell(v) for v in row])

    response = StreamingHttpResponse(stream(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="participants.csv"'
    return response


@role_required("ADMIN")
def distribution_report_csv(request):
    claims = Claim.objects.select_related("participant", "claimed_by").order_by("distribution_date", "participant__participant_code")

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    def stream():
        yield writer.writerow(["Participant", "Day", "Distribution Date", "Claim Time IST", "Staff"])
        for claim in claims.iterator():
            claim_time = timezone.localtime(claim.claimed_at, IST).strftime("%d-%m-%Y %I:%M:%S %p IST")
            yield writer.writerow(
                [
                    sanitize_csv_cell(claim.participant.participant_code),
                    sanitize_csv_cell(claim.navratri_day),
                    sanitize_csv_cell(claim.distribution_date),
                    sanitize_csv_cell(claim_time),
                    sanitize_csv_cell(claim.claimed_by.get_username()),
                ]
            )

    response = StreamingHttpResponse(stream(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="distribution.csv"'
    return response
