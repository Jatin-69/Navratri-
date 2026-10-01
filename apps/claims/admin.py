from django.contrib import admin

from .models import Claim, QRRegenerationLog

admin.site.register(Claim)
admin.site.register(QRRegenerationLog)
