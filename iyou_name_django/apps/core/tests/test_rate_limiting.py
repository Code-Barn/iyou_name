"""
Tests for rate limiting functionality.
"""

from unittest.mock import patch, Mock
from django.test import TestCase, RequestFactory
from django.http import HttpResponseTooManyRequests
from django.contrib.auth.models import User
from apps.core.rate_limiting import (
    rate_limit,
    upload_rate_limit,
    auth_rate_limit,
    user_rate_limit,
    rate_limiter,
)


class RateLimitingTests(TestCase):
    """Test rate limiting decorators and functionality."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def tearDown(self):
        # Clear rate limiter state between tests
        rate_limiter.requests.clear()

    def test_basic_rate_limiting(self):
        """Test that basic rate limiting works."""
        request = self.factory.get("/test/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        @rate_limit(limit=2, window=60)
        def test_view(request):
            return HttpResponse("OK")

        # First two requests should succeed
        response1 = test_view(request)
        self.assertEqual(response1.status_code, 200)

        response2 = test_view(request)
        self.assertEqual(response2.status_code, 200)

        # Third request should be rate limited
        response3 = test_view(request)
        self.assertEqual(response3.status_code, 429)
        self.assertIsInstance(response3, HttpResponseTooManyRequests)

    def test_upload_rate_limiting(self):
        """Test upload-specific rate limiting."""
        request = self.factory.post("/upload/")
        request.META["REMOTE_ADDR"] = "192.168.1.2"

        @upload_rate_limit
        def upload_view(request):
            return HttpResponse("Upload OK")

        # Should allow 5 uploads per minute
        for i in range(5):
            response = upload_view(request)
            self.assertEqual(response.status_code, 200)

        # 6th upload should be blocked
        response = upload_view(request)
        self.assertEqual(response.status_code, 429)

    def test_auth_rate_limiting(self):
        """Test authentication rate limiting."""
        request = self.factory.post("/login/")
        request.META["REMOTE_ADDR"] = "192.168.1.3"

        @auth_rate_limit
        def login_view(request):
            return HttpResponse("Login OK")

        # Should allow 5 attempts per minute
        for i in range(5):
            response = login_view(request)
            self.assertEqual(response.status_code, 200)

        # 6th attempt should be blocked
        response = login_view(request)
        self.assertEqual(response.status_code, 429)

    def test_user_rate_limiting(self):
        """Test user-specific rate limiting."""
        request = self.factory.post("/delete-file/")
        request.META["REMOTE_ADDR"] = "192.168.1.4"
        request.user = self.user

        @user_rate_limit(limit=2, window=60)
        def user_action_view(request):
            return HttpResponse("User action OK")

        # Should allow 2 actions per minute for authenticated user
        for i in range(2):
            response = user_action_view(request)
            self.assertEqual(response.status_code, 200)

        # 3rd action should be blocked
        response = user_action_view(request)
        self.assertEqual(response.status_code, 429)

    def test_user_rate_limiting_fallback_to_ip(self):
        """Test that user rate limiting falls back to IP for anonymous users."""
        request = self.factory.post("/action/")
        request.META["REMOTE_ADDR"] = "192.168.1.5"
        request.user = Mock()
        request.user.is_authenticated = False

        @user_rate_limit(limit=2, window=60)
        def action_view(request):
            return HttpResponse("Action OK")

        # Should work with IP-based limiting for anonymous users
        for i in range(2):
            response = action_view(request)
            self.assertEqual(response.status_code, 200)

        # 3rd action should be blocked
        response = action_view(request)
        self.assertEqual(response.status_code, 429)

    def test_different_ips_separate_limits(self):
        """Test that different IPs have separate rate limits."""

        @rate_limit(limit=1, window=60)
        def test_view(request):
            return HttpResponse("OK")

        # Request from IP 1
        request1 = self.factory.get("/test/")
        request1.META["REMOTE_ADDR"] = "192.168.1.10"

        # Request from IP 2
        request2 = self.factory.get("/test/")
        request2.META["REMOTE_ADDR"] = "192.168.1.11"

        # Both should succeed
        response1 = test_view(request1)
        response2 = test_view(request2)

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        # Second request from each should be blocked
        response1_blocked = test_view(request1)
        response2_blocked = test_view(request2)

        self.assertEqual(response1_blocked.status_code, 429)
        self.assertEqual(response2_blocked.status_code, 429)


from django.http import HttpResponse
