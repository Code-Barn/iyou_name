from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_delete
from django.dispatch import receiver


@dataclass
class PersonData:
    """Data class representing an individual in a family tree"""

    id: str
    full_name: str
    given_name: str
    surname: str
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_place: Optional[str] = None
    father: Optional[str] = None  # Reference to father's ID
    mother: Optional[str] = None  # Reference to mother's ID
    spouse: Optional[List[str]] = None  # List of spouse IDs
    children: Optional[List[str]] = None  # List of child IDs
    siblings: Optional[List[str]] = None  # List of sibling IDs
    adoptive_parents: Optional[List[str]] = None  # List of adoptive parent IDs
    foster_parents: Optional[List[str]] = None  # List of foster parent IDs
    step_parents: Optional[List[str]] = None  # List of step-parent IDs
    spouses_children: Optional[Dict[str, List[str]]] = (
        None  # Dictionary to store children for each spouse
    )
    birth_flag: Optional[bytes] = None  # Binary image data for birthplace flag
    death_flag: Optional[bytes] = None  # Binary image data for deathplace flag
    events: Optional[List[Dict]] = None  # List of events associated with the individual
    sex: Optional[str] = None  # Gender of the individual
    title: Optional[str] = None  # Professional or nobility titles
    occupation: Optional[str] = None  # Occupation or trade

    def get_full_name(self) -> str:
        """Return the full name in 'Given Surname' format"""
        return f"{self.given_name} {self.surname}"

    def get_birth_info(self) -> str:
        """Return formatted birth information"""
        parts = []
        if self.birth_date:
            parts.append(f"b. {self.birth_date}")
        if self.birth_place:
            parts.append(f"in {self.birth_place}")
        return " ".join(parts) if parts else ""

    def get_death_info(self) -> str:
        """Return formatted death information"""
        parts = []
        if self.death_date:
            parts.append(f"d. {self.death_date}")
        if self.death_place:
            parts.append(f"in {self.death_place}")
        return " ".join(parts) if parts else ""

    def to_dict(self):
        """Standard method to prepare data for JsonResponse"""
        data = asdict(self)
        # Ensure binary data is already Base64-encoded
        return data


class GedcomFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to="gedcom_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_data = JSONField(null=True, blank=True)  # Store parsed data directly here
    home_person_id = models.CharField(max_length=100, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    processing_date = models.DateTimeField(null=True, blank=True)

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
    # Clear the parsed_data field to free up memory
    instance.parsed_data = None
    instance.save()
