from django.contrib import admin

from .models import QRRegenerationLog


@admin.register(QRRegenerationLog)
class QRRegenerationLogAdmin(admin.ModelAdmin):
    list_display = ("participant", "regenerated_by", "created_at")
    readonly_fields = ("participant", "regenerated_by", "created_at")
