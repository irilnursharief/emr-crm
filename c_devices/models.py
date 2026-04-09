from django.db import models
from z_core.models import AuditModel
from b_customers.models import Customer


class Device(AuditModel):
    """
    Device model representing customer devices brought in for repair.

    Each device belongs to one customer and can have multiple repairs.
    """

    class DeviceType(models.TextChoices):
        LAPTOP = "laptop", "Laptop"
        PHONE = "phone", "Phone"
        TABLET = "tablet", "Tablet"
        CONSOLE = "console", "Console"
        OTHER = "other", "Other"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="devices",
    )
    type = models.CharField(max_length=50, choices=DeviceType.choices)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True, db_index=True)
    peripherals = models.CharField(
        max_length=255, blank=True, null=True, help_text="e.g. Charger, Case, Cable"
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["type"]),
            models.Index(fields=["brand"]),
        ]

    def __str__(self):
        return f"{self.brand} {self.model} ({self.serial_number})"
