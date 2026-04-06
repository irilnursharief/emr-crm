from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Customer
from d_repairs.models import Repair
from .forms import CustomerForm


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


@login_required
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()

            messages.success(
                request, f"Customer {customer.full_name} created successfully."
            )

            return redirect("customers:detail", pk=customer.pk)
    else:
        form = CustomerForm()

    return render(request, "customers/customer_form.html", {"form": form})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    next_url = request.GET.get("next")  # ← Get next parameter

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Customer {customer.full_name} updated successfully."
            )
            # ← Smart redirect
            if next_url:
                return redirect(next_url)
            return redirect("customers:detail", pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "is_edit": True,
            "customer": customer,
            "next": next_url,
        },
    )
