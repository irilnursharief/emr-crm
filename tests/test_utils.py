"""
Utility function tests for EMR CRM.

These tests verify that utility functions work correctly.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

from d_repairs.signing import create_signed_url, verify_signed_url
from z_core.logging_utils import (
    get_logger,
    get_user_info,
    get_request_info,
    log_user_action,
)

from tests.factories import UserFactory


# =============================================================================
# SIGNED URL TESTS
# =============================================================================


class TestSignedUrls:
    """Tests for URL signing functionality."""

    def test_create_signed_url(self):
        """Test that signed URL is created correctly."""
        url = "http://localhost:8000/repairs/1/job-order/"
        signed = create_signed_url(url)

        assert "signature=" in signed
        assert "expires=" in signed

    def test_verify_valid_signature(self):
        """Test that valid signature is verified."""
        factory = RequestFactory()

        # Create a signed URL
        url = "http://localhost:8000/repairs/1/job-order/"
        signed = create_signed_url(url)

        # Extract signature and expires from signed URL
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(signed)
        params = parse_qs(parsed.query)

        # Create a request with those parameters
        request = factory.get(
            "/repairs/1/job-order/",
            {
                "signature": params["signature"][0],
                "expires": params["expires"][0],
            },
        )

        assert verify_signed_url(request) is True

    def test_verify_missing_signature(self):
        """Test that missing signature fails verification."""
        factory = RequestFactory()
        request = factory.get("/repairs/1/job-order/", {"expires": "9999999999"})

        assert verify_signed_url(request) is False

    def test_verify_missing_expires(self):
        """Test that missing expires fails verification."""
        factory = RequestFactory()
        request = factory.get("/repairs/1/job-order/", {"signature": "abc123"})

        assert verify_signed_url(request) is False

    def test_verify_expired_url(self):
        """Test that expired URL fails verification."""
        factory = RequestFactory()

        # Create a request with expired timestamp
        request = factory.get(
            "/repairs/1/job-order/",
            {
                "signature": "abc123",
                "expires": "1000000000",  # Way in the past
            },
        )

        assert verify_signed_url(request) is False

    def test_verify_invalid_signature(self):
        """Test that invalid signature fails verification."""
        factory = RequestFactory()

        future_time = str(int(time.time()) + 3600)
        request = factory.get(
            "/repairs/1/job-order/",
            {
                "signature": "invalid_signature_here",
                "expires": future_time,
            },
        )

        assert verify_signed_url(request) is False


# =============================================================================
# LOGGING UTILITY TESTS
# =============================================================================


class TestLoggingUtils:
    """Tests for logging utility functions."""

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("emr")
        assert logger is not None
        assert logger.name == "emr"

    def test_get_user_info_authenticated(self):
        """Test getting user info for authenticated user."""
        user = UserFactory.build(username="testuser", id=123)

        factory = RequestFactory()
        request = factory.get("/")
        request.user = user

        info = get_user_info(request)

        assert "testuser" in info
        assert "123" in info

    def test_get_user_info_anonymous(self):
        """Test getting user info for anonymous user."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()

        info = get_user_info(request)

        assert "anonymous" in info

    def test_get_user_info_none_request(self):
        """Test getting user info with no request."""
        info = get_user_info(None)

        assert "system" in info

    def test_get_request_info(self):
        """Test getting request info."""
        factory = RequestFactory()
        request = factory.get("/some/path/")

        info = get_request_info(request)

        assert "GET" in info
        assert "/some/path/" in info

    def test_get_request_info_post(self):
        """Test getting request info for POST."""
        factory = RequestFactory()
        request = factory.post("/some/path/")

        info = get_request_info(request)

        assert "POST" in info
