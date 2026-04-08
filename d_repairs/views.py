from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db import models
from django.core.paginator import Paginator
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from c_devices.models import Device
from .models import Repair
from .forms import (
    RepairCreateForm,
    RepairIntakeForm,
    RepairTechnicianForm,
    RepairNoteForm,
)


from django.core.paginator import Paginator


@login_required
def repair_list(request):
    repairs = Repair.objects.select_related(
        "device", "device__customer", "assigned_to", "created_by"
    )

    # --- Filters ---
    status_filter = request.GET.get("status", "")
    assigned_filter = request.GET.get("assigned_to", "")
    search_query = request.GET.get("q", "")

    if status_filter:
        repairs = repairs.filter(status=status_filter)

    if assigned_filter:
        repairs = repairs.filter(assigned_to__id=assigned_filter)

    if search_query:
        repairs = repairs.annotate(
            customer_full_name=Concat(
                "device__customer__first_name",
                Value(" "),
                "device__customer__last_name",
            )
        ).filter(
            Q(device__customer__first_name__icontains=search_query)
            | Q(device__customer__last_name__icontains=search_query)
            | Q(customer_full_name__icontains=search_query)
            | Q(device__brand__icontains=search_query)
            | Q(device__model__icontains=search_query)
            | Q(issue_category__icontains=search_query)
        )

    active_filters = sum(
        [
            bool(status_filter),
            bool(assigned_filter),
            bool(search_query),
        ]
    )

    # --- Sorting ---
    sort_field = request.GET.get("sort", "created_at")
    sort_dir = request.GET.get("dir", "desc")

    valid_sort_fields = {
        "id": "id",
        "status": "status",
        "created_at": "created_at",
    }

    db_sort_field = valid_sort_fields.get(sort_field, "created_at")

    if sort_dir == "asc":
        repairs = repairs.order_by(db_sort_field)
    else:
        repairs = repairs.order_by(f"-{db_sort_field}")

    # --- Technicians ---
    from a_users.models import User

    technicians = User.objects.filter(role__in=["technician", "admin"]).order_by(
        "username"
    )

    # --- Pagination ---
    paginator = Paginator(repairs, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "repairs/repair_list.html",
        {
            "repairs": page_obj,
            "page_obj": page_obj,
            "technicians": technicians,
            "status_choices": Repair.Status.choices,
            "status_filter": status_filter,
            "assigned_filter": assigned_filter,
            "search_query": search_query,
            "active_filters": active_filters,
            "sort_field": sort_field,
            "sort_dir": sort_dir,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": None},
            ],
        },
    )


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

    try:
        quotation = repair.quotation
        quotation_items = quotation.items.all()
    except Repair.quotation.RelatedObjectDoesNotExist:
        quotation = None
        quotation_items = []

    form = RepairNoteForm()

    return render(
        request,
        "repairs/repair_detail.html",
        {
            "repair": repair,
            "quotation": quotation,
            "quotation_items": quotation_items,
            "form": form,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {"label": f"Repair #{repair.id:04d}", "url": None},
            ],
        },
    )


@login_required
def repair_create(request):
    device_id = request.GET.get("device")
    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = RepairCreateForm(request.POST)
        if form.is_valid():
            repair = form.save(commit=False)
            repair.created_by = request.user
            repair.save()
            messages.success(
                request, f"Repair ticket #{repair.id:04d} created successfully."
            )
            return redirect("repairs:detail", pk=repair.pk)
    else:
        form = RepairCreateForm()
        if device_id:
            try:
                device = Device.objects.get(pk=device_id)
                form.fields["device"].initial = device
            except Device.DoesNotExist:
                pass

    return render(
        request,
        "repairs/repair_form.html",
        {
            "form": form,
            "next": next_url,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {"label": "Create Repair", "url": None},
            ],
        },
    )


@login_required
def repair_edit_intake(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    next_url = request.GET.get("next")

    if request.method == "POST":
        form = RepairIntakeForm(request.POST, instance=repair)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Repair #{repair.id:04d} intake details updated."
            )
            if next_url:
                return redirect(next_url)
            return redirect("repairs:detail", pk=repair.pk)
    else:
        form = RepairIntakeForm(instance=repair)

    return render(
        request,
        "repairs/repair_intake_form.html",
        {
            "form": form,
            "repair": repair,
            "next": next_url,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {"label": f"Repair #{repair.id:04d}", "url": f"/repairs/{repair.pk}/"},
                {"label": "Edit Intake", "url": None},
            ],
        },
    )


@login_required
def repair_edit_technical(request, pk):
    repair = get_object_or_404(Repair, pk=pk)
    next_url = request.GET.get("next")

    if not (request.user.is_technician or request.user.is_admin):
        messages.error(request, "You do not have permission to edit technical details.")
        return redirect("repairs:detail", pk=repair.pk)

    if request.method == "POST":
        form = RepairTechnicianForm(request.POST, instance=repair)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Repair #{repair.id:04d} technical details updated."
            )
            if next_url:
                return redirect(next_url)
            return redirect("repairs:detail", pk=repair.pk)
    else:
        form = RepairTechnicianForm(instance=repair)

    return render(
        request,
        "repairs/repair_technical_form.html",
        {
            "form": form,
            "repair": repair,
            "next": next_url,
            "breadcrumbs": [
                {"label": "Home", "url": "/dashboard/"},
                {"label": "Repairs", "url": "/repairs/"},
                {"label": f"Repair #{repair.id:04d}", "url": f"/repairs/{repair.pk}/"},
                {"label": "Edit Technical", "url": None},
            ],
        },
    )


@login_required
def repair_add_note(request, pk):
    repair = get_object_or_404(Repair, pk=pk)

    if request.method == "POST":
        form = RepairNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.repair = repair
            note.created_by = request.user
            note.save()
            messages.success(request, "Note added to repair journal.")
            return redirect(f"{reverse('repairs:detail', args=[repair.pk])}#journal")

    return redirect("repairs:detail", pk=repair.pk)


def repair_job_order(request, pk):
    pdf_token = request.GET.get("pdf_token", "")
    if not request.user.is_authenticated and pdf_token != settings.PDF_SECRET_TOKEN:
        return redirect(settings.LOGIN_URL)

    repair = get_object_or_404(
        Repair.objects.select_related(
            "device",
            "device__customer",
            "assigned_to",
            "created_by",
        ),
        pk=pk,
    )

    return render(
        request,
        "repairs/job_order.html",
        {
            "repair": repair,
        },
    )


def repair_service_report(request, pk):
    pdf_token = request.GET.get("pdf_token", "")
    if not request.user.is_authenticated and pdf_token != settings.PDF_SECRET_TOKEN:
        return redirect(settings.LOGIN_URL)

    repair = get_object_or_404(
        Repair.objects.select_related(
            "device",
            "device__customer",
            "assigned_to",
            "created_by",
        ),
        pk=pk,
    )

    try:
        quotation = repair.quotation
        quotation_items = quotation.items.all()
    except Repair.quotation.RelatedObjectDoesNotExist:
        quotation = None
        quotation_items = []

    return render(
        request,
        "repairs/service_report.html",
        {
            "repair": repair,
            "quotation": quotation,
            "quotation_items": quotation_items,
        },
    )


@login_required
def repair_job_order_pdf(request, pk):
    repair = get_object_or_404(Repair, pk=pk)

    # Build the absolute URL of the print page
    print_url = request.build_absolute_uri(reverse("repairs:job_order", args=[pk]))

    try:
        from d_repairs.utils import generate_pdf

        pdf_bytes = generate_pdf(print_url)
    except Exception as e:
        messages.error(request, f"PDF generation failed: {str(e)}")
        return redirect("repairs:job_order", pk=pk)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="job-order-{repair.id:04d}.pdf"'
    )
    return response


@login_required
def repair_service_report_pdf(request, pk):
    repair = get_object_or_404(Repair, pk=pk)

    print_url = request.build_absolute_uri(reverse("repairs:service_report", args=[pk]))

    try:
        from d_repairs.utils import generate_pdf

        pdf_bytes = generate_pdf(print_url)
    except Exception as e:
        messages.error(request, f"PDF generation failed: {str(e)}")
        return redirect("repairs:service_report", pk=pk)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="service-report-{repair.id:04d}.pdf"'
    )
    return response


@login_required
def repair_send_job_order(request, pk):
    if request.method != "POST":
        return redirect("repairs:detail", pk=pk)

    repair = get_object_or_404(
        Repair.objects.select_related(
            "device", "device__customer", "assigned_to", "created_by"
        ),
        pk=pk,
    )

    customer = repair.device.customer

    # Check if customer has an email
    if not customer.email:
        messages.error(
            request, f"{customer.full_name} does not have an email address on file."
        )
        return redirect("repairs:detail", pk=pk)

    # Generate PDF
    try:
        from d_repairs.utils import generate_pdf

        print_url = request.build_absolute_uri(reverse("repairs:job_order", args=[pk]))
        pdf_bytes = generate_pdf(print_url)
    except Exception as e:
        messages.error(request, f"PDF generation failed: {str(e)}")
        return redirect("repairs:detail", pk=pk)

    # Send email
    from d_repairs.email_utils import send_document_email

    subject = f"Job Order #{repair.id:04d} — Elektro Master Repairs"
    body = (
        f"Dear {customer.full_name},\n\n"
        f"Please find attached your Job Order for the following repair:\n\n"
        f"Device: {repair.device.brand} {repair.device.model}\n"
        f"Issue: {repair.issue_category}\n"
        f"Date: {repair.created_at.strftime('%B %d, %Y')}\n\n"
        f"Please review and keep this document for your records.\n\n"
        f"If you have any questions, feel free to contact us.\n\n"
        f"Thank you for trusting Elektro Master Repairs.\n"
        f"Elektro Master Repairs Team"
    )
    filename = f"job-order-{repair.id:04d}.pdf"

    success = send_document_email(
        to_email=customer.email,
        subject=subject,
        body=body,
        pdf_bytes=pdf_bytes,
        filename=filename,
    )

    if success:
        messages.success(
            request,
            f"Job Order #{repair.id:04d} sent to {customer.email} successfully.",
        )
    else:
        messages.error(
            request, "Failed to send email. Please check your email settings."
        )

    return redirect("repairs:detail", pk=pk)


@login_required
def repair_send_service_report(request, pk):
    if request.method != "POST":
        return redirect("repairs:detail", pk=pk)

    repair = get_object_or_404(
        Repair.objects.select_related(
            "device", "device__customer", "assigned_to", "created_by"
        ),
        pk=pk,
    )

    customer = repair.device.customer

    if not customer.email:
        messages.error(
            request, f"{customer.full_name} does not have an email address on file."
        )
        return redirect("repairs:detail", pk=pk)

    if repair.status not in ["completed", "released"]:
        messages.error(
            request,
            "Service Report can only be sent for completed or released repairs.",
        )
        return redirect("repairs:detail", pk=pk)

    # Generate PDF
    try:
        from d_repairs.utils import generate_pdf

        print_url = request.build_absolute_uri(
            reverse("repairs:service_report", args=[pk])
        )
        pdf_bytes = generate_pdf(print_url)
    except Exception as e:
        messages.error(request, f"PDF generation failed: {str(e)}")
        return redirect("repairs:detail", pk=pk)

    # Send email
    from d_repairs.email_utils import send_document_email

    subject = f"Service Report #{repair.id:04d} — Elektro Master Repairs"
    body = (
        f"Dear {customer.full_name},\n\n"
        f"Your device has been serviced. Please find attached the Service Report:\n\n"
        f"Device: {repair.device.brand} {repair.device.model}\n"
        f"Issue: {repair.issue_category}\n"
        f"Status: {repair.get_status_display()}\n"
        f"Date Completed: {repair.updated_at.strftime('%B %d, %Y')}\n\n"
        f"The report includes details of all work performed, parts replaced, "
        f"and warranty information per line item.\n\n"
        f"Thank you for trusting Elektro Master Repairs.\n"
        f"Elektro Master Repairs Team"
    )
    filename = f"service-report-{repair.id:04d}.pdf"

    success = send_document_email(
        to_email=customer.email,
        subject=subject,
        body=body,
        pdf_bytes=pdf_bytes,
        filename=filename,
    )

    if success:
        messages.success(
            request,
            f"Service Report #{repair.id:04d} sent to {customer.email} successfully.",
        )
    else:
        messages.error(
            request, "Failed to send email. Please check your email settings."
        )

    return redirect("repairs:detail", pk=pk)
