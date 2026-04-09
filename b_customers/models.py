from django.db import models
from z_core.models import AuditModel


class Customer(AuditModel):
    """
    Customer model representing clients who bring devices for repair.

    Inherits from AuditModel which provides:
    - created_at, updated_at (automatic timestamps)
    - created_by, updated_by (user tracking)
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["last_name", "first_name"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
