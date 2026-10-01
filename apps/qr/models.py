from django.conf import settings
from django.db import models


class QRRegenerationLog(models.Model):
    participant = models.ForeignKey("participants.Participant", on_delete=models.PROTECT, related_name="qr_regenerations")
    regenerated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
