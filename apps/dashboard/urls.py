from django.urls import path

from .views import admin_dashboard, home, staff_dashboard

app_name = "dashboard"

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin_dashboard, name="admin_dashboard"),
    path("staff/", staff_dashboard, name="staff_dashboard"),
]
