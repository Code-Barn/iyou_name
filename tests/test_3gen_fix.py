#!/usr/bin/env python3
"""
Test script for 3gen generator
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

# Create test data
print("Creating test data...")

# Create test primary individual
primary_individual = PersonData(
    id="X1750",
    full_name="John Michael Doe",
    given_name="John Michael",
    surname="Doe",
    birth_date="1950-01-01",
    death_date="",
    birth_place="New York",
    death_place="",
    father="X1749",
    mother="X1748",
)

# Create test family data
family_data = {
    "individuals": {
        "X1750": primary_individual,
        "X1749": PersonData(
            id="X1749",
            full_name="Robert James Doe",
            given_name="Robert James",
            surname="Doe",
            birth_date="1925-01-01",
            death_date="2010-01-01",
            birth_place="Boston",
            death_place="California",
            father="X1747",
            mother="X1746",
        ),
        "X1748": PersonData(
            id="X1748",
            full_name="Mary Elizabeth Smith",
            given_name="Mary Elizabeth",
            surname="Smith",
            birth_date="1928-01-01",
            death_place="Florida",
            birth_place="Chicago",
            father="X1745",
            mother="X1744",
        ),
        "X1747": PersonData(
            id="X1747",
            full_name="William Thomas Doe",
            given_name="William Thomas",
            surname="Doe",
            birth_date="1900-01-01",
            death_date="1980-01-01",
            birth_place="London",
            death_place="New York",
        ),
        "X1746": PersonData(
            id="X1746",
            full_name="Margaret Anne Johnson",
            given_name="Margaret Anne",
            surname="Johnson",
            birth_date="1902-01-01",
            death_date="1985-01-01",
            birth_place="Manchester",
            death_place="Boston",
        ),
        "X1745": PersonData(
            id="X1745",
            full_name="Charles Henry Smith",
            given_name="Charles Henry",
            surname="Smith",
            birth_date="1901-01-01",
            death_place="Texas",
            birth_place="Philadelphia",
        ),
        "X1744": PersonData(
            id="X1744",
            full_name="Elizabeth Grace Wilson",
            given_name="Elizabeth Grace",
            surname="Wilson",
            birth_date="1903-01-01",
            birth_place="Baltimore",
        ),
    }
}

# Add primary_individual to family_data
family_data["primary_individual"] = primary_individual

print("Test data created successfully!")
print(f"Primary individual: {primary_individual.full_name}")
print(
    f"Father: {family_data['individuals'].get(primary_individual.father).full_name if primary_individual.father else 'None'}"
)
print(
    f"Mother: {family_data['individuals'].get(primary_individual.mother).full_name if primary_individual.mother else 'None'}"
)

# Test 3gen generation
print("\nTesting 3gen generation...")

try:
    # Test with minimal settings
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
        "grandparent_font_color": "#000000",
    }

    result = generate_3gen_preview(
        primary_individual, family_data, "preview", user_settings
    )

    if result:
        # Save result to file
        with open("/home/user/CODE_BASE/namechart/test_3gen_output.png", "wb") as f:
            f.write(result.getvalue())
        print("✅ 3gen generation successful! Output saved to test_3gen_output.png")
    else:
        print("❌ 3gen generation failed - no result returned")

except Exception as e:
    print(f"❌ 3gen generation failed with error: {e}")
    import traceback

    traceback.print_exc()

print("\nTest complete!")
