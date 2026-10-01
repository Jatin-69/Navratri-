from django.urls import path

from .views import distribution_report, participant_report

app_name = "reports"

urlpatterns = [
    path("participants.csv", participant_report, name="participants"),
    path("distribution.csv", distribution_report, name="distribution"),
]
