from django.conf import settings
from django.db import models
from django.utils import timezone


class Claim(models.Model):
    participant = models.ForeignKey("participants.Participant", on_delete=models.PROTECT, related_name="claims")
    distribution_date = models.DateField(db_index=True)
    navratri_day = models.PositiveSmallIntegerField()
    claimed_at = models.DateTimeField(default=timezone.now)
    claimed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="claims_given")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "distribution_date"],
                name="uniq_claim_per_participant_per_day",
            )
        ]

    def __str__(self):
        return f"{self.participant} D{self.navratri_day} {self.distribution_date}"
