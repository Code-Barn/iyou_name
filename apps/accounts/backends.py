import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = logging.getLogger(__name__)


class MyOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        username = claims.get("sub")
        logger.info(f"Creating user from OIDC claim sub={username}")
        return self.UserModel.objects.create_user(username=username)

    def update_user(self, user, claims):
        return user
