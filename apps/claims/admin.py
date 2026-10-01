from django.contrib import admin

from .models import Claim


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("participant", "distribution_date", "navratri_day", "claimed_by", "claimed_at")
    readonly_fields = ("participant", "distribution_date", "navratri_day", "claimed_by", "claimed_at", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
