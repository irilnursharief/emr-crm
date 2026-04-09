"""
Pytest configuration and fixtures for EMR CRM tests.

Fixtures are reusable pieces of test setup. They run before each test
that requests them, providing fresh test data.

Usage in tests:
    def test_something(user, customer):
        # user and customer are automatically created
        assert customer.created_by == user
"""

import pytest
from django.contrib.auth import get_user_model
from decimal import Decimal

from tests.factories import (
    UserFactory,
    CustomerFactory,
    DeviceFactory,
    RepairFactory,
    QuotationFactory,
    QuotationItemFactory,
    PaymentFactory,
)

User = get_user_model()


# =============================================================================
# DATABASE ACCESS
# =============================================================================


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Automatically enable database access for all tests.

    Without this, you'd need to mark every test with @pytest.mark.django_db
    """
    pass


# =============================================================================
# USER FIXTURES
# =============================================================================


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return UserFactory(role="admin", username="test_admin")


@pytest.fixture
def technician_user():
    """Create a technician user."""
    return UserFactory(role="technician", username="test_technician")


@pytest.fixture
def crs_user():
    """Create a CRS (Customer Relations Staff) user."""
    return UserFactory(role="crs", username="test_crs")


@pytest.fixture
def user(admin_user):
    """Default user fixture (alias for admin_user)."""
    return admin_user


# =============================================================================
# MODEL FIXTURES
# =============================================================================


@pytest.fixture
def customer(user):
    """Create a customer."""
    return CustomerFactory(created_by=user, updated_by=user)


@pytest.fixture
def device(customer, user):
    """Create a device for a customer."""
    return DeviceFactory(customer=customer, created_by=user, updated_by=user)


@pytest.fixture
def repair(device, user, technician_user):
    """Create a repair for a device."""
    return RepairFactory(
        device=device,
        created_by=user,
        updated_by=user,
        assigned_to=technician_user,
    )


@pytest.fixture
def quotation(repair, user):
    """Create a quotation for a repair."""
    return QuotationFactory(repair=repair, created_by=user, updated_by=user)


@pytest.fixture
def quotation_with_items(quotation, user):
    """Create a quotation with line items."""
    QuotationItemFactory(
        quotation=quotation,
        item_type="parts",
        description="Screen Replacement",
        quantity=1,
        unit_price=Decimal("2500.00"),
        created_by=user,
        updated_by=user,
    )
    QuotationItemFactory(
        quotation=quotation,
        item_type="labor",
        description="Labor Fee",
        quantity=1,
        unit_price=Decimal("500.00"),
        created_by=user,
        updated_by=user,
    )
    return quotation


@pytest.fixture
def payment(repair, user):
    """Create a payment for a repair."""
    return PaymentFactory(repair=repair, created_by=user, updated_by=user)


# =============================================================================
# CLIENT FIXTURES
# =============================================================================


@pytest.fixture
def authenticated_client(client, user):
    """A test client with an authenticated admin user."""
    client.force_login(user)
    return client


@pytest.fixture
def technician_client(client, technician_user):
    """A test client with an authenticated technician user."""
    client.force_login(technician_user)
    return client


@pytest.fixture
def crs_client(client, crs_user):
    """A test client with an authenticated CRS user."""
    client.force_login(crs_user)
    return client


@pytest.fixture
def anonymous_client(client):
    """A test client with no authentication."""
    return client
