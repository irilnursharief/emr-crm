from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Device


@login_required
def device_list(request):
    devices = Device.objects.select_related("customer", "created_by").order_by(
        "-created_at"
    )
    return render(request, "devices/device_list.html", {"devices": devices})
