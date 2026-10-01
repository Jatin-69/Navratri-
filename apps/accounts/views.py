from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from apps.core.decorators import role_required

from .forms import LoginForm, StaffCreateForm


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm

    def get_success_url(self):
        return "/"


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@role_required("ADMIN")
def staff_create_view(request):
    if request.method == "POST":
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.role = "STAFF"
            staff.save()
            messages.success(request, "Staff account created")
            return redirect("dashboard:admin_dashboard")
    else:
        form = StaffCreateForm()
    return render(request, "accounts/staff_create.html", {"form": form})
