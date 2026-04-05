from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Repair


@login_required
def repair_list(request):
    repairs = Repair.objects.select_related(
        "device", "device__customer", "assigned_to", "created_by"
    ).order_by("-created_at")
    return render(request, "repairs/repair_list.html", {"repairs": repairs})
