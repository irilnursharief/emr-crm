"""
Factory Boy factories for creating test data.

Factories are like blueprints for creating model instances.
They generate realistic fake data automatically.

Usage:
    # Create a single customer
    customer = CustomerFactory()

    # Create with specific values
    customer = CustomerFactory(first_name="John", email="john@example.com")

    # Create multiple
    customers = CustomerFactory.create_batch(5)
"""

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from decimal import Decimal

from b_customers.models import Customer
from c_devices.models import Device
from d_repairs.models import Repair, RepairNote
from e_quotations.models import Quotation, QuotationItem
from f_payments.models import Payment

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = "admin"
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        password = extracted or "testpass123"
        self.set_password(password)
        if create:
            self.save()


class CustomerFactory(DjangoModelFactory):
    """Factory for creating Customer instances."""

    class Meta:
        model = Customer

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    contact_number = factory.Faker("numerify", text="09#########")
    email = factory.Faker("email")
    address = factory.Faker("address")
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.LazyAttribute(lambda obj: obj.created_by)


class DeviceFactory(DjangoModelFactory):
    """Factory for creating Device instances."""

    class Meta:
        model = Device

    customer = factory.SubFactory(CustomerFactory)
    type = factory.Iterator(["laptop", "phone", "tablet", "console", "other"])
    brand = factory.Iterator(["Apple", "Samsung", "ASUS", "Lenovo", "HP"])
    model = factory.Faker("bothify", text="Model-????-####")
    serial_number = factory.Sequence(lambda n: f"SN-{n:08d}")
    peripherals = factory.Faker(
        "random_element", elements=["Charger", "Charger, Mouse", "Case", ""]
    )
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.LazyAttribute(lambda obj: obj.created_by)


class RepairFactory(DjangoModelFactory):
    """Factory for creating Repair instances."""

    class Meta:
        model = Repair

    device = factory.SubFactory(DeviceFactory)
    issue_category = factory.Iterator(
        [
            "No Power",
            "Screen Damage",
            "Battery Issue",
            "Charging Problem",
            "Software Issue",
        ]
    )
    issue_description = factory.Faker("paragraph", nb_sentences=2)
    vmi = factory.Faker("sentence")
    mi = ""
    diagnosis = ""
    recommendation = ""
    status = "pending"
    assigned_to = None
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.LazyAttribute(lambda obj: obj.created_by)


class RepairNoteFactory(DjangoModelFactory):
    """Factory for creating RepairNote instances."""

    class Meta:
        model = RepairNote

    repair = factory.SubFactory(RepairFactory)
    content = factory.Faker("paragraph")
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.LazyAttribute(lambda obj: obj.created_by)


class QuotationFactory(DjangoModelFactory):
    """Factory for creating Quotation instances."""

    class Meta:
        model = Quotation

    repair = factory.SubFactory(RepairFactory)
    status = "draft"
    discount_amount = Decimal("0.00")
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.LazyAttribute(lambda obj: obj.created_by)


class QuotationItemFactory(DjangoModelFactory):
    """Factory for creating QuotationItem instances."""

    class Meta:
        model = QuotationItem

    quotation = factory.SubFactory(QuotationFactory)
    item_type = factory.Iterator(["parts", "labor", "service_fee"])
    description = factory.Faker("sentence", nb_words=4)
    quantity = factory.Faker("random_int", min=1, max=3)
    unit_price = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
        min_value=100,
        max_value=5000,
    )
    warranty_days = factory.Faker("random_element", elements=[None, 7, 30, 90])
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.LazyAttribute(lambda obj: obj.created_by)


class PaymentFactory(DjangoModelFactory):
    """Factory for creating Payment instances."""

    class Meta:
        model = Payment

    repair = factory.SubFactory(RepairFactory)
    amount = factory.Faker(
        "pydecimal",
        left_digits=4,
        right_digits=2,
        positive=True,
        min_value=500,
        max_value=10000,
    )
    payment_type = factory.Iterator(["down_payment", "partial", "full_settlement"])
    mode_of_payment = factory.Iterator(
        ["cash", "credit_card", "bank_transfer", "e_wallet"]
    )
    reference_number = factory.Faker("bothify", text="REF-####-????")
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.LazyAttribute(lambda obj: obj.created_by)
