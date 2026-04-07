from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_string(context):
    """
    Returns the current GET parameters as a query string,
    excluding 'page' so pagination links don't stack page numbers.
    """
    request = context["request"]
    params = request.GET.copy()
    params.pop("page", None)
    return params.urlencode()


@register.simple_tag(takes_context=True)
def sort_url(context, field):
    """
    Builds a sort URL for a given field.
    Toggles direction if already sorting by this field.
    Resets page to 1 when sorting changes.
    """
    request = context["request"]
    params = request.GET.copy()

    current_sort = params.get("sort", "")
    current_dir = params.get("dir", "desc")

    if current_sort == field:
        # Toggle direction
        new_dir = "asc" if current_dir == "desc" else "desc"
    else:
        # Default to descending for new sort
        new_dir = "desc"

    params["sort"] = field
    params["dir"] = new_dir
    params.pop("page", None)  # Reset to page 1

    return params.urlencode()


@register.simple_tag(takes_context=True)
def sort_indicator(context, field):
    """
    Returns the sort arrow indicator for a column header.
    ↑ = ascending, ↓ = descending, ↕ = unsorted
    """
    request = context["request"]
    current_sort = request.GET.get("sort", "")
    current_dir = request.GET.get("dir", "desc")

    if current_sort == field:
        return "↑" if current_dir == "asc" else "↓"
    return "↕"


@register.simple_tag(takes_context=True)
def sort_header_class(context, field):
    """
    Returns extra CSS classes for an active sort column header.
    """
    request = context["request"]
    current_sort = request.GET.get("sort", "")

    if current_sort == field:
        return "text-primary"
    return "text-secondary hover:text-primary"
