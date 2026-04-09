"""
Centralized form styling and base form classes.

This module provides consistent styling for all forms across the application.
All form field classes are defined here to ensure visual consistency.

Usage:
    from z_core.forms import StyledModelForm, FIELD_CLASSES

    class MyForm(StyledModelForm):
        class Meta:
            model = MyModel
            fields = ['field1', 'field2']
"""

from django import forms


# =============================================================================
# FIELD STYLING CONSTANTS
# =============================================================================

# Base input styling (text, email, number, etc.)
FIELD_CLASS = (
    "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl "
    "text-gray-900 placeholder-gray-400 "
    "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent "
    "transition duration-200 shadow-sm"
)

# Select dropdown styling
SELECT_CLASS = (
    "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl "
    "text-gray-900 "
    "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent "
    "transition duration-200 shadow-sm"
)

# Textarea styling
TEXTAREA_CLASS = (
    "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl "
    "text-gray-900 placeholder-gray-400 "
    "focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent "
    "transition duration-200 shadow-sm resize-y"
)

# Checkbox styling
CHECKBOX_CLASS = (
    "w-5 h-5 text-primary bg-white border-gray-300 rounded "
    "focus:ring-primary focus:ring-2"
)

# File input styling
FILE_CLASS = (
    "w-full px-4 py-3 bg-white border border-gray-300 rounded-xl "
    "text-gray-900 "
    "file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 "
    "file:text-sm file:font-medium file:bg-primary file:text-white "
    "hover:file:bg-opacity-90 transition duration-200 shadow-sm"
)

# Monospace input (for serial numbers, codes, etc.)
MONO_FIELD_CLASS = FIELD_CLASS + " font-mono"

# Disabled field styling
DISABLED_CLASS = "bg-gray-100 cursor-not-allowed opacity-75"


# =============================================================================
# WIDGET DEFAULTS
# =============================================================================


def get_text_widget(placeholder: str = "", **kwargs) -> forms.TextInput:
    """Get a styled text input widget."""
    attrs = {"class": FIELD_CLASS, "placeholder": placeholder}
    attrs.update(kwargs)
    return forms.TextInput(attrs=attrs)


def get_email_widget(placeholder: str = "Email address", **kwargs) -> forms.EmailInput:
    """Get a styled email input widget."""
    attrs = {"class": FIELD_CLASS, "placeholder": placeholder}
    attrs.update(kwargs)
    return forms.EmailInput(attrs=attrs)


def get_number_widget(
    placeholder: str = "0", step: str = "1", **kwargs
) -> forms.NumberInput:
    """Get a styled number input widget."""
    attrs = {"class": FIELD_CLASS, "placeholder": placeholder, "step": step}
    attrs.update(kwargs)
    return forms.NumberInput(attrs=attrs)


def get_decimal_widget(placeholder: str = "0.00", **kwargs) -> forms.NumberInput:
    """Get a styled decimal input widget."""
    attrs = {"class": FIELD_CLASS, "placeholder": placeholder, "step": "0.01"}
    attrs.update(kwargs)
    return forms.NumberInput(attrs=attrs)


def get_textarea_widget(
    placeholder: str = "", rows: int = 4, **kwargs
) -> forms.Textarea:
    """Get a styled textarea widget."""
    attrs = {"class": TEXTAREA_CLASS, "placeholder": placeholder, "rows": rows}
    attrs.update(kwargs)
    return forms.Textarea(attrs=attrs)


def get_select_widget(**kwargs) -> forms.Select:
    """Get a styled select widget."""
    attrs = {"class": SELECT_CLASS}
    attrs.update(kwargs)
    return forms.Select(attrs=attrs)


def get_checkbox_widget(**kwargs) -> forms.CheckboxInput:
    """Get a styled checkbox widget."""
    attrs = {"class": CHECKBOX_CLASS}
    attrs.update(kwargs)
    return forms.CheckboxInput(attrs=attrs)


def get_mono_widget(placeholder: str = "", **kwargs) -> forms.TextInput:
    """Get a styled monospace text input widget (for serial numbers, etc.)."""
    attrs = {"class": MONO_FIELD_CLASS, "placeholder": placeholder}
    attrs.update(kwargs)
    return forms.TextInput(attrs=attrs)


# =============================================================================
# BASE FORM CLASSES
# =============================================================================


class StyledFormMixin:
    """
    Mixin that applies consistent styling to all form fields.

    Automatically applies the appropriate CSS classes based on field type.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()

    def _apply_styling(self):
        """Apply styling to all fields based on their widget type."""
        for field_name, field in self.fields.items():
            widget = field.widget
            existing_class = widget.attrs.get("class", "")

            # Skip if already styled
            if "rounded-xl" in existing_class or "rounded-lg" in existing_class:
                continue

            # Apply styling based on widget type
            if isinstance(widget, forms.Textarea):
                widget.attrs["class"] = f"{TEXTAREA_CLASS} {existing_class}".strip()
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = f"{SELECT_CLASS} {existing_class}".strip()
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{CHECKBOX_CLASS} {existing_class}".strip()
            elif isinstance(widget, forms.FileInput):
                widget.attrs["class"] = f"{FILE_CLASS} {existing_class}".strip()
            elif isinstance(
                widget,
                (
                    forms.TextInput,
                    forms.EmailInput,
                    forms.NumberInput,
                    forms.PasswordInput,
                ),
            ):
                widget.attrs["class"] = f"{FIELD_CLASS} {existing_class}".strip()


class StyledForm(StyledFormMixin, forms.Form):
    """
    Base Form class with automatic styling.

    Usage:
        class ContactForm(StyledForm):
            name = forms.CharField(max_length=100)
            email = forms.EmailField()
            message = forms.CharField(widget=forms.Textarea)
    """

    pass


class StyledModelForm(StyledFormMixin, forms.ModelForm):
    """
    Base ModelForm class with automatic styling.

    Usage:
        class CustomerForm(StyledModelForm):
            class Meta:
                model = Customer
                fields = ['first_name', 'last_name', 'email']
    """

    pass
