from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Customer


@login_required
def customer_list(request):
    customers = Customer.objects.select_related("created_by").order_by("-created_at")
    return render(request, "b_customers/customer_list.html", {"customers": customers})
