from django.db import models
from django.conf import settings
from django.urls import reverse
from z_core.models import AuditModel
from c_devices.models import Device


class Repair(AuditModel):
    """
    Repair model representing a repair job for a device.

    Workflow:
    1. PENDING: Device received, awaiting diagnosis
    2. IN_PROGRESS: Technician working on repair
    3. AWAITING_APPROVAL: Quotation sent, waiting for customer approval
    4. COMPLETED: Repair finished
    5. RELEASED: Device returned to customer
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Diagnosis"
        IN_PROGRESS = "in_progress", "In Progress"
        AWAITING_APPROVAL = "awaiting_approval", "Awaiting Customer Approval"
        COMPLETED = "completed", "Completed"
        RELEASED = "released", "Released to Customer"

    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name="repairs")

    # Intake Fields (Required at drop-off)
    issue_category = models.CharField(max_length=100)
    issue_description = models.TextField()
    vmi = models.TextField(verbose_name="VMI (Initial Inspection)")

    # Technician Fields (Filled later during repair)
    mi = models.TextField(blank=True, verbose_name="MI (Technical Inspection)")
    diagnosis = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_repairs",
        limit_choices_to={"role__in": ["technician", "admin"]},
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def __str__(self):
        return f"Repair #{self.id} | {self.device}"

    def get_absolute_url(self):
        return reverse("repairs:detail", args=[self.pk])

    @property
    def total_paid(self):
        """Calculate total amount paid for this repair."""
        return sum(p.amount for p in self.payments.all())

    @property
    def quotation_total(self):
        """Get quotation total, returns 0 if no quotation exists."""
        try:
            return self.quotation.total
        except Repair.quotation.RelatedObjectDoesNotExist:
            return 0

    @property
    def balance_due(self):
        """Calculate remaining balance to be paid."""
        return self.quotation_total - self.total_paid


class RepairNote(AuditModel):
    """
    Journal entries for a repair, tracking progress and notes.

    Note: RepairNote only uses created_by (notes are not edited after creation).
    """

    repair = models.ForeignKey(Repair, on_delete=models.PROTECT, related_name="notes")
    content = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Repair Journal Entry"
        verbose_name_plural = "Repair Journal"
        indexes = [
            models.Index(fields=["repair", "-created_at"]),
        ]

    def __str__(self):
        return (
            f"Note by {self.created_by.username} at {self.created_at.strftime('%H:%M')}"
        )
