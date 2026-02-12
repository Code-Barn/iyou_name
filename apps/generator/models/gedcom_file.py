import os
from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_delete
from django.dispatch import receiver


def user_gedcom_upload_path(instance, filename):
    """Generate user-specific upload path for GEDCOM files."""
    if instance.user:
        return f"gedcom_files/user_{instance.user.id}/{filename}"
    else:
        return f"gedcom_files/anonymous/{filename}"


class GedcomFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to=user_gedcom_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_data = JSONField(null=True, blank=True)  # Store parsed data directly here
    home_person_id = models.CharField(max_length=100, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    processing_date = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)  # Automatically updated on save

    def __str__(self):
        if self.user:
            return f"{self.user.username}'s GEDCOM file"
        return "Anonymous GEDCOM file"

    def get_home_person_name(self):
        """Get the full name of the home person from the parsed data."""
        if self.home_person_id and self.parsed_data:
            individuals = self.parsed_data.get("individuals", {})
            home_person = individuals.get(self.home_person_id)
            if home_person:
                return home_person.get("full_name", "Unknown")
        return "Unknown"


@receiver(post_delete, sender="generator.GedcomFile")
def delete_parsed_data(sender, instance, **kwargs):
    """
    Signal to handle deletion of parsed data when a GEDCOM file is deleted.
    """
    # No action needed - the file and its parsed data are already deleted
    pass
