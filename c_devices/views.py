from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from b_customers.models import Customer
from .models import Device
from .forms import DeviceForm


@login_required
def device_list(request):
    devices = Device.objects.select_related("customer", "created_by").order_by(
        "-created_at"
    )
    return render(request, "devices/device_list.html", {"devices": devices})


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

        # Preselect customer if ?customer=<id> is in URL
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
                form.fields["customer"].initial = customer
            except Customer.DoesNotExist:
                pass

    return render(request, "devices/device_form.html", {"form": form})
