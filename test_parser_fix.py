"""
Simple test script to verify the GEDCOM parser fix
"""

import os
import sys

sys.path.insert(0, "/home/user/CODE_BASE/namechart")

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from apps.parser.models import PersonData
from apps.parser.utils.gedcom_parser import parse_gedcom_data


def test_parser_fix():
    """Test that the parser creates unique PersonData objects"""
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

    print("Testing GEDCOM parser fix...")
    family_data = parse_gedcom_data(gedcom_content)

    print(f"Number of individuals parsed: {len(family_data['individuals'])}")

    # Check that we have 3 unique individuals
    individuals = family_data["individuals"]
    for ind_id, person in individuals.items():
        print(f"Individual {ind_id}: {person.full_name}")

    # Verify unique names
    names = [person.full_name for person in individuals.values()]
    unique_names = set(names)

    print(f"Names: {names}")
    print(f"Unique names: {unique_names}")

    if len(names) == len(unique_names):
        print("✓ SUCCESS: All individuals have unique names!")
        return True
    else:
        print("✗ FAILURE: Some individuals have duplicate names!")
        return False


if __name__ == "__main__":
    test_parser_fix()
