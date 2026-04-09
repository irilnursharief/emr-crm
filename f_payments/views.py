from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from d_repairs.models import Repair
from .models import Payment
from .forms import PaymentForm
from z_core.logging_utils import log_user_action, log_payment_event


@login_required
@transaction.atomic
def payment_create(request):
    repair_id = request.GET.get("repair")
    next_url = request.GET.get("next") or request.POST.get("next")

    if not repair_id:
        messages.error(request, "No repair record specified.")
        return redirect("repairs:list")

    repair = get_object_or_404(Repair, pk=repair_id)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.repair = repair
            payment.created_by = request.user
            payment.updated_by = request.user
            payment.save()

            log_payment_event(
                request=request,
                event="create",
                repair_id=repair.id,
                amount=float(payment.amount),
                payment_type=payment.payment_type,
                success=True,
            )

            messages.success(
                request, f"Payment of ₱{payment.amount:,.2f} recorded successfully."
            )
            return redirect(f"{repair.get_absolute_url()}#quotation")
    else:
        form = PaymentForm()

    return render(
        request,
        "payments/payment_form.html",
        {
            "form": form,
            "repair": repair,
            "next": next_url,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {"label": f"Repair #{repair.id:04d}", "url": f"/repairs/{repair.pk}/"},
                {"label": "Add Payment", "url": None},
            ],
        },
    )
