from django.db import models
from django.conf import settings
from b_customers.models import TimestampedModel
from d_repairs.models import Repair


class Payment(TimestampedModel):
    class PaymentType(models.TextChoices):
        DOWN_PAYMENT = "down_payment", "Down Payment"
        PARTIAL = "partial", "Partial Payment"
        FULL_SETTLEMENT = "full_settlement", "Full Settlement"

    class PaymentMode(models.TextChoices):
        CASH = "cash", "Cash"
        CREDIT_CARD = "credit_card", "Credit Card"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        E_WALLET = "e_wallet", "E-Wallet"

    # ForeignKey (1:N) — one repair can have multiple payments
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

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments_created",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["created_at"]  # Chronological order

    def __str__(self):
        return f"₱{self.amount:,.2f} ({self.get_payment_type_display()}) — Repair #{self.repair.id}"
