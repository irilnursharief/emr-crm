from django.urls import resolve, Resolver404


def current_url_name(request):
    try:
        match = resolve(request.path_info)
        return {
            "current_url_name": match.url_name,
            "current_app": match.app_name,
        }
    except Resolver404:
        return {
            "current_url_name": None,
            "current_app": None,
        }
