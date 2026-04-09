from django.urls import path
from . import views

app_name = "devices"

urlpatterns = [
    path("", views.device_list, name="list"),
    path("create/", views.device_create, name="create"),
    path("<int:pk>/edit/", views.device_edit, name="edit"),
    path("<int:pk>/", views.device_detail, name="detail"),
]
