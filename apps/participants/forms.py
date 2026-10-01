from django import forms

from .models import Participant


class ParticipantForm(forms.ModelForm):
    register_anyway = forms.BooleanField(required=False)

    class Meta:
        model = Participant
        fields = ["name", "phone", "photo", "extra_identifier", "register_anyway"]

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Photo must be <= 2MB")
        return photo

    def clean(self):
        cleaned = super().clean()
        phone = cleaned.get("phone")
        register_anyway = cleaned.get("register_anyway")
        if phone:
            normalized = Participant.normalize_phone(phone)
            qs = Participant.objects.filter(phone_normalized=normalized)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists() and not register_anyway:
                existing = qs.first()
                raise forms.ValidationError(
                    f"Possible duplicate phone found: {existing.participant_code} {existing.name}. Tick 'register anyway'."
                )
        return cleaned
