from django.urls import path

from .views import print_cards, qr_preview

app_name = "qr"

urlpatterns = [
    path("print/", print_cards, name="print_cards"),
    path("preview/<int:pk>/", qr_preview, name="preview"),
]
