from django.contrib import admin

from .models import EventConfig


@admin.register(EventConfig)
class EventConfigAdmin(admin.ModelAdmin):
    list_display = ("start_date", "end_date", "timezone", "updated_at")
