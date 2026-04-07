from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Sum, Q
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
