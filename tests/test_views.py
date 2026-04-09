"""
View tests for EMR CRM.

These tests verify that:
- Views return correct status codes
- Authentication is enforced
- Permissions are checked
- Forms work correctly
- Redirects happen properly
"""

import pytest
from django.urls import reverse
from decimal import Decimal

from b_customers.models import Customer
from c_devices.models import Device
from d_repairs.models import Repair
from e_quotations.models import Quotation

from tests.factories import (
    UserFactory,
    CustomerFactory,
    DeviceFactory,
    RepairFactory,
    QuotationFactory,
    QuotationItemFactory,
)


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================


class TestAuthentication:
    """Tests for authentication requirements."""

    def test_dashboard_requires_login(self, anonymous_client):
        """Test that dashboard redirects to login for anonymous users."""
        response = anonymous_client.get(reverse("dashboard"))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url or "/login" in response.url.lower()

    def test_dashboard_accessible_when_logged_in(self, authenticated_client):
        """Test that dashboard is accessible when logged in."""
        response = authenticated_client.get(reverse("dashboard"))
        assert response.status_code == 200

    def test_customer_list_requires_login(self, anonymous_client):
        """Test that customer list requires authentication."""
        response = anonymous_client.get(reverse("customers:list"))
        assert response.status_code == 302

    def test_repair_list_requires_login(self, anonymous_client):
        """Test that repair list requires authentication."""
        response = anonymous_client.get(reverse("repairs:list"))
        assert response.status_code == 302


# =============================================================================
# CUSTOMER VIEW TESTS
# =============================================================================


class TestCustomerViews:
    """Tests for customer views."""

    def test_customer_list_view(self, authenticated_client):
        """Test the customer list view."""
        CustomerFactory.create_batch(5)

        response = authenticated_client.get(reverse("customers:list"))

        assert response.status_code == 200
        assert "customers" in response.context

    def test_customer_detail_view(self, authenticated_client, customer):
        """Test the customer detail view."""
        response = authenticated_client.get(
            reverse("customers:detail", kwargs={"pk": customer.pk})
        )

        assert response.status_code == 200
        assert response.context["customer"] == customer

    def test_customer_detail_404(self, authenticated_client):
        """Test that non-existent customer returns 404."""
        response = authenticated_client.get(
            reverse("customers:detail", kwargs={"pk": 99999})
        )

        assert response.status_code == 404

    def test_customer_create_get(self, authenticated_client):
        """Test the customer create form displays."""
        response = authenticated_client.get(reverse("customers:create"))

        assert response.status_code == 200
        assert "form" in response.context

    def test_customer_create_post(self, authenticated_client, user):
        """Test creating a new customer."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "contact_number": "09123456789",
            "email": "john@example.com",
            "address": "123 Main St",
        }

        response = authenticated_client.post(reverse("customers:create"), data)

        assert response.status_code == 302  # Redirect after success
        assert Customer.objects.filter(first_name="John", last_name="Doe").exists()

    def test_customer_create_invalid(self, authenticated_client):
        """Test creating a customer with invalid data."""
        data = {
            "first_name": "",  # Required field
            "last_name": "Doe",
            "contact_number": "09123456789",
        }

        response = authenticated_client.post(reverse("customers:create"), data)

        assert response.status_code == 200  # Form re-displayed
        assert "form" in response.context
        assert response.context["form"].errors

    def test_customer_edit_get(self, authenticated_client, customer):
        """Test the customer edit form displays."""
        response = authenticated_client.get(
            reverse("customers:edit", kwargs={"pk": customer.pk})
        )

        assert response.status_code == 200
        assert response.context["customer"] == customer

    def test_customer_edit_post(self, authenticated_client, customer):
        """Test editing a customer."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "contact_number": customer.contact_number,
            "email": customer.email,
            "address": customer.address,
        }

        response = authenticated_client.post(
            reverse("customers:edit", kwargs={"pk": customer.pk}), data
        )

        assert response.status_code == 302
        customer.refresh_from_db()
        assert customer.first_name == "Updated"


# =============================================================================
# DEVICE VIEW TESTS
# =============================================================================


class TestDeviceViews:
    """Tests for device views."""

    def test_device_list_view(self, authenticated_client):
        """Test the device list view."""
        DeviceFactory.create_batch(5)

        response = authenticated_client.get(reverse("devices:list"))

        assert response.status_code == 200
        assert "devices" in response.context

    def test_device_detail_view(self, authenticated_client, device):
        """Test the device detail view."""
        response = authenticated_client.get(
            reverse("devices:detail", kwargs={"pk": device.pk})
        )

        assert response.status_code == 200
        assert response.context["device"] == device

    def test_device_create_with_customer_prefill(self, authenticated_client, customer):
        """Test that customer is prefilled when specified in URL."""
        response = authenticated_client.get(
            reverse("devices:create") + f"?customer={customer.pk}"
        )

        assert response.status_code == 200


# =============================================================================
# REPAIR VIEW TESTS
# =============================================================================


class TestRepairViews:
    """Tests for repair views."""

    def test_repair_list_view(self, authenticated_client):
        """Test the repair list view."""
        RepairFactory.create_batch(5)

        response = authenticated_client.get(reverse("repairs:list"))

        assert response.status_code == 200
        assert "repairs" in response.context

    def test_repair_list_filter_by_status(self, authenticated_client):
        """Test filtering repairs by status."""
        RepairFactory.create_batch(3, status="pending")
        RepairFactory.create_batch(2, status="completed")

        response = authenticated_client.get(reverse("repairs:list") + "?status=pending")

        assert response.status_code == 200
        # All displayed repairs should be pending
        for repair in response.context["repairs"]:
            assert repair.status == "pending"

    def test_repair_detail_view(self, authenticated_client, repair):
        """Test the repair detail view."""
        response = authenticated_client.get(
            reverse("repairs:detail", kwargs={"pk": repair.pk})
        )

        assert response.status_code == 200
        assert response.context["repair"] == repair

    def test_repair_create_get(self, authenticated_client):
        """Test the repair create form displays."""
        response = authenticated_client.get(reverse("repairs:create"))

        assert response.status_code == 200
        assert "form" in response.context

    def test_repair_create_with_device_prefill(self, authenticated_client, device):
        """Test that device is prefilled when specified in URL."""
        response = authenticated_client.get(
            reverse("repairs:create") + f"?device={device.pk}"
        )

        assert response.status_code == 200


# =============================================================================
# REPAIR PERMISSION TESTS
# =============================================================================


class TestRepairPermissions:
    """Tests for repair-related permissions."""

    def test_technician_can_edit_technical(self, technician_client, repair):
        """Test that technicians can access technical edit form."""
        response = technician_client.get(
            reverse("repairs:edit_technical", kwargs={"pk": repair.pk})
        )

        assert response.status_code == 200

    def test_crs_cannot_edit_technical(self, crs_client, repair):
        """Test that CRS users cannot access technical edit form."""
        response = crs_client.get(
            reverse("repairs:edit_technical", kwargs={"pk": repair.pk})
        )

        # Should redirect with error message
        assert response.status_code == 302

    def test_anyone_can_edit_intake(self, crs_client, repair):
        """Test that any authenticated user can edit intake info."""
        response = crs_client.get(
            reverse("repairs:edit_intake", kwargs={"pk": repair.pk})
        )

        assert response.status_code == 200


# =============================================================================
# QUOTATION VIEW TESTS
# =============================================================================


class TestQuotationViews:
    """Tests for quotation views."""

    def test_quotation_create(self, authenticated_client, repair):
        """Test creating a quotation for a repair."""
        response = authenticated_client.get(
            reverse("quotations:create", kwargs={"repair_id": repair.pk})
        )

        # Should redirect to quotation detail
        assert response.status_code == 302
        assert Quotation.objects.filter(repair=repair).exists()

    def test_quotation_create_existing(self, authenticated_client, repair):
        """Test that creating a quotation when one exists redirects."""
        QuotationFactory(repair=repair)

        response = authenticated_client.get(
            reverse("quotations:create", kwargs={"repair_id": repair.pk})
        )

        # Should still redirect (to existing quotation)
        assert response.status_code == 302
        # Should still only have one quotation
        assert Quotation.objects.filter(repair=repair).count() == 1

    def test_quotation_detail_view(self, authenticated_client, quotation):
        """Test the quotation detail view."""
        response = authenticated_client.get(
            reverse("quotations:detail", kwargs={"pk": quotation.pk})
        )

        assert response.status_code == 200
        assert response.context["quotation"] == quotation


# =============================================================================
# PAYMENT VIEW TESTS
# =============================================================================


class TestPaymentViews:
    """Tests for payment views."""

    def test_payment_create_requires_repair(self, authenticated_client):
        """Test that payment create requires a repair ID."""
        response = authenticated_client.get(reverse("payments:create"))

        # Should redirect with error
        assert response.status_code == 302

    def test_payment_create_get(self, authenticated_client, repair):
        """Test the payment create form displays."""
        response = authenticated_client.get(
            reverse("payments:create") + f"?repair={repair.pk}"
        )

        assert response.status_code == 200
        assert "form" in response.context

    def test_payment_create_post(self, authenticated_client, repair):
        """Test creating a payment."""
        data = {
            "amount": "1500.00",
            "payment_type": "down_payment",
            "mode_of_payment": "cash",
            "reference_number": "",
        }

        response = authenticated_client.post(
            reverse("payments:create") + f"?repair={repair.pk}", data
        )

        assert response.status_code == 302
        assert repair.payments.count() == 1
        assert repair.payments.first().amount == Decimal("1500.00")


# =============================================================================
# SEARCH VIEW TESTS
# =============================================================================


class TestSearchViews:
    """Tests for global search functionality."""

    def test_search_empty_query(self, authenticated_client):
        """Test search with empty query."""
        response = authenticated_client.get(reverse("global_search"))

        assert response.status_code == 200
        assert response.context["total_results"] == 0

    def test_search_finds_customers(self, authenticated_client):
        """Test that search finds customers by name."""
        CustomerFactory(first_name="UniqueTestName", last_name="Smith")

        response = authenticated_client.get(
            reverse("global_search") + "?q=UniqueTestName"
        )

        assert response.status_code == 200
        assert len(response.context["customers"]) == 1

    def test_search_finds_devices(self, authenticated_client):
        """Test that search finds devices by serial number."""
        DeviceFactory(serial_number="UNIQUE-SERIAL-123")

        response = authenticated_client.get(
            reverse("global_search") + "?q=UNIQUE-SERIAL-123"
        )

        assert response.status_code == 200
        assert len(response.context["devices"]) == 1


# =============================================================================
# DASHBOARD VIEW TESTS
# =============================================================================


class TestDashboardView:
    """Tests for the dashboard view."""

    def test_dashboard_loads(self, authenticated_client):
        """Test that dashboard loads with context data."""
        response = authenticated_client.get(reverse("dashboard"))

        assert response.status_code == 200
        assert "total_customers" in response.context
        assert "total_devices" in response.context
        assert "active_repairs" in response.context
        assert "total_revenue" in response.context

    def test_dashboard_shows_recent_repairs(self, authenticated_client):
        """Test that dashboard shows recent repairs."""
        RepairFactory.create_batch(5)

        response = authenticated_client.get(reverse("dashboard"))

        assert response.status_code == 200
        assert "recent_repairs" in response.context
        assert len(response.context["recent_repairs"]) <= 10

    def test_dashboard_technician_sees_assigned_repairs(
        self, technician_client, technician_user
    ):
        """Test that technicians see their assigned repairs."""
        RepairFactory.create_batch(3, assigned_to=technician_user, status="in_progress")

        response = technician_client.get(reverse("dashboard"))

        assert response.status_code == 200
        assert "my_repairs" in response.context
        assert response.context["my_repairs"] is not None
