"""
Authentication security monitoring — dismantled.

Classical password-based auth has been replaced by OIDC via
apps.accounts.backends.PKCEAuthenticationBackend. The in-memory
AuthenticationMonitor is no longer relevant.
"""
