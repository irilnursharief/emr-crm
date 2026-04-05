from django.urls import path
from . import views

app_name = "repairs"

urlpatterns = [
    path("", views.repair_list, name="list"),
]
