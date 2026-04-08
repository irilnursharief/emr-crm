from django.conf import settings
from django.shortcuts import redirect


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow unauthenticated access to admin and auth endpoints
        if request.path.startswith("/admin/") or request.path.startswith("/accounts/"):
            return self.get_response(request)

        # Allow static/media in debug (optional)
        if settings.DEBUG and (
            request.path.startswith("/static/") or request.path.startswith("/media/")
        ):
            return self.get_response(request)

        # Allow internal PDF generation requests
        pdf_token = request.GET.get("pdf_token", "")
        if pdf_token == settings.PDF_SECRET_TOKEN:
            return self.get_response(request)

        # If user not authenticated, redirect to login
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
