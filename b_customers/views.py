from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Customer
from d_repairs.models import Repair


@login_required
def customer_list(request):
    customers = Customer.objects.select_related("created_by").order_by("-created_at")
    return render(request, "customers/customer_list.html", {"customers": customers})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(
        Customer.objects.prefetch_related("devices"),
        pk=pk,
    )
    repairs = (
        Repair.objects.filter(device__customer=customer)
        .select_related("device")
        .order_by("-created_at")
    )
    return render(
        request,
        "customers/customer_detail.html",
        {"customer": customer, "repairs": repairs},
    )
