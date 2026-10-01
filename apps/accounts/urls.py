from django.urls import path

from .views import UserLoginView, logout_view, staff_create_view

app_name = "accounts"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("staff/new/", staff_create_view, name="staff_create"),
]
