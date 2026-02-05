#!/usr/bin/env python3
"""
Test 3gen generator with actual Byers GEDCOM file
"""

import os
import sys
import django

# Setup Django
sys.path.append("/home/user/CODE_BASE/namechart")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import required modules
from apps.generator.utils.image_3generator import (
    generate_3gen_preview,
    get_grandparents,
)
from apps.parser.utils.gedcom_parser import parse_gedcom_data, detect_encoding

try:
    # Load the Byers GEDCOM file directly
    gedcom_path = "/home/user/CODE_BASE/namechart/temp/gedcom_standards/Byers-Callahan_Family_Tree.ged"
    print(f"Loading GEDCOM file: {gedcom_path}")

    # Detect encoding and read file
    encoding = detect_encoding(gedcom_path)
    with open(gedcom_path, "r", encoding=encoding or "utf-8") as f:
        gedcom_content = f.read()

    family_data = parse_gedcom_data(gedcom_content)
    print(f"✅ Parsed {len(family_data['individuals'])} individuals")

    # Search for Winfield Scott Byers
    winfield_id = None
    for person_id, person in family_data["individuals"].items():
        if hasattr(person, "full_name") and person.full_name:
            if "Winfield" in person.full_name and "Byers" in person.full_name:
                winfield_id = person_id
                print(
                    f"✅ Found Winfield Scott Byers: {person_id} - {person.full_name}"
                )
                break

    if not winfield_id:
        print("❌ Winfield Scott Byers not found in GEDCOM file")
        # List first few individuals to debug
        print("First 10 individuals:")
        count = 0
        for person_id, person in family_data["individuals"].items():
            if hasattr(person, "full_name") and person.full_name:
                print(f"  {person_id}: {person.full_name}")
                count += 1
                if count >= 10:
                    break
        exit(1)

    # Get Winfield as primary individual
    primary_individual = family_data["individuals"][winfield_id]
    family_data["primary_individual"] = primary_individual

    print(f"Father ID: {primary_individual.father}")
    print(f"Mother ID: {primary_individual.mother}")

    # Test grandparent extraction
    print("\n🔍 Testing grandparent extraction...")
    grandparents = get_grandparents(family_data)
    print(f"Found {len(grandparents)} grandparents:")

    for i, gp in enumerate(grandparents):
        print(f"  {i}: {gp.full_name if gp else 'None'}")

    # Test 3gen generation
    print("\n🎨 Testing 3gen generation...")
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
        "grandparent_font_color": "#FF0000",  # Red for visibility
    }

    result = generate_3gen_preview(
        primary_individual, family_data, "preview", user_settings
    )

    if result:
        output_file = "/home/user/CODE_BASE/namechart/test_3gen_byers.png"
        with open(output_file, "wb") as f:
            f.write(result.getvalue())
        print(f"✅ 3gen generation successful! Output saved to {output_file}")
    else:
        print("❌ 3gen generation failed")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\nTest complete!")
