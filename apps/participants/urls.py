from django.urls import path

from . import views

app_name = "participants"

urlpatterns = [
    path("", views.participant_list, name="list"),
    path("new/", views.participant_create, name="create"),
    path("<int:pk>/", views.participant_detail, name="detail"),
    path("<int:pk>/edit/", views.participant_update, name="edit"),
    path("<int:pk>/qr/", views.participant_qr, name="qr"),
    path("<int:pk>/qr/download/", views.participant_qr_download, name="qr_download"),
    path("<int:pk>/qr/regenerate/", views.participant_regenerate_qr, name="qr_regenerate"),
]
