"""
Authentication security monitoring — dismantled.

Classical password-based auth has been replaced by OIDC via
apps.accounts.backends.MyOIDCAuthenticationBackend. The in-memory
AuthenticationMonitor is no longer relevant.
"""
