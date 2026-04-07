from django import forms
from .models import Customer

# Define the shared classes for light mode
FIELD_CLASS = "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition duration-200 shadow-sm"
TEXTAREA_CLASS = FIELD_CLASS  # Use the same class for textareas


class CustomerForm(forms.ModelForm):
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
