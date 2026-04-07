from django import forms
from .models import Payment

FIELD_CLASS = "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition duration-200 shadow-sm"
SELECT_CLASS = "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition duration-200 shadow-sm"


class PaymentForm(forms.ModelForm):
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
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount
