"""
Detailed debug test to understand why parser only finds one individual
"""

import os
import sys

sys.path.insert(0, "/home/user/CODE_BASE/namechart")

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

from apps.parser.utils.gedcom_parser import parse_gedcom_data

django.setup()


def debug_parser():
    """Debug the parser to understand why it only finds one individual"""
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

    print("=== DEBUG: Starting parser analysis ===")
    print("GEDCOM content:")
    print(gedcom_content)
    print("\n" + "=" * 50)

    try:
        family_data = parse_gedcom_data(gedcom_content)

        print("\nParsed data structure:")
        print(f"- Individuals: {len(family_data['individuals'])}")
        print(f"- Families: {len(family_data['families'])}")
        print(f"- Root individuals: {len(family_data['root_individuals'])}")

        print(f"\nIndividual IDs found: {list(family_data['individuals'].keys())}")

        for ind_id, person in family_data["individuals"].items():
            print(f"\nIndividual {ind_id}:")
            print(f"  Name: {person.full_name}")
            print(f"  Given: {person.given_name}")
            print(f"  Surname: {person.surname}")
            print(f"  Birth: {person.birth_date}")
            print(f"  Father: {person.father}")
            print(f"  Mother: {person.mother}")

        print(f"\nFamilies found: {list(family_data['families'].keys())}")

        for fam_id, family in family_data["families"].items():
            print(f"\nFamily {fam_id}:")
            print(f"  Husband: {family['husband']}")
            print(f"  Wife: {family['wife']}")
            print(f"  Children: {family['children']}")

    except Exception as e:
        print(f"Error during parsing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_parser()
