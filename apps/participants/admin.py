from django.contrib import admin

from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("participant_code", "name", "phone", "qr_active")
    search_fields = ("participant_code", "name", "phone")
