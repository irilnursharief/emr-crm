from django.urls import path
from . import views

app_name = "repairs"

urlpatterns = [
    path("", views.repair_list, name="list"),
    path("create/", views.repair_create, name="create"),
    path("<int:pk>/", views.repair_detail, name="detail"),
    path("<int:pk>/edit/intake/", views.repair_edit_intake, name="edit_intake"),
    path(
        "<int:pk>/edit/technical/", views.repair_edit_technical, name="edit_technical"
    ),
]
