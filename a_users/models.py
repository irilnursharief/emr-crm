from django.db import models
from django.contrib.auth.models import AbstractUser


class Users(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        CRS = "crs", "CRS"
        TECHNICIAN = "technician", "Technician"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CRS)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_crs(self):
        return self.role == self.Role.CRS

    @property
    def is_technician(self):
        return self.role == self.Role.TECHNICIAN
