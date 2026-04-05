from django import forms
from .models import Repair

FIELD_CLASS = "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
TEXTAREA_CLASS = FIELD_CLASS
SELECT_CLASS = "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"


class RepairCreateForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = [
            "device",
            "issue_category",
            "issue_description",
            "vmi",
            "assigned_to",
            "status",
        ]
        widgets = {
            "device": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                }
            ),
            "issue_category": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                    "placeholder": "e.g. No Power, Screen Damage, Software Issue",
                }
            ),
            "issue_description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                    "placeholder": "Describe the issue in detail",
                    "rows": 4,
                }
            ),
            "vmi": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                    "placeholder": "Visible condition at drop-off (scratches, dents, etc.)",
                    "rows": 3,
                }
            ),
            "assigned_to": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200",
                }
            ),
        }


class RepairIntakeForm(forms.ModelForm):
    """For all roles — editing intake fields only."""

    class Meta:
        model = Repair
        fields = ["issue_category", "issue_description", "vmi"]
        widgets = {
            "issue_category": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "e.g. No Power, Screen Damage",
                }
            ),
            "issue_description": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Describe the issue in detail",
                    "rows": 4,
                }
            ),
            "vmi": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Visible condition at drop-off",
                    "rows": 3,
                }
            ),
        }


class RepairTechnicianForm(forms.ModelForm):
    """For technicians and admins only — technical findings + status."""

    class Meta:
        model = Repair
        fields = ["mi", "diagnosis", "recommendation", "status", "assigned_to"]
        widgets = {
            "mi": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Internal technical findings",
                    "rows": 4,
                }
            ),
            "diagnosis": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Technical diagnosis result",
                    "rows": 4,
                }
            ),
            "recommendation": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Recommended course of action",
                    "rows": 4,
                }
            ),
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
            "assigned_to": forms.Select(attrs={"class": SELECT_CLASS}),
        }
