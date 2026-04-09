from django.db import models
from z_core.models import AuditModel
from d_repairs.models import Repair


class Payment(AuditModel):
    """
    Payment model for tracking payments against repairs.

    A repair can have multiple payments (down payment, partial, full settlement).
    """

    class PaymentType(models.TextChoices):
        DOWN_PAYMENT = "down_payment", "Down Payment"
        PARTIAL = "partial", "Partial Payment"
        FULL_SETTLEMENT = "full_settlement", "Full Settlement"

    class PaymentMode(models.TextChoices):
        CASH = "cash", "Cash"
        CREDIT_CARD = "credit_card", "Credit Card"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        E_WALLET = "e_wallet", "E-Wallet"

    repair = models.ForeignKey(
        Repair, on_delete=models.PROTECT, related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    mode_of_payment = models.CharField(max_length=20, choices=PaymentMode.choices)
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Transaction reference for card/bank/e-wallet payments",
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["repair", "created_at"]),
        ]

    def __str__(self):
        return f"₱{self.amount:,.2f} ({self.get_payment_type_display()}) — Repair #{self.repair.id}"
