import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User model with support for Decentralized Identifiers (DIDs).
    """

    did = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Decentralized Identifier (DID) for the user.",
    )
    did_method = models.CharField(
        max_length=50,
        default="key",
        help_text="The DID method used for this user's DID (e.g., 'key').",
    )
    did_key = models.TextField(
        blank=True,
        help_text="The private key associated with this user's DID (in JWK format).",
    )
    vcs = models.JSONField(
        default=list,
        blank=True,
        help_text="List of verifiable credentials associated with the user.",
    )

    class Meta:
        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return self.username

    def add_vc(self, vc: dict, name: str = None) -> None:
        """Add a verifiable credential to the user's list."""
        vcs = self.vcs.copy()
        vc_id = vc.get("credentialSubject", {}).get("id")

        existing_found = False
        if vc_id:
            for i, existing_vc_data in enumerate(vcs):
                existing_vc = existing_vc_data.get("credential", existing_vc_data)
                existing_vc_id = existing_vc.get("credentialSubject", {}).get("id")
                if existing_vc_id == vc_id:
                    existing_found = True
                    vcs[i] = {
                        "credential": vc,
                        "name": name or vc.get("type", ["Unknown"])[-1],
                        "added_date": datetime.datetime.now(
                            datetime.timezone.utc
                        ).isoformat(),
                    }
                    break

        if not existing_found:
            vcs.append(
                {
                    "credential": vc,
                    "name": name or vc.get("type", ["Unknown"])[-1],
                    "added_date": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                }
            )

        self.vcs = vcs

    def get_vcs_by_type(self, vc_type: str) -> list:
        """Get all VCs of a specific type."""
        result = []
        for vc_data in self.vcs:
            vc = vc_data.get("credential", vc_data)
            if vc.get("type") and vc_type in vc.get("type"):
                result.append(vc)
        return result
