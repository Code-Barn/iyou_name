#!/usr/bin/env python3
"""
Test 3gen generator with real individual X1758 (Winfield Scott Byers)
"""

import os
import sys
import django

# Setup Django
sys.path.append("/home/user/CODE_BASE/namechart")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import required modules
from apps.generator.utils.image_3generator import generate_3gen_preview
from apps.parser.models import PersonData
from apps.generator.models import GedcomFile

# Get real data from database
try:
    # Get the most recent GEDCOM file
    gedcom_file = GedcomFile.objects.latest("uploaded_at")
    print(f"Using GEDCOM file: {gedcom_file.filename}")

    # Get individual X1758
    individual = gedcom_file.parsed_data["individuals"].get("X1758")
    print(f"Found individual: {individual.full_name}")

    # Create family data structure
    family_data = gedcom_file.parsed_data.copy()
    family_data["primary_individual"] = individual

    # Test 3gen generation
    print("\nTesting 3gen generation with real data...")

    user_settings = {
        "primary_background_color": "#FFFFFF",
        "primary_stroke_color": "#000000",
        "primary_font_color": "#000000",
        "primary_name_font_size": 84,
        "primary_name_rotate": -45,
        "font_family": "Arial",
        "default_stroke_width": 0.5,
        "parent_name_font_size": 72,
        "parent_font_color": "#000000",
        "grandparent_name_font_size": 60,
        "grandparent_font_color": "#FF0000",  # Red color to make it more visible
    }

    result = generate_3gen_preview(individual, family_data, "preview", user_settings)

    if result:
        # Save result to file
        output_file = "/home/user/CODE_BASE/namechart/test_3gen_real_data.png"
        with open(output_file, "wb") as f:
            f.write(result.getvalue())
        print(f"✅ 3gen generation successful! Output saved to {output_file}")
        print("Check the file for red grandparent text in corners")
    else:
        print("❌ 3gen generation failed - no result returned")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\nTest complete!")
