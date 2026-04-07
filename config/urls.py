from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

handler404 = "config.views.handler404"
handler500 = "config.views.handler500"
handler403 = "config.views.handler403"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("a_users.urls")),
    path("customers/", include("b_customers.urls")),
    path("devices/", include("c_devices.urls")),
    path("repairs/", include("d_repairs.urls")),
    path("payments/", include("f_payments.urls")),
    path("quotations/", include("e_quotations.urls")),
]
