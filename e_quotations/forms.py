from django import forms
from .models import Quotation, QuotationItem

FIELD_CLASS = "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition duration-200 shadow-sm"
SELECT_CLASS = "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition duration-200 shadow-sm"


class QuotationForm(forms.ModelForm):
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


class QuotationItemForm(forms.ModelForm):
    """Form for adding/editing line items."""

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
        quantity = self.cleaned_data.get("quantity")
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity

    def clean_unit_price(self):
        price = self.cleaned_data.get("unit_price")
        if price <= 0:
            raise forms.ValidationError("Unit price must be greater than zero.")
        return price
