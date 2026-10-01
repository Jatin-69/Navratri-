from django import forms

from .models import Participant, normalize_phone


class ParticipantForm(forms.ModelForm):
    register_anyway = forms.BooleanField(required=False)

    class Meta:
        model = Participant
        fields = ["name", "phone", "photo", "extra_identifier", "register_anyway"]

    def clean_photo(self):
        photo = self.cleaned_data["photo"]
        if photo.size > 3 * 1024 * 1024:
            raise forms.ValidationError("Photo must be <= 3MB")
        return photo

    def clean(self):
        cleaned = super().clean()
        phone = normalize_phone(cleaned.get("phone", ""))
        register_anyway = cleaned.get("register_anyway")
        duplicates = [p for p in Participant.objects.all() if p.normalized_phone == phone]
        if duplicates and not register_anyway:
            raise forms.ValidationError(
                f"Possible duplicate phone with {duplicates[0].participant_code}. Check register anyway to continue."
            )
        return cleaned
