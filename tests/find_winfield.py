#!/usr/bin/env python3
"""
Debug script to find Winfield Scott Byers in the database
"""

import os
import sys
import django

# Setup Django
sys.path.append("/home/user/CODE_BASE/namechart")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import required modules
from apps.generator.models import GedcomFile

try:
    # Get the most recent GEDCOM file
    gedcom_file = GedcomFile.objects.latest("uploaded_at")
    print(f"Using GEDCOM file: {gedcom_file.file.name}")

    # Search for Winfield Scott Byers
    individuals = gedcom_file.parsed_data["individuals"]
    print(f"Total individuals in database: {len(individuals)}")

    # Search for anyone with "Winfield" or "Byers" in the name
    winfield_found = False
    byers_found = False

    print("\n🔍 Searching for 'Winfield'...")
    for person_id, person in individuals.items():
        if hasattr(person, "full_name") and person.full_name:
            if "Winfield" in person.full_name:
                print(f"  Found: {person_id} - {person.full_name}")
                winfield_found = True

    print("\n🔍 Searching for 'Byers'...")
    for person_id, person in individuals.items():
        if hasattr(person, "full_name") and person.full_name:
            if "Byers" in person.full_name:
                print(f"  Found: {person_id} - {person.full_name}")
                byers_found = True

    if not winfield_found and not byers_found:
        print("\n❌ No Winfield or Byers found. Listing first 10 individuals:")
        count = 0
        for person_id, person in individuals.items():
            if hasattr(person, "full_name") and person.full_name:
                print(f"  {person_id}: {person.full_name}")
                count += 1
                if count >= 10:
                    break

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\nDebug complete!")
