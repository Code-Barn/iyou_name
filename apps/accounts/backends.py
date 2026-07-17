"""
PKCEAuthenticationBackend — zero-secret OIDC backend for iyou_name.

Inherits from django.contrib.auth.Backend to avoid
OIDCAuthenticationBackend's __init__ which enforces
OIDC_RP_CLIENT_SECRET presence (Rule 2).  The PKCE code_verifier
proves client possession and replaces the shared secret for public
clients (RFC 7636).

User lookup filters strictly on username=claims.get('sub') (the root
DID string), completely bypassing email string fields to prevent unique
constraint violations when multiple DID records share an email address
(Rule 4).

Privilege evaluation reads settings.ADMIN_DID and calls
set_unusable_password() on the admin account to enforce passwordless
posture (AUTH_FLOW_SPECIFICATION.md Section 6.2).
"""

import logging

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.urls import reverse
from mozilla_django_oidc.utils import absolutify

logger = logging.getLogger(__name__)

User = get_user_model()


class PKCEAuthenticationBackend(ModelBackend):
    """Public-client OIDC backend — PKCE S256, no client_secret."""

    def authenticate(self, request, code_verifier=None, **kwargs):
        if not request:
            return None

        code = request.GET.get("code")
        state = request.GET.get("state")
        if not (code and state):
            return None

        token_payload = {
            "client_id": self._get_setting("OIDC_RP_CLIENT_ID"),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": absolutify(
                request,
                reverse(
                    self._get_setting(
                        "OIDC_AUTHENTICATION_CALLBACK_URL",
                        "oidc_authentication_callback",
                    )
                ),
            ),
        }

        if code_verifier:
            token_payload["code_verifier"] = code_verifier

        try:
            token_info = self._do_token_request(token_payload)
        except requests.ConnectionError:
            logger.error("Connection refused by token endpoint")
            return None
        except requests.Timeout:
            logger.error("Token endpoint timed out")
            return None
        except requests.RequestException as exc:
            logger.error("Token exchange failed: %s", exc)
            return None

        if "error" in token_info:
            logger.warning(
                "Token error [%s]: %s",
                token_info.get("error"),
                token_info.get("error_description", "(no description)"),
            )
            return None

        try:
            user_info = self._do_userinfo_request(token_info)
        except requests.ConnectionError:
            logger.error("Connection refused by userinfo endpoint")
            return None
        except requests.Timeout:
            logger.error("UserInfo endpoint timed out")
            return None
        except requests.RequestException as exc:
            logger.error("UserInfo request failed: %s", exc)
            return None

        return self._get_or_create_user(user_info)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    # ------------------------------------------------------------------
    # Back-channel HTTP helpers
    # ------------------------------------------------------------------

    def _do_token_request(self, payload):
        response = requests.post(
            self._get_setting("OIDC_OP_TOKEN_ENDPOINT"),
            data=payload,
            verify=self._get_setting("OIDC_VERIFY_SSL", True),
            timeout=self._get_setting("OIDC_TIMEOUT", 10),
        )
        response.raise_for_status()
        return response.json()

    def _do_userinfo_request(self, token_info):
        access_token = token_info.get("access_token")
        if not access_token:
            raise ValueError("Token response missing access_token")

        response = requests.get(
            self._get_setting("OIDC_OP_USER_ENDPOINT"),
            headers={"Authorization": f"Bearer {access_token}"},
            verify=self._get_setting("OIDC_VERIFY_SSL", True),
            timeout=self._get_setting("OIDC_TIMEOUT", 10),
        )
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # User provisioning — DID-only lookup, no email fallback
    # ------------------------------------------------------------------

    def _get_or_create_user(self, user_info):
        sub = user_info.get("sub")
        if not sub:
            logger.warning("OIDC userinfo missing 'sub' claim")
            return None

        username = sub

        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": user_info.get("email", ""),
                    "first_name": user_info.get("given_name", ""),
                    "last_name": user_info.get("family_name", ""),
                },
            )
        except Exception:
            logger.exception("User provisioning failed for %s", username)
            return None

        self._evaluate_admin_elevation(user, claims=user_info)
        return user

    # ------------------------------------------------------------------
    # Settings helper
    # ------------------------------------------------------------------

    @staticmethod
    def _get_setting(key, default=None):
        return getattr(settings, key, default)

    # ------------------------------------------------------------------
    # Sovereign Admin Posture — elevation only (Section 6.2)
    # ------------------------------------------------------------------

    def _evaluate_admin_elevation(self, user, claims=None):
        if not user or user.is_anonymous:
            return user

        target_admin_did = getattr(settings, "ADMIN_DID", None)
        if user.username == target_admin_did:
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.set_unusable_password()
                user.save(update_fields=["is_staff", "is_superuser"])
        return user
