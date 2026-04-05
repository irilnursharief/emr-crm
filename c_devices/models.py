from django.db import models
from b_customers.models import Customer, TimestampedModel
from django.conf import settings


class Device(TimestampedModel):
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
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="devices_created",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.model} ({self.serial_number})"
