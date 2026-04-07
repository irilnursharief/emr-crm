from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from b_customers.models import Customer
from .models import Device
from .forms import DeviceForm
from d_repairs.models import Repair


@login_required
def device_list(request):
    devices = Device.objects.select_related("customer", "created_by").order_by(
        "-created_at"
    )
    return render(
        request,
        "devices/device_list.html",
        {
            "devices": devices,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Devices", "url": None},
            ],
        },
    )


@login_required
def device_create(request):
    customer_id = request.GET.get("customer")

    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.created_by = request.user
            device.save()
            messages.success(
                request, f"Device {device.brand} {device.model} created successfully."
            )
            return redirect("customers:detail", pk=device.customer.pk)
    else:
        form = DeviceForm()
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
                form.fields["customer"].initial = customer
            except Customer.DoesNotExist:
                pass

    return render(
        request,
        "devices/device_form.html",
        {
            "form": form,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Devices", "url": "/devices/"},
                {"label": "Add Device", "url": None},
            ],
        },
    )


@login_required
def device_detail(request, pk):
    device = get_object_or_404(
        Device.objects.select_related("customer", "created_by"), pk=pk
    )
    repairs = (
        Repair.objects.filter(device=device)
        .select_related("device", "device__customer", "assigned_to")
        .order_by("-created_at")
    )
    return render(
        request,
        "devices/device_detail.html",
        {
            "device": device,
            "repairs": repairs,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Devices", "url": "/devices/"},
                {"label": f"{device.brand} {device.model}", "url": None},
            ],
        },
    )


@login_required
def device_edit(request, pk):
    device = get_object_or_404(Device, pk=pk)
    next_url = request.GET.get("next")

    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Device {device.brand} {device.model} updated successfully."
            )
            if next_url:
                return redirect(next_url)
            return redirect("devices:detail", pk=device.pk)
    else:
        form = DeviceForm(instance=device)

    return render(
        request,
        "devices/device_form.html",
        {
            "form": form,
            "is_edit": True,
            "device": device,
            "next": next_url,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Devices", "url": "/devices/"},
                {
                    "label": f"{device.brand} {device.model}",
                    "url": f"/devices/{device.pk}/",
                },
                {"label": "Edit", "url": None},
            ],
        },
    )
