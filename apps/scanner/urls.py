from django.urls import path

from . import views

app_name = "scanner"

urlpatterns = [
    path("", views.scanner_page, name="page"),
    path("api/scan/", views.scan_api, name="scan_api"),
    path("api/claim/", views.claim_api, name="claim_api"),
]
