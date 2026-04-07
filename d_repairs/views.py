from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from c_devices.models import Device
from .models import Repair
from .forms import (
    RepairCreateForm,
    RepairIntakeForm,
    RepairTechnicianForm,
    RepairNoteForm,
)


@login_required
def repair_list(request):
    repairs = Repair.objects.select_related(
        "device", "device__customer", "assigned_to", "created_by"
    ).order_by("-created_at")
    return render(
        request,
        "repairs/repair_list.html",
        {
            "repairs": repairs,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": None},
            ],
        },
    )


@login_required
def repair_detail(request, pk):
    repair = get_object_or_404(
        Repair.objects.select_related(
            "device",
            "device__customer",
            "assigned_to",
            "created_by",
        ).prefetch_related(
            "notes",
            "notes__created_by",
            "payments",
            "payments__created_by",
        ),
        pk=pk,
    )

    try:
        quotation = repair.quotation
        quotation_items = quotation.items.all()
    except Repair.quotation.RelatedObjectDoesNotExist:
        quotation = None
        quotation_items = []

    form = RepairNoteForm()

    return render(
        request,
        "repairs/repair_detail.html",
        {
            "repair": repair,
            "quotation": quotation,
            "quotation_items": quotation_items,
            "form": form,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {"label": f"Repair #{repair.id:04d}", "url": None},
            ],
        },
    )


@login_required
def repair_create(request):
    device_id = request.GET.get("device")
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = RepairCreateForm(request.POST)
        if form.is_valid():
            repair = form.save(commit=False)
            repair.created_by = request.user
            repair.save()
            messages.success(
                request, f"Repair ticket #{repair.id:04d} created successfully."
            )
            return redirect("repairs:detail", pk=repair.pk)
    else:
        form = RepairCreateForm()
        if device_id:
            try:
                device = Device.objects.get(pk=device_id)
                form.fields["device"].initial = device
            except Device.DoesNotExist:
                pass

    return render(
        request,
        "repairs/repair_form.html",
        {
            "form": form,
            "next": next_url,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {"label": "Create Repair", "url": None},
            ],
        },
    )


@login_required
def repair_edit_intake(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    next_url = request.GET.get("next")

    if request.method == "POST":
        form = RepairIntakeForm(request.POST, instance=repair)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Repair #{repair.id:04d} intake details updated."
            )
            if next_url:
                return redirect(next_url)
            return redirect("repairs:detail", pk=repair.pk)
    else:
        form = RepairIntakeForm(instance=repair)

    return render(
        request,
        "repairs/repair_intake_form.html",
        {
            "form": form,
            "repair": repair,
            "next": next_url,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {"label": f"Repair #{repair.id:04d}", "url": f"/repairs/{repair.pk}/"},
                {"label": "Edit Intake", "url": None},
            ],
        },
    )


@login_required
def repair_edit_technical(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    next_url = request.GET.get("next")

    if not (request.user.is_technician or request.user.is_admin):
        messages.error(request, "You do not have permission to edit technical details.")
        return redirect("repairs:detail", pk=repair.pk)

    if request.method == "POST":
        form = RepairTechnicianForm(request.POST, instance=repair)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Repair #{repair.id:04d} technical details updated."
            )
            if next_url:
                return redirect(next_url)
            return redirect("repairs:detail", pk=repair.pk)
    else:
        form = RepairTechnicianForm(instance=repair)

    return render(
        request,
        "repairs/repair_technical_form.html",
        {
            "form": form,
            "repair": repair,
            "next": next_url,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {"label": f"Repair #{repair.id:04d}", "url": f"/repairs/{repair.pk}/"},
                {"label": "Edit Technical", "url": None},
            ],
        },
    )


@login_required
def repair_add_note(request, pk):
    repair = get_object_or_404(Repair, pk=pk)

    if request.method == "POST":
        form = RepairNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.repair = repair
            note.created_by = request.user
            note.save()
            messages.success(request, "Note added to repair journal.")
            return redirect(f"{reverse('repairs:detail', args=[repair.pk])}#journal")

    return redirect("repairs:detail", pk=repair.pk)
