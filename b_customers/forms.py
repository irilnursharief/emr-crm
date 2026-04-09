"""
Customer forms with centralized styling.
"""

from django import forms
from z_core.forms import StyledModelForm, FIELD_CLASS, TEXTAREA_CLASS
from .models import Customer


class CustomerForm(StyledModelForm):
    """Form for creating and editing customers."""

    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "contact_number", "email", "address"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Last name",
                }
            ),
            "contact_number": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Contact number",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Email (optional)",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Address (optional)",
                    "rows": 3,
                }
            ),
        }
