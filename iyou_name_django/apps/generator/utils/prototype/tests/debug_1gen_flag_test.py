"""
Debug test to verify flag placement on 1gen.
Run via: uv run python manage.py shell < debug_1gen_flag_test.py
"""

import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.prototype.prototype_image_1generator import (
    Generation1Constants,
)
from apps.generator.utils.prototype.individual_printer import print_individual
from apps.generator.utils.prototype.place_name_utils import (
    get_flag_from_place,
    get_flag_image_path,
    parse_place,
)
from apps.generator.utils.settings_validator import get_validated_settings
from apps.generator.utils.simple_buffer_manager import create_preview_buffer

DEBUG_SCHEMA = {
    "font_family": (str, "Arial"),
    "primary_font_color": (Color, "black"),
    "primary_stroke_color": (Color, "black"),
    "primary_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "primary_name_font_size": (int, 72),
    "primary_date_info_font_size": (int, 48),
    "primary_place_info_font_size": (int, 48),
    "primary_name_rotate": (int, 0),
    "primary_birth_translate_x": (int, 0),
    "primary_birth_translate_y": (int, 0),
    "primary_birth_rotate": (int, 0),
    "primary_birth_place_translate_x": (int, 0),
    "primary_birth_place_translate_y": (int, 0),
    "primary_birth_place_rotate": (int, 0),
    "primary_death_translate_x": (int, 0),
    "primary_death_translate_y": (int, 0),
    "primary_death_rotate": (int, 0),
    "primary_death_place_translate_x": (int, 0),
    "primary_death_place_translate_y": (int, 0),
    "primary_death_place_rotate": (int, 0),
    "primary_name_background_color": (Color, "white"),
    "place_show_flag": (bool, True),
    "place_flag_type": (str, "birth"),
    "place_flag_format": (str, "png"),
    "place_flag_size": (int, 48),
}


class MockIndividual:
    """Simple mock individual for testing."""

    def __init__(self, full_name, birth_place, death_place=""):
        self.full_name = full_name
        self.birth_date = "1 Jan 1980"
        self.birth_place = birth_place
        self.death_date = ""
        self.death_place = death_place


def test_flag_parsing():
    """Test flag parsing from places."""
    print("\n=== Testing Flag Parsing ===")

    test_places = [
        "Arlington Heights, Cook, Illinois, USA",
        "London, England",
        "Edinburgh, Scotland",
        "Cardiff, Wales",
        "Toronto, Ontario, Canada",
        "Sydney, New South Wales, Australia",
        "Berlin, Germany",
        "Paris, France",
        "Mexico City, Mexico",
        "Dublin, Ireland",
    ]

    for place in test_places:
        parsed = parse_place(place)
        emoji = get_flag_from_place(place)
        png_path = get_flag_image_path(place)
        print(f"Place: {place}")
        print(f"  Parsed country: '{parsed.get('country', '')}'")
        print(f"  Emoji: '{emoji}'")
        print(f"  PNG path: '{png_path}'")
        print()


def test_flag_image_exists():
    """Test that flag images exist."""
    print("\n=== Testing Flag Image Existence ===")

    test_codes = [
        "us",
        "gb",
        "gb-eng",
        "gb-sct",
        "gb-wls",
        "ca",
        "au",
        "de",
        "fr",
        "mx",
        "ie",
    ]

    for code in test_codes:
        path = f"charts/images/flags/{code}.png"
        full_path = os.path.join(settings.BASE_DIR, "apps", "charts", "static", path)
        exists = os.path.exists(full_path)
        print(f"Flag {code}.png: {'EXISTS' if exists else 'MISSING'} ({full_path})")


def generate_flag_debug_chart():
    """Generate a debug chart with flag."""
    print("\n=== Generating Flag Debug Chart ===")

    validated_settings = get_validated_settings({}, DEBUG_SCHEMA, "1gen")

    # Print key settings
    print(f"place_show_flag: {validated_settings.get('place_show_flag')}")
    print(f"place_flag_type: {validated_settings.get('place_flag_type')}")
    print(f"place_flag_format: {validated_settings.get('place_flag_format')}")
    print(f"place_flag_size: {validated_settings.get('place_flag_size')}")

    # Create test individual with US birthplace
    test_individual = MockIndividual(
        full_name="John Doe",
        birth_place="Arlington Heights, Cook, Illinois, USA",
        death_place="",
    )

    # Check what flag we get
    print(f"\nTest individual birth_place: {test_individual.birth_place}")
    print(f"Flag emoji: {get_flag_from_place(test_individual.birth_place)}")
    print(f"Flag PNG path: {get_flag_image_path(test_individual.birth_place)}")

    template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_1GEN_BW.pdf",
    )

    if not os.path.exists(template_path):
        print(f"ERROR: Template not found: {template_path}")
        return

    with Image(filename=template_path, resolution=150) as base_img:
        content_img = base_img.clone()

        draw = Drawing()
        draw.font = validated_settings["font_family"]
        draw.font_size = validated_settings["primary_name_font_size"]
        draw.fill_color = validated_settings["primary_font_color"]

        print("\nCalling print_individual with flag parameters...")
        print(f"  flag_base_x: {Generation1Constants.CENTER_X}")
        print(f"  flag_base_y: {Generation1Constants.CENTER_Y + 80}")

        print_individual(
            draw=draw,
            content_img=content_img,
            individual=test_individual,
            settings=validated_settings,
            chart_settings=validated_settings,
            center_x=Generation1Constants.CENTER_X,
            center_y=Generation1Constants.CENTER_Y,
            rotation=0,
            name_font_size=validated_settings["primary_name_font_size"],
            date_font_size=validated_settings["primary_date_info_font_size"],
            place_font_size=validated_settings["primary_place_info_font_size"],
            first_name_rotation=validated_settings["primary_name_rotate"],
            birth_date_base_x=207,
            birth_date_base_y=975,
            birth_date_offset_x=validated_settings["primary_birth_translate_x"],
            birth_date_offset_y=validated_settings["primary_birth_translate_y"],
            birth_date_rotation=validated_settings["primary_birth_rotate"],
            birth_place_base_y=1875,
            birth_place_offset_x=validated_settings["primary_birth_place_translate_x"],
            birth_place_offset_y=validated_settings["primary_birth_place_translate_y"],
            birth_place_rotation=validated_settings["primary_birth_place_rotate"],
            death_date_base_x=975,
            death_date_base_y=207,
            death_date_offset_x=validated_settings["primary_death_translate_x"],
            death_date_offset_y=validated_settings["primary_death_translate_y"],
            death_date_rotation=validated_settings["primary_death_rotate"],
            death_place_base_x=1875,
            death_place_offset_x=validated_settings["primary_death_place_translate_x"],
            death_place_offset_y=validated_settings["primary_death_place_translate_y"],
            death_place_rotation=validated_settings["primary_death_place_rotate"],
            flag_base_x=Generation1Constants.CENTER_X,
            flag_base_y=Generation1Constants.CENTER_Y + 80,
            flag_rotation=validated_settings["primary_name_rotate"],
            flag_font_size=validated_settings["primary_place_info_font_size"],
            use_display_text=True,
            use_gravity_center=True,
        )

        draw(content_img)

        # Save debug image
        output_path = os.path.join(settings.MEDIA_ROOT, "debug_flag_test.png")
        content_img.save(filename=output_path)
        print(f"\nDebug image saved to: {output_path}")


if __name__ == "__main__":
    test_flag_parsing()
    test_flag_image_exists()
    generate_flag_debug_chart()
    print("\n=== Done ===")
