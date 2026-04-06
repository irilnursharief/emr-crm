from django.urls import path
from . import views

app_name = "quotations"

urlpatterns = [
    path("create/repair/<int:repair_id>/", views.quotation_create, name="create"),
    path("<int:pk>/", views.quotation_detail, name="detail"),
    path("<int:quotation_id>/items/add/", views.quotation_item_add, name="item_add"),
    path("items/<int:pk>/edit/", views.quotation_item_edit, name="item_edit"),
    path("items/<int:pk>/delete/", views.quotation_item_delete, name="item_delete"),
]
