from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "contact_number", "email", "created_at", "updated_at"]
    list_filter = ["created_at"]
    search_fields = ["first_name", "last_name", "contact_number", "email"]
    readonly_fields = ["created_at", "updated_at", "created_by"]

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
