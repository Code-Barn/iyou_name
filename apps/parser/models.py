from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


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
    siblings: Optional[List[str]] = None  # List of full sibling IDs (both parents)
    half_siblings: Optional[List[str]] = None  # List of half-sibling IDs (one parent)
    adoptive_parents: Optional[List[str]] = None  # List of adoptive parent IDs
    foster_parents: Optional[List[str]] = None  # List of foster parent IDs
    step_parents: Optional[List[str]] = None  # List of step-parent IDs
    step_siblings: Optional[List[str]] = None  # List of step-sibling IDs (no biological relation)
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
