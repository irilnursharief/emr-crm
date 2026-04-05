from decimal import Decimal
from django.db import models
from django.conf import settings
from b_customers.models import TimestampedModel
from d_repairs.models import Repair


class Quotation(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent to Customer"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    # OneToOneField enforces exactly ONE quotation per repair
    repair = models.OneToOneField(
        Repair, on_delete=models.PROTECT, related_name="quotation"
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    # Using DecimalField for currency to prevent floating-point math errors
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="quotations_created",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"QTN-{self.id:04d} | {self.repair.device.brand} {self.repair.device.model}"
        )

    @property
    def subtotal(self):
        # Calculates sum of all line items
        return sum(item.subtotal for item in self.items.all())

    @property
    def total(self):
        # Applies discount, ensures total doesn't drop below zero
        calculated_total = self.subtotal - self.discount_amount
        return max(Decimal("0.00"), calculated_total)


class QuotationItem(TimestampedModel):
    class ItemType(models.TextChoices):
        PARTS = "parts", "Parts"
        LABOR = "labor", "Labor"
        SERVICE_FEE = "service_fee", "Service Fee"

    # CASCADE here: If a quotation is deleted, its line items should be deleted too
    quotation = models.ForeignKey(
        Quotation, on_delete=models.CASCADE, related_name="items"
    )

    item_type = models.CharField(max_length=20, choices=ItemType.choices)
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    warranty_days = models.PositiveIntegerField(
        blank=True, null=True, help_text="Optional warranty period in days"
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.quantity}x {self.description} (@ {self.unit_price})"

    @property
    def subtotal(self):
        # Computed property as defined in your project plan
        return Decimal(self.quantity) * self.unit_price
