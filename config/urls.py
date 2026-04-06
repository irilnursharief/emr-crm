from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("a_users.urls")),
    path("customers/", include("b_customers.urls")),
    path("devices/", include("c_devices.urls")),
    path("repairs/", include("d_repairs.urls")),
    path("payments/", include("f_payments.urls")),
]
