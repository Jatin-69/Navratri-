from django.urls import path

from .views import participant_create, participant_detail, participant_edit, participant_list

app_name = "participants"

urlpatterns = [
    path("", participant_list, name="list"),
    path("new/", participant_create, name="create"),
    path("<int:pk>/", participant_detail, name="detail"),
    path("<int:pk>/edit/", participant_edit, name="edit"),
]
