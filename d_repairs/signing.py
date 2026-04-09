"""
URL Signing Utility for Secure PDF Generation

This module provides functions to create and verify signed URLs.
Signed URLs are used to allow Playwright (headless browser) to access
protected pages without a login session.

How it works:
1. When generating a PDF, we create a "signature" that includes the URL path
2. The signature is created using Django's SECRET_KEY (cryptographically secure)
3. We add an expiration timestamp to prevent indefinite reuse
4. When the signed URL is accessed, we verify the signature matches and hasn't expired

This is more secure than a static token because:
- Each URL has a unique signature based on the path
- URLs expire after a short time (default: 60 seconds)
- Signatures can't be guessed or forged
"""

import hashlib
import hmac
import time
from django.conf import settings
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse


def _get_secret_key() -> bytes:
    """Get the Django SECRET_KEY as bytes for HMAC signing."""
    secret = settings.SECRET_KEY
    if isinstance(secret, str):
        return secret.encode("utf-8")
    return secret


def _create_signature(path: str, expires: int) -> str:
    """
    Create an HMAC signature for the given path and expiration time.

    Args:
        path: URL path (e.g., "/repairs/1/job-order/")
        expires: Unix timestamp when the signature expires

    Returns:
        Hex-encoded HMAC signature
    """
    # Create the message to sign
    message = f"{path}:{expires}".encode("utf-8")

    # Create HMAC signature using SECRET_KEY
    signature = hmac.new(
        key=_get_secret_key(), msg=message, digestmod=hashlib.sha256
    ).hexdigest()

    return signature


def create_signed_url(url: str) -> str:
    """
    Create a signed URL that expires after PDF_URL_EXPIRY_SECONDS.

    Args:
        url: The original URL (e.g., "http://localhost:8000/repairs/1/job-order/")

    Returns:
        The URL with signature and expiry parameters added

    Example:
        >>> signed = create_signed_url("http://localhost:8000/repairs/1/job-order/")
        >>> print(signed)
        http://localhost:8000/repairs/1/job-order/?expires=1699999999&signature=abc123...
    """
    # Parse the URL into components
    parsed = urlparse(url)

    # Calculate expiration timestamp
    expiry_seconds = getattr(settings, "PDF_URL_EXPIRY_SECONDS", 60)
    expires = int(time.time()) + expiry_seconds

    # Create HMAC signature
    signature = _create_signature(parsed.path, expires)

    # Add signature and expiry to query parameters
    # Start with existing params (if any)
    params = parse_qs(parsed.query)
    params["expires"] = [str(expires)]
    params["signature"] = [signature]

    # Rebuild the URL with new parameters
    new_query = urlencode(params, doseq=True)
    signed_url = urlunparse(parsed._replace(query=new_query))

    return signed_url


def verify_signed_url(request) -> bool:
    """
    Verify that a request has a valid, non-expired signature.

    Args:
        request: Django HttpRequest object

    Returns:
        True if signature is valid and not expired, False otherwise

    Usage in views:
        if verify_signed_url(request):
            # Allow access
        else:
            # Deny access (return 403)
    """
    signature = request.GET.get("signature", "")
    expires = request.GET.get("expires", "")

    # Both parameters are required
    if not signature or not expires:
        return False

    try:
        # Convert expires to integer
        expires_int = int(expires)

        # Check if URL has expired
        if time.time() > expires_int:
            return False

        # Recreate the expected signature
        expected_signature = _create_signature(request.path, expires_int)

        # Compare signatures using constant-time comparison (prevents timing attacks)
        if not hmac.compare_digest(signature, expected_signature):
            return False

        return True

    except (ValueError, TypeError):
        # Invalid expires format or other error
        return False


def get_signature_error_message(request) -> str:
    """
    Get a user-friendly error message explaining why signature verification failed.

    Useful for debugging and logging.
    """
    signature = request.GET.get("signature", "")
    expires = request.GET.get("expires", "")

    if not signature:
        return "Missing signature parameter"

    if not expires:
        return "Missing expires parameter"

    try:
        expires_int = int(expires)
        current_time = time.time()

        if current_time > expires_int:
            seconds_ago = int(current_time - expires_int)
            return f"URL expired {seconds_ago} seconds ago"

        # Check signature
        expected_signature = _create_signature(request.path, expires_int)
        if signature != expected_signature:
            return "Invalid signature (path or secret mismatch)"

    except ValueError:
        return "Invalid expires parameter (not a valid number)"

    return "Unknown error"
