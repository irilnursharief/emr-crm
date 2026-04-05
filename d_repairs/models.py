from django.db import models
from django.conf import settings
from b_customers.models import TimestampedModel
from c_devices.models import Device


class Repair(TimestampedModel):
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
        max_length=30, choices=Status.choices, default=Status.PENDING, db_index=True
    )

    # Assignment & Audit
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_repairs",
        limit_choices_to={"role__in": ["technician", "admin"]},  # Only techs/admins
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="repairs_created",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Repair #{self.id} | {self.device}"


class RepairNote(TimestampedModel):
    repair = models.ForeignKey(Repair, on_delete=models.PROTECT, related_name="notes")
    content = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="repair_notes"
    )

    class Meta:
        ordering = ["created_at"]  # Chronological order (oldest first)
        verbose_name = "Repair Journal Entry"
        verbose_name_plural = "Repair Journal"

    def __str__(self):
        return (
            f"Note by {self.created_by.username} at {self.created_at.strftime('%H:%M')}"
        )
