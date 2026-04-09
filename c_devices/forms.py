"""
Device forms with centralized styling.
"""

from django import forms
from z_core.forms import StyledModelForm, FIELD_CLASS, SELECT_CLASS, MONO_FIELD_CLASS
from .models import Device


class DeviceForm(StyledModelForm):
    """Form for creating and editing devices."""

    class Meta:
        model = Device
        fields = ["customer", "type", "brand", "model", "serial_number", "peripherals"]
        widgets = {
            "customer": forms.Select(attrs={"class": SELECT_CLASS}),
            "type": forms.Select(attrs={"class": SELECT_CLASS}),
            "brand": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "e.g. ASUS, Apple, Samsung",
                }
            ),
            "model": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "e.g. ROG Zephyrus G14",
                }
            ),
            "serial_number": forms.TextInput(
                attrs={
                    "class": MONO_FIELD_CLASS,
                    "placeholder": "Enter unique serial number",
                }
            ),
            "peripherals": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "e.g. Charger, Mouse, Case (optional)",
                }
            ),
        }
