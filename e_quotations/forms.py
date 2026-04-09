"""
Quotation forms with centralized styling.
"""

from django import forms
from z_core.forms import StyledModelForm, FIELD_CLASS, SELECT_CLASS
from .models import Quotation, QuotationItem


class QuotationForm(StyledModelForm):
    """Form for updating quotation status and discount."""

    class Meta:
        model = Quotation
        fields = ["status", "discount_amount"]
        widgets = {
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "discount_amount": forms.NumberInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
        }


class QuotationItemForm(StyledModelForm):
    """Form for adding/editing quotation line items."""

    class Meta:
        model = QuotationItem
        fields = ["item_type", "description", "quantity", "unit_price", "warranty_days"]
        widgets = {
            "item_type": forms.Select(attrs={"class": SELECT_CLASS}),
            "description": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "e.g., Screen Replacement, Labor Fee",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "1",
                    "min": "1",
                }
            ),
            "unit_price": forms.NumberInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "warranty_days": forms.NumberInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Optional",
                    "min": "0",
                }
            ),
        }

    def clean_quantity(self):
        """Validate that quantity is at least 1."""
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity

    def clean_unit_price(self):
        """Validate that unit price is greater than zero."""
        price = self.cleaned_data.get("unit_price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Unit price must be greater than zero.")
        return price
