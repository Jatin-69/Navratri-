from django.core.exceptions import ValidationError
from django.db import models


class EventConfig(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    timezone = models.CharField(max_length=40, default="Asia/Kolkata")
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date must be on or after start date")

    def save(self, *args, **kwargs):
        self.pk = 1
        self.full_clean()
        return super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        return cls.objects.first()

    def __str__(self):
        return f"{self.start_date} to {self.end_date}"
