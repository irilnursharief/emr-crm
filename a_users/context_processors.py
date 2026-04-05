from django.urls import resolve


def current_url_name(request):
    match = resolve(request.path_info)
    return {"current_url_name": match.url_name, "current_app": match.app_name}
