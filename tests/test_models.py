"""
Model tests for EMR CRM.

These tests verify that:
- Models can be created with valid data
- Model properties work correctly
- Model relationships are correct
- Computed fields calculate properly
"""

import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model

from b_customers.models import Customer
from c_devices.models import Device
from d_repairs.models import Repair, RepairNote
from e_quotations.models import Quotation, QuotationItem
from f_payments.models import Payment

from tests.factories import (
    UserFactory,
    CustomerFactory,
    DeviceFactory,
    RepairFactory,
    RepairNoteFactory,
    QuotationFactory,
    QuotationItemFactory,
    PaymentFactory,
)

User = get_user_model()


# =============================================================================
# USER MODEL TESTS
# =============================================================================


class TestUserModel:
    """Tests for the custom User model."""

    def test_create_user(self):
        """Test that a user can be created."""
        user = UserFactory(username="testuser", role="admin")
        assert user.username == "testuser"
        assert user.role == "admin"
        assert user.is_active is True

    def test_user_str(self):
        """Test the string representation of a user."""
        user = UserFactory(username="john", role="technician")
        assert str(user) == "john (technician)"

    def test_is_admin_property(self):
        """Test the is_admin property."""
        admin = UserFactory(role="admin")
        tech = UserFactory(role="technician")

        assert admin.is_admin is True
        assert tech.is_admin is False

    def test_is_technician_property(self):
        """Test the is_technician property."""
        admin = UserFactory(role="admin")
        tech = UserFactory(role="technician")

        assert admin.is_technician is False
        assert tech.is_technician is True

    def test_is_crs_property(self):
        """Test the is_crs property."""
        crs = UserFactory(role="crs")
        admin = UserFactory(role="admin")

        assert crs.is_crs is True
        assert admin.is_crs is False


# =============================================================================
# CUSTOMER MODEL TESTS
# =============================================================================


class TestCustomerModel:
    """Tests for the Customer model."""

    def test_create_customer(self):
        """Test that a customer can be created."""
        customer = CustomerFactory(
            first_name="John", last_name="Doe", contact_number="09123456789"
        )
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.pk is not None

    def test_customer_str(self):
        """Test the string representation."""
        customer = CustomerFactory(first_name="Jane", last_name="Smith")
        assert str(customer) == "Jane Smith"

    def test_full_name_property(self):
        """Test the full_name property."""
        customer = CustomerFactory(first_name="John", last_name="Doe")
        assert customer.full_name == "John Doe"

    def test_customer_ordering(self):
        """Test that customers are ordered by created_at descending."""
        customer1 = CustomerFactory()
        customer2 = CustomerFactory()
        customer3 = CustomerFactory()

        customers = list(Customer.objects.all())

        # Most recent first
        assert customers[0] == customer3
        assert customers[1] == customer2
        assert customers[2] == customer1

    def test_customer_audit_fields(self):
        """Test that audit fields are set correctly."""
        user = UserFactory()
        customer = CustomerFactory(created_by=user, updated_by=user)

        assert customer.created_by == user
        assert customer.updated_by == user
        assert customer.created_at is not None
        assert customer.updated_at is not None


# =============================================================================
# DEVICE MODEL TESTS
# =============================================================================


class TestDeviceModel:
    """Tests for the Device model."""

    def test_create_device(self):
        """Test that a device can be created."""
        device = DeviceFactory(
            brand="Apple", model="MacBook Pro", serial_number="ABC123"
        )
        assert device.brand == "Apple"
        assert device.model == "MacBook Pro"
        assert device.serial_number == "ABC123"

    def test_device_str(self):
        """Test the string representation."""
        device = DeviceFactory(
            brand="Samsung", model="Galaxy S24", serial_number="XYZ789"
        )
        assert str(device) == "Samsung Galaxy S24 (XYZ789)"

    def test_device_customer_relationship(self):
        """Test that device belongs to a customer."""
        customer = CustomerFactory(first_name="John", last_name="Doe")
        device = DeviceFactory(customer=customer)

        assert device.customer == customer
        assert device in customer.devices.all()

    def test_serial_number_unique(self):
        """Test that serial numbers must be unique."""
        DeviceFactory(serial_number="UNIQUE123")

        with pytest.raises(Exception):  # IntegrityError
            DeviceFactory(serial_number="UNIQUE123")

    def test_device_type_choices(self):
        """Test that device type is validated."""
        device = DeviceFactory(type="laptop")
        assert device.type == "laptop"
        assert device.get_type_display() == "Laptop"


# =============================================================================
# REPAIR MODEL TESTS
# =============================================================================


class TestRepairModel:
    """Tests for the Repair model."""

    def test_create_repair(self):
        """Test that a repair can be created."""
        repair = RepairFactory(issue_category="No Power", status="pending")
        assert repair.issue_category == "No Power"
        assert repair.status == "pending"
        assert repair.pk is not None

    def test_repair_str(self):
        """Test the string representation."""
        repair = RepairFactory()
        assert f"Repair #{repair.id}" in str(repair)

    def test_repair_device_relationship(self):
        """Test that repair belongs to a device."""
        device = DeviceFactory()
        repair = RepairFactory(device=device)

        assert repair.device == device
        assert repair in device.repairs.all()

    def test_repair_status_choices(self):
        """Test all valid status values."""
        statuses = [
            "pending",
            "in_progress",
            "awaiting_approval",
            "completed",
            "released",
        ]

        for status in statuses:
            repair = RepairFactory(status=status)
            assert repair.status == status

    def test_get_absolute_url(self):
        """Test the get_absolute_url method."""
        repair = RepairFactory()
        url = repair.get_absolute_url()
        assert f"/repairs/{repair.pk}/" == url

    def test_total_paid_no_payments(self):
        """Test total_paid when there are no payments."""
        repair = RepairFactory()
        assert repair.total_paid == 0

    def test_total_paid_with_payments(self):
        """Test total_paid with multiple payments."""
        repair = RepairFactory()
        PaymentFactory(repair=repair, amount=Decimal("1000.00"))
        PaymentFactory(repair=repair, amount=Decimal("500.00"))

        assert repair.total_paid == Decimal("1500.00")

    def test_quotation_total_no_quotation(self):
        """Test quotation_total when there's no quotation."""
        repair = RepairFactory()
        assert repair.quotation_total == 0

    def test_quotation_total_with_quotation(self):
        """Test quotation_total with a quotation."""
        repair = RepairFactory()
        quotation = QuotationFactory(repair=repair)
        QuotationItemFactory(
            quotation=quotation, quantity=1, unit_price=Decimal("1000.00")
        )

        assert repair.quotation_total == Decimal("1000.00")

    def test_balance_due(self):
        """Test balance_due calculation."""
        repair = RepairFactory()
        quotation = QuotationFactory(repair=repair)
        QuotationItemFactory(
            quotation=quotation, quantity=1, unit_price=Decimal("2000.00")
        )
        PaymentFactory(repair=repair, amount=Decimal("500.00"))

        assert repair.balance_due == Decimal("1500.00")


# =============================================================================
# REPAIR NOTE MODEL TESTS
# =============================================================================


class TestRepairNoteModel:
    """Tests for the RepairNote model."""

    def test_create_repair_note(self):
        """Test that a repair note can be created."""
        note = RepairNoteFactory(content="Test note content")
        assert note.content == "Test note content"
        assert note.pk is not None

    def test_repair_note_relationship(self):
        """Test that note belongs to a repair."""
        repair = RepairFactory()
        note = RepairNoteFactory(repair=repair)

        assert note.repair == repair
        assert note in repair.notes.all()

    def test_repair_notes_ordering(self):
        """Test that notes are ordered by created_at descending."""
        repair = RepairFactory()
        note1 = RepairNoteFactory(repair=repair)
        note2 = RepairNoteFactory(repair=repair)
        note3 = RepairNoteFactory(repair=repair)

        notes = list(repair.notes.all())

        # Most recent first
        assert notes[0] == note3
        assert notes[1] == note2
        assert notes[2] == note1


# =============================================================================
# QUOTATION MODEL TESTS
# =============================================================================


class TestQuotationModel:
    """Tests for the Quotation model."""

    def test_create_quotation(self):
        """Test that a quotation can be created."""
        quotation = QuotationFactory(status="draft")
        assert quotation.status == "draft"
        assert quotation.pk is not None

    def test_quotation_str(self):
        """Test the string representation."""
        quotation = QuotationFactory()
        assert f"QTN-{quotation.id:04d}" in str(quotation)

    def test_quotation_repair_one_to_one(self):
        """Test that each repair can only have one quotation."""
        repair = RepairFactory()
        QuotationFactory(repair=repair)

        with pytest.raises(Exception):  # IntegrityError
            QuotationFactory(repair=repair)

    def test_subtotal_no_items(self):
        """Test subtotal with no items."""
        quotation = QuotationFactory()
        assert quotation.subtotal == 0

    def test_subtotal_with_items(self):
        """Test subtotal with multiple items."""
        quotation = QuotationFactory()
        QuotationItemFactory(
            quotation=quotation, quantity=2, unit_price=Decimal("500.00")
        )
        QuotationItemFactory(
            quotation=quotation, quantity=1, unit_price=Decimal("1000.00")
        )

        # (2 * 500) + (1 * 1000) = 2000
        assert quotation.subtotal == Decimal("2000.00")

    def test_total_no_discount(self):
        """Test total without discount."""
        quotation = QuotationFactory(discount_amount=Decimal("0.00"))
        QuotationItemFactory(
            quotation=quotation, quantity=1, unit_price=Decimal("1000.00")
        )

        assert quotation.total == Decimal("1000.00")

    def test_total_with_discount(self):
        """Test total with discount applied."""
        quotation = QuotationFactory(discount_amount=Decimal("200.00"))
        QuotationItemFactory(
            quotation=quotation, quantity=1, unit_price=Decimal("1000.00")
        )

        assert quotation.total == Decimal("800.00")

    def test_total_discount_exceeds_subtotal(self):
        """Test that total doesn't go below zero."""
        quotation = QuotationFactory(discount_amount=Decimal("5000.00"))
        QuotationItemFactory(
            quotation=quotation, quantity=1, unit_price=Decimal("1000.00")
        )

        # Discount (5000) > Subtotal (1000), but total should be 0, not negative
        assert quotation.total == Decimal("0.00")


# =============================================================================
# QUOTATION ITEM MODEL TESTS
# =============================================================================


class TestQuotationItemModel:
    """Tests for the QuotationItem model."""

    def test_create_quotation_item(self):
        """Test that a quotation item can be created."""
        item = QuotationItemFactory(
            item_type="parts",
            description="Screen Replacement",
            quantity=1,
            unit_price=Decimal("2500.00"),
        )
        assert item.item_type == "parts"
        assert item.description == "Screen Replacement"

    def test_quotation_item_str(self):
        """Test the string representation."""
        item = QuotationItemFactory(
            description="Labor Fee", quantity=2, unit_price=Decimal("500.00")
        )
        assert "2x" in str(item)
        assert "Labor Fee" in str(item)

    def test_subtotal_property(self):
        """Test the subtotal calculation."""
        item = QuotationItemFactory(quantity=3, unit_price=Decimal("100.00"))
        assert item.subtotal == Decimal("300.00")

    def test_item_type_choices(self):
        """Test all valid item types."""
        types = ["parts", "labor", "service_fee"]

        for item_type in types:
            item = QuotationItemFactory(item_type=item_type)
            assert item.item_type == item_type


# =============================================================================
# PAYMENT MODEL TESTS
# =============================================================================


class TestPaymentModel:
    """Tests for the Payment model."""

    def test_create_payment(self):
        """Test that a payment can be created."""
        payment = PaymentFactory(
            amount=Decimal("1500.00"),
            payment_type="full_settlement",
            mode_of_payment="cash",
        )
        assert payment.amount == Decimal("1500.00")
        assert payment.payment_type == "full_settlement"

    def test_payment_str(self):
        """Test the string representation."""
        repair = RepairFactory()
        payment = PaymentFactory(
            repair=repair, amount=Decimal("1000.00"), payment_type="down_payment"
        )
        assert "1,000.00" in str(payment)
        assert "Down Payment" in str(payment)

    def test_payment_repair_relationship(self):
        """Test that payment belongs to a repair."""
        repair = RepairFactory()
        payment = PaymentFactory(repair=repair)

        assert payment.repair == repair
        assert payment in repair.payments.all()

    def test_multiple_payments_per_repair(self):
        """Test that a repair can have multiple payments."""
        repair = RepairFactory()
        payment1 = PaymentFactory(repair=repair, amount=Decimal("500.00"))
        payment2 = PaymentFactory(repair=repair, amount=Decimal("500.00"))
        payment3 = PaymentFactory(repair=repair, amount=Decimal("500.00"))

        assert repair.payments.count() == 3
        assert repair.total_paid == Decimal("1500.00")

    def test_payment_ordering(self):
        """Test that payments are ordered chronologically."""
        repair = RepairFactory()
        payment1 = PaymentFactory(repair=repair)
        payment2 = PaymentFactory(repair=repair)
        payment3 = PaymentFactory(repair=repair)

        payments = list(repair.payments.all())

        # Chronological order (oldest first)
        assert payments[0] == payment1
        assert payments[1] == payment2
        assert payments[2] == payment3
