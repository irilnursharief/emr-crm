from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "repair",
        "formatted_amount",
        "payment_type",
        "mode_of_payment",
        "reference_number",
        "created_by",
        "created_at",
    ]
    list_filter = ["payment_type", "mode_of_payment", "created_at"]
    search_fields = ["repair__device__serial_number", "reference_number"]
    readonly_fields = ["created_at", "updated_at", "created_by"]

    def formatted_amount(self, obj):
        return f"₱ {obj.amount:,.2f}"

    formatted_amount.short_description = "Amount"

    # Payments are immutable once saved
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing payment
            return [
                "repair",
                "amount",
                "payment_type",
                "mode_of_payment",
                "reference_number",
                "created_by",
                "created_at",
                "updated_at",
            ]
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
