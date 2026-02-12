"""
Rate limiting utilities for Django views to prevent abuse and DoS attacks.
"""

import time
import logging
from collections import defaultdict, deque
from functools import wraps
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

# Try to import HttpResponseTooManyRequests, fallback to HttpResponse with status 429
try:
    from django.http import HttpResponseTooManyRequests
except ImportError:
    # Fallback for older Django versions
    class HttpResponseTooManyRequests(HttpResponse):
        status_code = 429

        def __init__(self, content, *args, **kwargs):
            super().__init__(content, status=429, *args, **kwargs)


logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter using sliding window approach.
    For production, consider using Redis-based rate limiting.
    """

    def __init__(self):
        # Dictionary to store request timestamps per IP
        self.requests = defaultdict(deque)

    def is_allowed(self, key, limit, window_seconds=60):
        """
        Check if request is allowed based on rate limit.

        Args:
            key: Unique identifier (usually IP address)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            bool: True if request is allowed, False otherwise
        """
        now = time.time()

        # Get existing requests for this key
        request_times = self.requests[key]

        # Remove requests outside the time window
        while request_times and request_times[0] <= now - window_seconds:
            request_times.popleft()

        # Check if limit exceeded
        if len(request_times) >= limit:
            logger.warning(
                f"Rate limit exceeded for {key}: {len(request_times)} requests in {window_seconds}s"
            )
            return False

        # Add current request
        request_times.append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(limit=5, window=60, key_func=None):
    """
    Decorator to rate limit Django views.

    Args:
        limit: Maximum requests allowed
        window: Time window in seconds
        key_func: Function to generate unique key (defaults to IP address)
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate key for rate limiting
            if key_func:
                key = key_func(request)
            else:
                # Default: use IP address
                key = get_client_ip(request)

            # Check rate limit
            if not rate_limiter.is_allowed(key, limit, window):
                logger.warning(
                    f"Rate limit blocked request from {key} to {request.path}"
                )
                return HttpResponseTooManyRequests(
                    f"Rate limit exceeded. Maximum {limit} requests per {window} seconds allowed."
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def upload_rate_limit(view_func):
    """
    Specific rate limiting for upload endpoints.
    More restrictive than general rate limiting.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get client IP
        ip = get_client_ip(request)

        # Rate limits for uploads
        upload_limits = [
            # 5 uploads per minute
            (5, 60, "per minute"),
            # 20 uploads per hour
            (20, 3600, "per hour"),
            # 100 uploads per day
            (100, 86400, "per day"),
        ]

        for limit, window, description in upload_limits:
            if not rate_limiter.is_allowed(f"upload_{ip}_{window}", limit, window):
                logger.warning(
                    f"Upload rate limit exceeded for {ip}: {limit} uploads {description}"
                )
                return HttpResponseTooManyRequests(
                    f"Upload rate limit exceeded. Maximum {limit} uploads {description}."
                )

        return view_func(request, *args, **kwargs)

    return wrapper


def auth_rate_limit(view_func):
    """
    Rate limiting for authentication endpoints (login, register).
    Very restrictive to prevent credential stuffing attacks.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get client IP
        ip = get_client_ip(request)

        # Rate limits for auth
        auth_limits = [
            # 5 attempts per minute
            (5, 60, "per minute"),
            # 15 attempts per hour
            (15, 3600, "per hour"),
        ]

        for limit, window, description in auth_limits:
            if not rate_limiter.is_allowed(f"auth_{ip}_{window}", limit, window):
                logger.warning(
                    f"Auth rate limit exceeded for {ip}: {limit} attempts {description}"
                )
                return HttpResponseTooManyRequests(
                    f"Too many authentication attempts. Please try again later."
                )

        return view_func(request, *args, **kwargs)

    return wrapper


def get_client_ip(request):
    """
    Get the real client IP address, considering proxies and load balancers.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    return ip or "unknown"


def user_rate_limit(limit=10, window=60):
    """
    Rate limiting per authenticated user rather than IP.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Fall back to IP-based rate limiting for anonymous users
                return rate_limit(limit, window)(view_func)(request, *args, **kwargs)

            # Use user ID as key for authenticated users
            key = f"user_{request.user.id}"

            if not rate_limiter.is_allowed(key, limit, window):
                logger.warning(
                    f"User rate limit exceeded for {request.user.username}: {limit} requests per {window}s"
                )
                return HttpResponseTooManyRequests(
                    f"Rate limit exceeded. Maximum {limit} requests per {window} seconds per user."
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


class RateLimitMiddleware:
    """
    Middleware for global rate limiting.
    Can be used for site-wide rate limiting.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Apply global rate limiting (100 requests per minute)
        ip = get_client_ip(request)

        # Skip rate limiting for static files and admin
        skip_paths = ["/static/", "/media/", "/admin/"]
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)

        # Global rate limit
        if not rate_limiter.is_allowed(f"global_{ip}", 100, 60):
            logger.warning(f"Global rate limit exceeded for {ip}")
            return HttpResponseTooManyRequests(
                "Global rate limit exceeded. Please slow down your requests."
            )

        response = self.get_response(request)

        # Add rate limit headers
        response["X-RateLimit-Limit"] = "100"
        response["X-RateLimit-Window"] = "60"
        response["X-RateLimit-Remaining"] = str(
            max(0, 100 - len(rate_limiter.requests[f"global_{ip}"]))
        )

        return response
