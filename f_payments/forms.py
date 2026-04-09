"""
Payment forms with centralized styling.
"""

from django import forms
from z_core.forms import StyledModelForm, FIELD_CLASS, SELECT_CLASS
from .models import Payment


class PaymentForm(StyledModelForm):
    """Form for recording payments."""

    class Meta:
        model = Payment
        fields = ["amount", "payment_type", "mode_of_payment", "reference_number"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "payment_type": forms.Select(attrs={"class": SELECT_CLASS}),
            "mode_of_payment": forms.Select(attrs={"class": SELECT_CLASS}),
            "reference_number": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Transaction reference (optional for cash)",
                }
            ),
        }

    def clean_amount(self):
        """Validate that payment amount is greater than zero."""
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount
