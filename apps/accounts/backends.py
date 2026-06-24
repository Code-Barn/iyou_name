from django.conf import settings
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class MyOIDCAuthenticationBackend(OIDCAuthenticationBackend):

    def _evaluate_admin_elevation(self, user):
        """Hardens admin DID validation rules and forces persistent database synchronization."""
        if not user or user.is_anonymous:
            return user

        admin_did_target = getattr(settings, "ADMIN_DID", None)
        if admin_did_target and user.username == admin_did_target:
            user.is_staff = True
            user.is_superuser = True
            user.save()  # Explicit row update commit
        return user

    def create_user(self, claims):
        user = super().create_user(claims)
        return self._evaluate_admin_elevation(user)

    def update_user(self, user, claims):
        user = super().update_user(user, claims)
        return self._evaluate_admin_elevation(user)

    def filter_users_by_claims(self, claims):
        username = claims.get("sub")
        if not username:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(username=username)
