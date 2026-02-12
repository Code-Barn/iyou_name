"""
Error message sanitization utilities.
Ensures error messages don't leak sensitive information.
"""

import re
import logging
import traceback
from typing import Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

SENSITIVE_PATTERNS = [
    (
        re.compile(r'password["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', re.IGNORECASE),
        "PASSWORD",
    ),
    (re.compile(r'secret["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', re.IGNORECASE), "SECRET"),
    (re.compile(r'token["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', re.IGNORECASE), "TOKEN"),
    (
        re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', re.IGNORECASE),
        "API_KEY",
    ),
    (
        re.compile(
            r'connection[_-]?string["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', re.IGNORECASE
        ),
        "CONNECTION_STRING",
    ),
    (
        re.compile(r'database["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', re.IGNORECASE),
        "DATABASE",
    ),
    (
        re.compile(r's3[_-]?key["\']?\s*[:=]\s*["\']?[^"\'\s,}]+', re.IGNORECASE),
        "AWS_KEY",
    ),
    (
        re.compile(r'private[_-]?key["\']?\s*[:=]\s*["\']?[^\s"\']+', re.IGNORECASE),
        "PRIVATE_KEY",
    ),
]

PATH_PATTERNS = [
    r"/home/[^/]+/",
    r"/Users/[^/]+/",
    r"C:\\Users\\[^\\]+\\",
    r"/var/www/",
    r"/app/",
    r"/root/",
]

INTERNAL_PATTERNS = [
    r"DEBUG = True",
    r"SECRET_KEY",
    r"Internal Server Error",
    r"Traceback \(most recent call last\)",
]


def sanitize_error_message(message: str, include_debug: bool = False) -> str:
    """
    Sanitize an error message to remove sensitive information.

    Args:
        message: The original error message
        include_debug: Whether to include debug info (should be False in production)

    Returns:
        Sanitized error message safe for display to users
    """
    if not message:
        return "An error occurred"

    sanitized = message

    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(f"[{replacement} REDACTED]", sanitized)

    for path_pattern in PATH_PATTERNS:
        sanitized = re.sub(path_pattern, "[PATH REDACTED]", sanitized)

    if not include_debug:
        for internal_pattern in INTERNAL_PATTERNS:
            sanitized = re.sub(internal_pattern, "[INTERNAL INFO REDACTED]", sanitized)

    sanitized = re.sub(
        r"Database\[.*?\]\s*at\s*.*?", "Database error", sanitized, flags=re.IGNORECASE
    )
    sanitized = re.sub(r'File\s+"[^"]+"', 'File "[FILE]"', sanitized)
    sanitized = re.sub(r"Line\s+\d+", "Line N", sanitized)

    return sanitized


def sanitize_exception(exc: Exception, include_debug: bool = None) -> str:
    """
    Sanitize an exception for display.

    Args:
        exc: The exception to sanitize
        include_debug: Whether to include debug info (defaults to settings.DEBUG)

    Returns:
        Sanitized exception message safe for display
    """
    if include_debug is None:
        include_debug = getattr(settings, "DEBUG", False)

    message = str(exc)

    if include_debug:
        tb = traceback.format_exc()
        return f"{sanitize_error_message(message, True)}\n\nTraceback:\n{tb}"

    return sanitize_error_message(message, False)


def get_user_safe_error(
    error: Any, default_message: str = "An error occurred. Please try again."
) -> str:
    """
    Get a user-safe error message from any error type.

    Args:
        error: The error (exception, string, or other)
        default_message: Default message if error is None or empty

    Returns:
        User-safe error message
    """
    if error is None:
        return default_message

    if isinstance(error, Exception):
        return sanitize_exception(error)

    if isinstance(error, str):
        return sanitize_error_message(error)

    return default_message


def format_validation_error(field: str, message: str) -> str:
    """
    Format a validation error message safely.

    Args:
        field: The field that failed validation
        message: The validation error message

    Returns:
        Formatted error message
    """
    safe_message = sanitize_error_message(message)
    return f"{field}: {safe_message}"


def get_api_error_response(error: Any, status_code: int = 400) -> dict:
    """
    Get a sanitized API error response.

    Args:
        error: The error to format
        status_code: HTTP status code

    Returns:
        Sanitized error dictionary for JSON API response
    """
    return {"error": get_user_safe_error(error), "status": status_code}


class SafeError(Exception):
    """
    Exception that automatically sanitizes its message.
    """

    def __init__(self, message: str, error_code: str = "ERROR"):
        self.error_code = error_code
        self.message = sanitize_error_message(message)
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {"error": self.message, "code": self.error_code}


def handle_view_error(
    request, error: Exception, log_message: str = "Error processing request"
) -> tuple:
    """
    Handle an error in a view, logging it and returning safe response.

    Args:
        request: The HTTP request
        error: The exception that occurred
        log_message: Custom log message

    Returns:
        Tuple of (sanitized_message, status_code)
    """
    is_debug = getattr(settings, "DEBUG", False)

    if is_debug:
        logger.exception(f"{log_message}: {error}")
        return str(error), 500

    logger.warning(f"{log_message}: {sanitize_error_message(str(error))}")

    return (
        "An error occurred. Please try again or contact support if the problem persists.",
        500,
    )
