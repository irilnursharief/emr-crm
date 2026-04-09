"""
Login Required Middleware

This middleware ensures that all pages require authentication by default,
with specific exceptions for:
1. Admin panel (/admin/)
2. Authentication pages (/accounts/)
3. Static/media files (in DEBUG mode)
4. Pages with valid signed URLs (for PDF generation)

This approach is more secure than decorating each view with @login_required
because you can't accidentally forget to protect a new view.
"""

from django.conf import settings
from django.shortcuts import redirect
from d_repairs.signing import verify_signed_url


class LoginRequiredMiddleware:
    """
    Middleware that requires authentication for all views by default.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Allow unauthenticated access to admin and auth endpoints
        #    These have their own authentication handling
        if request.path.startswith("/admin/") or request.path.startswith("/accounts/"):
            return self.get_response(request)

        # 2. Allow static/media files in debug mode
        #    In production, these should be served by your web server (nginx)
        if settings.DEBUG and (
            request.path.startswith("/static/") or request.path.startswith("/media/")
        ):
            return self.get_response(request)

        # 3. Allow requests with valid signed URLs (for PDF generation)
        #    This lets our headless browser access protected pages
        if verify_signed_url(request):
            return self.get_response(request)

        # 4. Require authentication for everything else
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
