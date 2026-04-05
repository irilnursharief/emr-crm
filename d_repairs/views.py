from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Repair


@login_required
def repair_list(request):
    repairs = Repair.objects.select_related(
        "device", "device__customer", "assigned_to", "created_by"
    ).order_by("-created_at")
    return render(request, "repairs/repair_list.html", {"repairs": repairs})


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

    # Safely get quotation if it exists
    try:
        quotation = repair.quotation
        quotation_items = quotation.items.all()
    except Repair.quotation.RelatedObjectDoesNotExist:
        quotation = None
        quotation_items = []

    return render(
        request,
        "repairs/repair_detail.html",
        {
            "repair": repair,
            "quotation": quotation,
            "quotation_items": quotation_items,
        },
    )
