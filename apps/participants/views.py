from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.decorators import role_required
from apps.events.models import EventConfig

from .forms import ParticipantForm
from .models import Participant


@role_required("ADMIN")
def participant_list(request):
    query = request.GET.get("q", "").strip()
    participants = Participant.objects.all().order_by("participant_code")
    if query:
        participants = participants.filter(
            Q(name__icontains=query) | Q(phone__icontains=query) | Q(participant_code__icontains=query)
        )
    paginator = Paginator(participants, 50)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "participants/list.html", {"page_obj": page_obj, "query": query})


@role_required("ADMIN")
def participant_create(request):
    if request.method == "POST":
        form = ParticipantForm(request.POST, request.FILES)
        if form.is_valid():
            participant, _ = Participant.create_with_new_token(
                name=form.cleaned_data["name"],
                phone=form.cleaned_data["phone"],
                photo=form.cleaned_data["photo"],
                extra_identifier=form.cleaned_data["extra_identifier"],
            )
            messages.success(request, f"Participant {participant.participant_code} registered.")
            return redirect("participants:detail", pk=participant.pk)
    else:
        form = ParticipantForm()
    return render(request, "participants/form.html", {"form": form})


@role_required("ADMIN", "STAFF")
def participant_detail(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    config = EventConfig.get_solo()
    days = []
    if config:
        claims = set(participant.claims.values_list("navratri_day", flat=True))
        for day in range(1, (config.end_date - config.start_date).days + 2):
            days.append({"day": day, "claimed": day in claims})
    return render(request, "participants/detail.html", {"participant": participant, "days": days})


@role_required("ADMIN")
def participant_edit(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == "POST":
        form = ParticipantForm(request.POST, request.FILES, instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant updated.")
            return redirect("participants:detail", pk=participant.pk)
    else:
        form = ParticipantForm(instance=participant)
    return render(request, "participants/form.html", {"form": form})
