from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = [
        "device_summary",
        "customer",
        "serial_number",
        "created_by",
        "created_at",
    ]
    list_filter = ["type", "brand", "created_at", "created_by"]
    search_fields = [
        "serial_number",
        "brand",
        "model",
        "customer__first_name",
        "customer__last_name",
    ]
    readonly_fields = ["created_at", "updated_at", "created_by"]

    def device_summary(self, obj):
        return f"{obj.brand} {obj.model}"

    device_summary.short_description = "Device"

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
