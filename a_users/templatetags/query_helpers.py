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
