"""
Core models and mixins used across the application.

This module provides:
- TimestampedModel: Adds created_at and updated_at fields
- AuditModel: Extends TimestampedModel with created_by and updated_by fields
"""

from django.db import models
from django.conf import settings


class TimestampedModel(models.Model):
    """
    Abstract base model that provides created_at and updated_at timestamps.

    These fields are automatically managed:
    - created_at: Set once when the record is first created
    - updated_at: Updated every time the record is saved

    Usage:
        class MyModel(TimestampedModel):
            name = models.CharField(max_length=100)
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditModel(TimestampedModel):
    """
    Abstract base model that tracks who created and last modified a record.

    Extends TimestampedModel with:
    - created_by: The user who created the record (set once)
    - updated_by: The user who last modified the record (updated on each save)

    Usage:
        class MyModel(AuditModel):
            name = models.CharField(max_length=100)

        # In your view:
        obj = MyModel(name="Test", created_by=request.user, updated_by=request.user)
        obj.save()

        # On update:
        obj.name = "Updated"
        obj.updated_by = request.user
        obj.save()
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_created",
        null=True,
        blank=True,
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_updated",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
