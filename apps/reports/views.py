import csv

from django.http import StreamingHttpResponse

from apps.claims.models import Claim
from apps.core.decorators import role_required
from apps.participants.models import Participant


def _safe_cell(value):
    value = str(value)
    return f"'{value}" if value.startswith(("=", "+", "-", "@")) else value


class Echo:
    def write(self, value):
        return value


@role_required("ADMIN")
def participant_report(request):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    rows = (["Name", "Phone", "Registration Date", "QR Status"],)
    participants = Participant.objects.all().order_by("participant_code")
    data_rows = (
        [_safe_cell(p.name), _safe_cell(p.phone), p.created_at.date().isoformat(), "ACTIVE" if p.qr_active else "INACTIVE"]
        for p in participants
    )

    def row_generator():
        for row in rows:
            yield writer.writerow(row)
        for row in data_rows:
            yield writer.writerow(row)

    response = StreamingHttpResponse(row_generator(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="participants.csv"'
    return response


@role_required("ADMIN")
def distribution_report(request):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    claims = Claim.objects.select_related("participant", "claimed_by").order_by("distribution_date", "participant__participant_code")

    def row_generator():
        yield writer.writerow(["Participant", "Day", "Distribution Date", "Claim Time", "Staff"])
        for claim in claims:
            yield writer.writerow(
                [
                    _safe_cell(claim.participant.name),
                    claim.navratri_day,
                    claim.distribution_date.isoformat(),
                    claim.claimed_at.astimezone().isoformat(),
                    _safe_cell(claim.claimed_by.username),
                ]
            )

    response = StreamingHttpResponse(row_generator(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="distribution.csv"'
    return response
