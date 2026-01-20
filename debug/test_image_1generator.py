#!/usr/bin/env python3

import logging
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)


# Mock Django settings
class MockSettings:
    BASE_DIR = project_root


# Configure mock settings
sys.modules["django.conf"] = type("module", (), {})()
sys.modules["django.conf"].settings = MockSettings()

# Import required modules

from apps.generator.utils.image_1generator import generate_family_tree


# Mock individual data
class PersonData:
    def __init__(self, full_name, birth_date=None, birth_place=None, death_date=None):
        self.full_name = full_name
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.death_date = death_date
        self.id = "X1"


def test_image_generation():
    """Test image_1generator.py with settings"""
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    try:
        # Create a mock individual
        individual = PersonData(
            full_name="TEST NAME",
            birth_date="1 JAN 2000",
            birth_place="TEST CITY",
            death_date="",
        )

        # Mock family data
        family_data = {
            "individuals": {},
            "families": {},
        }

        # Test settings - these should be clearly visible in the output
        test_settings = {
            "primary_name_font_size": 60,  # Large font size
            "primary_info_font_size": 40,
            "font_family": "Arial",
            "primary_font_color": "red",  # Bright color
            "primary_name_x": 200,  # Move text away from edge
            "primary_name_y": 200,
        }

        print("Testing image_1generator.py with settings...")
        print(f"Settings: {test_settings}")

        # Generate the image with test settings
        img_buffer = generate_family_tree(
            individual, family_data, "1gen", test_settings
        )

        # Save the image to a file
        output_path = "test_preview.png"
        with open(output_path, "wb") as f:
            f.write(img_buffer.getvalue())

        print(f"Successfully generated preview image: {output_path}")

        # Verify the image
        from wand.image import Image

        with Image(blob=img_buffer.getvalue()) as img:
            print(f"Image dimensions: {img.width}x{img.height}")
            print(f"Image format: {img.format}")

        return True

    except Exception as e:
        print(f"Error generating preview: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_image_generation()
