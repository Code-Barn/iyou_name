import logging

import environ
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = logging.getLogger(__name__)
env = environ.Env()


class MyOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        username = claims.get("sub")
        logger.info(f"Creating user from OIDC claim sub={username}")
        user = self.UserModel.objects.create_user(username=username)
        user.set_unusable_password()
        return self._evaluate_admin_elevation(user)

    def update_user(self, user, claims):
        return self._evaluate_admin_elevation(user)

    def filter_users_by_claims(self, claims):
        did = claims.get("sub")
        if not did:
            return self.UserModel.objects.none()
        users = self.UserModel.objects.filter(username=did)
        if not users.exists():
            user = self.UserModel.objects.create_user(username=did)
            user.set_unusable_password()
            user.save()
            return self._evaluate_admin_elevation(user)
        for user in users:
            self._evaluate_admin_elevation(user)
        return users

    def _evaluate_admin_elevation(self, user):
        if not user or user.is_anonymous:
            return user
        master_admin_did = env.str("ADMIN_DID", default="")
        if master_admin_did and user.username == master_admin_did:
            user.is_staff = True
            user.is_superuser = True
        user.save()
        return user
