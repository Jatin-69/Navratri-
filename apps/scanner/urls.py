from django.urls import path

from .views import claim_api, scan_api, scanner_page

app_name = "scanner"

urlpatterns = [
    path("", scanner_page, name="page"),
    path("api/scan/", scan_api, name="scan_api"),
    path("api/claim/", claim_api, name="claim_api"),
]
