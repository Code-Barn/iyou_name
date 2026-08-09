"""
Test settings for Family Tree Generator project.

This settings file is used specifically for running tests and should not be used
in production environments.
"""

import tempfile

from .settings import TEMPLATES

# Use SQLite for testing - faster and doesn't require database permissions
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # In-memory database for fastest test execution
    }
}

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use faster template backend for tests
TEMPLATES[0]["OPTIONS"]["debug"] = False

# Disable logging for cleaner test output
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["null"],
            "level": "CRITICAL",
        },
        "apps": {
            "handlers": ["null"],
            "level": "CRITICAL",
        },
    },
}

# Email backend for tests - don't actually send emails
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Media root for tests
MEDIA_ROOT = tempfile.mkdtemp()
