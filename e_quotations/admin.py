from django.contrib import admin
from .models import Quotation, QuotationItem


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1
    fields = [
        "item_type",
        "description",
        "quantity",
        "unit_price",
        "get_subtotal",
        "warranty_days",
    ]
    readonly_fields = ["get_subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal if obj.id else "0.00"

    get_subtotal.short_description = "Subtotal"


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "repair",
        "status",
        "get_total",
        "created_by",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["repair__device__serial_number", "id"]
    readonly_fields = [
        "get_subtotal",
        "get_total",
        "created_at",
        "updated_at",
        "created_by",
    ]

    inlines = [QuotationItemInline]

    fieldsets = (
        ("Link & Status", {"fields": ("repair", "status")}),
        ("Financials", {"fields": ("discount_amount", "get_subtotal", "get_total")}),
        (
            "Audit",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_subtotal(self, obj):
        return f"₱ {obj.subtotal:,.2f}"  # Assuming PHP based on Manila timezone, change symbol if needed

    get_subtotal.short_description = "Subtotal (Before Discount)"

    def get_total(self, obj):
        return f"₱ {obj.total:,.2f}"

    get_total.short_description = "Final Total"

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
