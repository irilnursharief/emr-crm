from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path("", lambda request: redirect("login"), name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("search/", views.global_search, name="global_search"),
]
