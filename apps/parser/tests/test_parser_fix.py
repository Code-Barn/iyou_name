"""
Test to verify that the GEDCOM parser creates unique PersonData objects
for each individual in the file, fixing the issue where all individuals
showed the same name in the dropdown.
"""

import io

from apps.parser.models import PersonData
from apps.parser.utils.gedcom_parser import parse_gedcom_data


def test_unique_individuals_in_parser():
    """
    Test that the parser creates unique PersonData objects for each individual
    """
    # Create a simple GEDCOM content with multiple individuals
    gedcom_content = """0 HEAD
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1 JAN 1980
2 PLAC New York
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
1 BIRT
2 DATE 15 MAR 1985
2 PLAC Boston
0 @I3@ INDI
1 NAME Robert /Johnson/
1 SEX M
1 BIRT
2 DATE 20 JUL 1975
2 PLAC Chicago
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
0 TRLR
"""

    # Parse the GEDCOM data
    family_data = parse_gedcom_data(gedcom_content)

    # Verify we have the correct number of individuals
    assert len(family_data["individuals"]) == 3, (
        f"Expected 3 individuals, got {len(family_data['individuals'])}"
    )

    # Verify each individual has unique data
    individuals = family_data["individuals"]
    john = individuals["I1"]
    jane = individuals["I2"]
    robert = individuals["I3"]

    # Test that each individual has unique names
    assert john.full_name == "John Doe", f"Expected 'John Doe', got '{john.full_name}'"
    assert jane.full_name == "Jane Smith", (
        f"Expected 'Jane Smith', got '{jane.full_name}'"
    )
    assert robert.full_name == "Robert Johnson", (
        f"Expected 'Robert Johnson', got '{robert.full_name}'"
    )

    # Test that they are different objects (not the same object repeated)
    assert john is not jane, "John and Jane should be different objects"
    assert john is not robert, "John and Robert should be different objects"
    assert jane is not robert, "Jane and Robert should be different objects"

    # Test that each has unique IDs
    assert john.id == "I1", f"Expected ID 'I1', got '{john.id}'"
    assert jane.id == "I2", f"Expected ID 'I2', got '{jane.id}'"
    assert robert.id == "I3", f"Expected ID 'I3', got '{robert.id}'"

    # Test that each has unique birth information
    assert john.birth_date == "1 JAN 1980", (
        f"Expected birth date '1 JAN 1980', got '{john.birth_date}'"
    )
    assert jane.birth_date == "15 MAR 1985", (
        f"Expected birth date '15 MAR 1985', got '{jane.birth_date}'"
    )
    assert robert.birth_date == "20 JUL 1975", (
        f"Expected birth date '20 JUL 1975', got '{robert.birth_date}'"
    )

    print("✓ All tests passed! Parser correctly creates unique PersonData objects.")
    return True


if __name__ == "__main__":
    test_unique_individuals_in_parser()
