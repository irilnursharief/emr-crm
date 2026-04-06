from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from d_repairs.models import Repair
from .models import Quotation, QuotationItem
from .forms import QuotationForm, QuotationItemForm


@login_required
def quotation_create(request, repair_id):
    """
    Creates a blank Draft Quotation for a Repair.
    If one already exists, just redirects to it.
    """
    repair = get_object_or_404(Repair, pk=repair_id)

    # Check if a quotation already exists (OneToOne relationship)
    try:
        quotation = repair.quotation
        messages.info(request, "This repair already has a quotation.")
    except Repair.quotation.RelatedObjectDoesNotExist:
        # Create a new draft quotation
        quotation = Quotation.objects.create(
            repair=repair,
            created_by=request.user,
            status=Quotation.Status.DRAFT,
            discount_amount=0.00,
        )
        messages.success(
            request, "Draft quotation created. You can now add line items."
        )

    return redirect("quotations:detail", pk=quotation.pk)


@login_required
def quotation_detail(request, pk):
    """
    Main quotation management interface.
    Displays line items, financial summary, and status controls.
    """
    quotation = get_object_or_404(
        Quotation.objects.select_related(
            "repair", "repair__device", "repair__device__customer"
        ).prefetch_related("items"),
        pk=pk,
    )

    repair = quotation.repair

    # Handle status updates or discount changes via POST
    if request.method == "POST":
        form = QuotationForm(request.POST, instance=quotation)
        if form.is_valid():
            form.save()
            messages.success(request, "Quotation updated successfully.")
            return redirect("quotations:detail", pk=quotation.pk)
    else:
        form = QuotationForm(instance=quotation)

    # Calculate financials
    subtotal = quotation.subtotal
    discount = quotation.discount_amount
    total = quotation.total

    context = {
        "quotation": quotation,
        "repair": repair,
        "form": form,
        "items": quotation.items.all(),
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "can_edit": quotation.status in [Quotation.Status.DRAFT, Quotation.Status.SENT],
        "is_approved": quotation.status == Quotation.Status.APPROVED,
    }

    return render(request, "quotations/quotation_detail.html", context)


@login_required
def quotation_item_add(request, quotation_id):
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
            item.save()
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
        },
    )


@login_required
def quotation_item_edit(request, pk):
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
            form.save()
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
        },
    )


@login_required
@require_POST
def quotation_item_delete(request, pk):
    item = get_object_or_404(
        QuotationItem.objects.select_related("quotation"),
        pk=pk,
    )
    quotation = item.quotation

    if quotation.status not in [Quotation.Status.DRAFT, Quotation.Status.SENT]:
        messages.error(request, "You cannot delete items from this quotation.")
        return redirect("quotations:detail", pk=quotation.pk)

    item.delete()
    messages.success(request, "Quotation item deleted successfully.")
    return redirect("quotations:detail", pk=quotation.pk)
