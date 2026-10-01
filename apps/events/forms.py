from django import forms

from .models import EventConfig


class EventConfigForm(forms.ModelForm):
    class Meta:
        model = EventConfig
        fields = ["start_date", "end_date", "timezone"]
