from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users


@admin.register(Users)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "role", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["username", "email"]
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
