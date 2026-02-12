"""
Authentication security monitoring and detection system.
Tracks failed login attempts, suspicious activity, and provides alerts.
"""

import logging
import hashlib
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from django.conf import settings

logger = logging.getLogger(__name__)


class AuthenticationMonitor:
    """
    Monitor authentication attempts and detect suspicious patterns.
    """

    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.successful_logins = defaultdict(list)
        self.suspicious_ips = set()
        self.locked_accounts = set()

    def record_failed_attempt(
        self, username: str, ip_address: str, user_agent: str = ""
    ):
        """Record a failed login attempt."""
        key = username.lower()
        now = time.time()

        self.failed_attempts[key].append(
            {"timestamp": now, "ip": ip_address, "user_agent": user_agent}
        )

        self.failed_attempts[key] = [
            attempt
            for attempt in self.failed_attempts[key]
            if now - attempt["timestamp"] < 3600
        ]

        attempt_count = len(self.failed_attempts[key])

        if attempt_count >= 5:
            self.suspicious_ips.add(ip_address)
            logger.warning(
                f"Multiple failed login attempts detected",
                extra={
                    "username": username,
                    "ip_address": ip_address,
                    "attempt_count": attempt_count,
                    "time_window": "1 hour",
                },
            )

        if attempt_count >= 10:
            if username not in self.locked_accounts:
                self.locked_accounts.add(username)
                logger.warning(
                    f"Account locked due to failed attempts",
                    extra={
                        "username": username,
                        "attempt_count": attempt_count,
                        "ip_address": ip_address,
                    },
                )

    def record_successful_login(
        self, username: str, ip_address: str, user_agent: str = ""
    ):
        """Record a successful login."""
        key = username.lower()
        now = time.time()

        self.successful_logins[key].append(
            {"timestamp": now, "ip": ip_address, "user_agent": user_agent}
        )

        self.successful_logins[key] = [
            login
            for login in self.successful_logins[key]
            if now - login["timestamp"] < 86400
        ]

        if key in self.failed_attempts:
            self.failed_attempts[key] = []

    def is_account_locked(self, username: str) -> bool:
        """Check if account is locked."""
        return username.lower() in self.locked_accounts

    def unlock_account(self, username: str):
        """Unlock an account."""
        key = username.lower()
        if key in self.locked_accounts:
            self.locked_accounts.remove(key)
        if key in self.failed_attempts:
            self.failed_attempts[key] = []
        logger.info(f"Account unlocked: {username}")

    def is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP is flagged as suspicious."""
        return ip_address in self.suspicious_ips

    def get_failed_attempt_count(self, username: str) -> int:
        """Get number of recent failed attempts for username."""
        key = username.lower()
        return len(self.failed_attempts.get(key, []))

    def check_unusual_login_location(self, username: str, ip_address: str) -> bool:
        """Check if login is from unusual location based on history."""
        key = username.lower()
        logins = self.successful_logins.get(key, [])

        if not logins:
            return False

        ips = set(login["ip"] for login in logins)

        if ip_address not in ips and len(ips) > 0:
            logger.warning(
                f"Login from new IP address",
                extra={
                    "username": username,
                    "new_ip": ip_address,
                    "previous_ips": list(ips),
                },
            )
            return True

        return False

    def get_security_status(self, username: str) -> Dict:
        """Get security status for a user."""
        key = username.lower()

        return {
            "failed_attempts": len(self.failed_attempts.get(key, [])),
            "is_locked": key in self.locked_accounts,
            "last_login_ip": self.successful_logins.get(key, [{}])[-1].get("ip")
            if self.successful_logins.get(key)
            else None,
            "login_count_24h": len(self.successful_logins.get(key, [])),
        }


auth_monitor = AuthenticationMonitor()


def check_login_security(
    username: str, password: str, ip_address: str, user_agent: str = ""
) -> tuple:
    """
    Check if login should be allowed based on security rules.

    Returns:
        tuple: (is_allowed, error_message)
    """
    username_lower = username.lower()

    if auth_monitor.is_account_locked(username_lower):
        logger.warning(f"Login attempt on locked account: {username} from {ip_address}")
        return (
            False,
            "Account is temporarily locked due to too many failed attempts. Please try again later.",
        )

    if auth_monitor.is_suspicious_ip(ip_address):
        logger.warning(
            f"Login attempt from suspicious IP: {ip_address} for user {username}"
        )

    return True, None


def record_authentication_result(
    username: str, success: bool, ip_address: str, user_agent: str = ""
):
    """Record authentication result for monitoring."""
    if success:
        auth_monitor.record_successful_login(username, ip_address, user_agent)
        logger.info(f"Successful login", extra={"username": username, "ip": ip_address})
    else:
        auth_monitor.record_failed_attempt(username, ip_address, user_agent)
        logger.warning(
            f"Failed login attempt", extra={"username": username, "ip": ip_address}
        )


def get_client_ip(request) -> str:
    """Get client IP from request, considering proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip or "unknown"


def get_user_agent(request) -> str:
    """Get user agent from request."""
    return request.META.get("HTTP_USER_AGENT", "")[:500]
