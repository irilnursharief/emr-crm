from django.urls import path
from django.shortcuts import redirect
from . import views
from config.views import handler404, handler500, handler403


def test_404(request):
    return handler404(request, None)


def test_500(request):
    return handler500(request)


def test_403(request):
    return handler403(request, None)


urlpatterns = [
    path("", lambda request: redirect("login"), name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("search/", views.global_search, name="global_search"),
    # TEMPORARY - remove after testing
    path("test-404/", test_404, name="test_404"),
    path("test-500/", test_500, name="test_500"),
    path("test-403/", test_403, name="test_403"),
]
