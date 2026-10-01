from django.urls import path

from .views import download_qr, qr_public_landing, regenerate_qr, view_qr

app_name = "qr"

urlpatterns = [
    path("<int:participant_id>/view/", view_qr, name="view"),
    path("<int:participant_id>/download/", download_qr, name="download"),
    path("<int:participant_id>/regenerate/", regenerate_qr, name="regenerate"),
    path("q/<str:token>/", qr_public_landing, name="public_landing"),
]
