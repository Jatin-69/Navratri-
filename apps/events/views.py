from django.contrib import messages
from django.shortcuts import redirect, render

from apps.claims.models import Claim
from apps.core.decorators import role_required

from .forms import EventConfigForm
from .models import EventConfig


@role_required("ADMIN")
def event_config_view(request):
    instance = EventConfig.get_solo() or EventConfig(pk=1)
    has_claims = Claim.objects.exists()
    if request.method == "POST":
        form = EventConfigForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Event configuration updated")
            return redirect("events:config")
    else:
        form = EventConfigForm(instance=instance)
    return render(request, "events/config.html", {"form": form, "has_claims": has_claims})
