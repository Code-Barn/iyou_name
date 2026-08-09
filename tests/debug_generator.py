#!/usr/bin/env python3
"""
Debug script to test the 2gen generator directly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "namechart.settings")
django.setup()

from apps.generator.utils.image_2generator import generate_2gen_preview
from apps.generator.models import GedcomFile, PersonData

# Get a test individual
try:
    gedcom_file = GedcomFile.objects.first()
    if not gedcom_file or not gedcom_file.parsed_data:
        print("No GEDCOM file data found")
        sys.exit(1)

    individuals = gedcom_file.parsed_data.get("individuals", {})
    if not individuals:
        print("No individuals found")
        sys.exit(1)

    # Get first individual
    individual_id = list(individuals.keys())[0]
    individual_data = individuals[individual_id]
    primary_individual = PersonData(**individual_data)

    # Convert all individuals to PersonData objects
    person_data_objects = {}
    for person_id, person_data in individuals.items():
        person_data_objects[person_id] = PersonData(**person_data)

    # Update family_data with PersonData objects
    family_data_with_person_objects = gedcom_file.parsed_data.copy()
    family_data_with_person_objects["individuals"] = person_data_objects

    print(f"Testing with individual: {primary_individual.full_name} ({individual_id})")
    print(f"Total individuals in dataset: {len(individuals)}")

    # Test with basic settings
    user_settings = {
        "font_family": "Arial",
        "primary_name_font_size": 84,
        "primary_date_info_font_size": 60,
        "default_stroke_width": 0.5,
        "primary_stroke_color": "#000000",
        "primary_background_color": "#ffffff",
        "primary_font_color": "#000000",
    }

    print("Calling generate_2gen_preview...")
    result = generate_2gen_preview(
        primary_individual, family_data_with_person_objects, "preview", user_settings
    )

    if result:
        print(f"SUCCESS: Generator returned buffer of type {type(result)}")
        print(
            f"Buffer size: {len(result.getvalue()) if hasattr(result, 'getvalue') else 'Unknown'}"
        )
    else:
        print("ERROR: Generator returned None")

except Exception as e:
    import traceback

    print(f"ERROR: {e}")
    print(traceback.format_exc())
