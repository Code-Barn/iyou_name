#!/usr/bin/env python3
"""
Debug script to check if grandparents are being found and drawn
"""

import os
import sys
import django

# Setup Django
sys.path.append("/home/user/CODE_BASE/namechart")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import required modules
from apps.generator.utils.image_3generator import get_grandparents, draw_grandparents
from apps.parser.models import PersonData
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

# Create test data
primary_individual = PersonData(
    id="X1750",
    full_name="Primary Person",
    given_name="Primary",
    surname="Person",
    father="X1749",
    mother="X1748",
)

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
        "X1747": PersonData(  # A - Father's father
            id="X1747",
            full_name="A Father Father",
            given_name="A Father",
            surname="Father",
        ),
        "X1746": PersonData(  # B - Father's mother
            id="X1746",
            full_name="B Father Mother",
            given_name="B Father",
            surname="Mother",
        ),
        "X1745": PersonData(  # C - Mother's father
            id="X1745",
            full_name="C Mother Father",
            given_name="C Mother",
            surname="Father",
        ),
        "X1744": PersonData(  # D - Mother's mother
            id="X1744",
            full_name="D Mother Mother",
            given_name="D Mother",
            surname="Mother",
        ),
    }
}

# Add primary_individual to family_data
family_data["primary_individual"] = primary_individual

print("Testing grandparent extraction...")
grandparents = get_grandparents(family_data)
print(f"Found {len(grandparents)} grandparents:")
for i, gp in enumerate(grandparents):
    print(f"  {i}: {gp.full_name if gp else 'None'}")

print("\nTesting grandparent drawing...")
settings = {
    "grandparent_font_size": 60,
    "grandparent_font_color": "#000000",
    "font_family": "Arial",
}

# Create a simple test image
with Image(width=1950, height=1950, background=Color("white")) as test_img:
    with Drawing() as draw:
        draw.font = settings["font_family"]
        draw.font_size = settings["grandparent_font_size"]
        draw.fill_color = Color(settings["grandparent_font_color"])

        # Test drawing grandparents
        try:
            draw_grandparents(draw, family_data, settings, None)
            print("✅ Grandparent drawing completed successfully")

            # Apply drawing to test image
            draw(test_img)

            # Save test image
            test_img.save(
                filename="/home/user/CODE_BASE/namechart/debug_grandparents.png"
            )
            print("✅ Test image saved to debug_grandparents.png")

        except Exception as e:
            print(f"❌ Error drawing grandparents: {e}")
            import traceback

            traceback.print_exc()

print("\nDebug complete!")
