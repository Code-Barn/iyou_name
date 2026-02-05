#!/usr/bin/env python3
"""
Debug script to check actual Winfield Scott Byers data and grandparent extraction
"""

import os
import sys
import django

# Setup Django
sys.path.append("/home/user/CODE_BASE/namechart")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import required modules
from apps.generator.utils.image_3generator import get_grandparents
from apps.generator.models import GedcomFile

try:
    # Get the most recent GEDCOM file
    gedcom_file = GedcomFile.objects.latest("uploaded_at")
    print(f"Using GEDCOM file: {gedcom_file.file.name}")

    # Get individual X1758 (Winfield Scott Byers)
    individual = gedcom_file.parsed_data["individuals"].get("X1758")
    if not individual:
        print("❌ Individual X1758 not found!")
        exit(1)

    print(f"✅ Found individual: {individual.full_name}")
    print(f"   Father ID: {individual.father}")
    print(f"   Mother ID: {individual.mother}")

    # Create family data structure
    family_data = gedcom_file.parsed_data.copy()
    family_data["primary_individual"] = individual

    # Check if parents exist
    father = None
    mother = None
    if individual.father:
        father = family_data["individuals"].get(individual.father)
        print(f"✅ Father found: {father.full_name if father else 'None'}")
        if father:
            print(f"   Father's father ID: {father.father}")
            print(f"   Father's mother ID: {father.mother}")

    if individual.mother:
        mother = family_data["individuals"].get(individual.mother)
        print(f"✅ Mother found: {mother.full_name if mother else 'None'}")
        if mother:
            print(f"   Mother's father ID: {mother.father}")
            print(f"   Mother's mother ID: {mother.mother}")

    # Test grandparent extraction
    print("\n🔍 Testing grandparent extraction...")
    grandparents = get_grandparents(family_data)
    print(f"Found {len(grandparents)} grandparents:")

    for i, gp in enumerate(grandparents):
        print(f"  {i}: {gp.full_name if gp else 'None'}")

    # Check if grandparents are in the individuals dict
    print("\n🔍 Checking individuals dictionary for grandparents...")
    if individual.father and father:
        if father.father:
            pgf = family_data["individuals"].get(father.father)
            print(f"Paternal grandfather in dict: {pgf.full_name if pgf else 'None'}")
        if father.mother:
            pgm = family_data["individuals"].get(father.mother)
            print(f"Paternal grandmother in dict: {pgm.full_name if pgm else 'None'}")

    if individual.mother and mother:
        if mother.father:
            mgf = family_data["individuals"].get(mother.father)
            print(f"Maternal grandfather in dict: {mgf.full_name if mgf else 'None'}")
        if mother.mother:
            mgm = family_data["individuals"].get(mother.mother)
            print(f"Maternal grandmother in dict: {mgm.full_name if mgm else 'None'}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\nDebug complete!")
