from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
from django.db import transaction
from d_repairs.models import Repair
from d_repairs.signing import verify_signed_url
from .models import Quotation, QuotationItem
from .forms import QuotationForm, QuotationItemForm
from z_core.logging_utils import get_logger, log_user_action, log_pdf_event
import time

logger = get_logger("emr")


@login_required
@transaction.atomic
def quotation_create(request, repair_id):
    """
    Create a quotation for a repair, or redirect to existing one.

    Uses get_or_create to prevent race conditions when multiple users
    try to create a quotation simultaneously.
    """
    repair = get_object_or_404(Repair, pk=repair_id)

    quotation, created = Quotation.objects.get_or_create(
        repair=repair,
        defaults={
            "created_by": request.user,
            "updated_by": request.user,
            "status": Quotation.Status.DRAFT,
        },
    )

    if created:
        messages.success(
            request, "Draft quotation created. You can now add line items."
        )
    else:
        messages.info(request, "This repair already has a quotation.")

    return redirect("quotations:detail", pk=quotation.pk)


@login_required
def quotation_detail(request, pk):
    """Display quotation details with edit form."""
    quotation = get_object_or_404(
        Quotation.objects.select_related(
            "repair", "repair__device", "repair__device__customer"
        ).prefetch_related("items"),
        pk=pk,
    )
    repair = quotation.repair

    if request.method == "POST":
        form = QuotationForm(request.POST, instance=quotation)
        if form.is_valid():
            quotation = form.save(commit=False)
            quotation.updated_by = request.user
            quotation.save()
            messages.success(request, "Quotation updated successfully.")
            return redirect("quotations:detail", pk=quotation.pk)
    else:
        form = QuotationForm(instance=quotation)

    return render(
        request,
        "quotations/quotation_detail.html",
        {
            "quotation": quotation,
            "repair": repair,
            "form": form,
            "items": quotation.items.all(),
            "subtotal": quotation.subtotal,
            "discount": quotation.discount_amount,
            "total": quotation.total,
            "can_edit": quotation.status
            in [Quotation.Status.DRAFT, Quotation.Status.SENT],
            "is_approved": quotation.status == Quotation.Status.APPROVED,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {
                    "label": f"Repair # {repair.repair_id}",
                    "url": f"/repairs/{repair.pk}/",
                },
                {"label": "Quotation", "url": None},
            ],
        },
    )


@login_required
@transaction.atomic
def quotation_item_add(request, quotation_id):
    """Add a line item to a quotation."""
    quotation = get_object_or_404(
        Quotation.objects.select_related(
            "repair", "repair__device", "repair__device__customer"
        ),
        pk=quotation_id,
    )

    if quotation.status not in [Quotation.Status.DRAFT, Quotation.Status.SENT]:
        messages.error(request, "You cannot modify items for this quotation.")
        return redirect("quotations:detail", pk=quotation.pk)

    if request.method == "POST":
        form = QuotationItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.quotation = quotation
            item.created_by = request.user
            item.updated_by = request.user
            item.save()

            # Update quotation's updated_by
            quotation.updated_by = request.user
            quotation.save(update_fields=["updated_by", "updated_at"])

            messages.success(request, "Quotation item added successfully.")
            return redirect("quotations:detail", pk=quotation.pk)
    else:
        form = QuotationItemForm()

    return render(
        request,
        "quotations/quotation_item_form.html",
        {
            "form": form,
            "quotation": quotation,
            "repair": quotation.repair,
            "is_edit": False,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {
                    "label": f"Repair # {quotation.repair.repair_id}",
                    "url": f"/repairs/{quotation.repair.pk}/",
                },
                {"label": "Quotation", "url": f"/quotations/{quotation.pk}/"},
                {"label": "Add Item", "url": None},
            ],
        },
    )


@login_required
@transaction.atomic
def quotation_item_edit(request, pk):
    """Edit a quotation line item."""
    item = get_object_or_404(
        QuotationItem.objects.select_related(
            "quotation",
            "quotation__repair",
            "quotation__repair__device",
            "quotation__repair__device__customer",
        ),
        pk=pk,
    )
    quotation = item.quotation

    if quotation.status not in [Quotation.Status.DRAFT, Quotation.Status.SENT]:
        messages.error(request, "You cannot modify items for this quotation.")
        return redirect("quotations:detail", pk=quotation.pk)

    if request.method == "POST":
        form = QuotationItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.updated_by = request.user
            item.save()

            # Update quotation's updated_by
            quotation.updated_by = request.user
            quotation.save(update_fields=["updated_by", "updated_at"])

            messages.success(request, "Quotation item updated successfully.")
            return redirect("quotations:detail", pk=quotation.pk)
    else:
        form = QuotationItemForm(instance=item)

    return render(
        request,
        "quotations/quotation_item_form.html",
        {
            "form": form,
            "quotation": quotation,
            "repair": quotation.repair,
            "item": item,
            "is_edit": True,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {
                    "label": f"Repair #{quotation.repair.repair_id:04d}",
                    "url": f"/repairs/{quotation.repair.pk}/",
                },
                {"label": "Quotation", "url": f"/quotations/{quotation.pk}/"},
                {"label": "Edit Item", "url": None},
            ],
        },
    )


@login_required
@require_POST
@transaction.atomic
def quotation_item_delete(request, pk):
    """Delete a quotation line item."""
    item = get_object_or_404(
        QuotationItem.objects.select_related("quotation"),
        pk=pk,
    )
    quotation = item.quotation

    if quotation.status not in [Quotation.Status.DRAFT, Quotation.Status.SENT]:
        messages.error(request, "You cannot delete items from this quotation.")
        return redirect("quotations:detail", pk=quotation.pk)

    item.delete()

    # Update quotation's updated_by
    quotation.updated_by = request.user
    quotation.save(update_fields=["updated_by", "updated_at"])

    messages.success(request, "Quotation item deleted successfully.")
    return redirect("quotations:detail", pk=quotation.pk)


def quotation_print(request, pk):
    """Render quotation for printing or PDF generation."""
    if not request.user.is_authenticated:
        if not verify_signed_url(request):
            return redirect(settings.LOGIN_URL)

    quotation = get_object_or_404(
        Quotation.objects.select_related(
            "repair",
            "repair__device",
            "repair__device__customer",
            "created_by",
        ).prefetch_related("items"),
        pk=pk,
    )

    return render(
        request,
        "quotations/quotation_print.html",
        {
            "quotation": quotation,
            "repair": quotation.repair,
            "items": quotation.items.all(),
            "subtotal": quotation.subtotal,
            "discount": quotation.discount_amount,
            "total": quotation.total,
        },
    )


@login_required
def quotation_pdf(request, pk):
    """Generate and download quotation as PDF."""
    quotation = get_object_or_404(Quotation, pk=pk)

    print_url = request.build_absolute_uri(reverse("quotations:print", args=[pk]))

    try:
        from d_repairs.utils import generate_pdf

        pdf_bytes = generate_pdf(print_url)
    except Exception as e:
        messages.error(request, f"PDF generation failed: {str(e)}")
        return redirect("quotations:print", pk=pk)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="quotation-repair-{quotation.repair.repair_id:04d}.pdf"'
    )
    return response


@login_required
@transaction.atomic
def quotation_send(request, pk):
    """Send quotation to customer via email."""
    if request.method != "POST":
        return redirect("quotations:detail", pk=pk)

    quotation = get_object_or_404(
        Quotation.objects.select_related(
            "repair",
            "repair__device",
            "repair__device__customer",
        ),
        pk=pk,
    )

    repair = quotation.repair
    customer = repair.device.customer

    if not customer.email:
        messages.error(
            request, f"{customer.full_name} does not have an email address on file."
        )
        log_user_action(
            request, "send_quotation_failed", {"quotation_id": pk, "reason": "no_email"}
        )
        return redirect("quotations:detail", pk=pk)

    # Generate PDF
    start_time = time.time()
    try:
        from d_repairs.utils import generate_pdf

        print_url = request.build_absolute_uri(reverse("quotations:print", args=[pk]))
        pdf_bytes = generate_pdf(print_url)

        log_pdf_event(
            request=request,
            event="generate_for_email",
            document_type="quotation",
            document_id=quotation.id,
            success=True,
            duration_ms=(time.time() - start_time) * 1000,
        )

    except Exception as e:
        log_pdf_event(
            request=request,
            event="generate_for_email",
            document_type="quotation",
            document_id=quotation.id,
            success=False,
            duration_ms=(time.time() - start_time) * 1000,
            error=str(e),
        )
        messages.error(request, f"PDF generation failed: {str(e)}")
        return redirect("quotations:detail", pk=pk)

    # Send email
    from d_repairs.email_utils import send_document_email

    subject = f"Quotation for Repair # {repair.repair_id} — Elektro Master Repairs"
    body = (
        f"Dear {customer.full_name},\n\n"
        f"Please find attached the quotation for your device repair:\n\n"
        f"Device: {repair.device.brand} {repair.device.model}\n"
        f"Issue: {repair.issue_category}\n"
        f"Quotation Total: ₱{quotation.total:,.2f}\n"
        f"Date: {quotation.created_at.strftime('%B %d, %Y')}\n\n"
        f"Please review the attached quotation. "
        f"If you approve, kindly contact us to proceed with the repair.\n\n"
        f"This quotation is valid for 7 days from the date of issue.\n\n"
        f"Thank you for trusting Elektro Master Repairs.\n"
        f"Elektro Master Repairs Team"
    )
    filename = f"quotation-repair-{repair.repair_id}.pdf"

    success = send_document_email(
        to_email=customer.email,
        subject=subject,
        body=body,
        pdf_bytes=pdf_bytes,
        filename=filename,
        request=request,
        event_type="send_quotation",
    )

    if success:
        messages.success(request, f"Quotation sent to {customer.email} successfully.")

        if quotation.status == Quotation.Status.DRAFT:
            quotation.status = Quotation.Status.SENT
            Quotation.objects.filter(pk=quotation.pk).update(
                status=Quotation.Status.SENT, updated_by=request.user
            )
            messages.info(request, "Quotation status updated to Sent.")
    else:
        messages.error(
            request, "Failed to send email. Please check your email settings."
        )

    return redirect("quotations:detail", pk=pk)
