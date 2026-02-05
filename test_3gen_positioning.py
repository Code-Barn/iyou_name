#!/usr/bin/env python3
"""
Test script to verify 3gen grandparent positioning according to specification:
A - Father's father (at bottom) - text rotated 90° to point outward
B - Father's mother (to the right) - text rotated 180° to point outward
C - Mother's father (at top) - text rotated 270° to point outward
D - Mother's mother (at the left) - text rotated 0° to point outward
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

# Create test data with clear names to verify positioning
print("Creating test data for positioning verification...")

# Create test primary individual
primary_individual = PersonData(
    id="X1750",
    full_name="Primary Person",
    given_name="Primary",
    surname="Person",
    father="X1749",
    mother="X1748",
)

# Create test family data with descriptive names
family_data = {
    "individuals": {
        "X1750": primary_individual,
        "X1749": PersonData(
            id="X1749",
            full_name="Father Person",
            given_name="Father",
            surname="Person",
            father="X1747",  # Father's father = A
            mother="X1746",  # Father's mother = B
        ),
        "X1748": PersonData(
            id="X1748",
            full_name="Mother Person",
            given_name="Mother",
            surname="Person",
            father="X1745",  # Mother's father = C
            mother="X1744",  # Mother's mother = D
        ),
        "X1747": PersonData(  # A - Father's father (should be at bottom)
            id="X1747",
            full_name="A Father Father",
            given_name="A Father",
            surname="Father",
        ),
        "X1746": PersonData(  # B - Father's mother (should be at right)
            id="X1746",
            full_name="B Father Mother",
            given_name="B Father",
            surname="Mother",
        ),
        "X1745": PersonData(  # C - Mother's father (should be at top)
            id="X1745",
            full_name="C Mother Father",
            given_name="C Mother",
            surname="Father",
        ),
        "X1744": PersonData(  # D - Mother's mother (should be at left)
            id="X1744",
            full_name="D Mother Mother",
            given_name="D Mother",
            surname="Mother",
        ),
    }
}

# Add primary_individual to family_data
family_data["primary_individual"] = primary_individual

print("Test data created with clear naming for positioning verification!")
print("Expected positions:")
print("A - Father's father (at bottom, text rotated 90° to point outward)")
print("B - Father's mother (to the right, text rotated 180° to point outward)")
print("C - Mother's father (at top, text rotated 270° to point outward)")
print("D - Mother's mother (at the left, text rotated 0° to point outward)")

# Test 3gen generation
print("\nGenerating 3gen chart...")

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
        output_file = "/home/user/CODE_BASE/namechart/test_3gen_positioning.png"
        with open(output_file, "wb") as f:
            f.write(result.getvalue())
        print(f"✅ 3gen generation successful! Output saved to {output_file}")
        print("Check the file to verify:")
        print("- A (Father's father) should be at bottom with text pointing downward")
        print("- B (Father's mother) should be at right with text pointing rightward")
        print("- C (Mother's father) should be at top with text pointing upward")
        print("- D (Mother's mother) should be at left with text pointing leftward")
    else:
        print("❌ 3gen generation failed - no result returned")

except Exception as e:
    print(f"❌ 3gen generation failed with error: {e}")
    import traceback

    traceback.print_exc()

print("\nTest complete!")
