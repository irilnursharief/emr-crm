"""
Status badge template tags for consistent status rendering across templates.

Usage in templates:
    {% load status_tags %}

    {# Repair status badge #}
    {% repair_status_badge repair.status repair.get_status_display %}

    {# Quotation status badge #}
    {% quotation_status_badge quotation.status quotation.get_status_display %}

    {# Generic badge with custom colors #}
    {% status_badge "success" "Completed" "green" %}
"""

from django import template
from django.utils.html import format_html

register = template.Library()


# Status color mappings
REPAIR_STATUS_COLORS = {
    "pending": ("yellow", "100", "700"),
    "in_progress": ("blue", "100", "700"),
    "awaiting_approval": ("purple", "100", "700"),
    "completed": ("green", "100", "700"),
    "released": ("gray", "100", "700"),
}

QUOTATION_STATUS_COLORS = {
    "draft": ("gray", "100", "700"),
    "sent": ("blue", "100", "700"),
    "approved": ("green", "100", "700"),
    "rejected": ("red", "100", "700"),
}

PAYMENT_TYPE_COLORS = {
    "down_payment": ("blue", "100", "700"),
    "partial": ("yellow", "100", "700"),
    "full_settlement": ("green", "100", "700"),
}


def _render_badge(
    display_text: str, color: str, bg_shade: str = "100", text_shade: str = "700"
) -> str:
    """
    Render a status badge with the given colors.

    Args:
        display_text: Text to display in the badge
        color: Tailwind color name (e.g., "green", "blue", "yellow")
        bg_shade: Background shade (default "100")
        text_shade: Text shade (default "700")

    Returns:
        HTML string for the badge
    """
    return format_html(
        '<span class="px-2.5 py-1 rounded-full text-xs font-medium bg-{}-{} text-{}-{} whitespace-nowrap">{}</span>',
        color,
        bg_shade,
        color,
        text_shade,
        display_text,
    )


@register.simple_tag
def repair_status_badge(status: str, display_text: str = None) -> str:
    """
    Render a repair status badge.

    Args:
        status: Repair status value (e.g., "pending", "in_progress")
        display_text: Optional display text (defaults to status if not provided)

    Usage:
        {% repair_status_badge repair.status repair.get_status_display %}
        {% repair_status_badge "pending" "Pending Diagnosis" %}
    """
    if display_text is None:
        display_text = status.replace("_", " ").title()

    colors = REPAIR_STATUS_COLORS.get(status, ("gray", "100", "700"))
    return _render_badge(display_text, *colors)


@register.simple_tag
def quotation_status_badge(status: str, display_text: str = None) -> str:
    """
    Render a quotation status badge.

    Args:
        status: Quotation status value (e.g., "draft", "approved")
        display_text: Optional display text

    Usage:
        {% quotation_status_badge quotation.status quotation.get_status_display %}
    """
    if display_text is None:
        display_text = status.replace("_", " ").title()

    colors = QUOTATION_STATUS_COLORS.get(status, ("gray", "100", "700"))
    return _render_badge(display_text, *colors)


@register.simple_tag
def payment_type_badge(payment_type: str, display_text: str = None) -> str:
    """
    Render a payment type badge.

    Args:
        payment_type: Payment type value (e.g., "down_payment", "full_settlement")
        display_text: Optional display text

    Usage:
        {% payment_type_badge payment.payment_type payment.get_payment_type_display %}
    """
    if display_text is None:
        display_text = payment_type.replace("_", " ").title()

    colors = PAYMENT_TYPE_COLORS.get(payment_type, ("gray", "100", "700"))
    return _render_badge(display_text, *colors)


@register.simple_tag
def status_badge(
    status: str,
    display_text: str,
    color: str,
    bg_shade: str = "100",
    text_shade: str = "700",
) -> str:
    """
    Render a generic status badge with custom colors.

    Args:
        status: Status value (not used, for consistency)
        display_text: Text to display
        color: Tailwind color name
        bg_shade: Background shade (default "100")
        text_shade: Text shade (default "700")

    Usage:
        {% status_badge "custom" "My Status" "indigo" %}
        {% status_badge "custom" "Warning" "orange" "200" "800" %}
    """
    return _render_badge(display_text, color, bg_shade, text_shade)


@register.inclusion_tag("components/status_badge.html")
def status_badge_component(status: str, status_type: str = "repair") -> dict:
    """
    Alternative: Render status badge using an inclusion tag with template.

    This allows for more complex badge markup if needed.

    Args:
        status: Status value
        status_type: Type of status ("repair", "quotation", "payment")

    Usage:
        {% status_badge_component repair.status "repair" %}
    """
    color_maps = {
        "repair": REPAIR_STATUS_COLORS,
        "quotation": QUOTATION_STATUS_COLORS,
        "payment": PAYMENT_TYPE_COLORS,
    }

    colors = color_maps.get(status_type, {}).get(status, ("gray", "100", "700"))

    return {
        "status": status,
        "color": colors[0],
        "bg_shade": colors[1],
        "text_shade": colors[2],
    }
