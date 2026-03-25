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
    burial_place: Optional[str] = None
    father: Optional[str] = None
    mother: Optional[str] = None
    spouse: Optional[List[str]] = None
    children: Optional[List[str]] = None
    siblings: Optional[List[str]] = None
    half_siblings: Optional[List[str]] = None
    step_siblings: Optional[List[str]] = None
    all_siblings: Optional[List[str]] = None
    adoptive_parents: Optional[List[str]] = None
    foster_parents: Optional[List[str]] = None
    step_parents: Optional[List[str]] = None
    adopted: bool = False
    spouses_children: Optional[Dict[str, List[str]]] = None
    birth_flag: Optional[bytes] = None
    death_flag: Optional[bytes] = None
    events: Optional[List[Dict]] = None
    sex: Optional[str] = None
    title: Optional[str] = None
    honorific: Optional[str] = None
    suffix: Optional[str] = None
    occupation: Optional[str] = None
    paternal_grandfather: Optional[str] = None
    paternal_grandmother: Optional[str] = None
    maternal_grandfather: Optional[str] = None
    maternal_grandmother: Optional[str] = None

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

    def get_burial_info(self) -> str:
        """Return formatted burial information"""
        parts = []
        if self.burial_place:
            parts.append(f"buried in {self.burial_place}")
        return " ".join(parts) if parts else ""

    def to_dict(self):
        """Standard method to prepare data for JsonResponse"""
        data = asdict(self)
        # Ensure binary data is already Base64-encoded
        return data
