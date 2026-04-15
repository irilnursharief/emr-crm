from django.contrib import admin
from .models import Repair, RepairNote
from f_payments.models import Payment


class RepairNoteInline(admin.StackedInline):
    model = RepairNote
    extra = 1
    readonly_fields = ["created_by", "created_at"]

    def has_change_permission(self, request, obj=None):
        # Once a note is saved, it cannot be edited via inline
        return False

    def has_delete_permission(self, request, obj=None):
        # Notes are immutable audit trail
        return False


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = [
        "amount",
        "payment_type",
        "mode_of_payment",
        "reference_number",
        "created_by",
        "created_at",
    ]
    readonly_fields = ["created_by", "created_at"]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    list_display = ["repair_id", "id", "device", "status", "assigned_to", "created_at"]
    list_filter = ["status", "created_at", "assigned_to"]
    search_fields = [
        "repair_id",
        "device__serial_number",
        "device__customer__first_name",
        "issue_category",
    ]
    readonly_fields = [
        "repair_id",
        "created_at",
        "updated_at",
        "created_by",
        "get_total_paid",
        "get_balance_due",
    ]
    inlines = [RepairNoteInline, PaymentInline]

    fieldsets = (
        ("Device & Assignment", {"fields": ("device", "status", "assigned_to")}),
        (
            "Intake Information (Front Desk)",
            {
                "fields": ("issue_category", "issue_description", "vmi"),
                "description": "Required fields collected when customer drops off device.",
            },
        ),
        (
            "Technical Findings (Technician)",
            {
                "fields": ("mi", "diagnosis", "recommendation"),
                "classes": ("collapse",),
                "description": "To be filled during technical inspection.",
            },
        ),
        (
            "Financial Summary",
            {
                "fields": ("get_total_paid", "get_balance_due"),
            },
        ),
        (
            "Audit Trail",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_total_paid(self, obj):
        return f"₱ {obj.total_paid:,.2f}"

    get_total_paid.short_description = "Total Paid"

    def get_balance_due(self, obj):
        balance = obj.balance_due
        if balance > 0:
            return f"₱ {balance:,.2f} (Outstanding)"
        return "₱ 0.00 (Fully Paid)"

    get_balance_due.short_description = "Balance Due"

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.created_by_id:
                instance.created_by = request.user
            instance.save()
        formset.save_m2m()


@admin.register(RepairNote)
class RepairNoteAdmin(admin.ModelAdmin):
    list_display = ["repair", "created_by", "created_at", "content_preview"]
    list_filter = ["created_at", "created_by"]
    readonly_fields = ["repair", "content", "created_by", "created_at", "updated_at"]

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Note Preview"

    def has_add_permission(self, request):
        # Notes should only be added via Repair inline, not standalone
        return False

    def has_change_permission(self, request, obj=None):
        # Immutable audit trail - no edits allowed
        return False

    def has_delete_permission(self, request, obj=None):
        # Immutable audit trail - no deletes allowed
        return False
