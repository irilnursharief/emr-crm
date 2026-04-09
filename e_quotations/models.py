from decimal import Decimal
from django.db import models
from z_core.models import AuditModel
from d_repairs.models import Repair


class Quotation(AuditModel):
    """
    Quotation model for repair pricing.

    Each repair can have only ONE quotation (OneToOneField).
    The quotation contains line items (parts, labor, fees) and a discount.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent to Customer"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    repair = models.OneToOneField(
        Repair, on_delete=models.PROTECT, related_name="quotation"
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return (
            f"QTN-{self.id:04d} | {self.repair.device.brand} {self.repair.device.model}"
        )

    @property
    def subtotal(self):
        """Calculate sum of all line items."""
        return sum(item.subtotal for item in self.items.all())

    @property
    def total(self):
        """Calculate total after discount (minimum 0)."""
        calculated_total = self.subtotal - self.discount_amount
        return max(Decimal("0.00"), calculated_total)


class QuotationItem(AuditModel):
    """
    Line item for a quotation (parts, labor, or service fees).
    """

    class ItemType(models.TextChoices):
        PARTS = "parts", "Parts"
        LABOR = "labor", "Labor"
        SERVICE_FEE = "service_fee", "Service Fee"

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
        indexes = [
            models.Index(fields=["quotation", "created_at"]),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.description} (@ {self.unit_price})"

    @property
    def subtotal(self):
        """Calculate line item subtotal."""
        return Decimal(self.quantity) * self.unit_price
