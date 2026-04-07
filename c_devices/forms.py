from django import forms
from .models import Device

# Define the shared classes for light mode
FIELD_CLASS = "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition duration-200 shadow-sm"
SELECT_CLASS = "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition duration-200 shadow-sm"


class DeviceForm(forms.ModelForm):
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
                    "class": f"{FIELD_CLASS} font-mono",  # Added font-mono back in
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
