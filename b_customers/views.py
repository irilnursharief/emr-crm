from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Customer
from d_repairs.models import Repair
from .forms import CustomerForm


from django.core.paginator import Paginator
from django.db import models


@login_required
def customer_list(request):
    customers_qs = Customer.objects.select_related("created_by").order_by("-created_at")

    # --- Filters ---
    search_query = request.GET.get("q", "")

    if search_query:
        customers_qs = customers_qs.annotate(
            full_name_search=Concat("first_name", Value(" "), "last_name")
        ).filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(full_name_search__icontains=search_query)
            | Q(contact_number__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    active_filters = sum(
        [
            bool(search_query),
        ]
    )

    # --- Pagination ---
    paginator = Paginator(customers_qs, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "customers/customer_list.html",
        {
            "customers": page_obj,
            "page_obj": page_obj,
            "search_query": search_query,
            "active_filters": active_filters,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Customers", "url": None},
            ],
        },
    )


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
        {
            "customer": customer,
            "repairs": repairs,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Customers", "url": "/customers/"},
                {"label": customer.full_name, "url": None},
            ],
        },
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

    return render(
        request,
        "customers/customer_form.html",
        {
            "form": form,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Customers", "url": "/customers/"},
                {"label": "Add Customer", "url": None},
            ],
        },
    )


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    next_url = request.GET.get("next")

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Customer {customer.full_name} updated successfully."
            )
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
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Customers", "url": "/customers/"},
                {"label": customer.full_name, "url": f"/customers/{customer.pk}/"},
                {"label": "Edit", "url": None},
            ],
        },
    )
