from django import forms
from .models import Device


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["customer", "type", "brand", "model", "serial_number", "peripherals"]
        widgets = {
            "customer": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                }
            ),
            "type": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                }
            ),
            "brand": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                    "placeholder": "e.g. ASUS, Apple, Samsung",
                }
            ),
            "model": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                    "placeholder": "e.g. ROG Zephyrus G14",
                }
            ),
            "serial_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                    "placeholder": "Enter unique serial number",
                }
            ),
            "peripherals": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                    "placeholder": "e.g. Charger, Mouse, Case (optional)",
                }
            ),
        }
