"""
Child counting utilities for GEDCOM family relationships.
Handles compound relationships including ex-spouses, step-children, and adopted children.
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class RelationshipType(Enum):
    """Types of relationships between individuals."""

    CURRENT_SPOUSE = "current_spouse"
    EX_SPOUSE = "ex_spouse"
    BIOLOGICAL_CHILD = "biological_child"
    STEP_CHILD = "step_child"
    ADOPTED_CHILD = "adopted_child"
    FOSTER_CHILD = "foster_child"


@dataclass
class ChildInfo:
    """Information about a child and their relationship to a parent."""

    individual_id: str
    relationship_type: RelationshipType
    from_spouse_id: Optional[str] = None
    pedigree: Optional[str] = None


@dataclass
class SpouseInfo:
    """Information about a spouse relationship."""

    spouse_id: str
    is_current: bool = True
    divorce_date: Optional[str] = None
    marriage_date: Optional[str] = None


class ChildCountingService:
    """
    Service for counting and categorizing children in GEDCOM family relationships.
    Handles compound relationships (multiple marriages), step-children, and adopted children.
    """

    def __init__(self, individuals: Dict[str, Any], families: Dict[str, Any]):
        """
        Initialize with parsed GEDCOM data.

        Args:
            individuals: Dictionary of individual_id -> PersonData
            families: Dictionary of family_id -> FamilyData
        """
        self.individuals = individuals
        self.families = families

        self._ex_spouses_cache: Dict[str, Set[str]] = {}
        self._current_spouses_cache: Dict[str, Set[str]] = {}
        self._step_children_cache: Dict[str, List[ChildInfo]] = {}

    def get_all_children(self, individual_id: str) -> List[ChildInfo]:
        """
        Get all children of an individual, regardless of which marriage.

        Args:
            individual_id: The ID of the individual

        Returns:
            List of ChildInfo objects for all children
        """
        children = []

        if individual_id not in self.individuals:
            return children

        individual = self.individuals[individual_id]

        if hasattr(individual, "children") and individual.children:
            for child_id in individual.children:
                children.append(
                    ChildInfo(
                        individual_id=child_id,
                        relationship_type=RelationshipType.BIOLOGICAL_CHILD,
                    )
                )

        if hasattr(individual, "spouses_children") and individual.spouses_children:
            for spouse_id, spouse_children in individual.spouses_children.items():
                for child_id in spouse_children:
                    if not any(c.individual_id == child_id for c in children):
                        children.append(
                            ChildInfo(
                                individual_id=child_id,
                                relationship_type=RelationshipType.BIOLOGICAL_CHILD,
                                from_spouse_id=spouse_id,
                            )
                        )

        return children

    def get_step_children(self, individual_id: str) -> List[ChildInfo]:
        """
        Get step-children (children from ex-spouse's previous relationships).

        Args:
            individual_id: The ID of the individual

        Returns:
            List of step-children
        """
        if individual_id in self._step_children_cache:
            return self._step_children_cache[individual_id]

        step_children = []
        ex_spouses = self.get_ex_spouses(individual_id)

        for ex_spouse_id in ex_spouses:
            spouse_info = self.get_spouse_info(individual_id, ex_spouse_id)
            if spouse_info:
                ex_spouse_children = self._get_children_from_family(ex_spouse_id)

                for child in ex_spouse_children:
                    if child.individual_id not in self._get_own_children(individual_id):
                        step_children.append(
                            ChildInfo(
                                individual_id=child.individual_id,
                                relationship_type=RelationshipType.STEP_CHILD,
                                from_spouse_id=ex_spouse_id,
                            )
                        )

        self._step_children_cache[individual_id] = step_children
        return step_children

    def get_current_spouse_children(self, individual_id: str) -> List[ChildInfo]:
        """
        Get children from current spouse(s).

        Args:
            individual_id: The ID of the individual

        Returns:
            List of children from current marriage(s)
        """
        children = []
        current_spouses = self.get_current_spouses(individual_id)

        for current_spouse_id in current_spouses:
            spouse_children = self._get_children_from_family(current_spouse_id)
            for child in spouse_children:
                if child.individual_id in self._get_own_children(individual_id):
                    children.append(child)

        return children

    def get_adopted_children(self, individual_id: str) -> List[ChildInfo]:
        """
        Get adopted children of an individual.

        Args:
            individual_id: The ID of the individual

        Returns:
            List of adopted children
        """
        adopted = []
        all_children = self.get_all_children(individual_id)

        for child in all_children:
            if child.individual_id in self.individuals:
                child_person = self.individuals[child.individual_id]
                if (
                    hasattr(child_person, "pedigree")
                    and child_person.pedigree == "adopted"
                ):
                    adopted.append(child)

        return adopted

    def get_ex_spouses(self, individual_id: str) -> Set[str]:
        """
        Get all ex-spouses of an individual.

        Args:
            individual_id: The ID of the individual

        Returns:
            Set of ex-spouse IDs
        """
        if individual_id in self._ex_spouses_cache:
            return self._ex_spouses_cache[individual_id]

        ex_spouses = set()

        for fam_id, family in self.families.items():
            events = family.get("events", [])
            is_divorced = any(event.get("tag") == "DIV" for event in events)

            husband = family.get("husband", "").replace("@", "")
            wife = family.get("wife", "").replace("@", "")

            if husband == individual_id and wife:
                if is_divorced:
                    ex_spouses.add(wife)
            elif wife == individual_id and husband:
                if is_divorced:
                    ex_spouses.add(husband)

        self._ex_spouses_cache[individual_id] = ex_spouses
        return ex_spouses

    def get_current_spouses(self, individual_id: str) -> Set[str]:
        """
        Get current spouse(s) of an individual.

        Args:
            individual_id: The ID of the individual

        Returns:
            Set of current spouse IDs
        """
        if individual_id in self._current_spouses_cache:
            return self._current_spouses_cache[individual_id]

        current_spouses = set()
        ex_spouses = self.get_ex_spouses(individual_id)

        if hasattr(self.individuals.get(individual_id), "spouse"):
            all_spouses = self.individuals[individual_id].spouse or []
            for spouse_id in all_spouses:
                if spouse_id not in ex_spouses:
                    current_spouses.add(spouse_id)

        self._current_spouses_cache[individual_id] = current_spouses
        return current_spouses

    def get_spouse_info(
        self, individual_id: str, spouse_id: str
    ) -> Optional[SpouseInfo]:
        """
        Get detailed information about a spouse relationship.

        Args:
            individual_id: The ID of the individual
            spouse_id: The ID of the spouse

        Returns:
            SpouseInfo if found, None otherwise
        """
        current_spouses = self.get_current_spouses(individual_id)
        ex_spouses = self.get_ex_spouses(individual_id)

        if spouse_id in current_spouses:
            return SpouseInfo(spouse_id=spouse_id, is_current=True)
        elif spouse_id in ex_spouses:
            for fam_id, family in self.families.items():
                husband = family.get("husband", "").replace("@", "")
                wife = family.get("wife", "").replace("@", "")

                if (husband == individual_id and wife == spouse_id) or (
                    wife == individual_id and husband == spouse_id
                ):
                    events = family.get("events", [])
                    div_event = next((e for e in events if e.get("tag") == "DIV"), None)
                    marr_event = next(
                        (e for e in events if e.get("tag") == "MARR"), None
                    )

                    return SpouseInfo(
                        spouse_id=spouse_id,
                        is_current=False,
                        divorce_date=div_event.get("date") if div_event else None,
                        marriage_date=marr_event.get("date") if marr_event else None,
                    )

        return None

    def get_relationship_summary(self, individual_id: str) -> Dict[str, Any]:
        """
        Get a comprehensive summary of all relationships and children.

        Args:
            individual_id: The ID of the individual

        Returns:
            Dictionary with relationship counts and details
        """
        return {
            "total_children": len(self.get_all_children(individual_id)),
            "biological_children": len(
                [
                    c
                    for c in self.get_all_children(individual_id)
                    if c.relationship_type == RelationshipType.BIOLOGICAL_CHILD
                ]
            ),
            "step_children": len(self.get_step_children(individual_id)),
            "adopted_children": len(self.get_adopted_children(individual_id)),
            "current_spouses": list(self.get_current_spouses(individual_id)),
            "ex_spouses": list(self.get_ex_spouses(individual_id)),
            "children_from_current_spouse": len(
                self.get_current_spouse_children(individual_id)
            ),
        }

    def _get_own_children(self, individual_id: str) -> Set[str]:
        """Get IDs of individual's own biological/adopted children."""
        children = set()
        if hasattr(self.individuals.get(individual_id), "children"):
            children = set(self.individuals[individual_id].children or [])
        return children

    def _get_children_from_family(self, spouse_id: str) -> List[ChildInfo]:
        """Get children associated with a spouse through family."""
        children = []

        for fam_id, family in self.families.items():
            husband = family.get("husband", "").replace("@", "")
            wife = family.get("wife", "").replace("@", "")

            if husband == spouse_id or wife == spouse_id:
                for child_id in family.get("children", []):
                    children.append(
                        ChildInfo(
                            individual_id=child_id,
                            relationship_type=RelationshipType.BIOLOGICAL_CHILD,
                            from_spouse_id=spouse_id,
                        )
                    )

        return children


def count_children(
    individuals: Dict[str, Any], families: Dict[str, Any], individual_id: str
) -> Dict[str, int]:
    """
    Convenience function to count children for an individual.

    Args:
        individuals: Dictionary of individuals from parsed GEDCOM
        families: Dictionary of families from parsed GEDCOM
        individual_id: The ID of the individual

    Returns:
        Dictionary with child counts by type
    """
    service = ChildCountingService(individuals, families)
    summary = service.get_relationship_summary(individual_id)

    return {
        "total": summary["total_children"],
        "biological": summary["biological_children"],
        "step": summary["step_children"],
        "adopted": summary["adopted_children"],
    }


def get_compound_relationship_info(
    individuals: Dict[str, Any], families: Dict[str, Any], individual_id: str
) -> Dict[str, Any]:
    """
    Get detailed compound relationship information.

    Args:
        individuals: Dictionary of individuals from parsed GEDCOM
        families: Dictionary of families from parsed GEDCOM
        individual_id: The ID of the individual

    Returns:
        Detailed relationship information
    """
    service = ChildCountingService(individuals, families)
    return service.get_relationship_summary(individual_id)
