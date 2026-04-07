from django.urls import path
from . import views

app_name = "repairs"

urlpatterns = [
    path("", views.repair_list, name="list"),
    path("create/", views.repair_create, name="create"),
    path("<int:pk>/add-note/", views.repair_add_note, name="add_note"),
    path("<int:pk>/", views.repair_detail, name="detail"),
    path("<int:pk>/edit/intake/", views.repair_edit_intake, name="edit_intake"),
    path(
        "<int:pk>/edit/technical/", views.repair_edit_technical, name="edit_technical"
    ),
    # Document views
    path("<int:pk>/job-order/", views.repair_job_order, name="job_order"),
    path(
        "<int:pk>/service-report/", views.repair_service_report, name="service_report"
    ),
    # PDF views
    path("<int:pk>/job-order/pdf/", views.repair_job_order_pdf, name="job_order_pdf"),
    path(
        "<int:pk>/service-report/pdf/",
        views.repair_service_report_pdf,
        name="service_report_pdf",
    ),
]
