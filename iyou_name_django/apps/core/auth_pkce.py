import hashlib
import logging
import secrets
import time
from base64 import urlsafe_b64encode

from django.conf import settings
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)

OIDC_STATES_KEY = "oidc_states"
VERIFIER_AGE_MAX = 300  # 5 minutes


def _base64_url_encode(data: bytes) -> str:
    return urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def generate_code_verifier(length: int = 64) -> str:
    if not 43 <= length <= 128:
        raise ValueError("code_verifier length must be between 43 and 128")
    return get_random_string(length)


def generate_code_challenge(verifier: str, method: str = "S256") -> str:
    if method == "plain":
        return verifier
    if method == "S256":
        return _base64_url_encode(hashlib.sha256(verifier.encode("ascii")).digest())
    raise ValueError("method must be 'plain' or 'S256'")


def generate_pkce_pair(length: int = 64, method: str = "S256"):
    verifier = generate_code_verifier(length)
    challenge = generate_code_challenge(verifier, method)
    return verifier, challenge, method


def store_verifier(session, state: str, verifier: str | None) -> None:
    if OIDC_STATES_KEY not in session or not isinstance(session[OIDC_STATES_KEY], dict):
        session[OIDC_STATES_KEY] = {}
    limit = getattr(settings, "OIDC_MAX_STATES", 50)
    if len(session[OIDC_STATES_KEY]) >= limit:
        oldest = min(
            session[OIDC_STATES_KEY].items(),
            key=lambda kv: kv[1].get("added_on", 0),
        )[0]
        del session[OIDC_STATES_KEY][oldest]
    session[OIDC_STATES_KEY][state] = {
        "code_verifier": verifier,
        "added_on": time.time(),
    }


def retrieve_verifier(session, state: str) -> str | None:
    states = session.get(OIDC_STATES_KEY, {})
    entry = states.pop(state, None)
    if entry is not None:
        session.save()
        return entry.get("code_verifier")
    return None


def prune_expired_verifiers(session, max_age: int = VERIFIER_AGE_MAX) -> int:
    states = session.get(OIDC_STATES_KEY, {})
    if not states:
        return 0
    now = time.time()
    expired = [s for s, v in states.items() if now - v.get("added_on", 0) > max_age]
    for state in expired:
        del states[state]
    if expired:
        session.save()
    return len(expired)


class PkceAuthMixin:
    """
    Mixin for views that need session-backed PKCE verifier management.

    Provides clean methods for generating, storing, and retrieving PKCE
    code verifiers during the OIDC authorization code flow.
    """

    pkce_verifier_length: int = 64
    pkce_challenge_method: str = "S256"

    def generate_auth_params(self) -> dict:
        verifier, challenge, method = generate_pkce_pair(
            self.pkce_verifier_length, self.pkce_challenge_method
        )
        state = secrets.token_urlsafe(32)
        store_verifier(self.request.session, state, verifier)
        self.request.session["pkce_state"] = state
        return {
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": method,
        }

    def get_verifier(self) -> str | None:
        state = self.request.session.pop("pkce_state", None)
        if not state:
            return None
        return retrieve_verifier(self.request.session, state)

    def prune(self, max_age: int = VERIFIER_AGE_MAX) -> int:
        return prune_expired_verifiers(self.request.session, max_age)

    @staticmethod
    def get_sub_claim(claims: dict) -> str | None:
        return claims.get("sub")

    @staticmethod
    def provision_user_from_claims(backend, claims: dict):
        sub = claims.get("sub")
        if not sub:
            logger.error("OIDC claims missing required 'sub' claim")
            return None
        users = backend.UserModel.objects.filter(username=sub)
        if users.exists():
            return backend.update_user(users.first(), claims)
        return backend.create_user(claims)
