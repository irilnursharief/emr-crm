from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.db.models import Q, Value
from django.db.models.functions import Concat
from b_customers.models import Customer
from c_devices.models import Device
from d_repairs.models import Repair
from f_payments.models import Payment


@login_required
def dashboard(request):
    # --- Stat Cards ---
    total_customers = Customer.objects.count()
    total_devices = Device.objects.count()

    active_repairs = Repair.objects.exclude(
        status__in=["completed", "released"]
    ).count()

    completed_repairs = Repair.objects.filter(
        status__in=["completed", "released"]
    ).count()

    pending_approval = Repair.objects.filter(status="awaiting_approval").count()

    # Total revenue (sum of all payments)
    total_revenue = Payment.objects.aggregate(total=Sum("amount"))["total"] or 0

    # --- Recent Repairs (last 10) ---
    recent_repairs = Repair.objects.select_related(
        "device", "device__customer", "assigned_to"
    ).order_by("-created_at")[:10]

    # --- Repairs assigned to current user (for technicians) ---
    my_repairs = None
    if request.user.is_technician:
        my_repairs = (
            Repair.objects.filter(assigned_to=request.user)
            .exclude(status__in=["completed", "released"])
            .select_related("device", "device__customer")
            .order_by("-created_at")[:5]
        )

    context = {
        "total_customers": total_customers,
        "total_devices": total_devices,
        "active_repairs": active_repairs,
        "completed_repairs": completed_repairs,
        "pending_approval": pending_approval,
        "total_revenue": total_revenue,
        "recent_repairs": recent_repairs,
        "my_repairs": my_repairs,
    }

    return render(request, "dashboard.html", context)


@login_required
def global_search(request):
    query = request.GET.get("q", "").strip()

    customers = []
    devices = []
    repairs = []
    total_results = 0

    if query:
        # --- Search Customers ---
        customers = (
            Customer.objects.annotate(
                full_name_search=Concat("first_name", Value(" "), "last_name")
            )
            .filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(full_name_search__icontains=query)
                | Q(contact_number__icontains=query)
                | Q(email__icontains=query)
            )
            .order_by("-created_at")[:10]
        )

        # --- Search Devices ---
        devices = (
            Device.objects.select_related("customer")
            .annotate(
                customer_full_name=Concat(
                    "customer__first_name", Value(" "), "customer__last_name"
                )
            )
            .filter(
                Q(brand__icontains=query)
                | Q(model__icontains=query)
                | Q(serial_number__icontains=query)
                | Q(customer_full_name__icontains=query)
            )
            .order_by("-created_at")[:10]
        )

        # --- Search Repairs ---
        repairs = (
            Repair.objects.select_related("device", "device__customer", "assigned_to")
            .annotate(
                customer_full_name=Concat(
                    "device__customer__first_name",
                    Value(" "),
                    "device__customer__last_name",
                )
            )
            .filter(
                Q(device__customer__first_name__icontains=query)
                | Q(device__customer__last_name__icontains=query)
                | Q(customer_full_name__icontains=query)
                | Q(device__brand__icontains=query)
                | Q(device__model__icontains=query)
                | Q(device__serial_number__icontains=query)
                | Q(issue_category__icontains=query)
            )
            .order_by("-created_at")[:10]
        )

        total_results = len(customers) + len(devices) + len(repairs)

    return render(
        request,
        "search_results.html",
        {
            "query": query,
            "customers": customers,
            "devices": devices,
            "repairs": repairs,
            "total_results": total_results,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Search Results", "url": None},
            ],
        },
    )
