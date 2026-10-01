from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.participants.views import public_qr_landing

urlpatterns = [
    path("secure-admin/", admin.site.urls),
    path("", include("apps.dashboard.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("participants/", include("apps.participants.urls")),
    path("events/", include("apps.events.urls")),
    path("scanner/", include("apps.scanner.urls")),
    path("reports/", include("apps.reports.urls")),
    path("qr/", include("apps.qr.urls")),
    path("q/<str:token>/", public_qr_landing, name="public_qr_landing"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
