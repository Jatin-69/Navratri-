from django.urls import path

from .views import event_config_view

app_name = "events"

urlpatterns = [
    path("config/", event_config_view, name="config"),
]
