from django.urls import path

from .views import distribution_report_csv, participant_report_csv

app_name = "reports"

urlpatterns = [
    path("participants.csv", participant_report_csv, name="participants_csv"),
    path("distribution.csv", distribution_report_csv, name="distribution_csv"),
]
