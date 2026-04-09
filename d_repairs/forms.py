"""
Repair forms with centralized styling.
"""

from django import forms
from z_core.forms import StyledModelForm, FIELD_CLASS, TEXTAREA_CLASS, SELECT_CLASS
from .models import Repair, RepairNote


class RepairCreateForm(StyledModelForm):
    """Form for creating new repair tickets."""

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
            "device": forms.Select(attrs={"class": SELECT_CLASS}),
            "issue_category": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "e.g. No Power, Screen Damage, Software Issue",
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
                    "placeholder": "Visible condition at drop-off (scratches, dents, etc.)",
                    "rows": 3,
                }
            ),
            "assigned_to": forms.Select(attrs={"class": SELECT_CLASS}),
            "status": forms.Select(attrs={"class": SELECT_CLASS}),
        }


class RepairIntakeForm(StyledModelForm):
    """Form for editing intake information (all roles)."""

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


class RepairTechnicianForm(StyledModelForm):
    """Form for editing technical details (technicians and admins only)."""

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


class RepairNoteForm(StyledModelForm):
    """Form for adding repair journal notes."""

    class Meta:
        model = RepairNote
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": TEXTAREA_CLASS,
                    "placeholder": "Add a repair note...",
                    "rows": 4,
                }
            ),
        }
