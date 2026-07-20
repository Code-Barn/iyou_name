"""
Debug test to visualize all 1gen positions for HUD preview.
Run via: cd /home/user/CODE_BASE/namechart && uv run python apps/generator/utils/prototype/debug_1gen_positions_test.py
"""

import os
import sys

# Don't modify sys.path[0] - keep it empty so Django can find settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.prototype.prototype_image_1generator import (
    Generation1Constants,
)
from apps.generator.utils.prototype.individual_printer import print_individual
from apps.generator.utils.settings_validator import get_validated_settings

DEBUG_SCHEMA = {
    "font_family": (str, "Arial"),
    "primary_background_color": (Color, "#000000"),
    "primary_font_color": (Color, "white"),
    "primary_stroke_color": (Color, "white"),
    "primary_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "primary_birth_color": (Color, "white"),
    "primary_birth_place_color": (Color, "white"),
    "primary_death_color": (Color, "white"),
    "primary_death_place_color": (Color, "white"),
    "primary_name_font_size": (int, 84),
    "primary_date_info_font_size": (int, 52),
    "primary_place_info_font_size": (int, 36),
    "primary_name_rotate": (int, -45),
    "primary_birth_translate_x": (int, 0),
    "primary_birth_translate_y": (int, 0),
    "primary_birth_rotate": (int, -90),
    "primary_birth_place_translate_x": (int, 0),
    "primary_birth_place_translate_y": (int, 0),
    "primary_birth_place_rotate": (int, 0),
    "primary_death_translate_x": (int, 0),
    "primary_death_translate_y": (int, 0),
    "primary_death_rotate": (int, 0),
    "primary_death_place_translate_x": (int, 0),
    "primary_death_place_translate_y": (int, 0),
    "primary_death_place_rotate": (int, -90),
    "place_show_flag": (bool, True),
    "place_flag_type": (str, "birth"),
    "place_flag_format": (str, "png"),
    "place_flag_size": (int, 48),
}


class MockIndividual:
    """Simple mock individual for testing."""

    def __init__(self):
        self.full_name = "John Michael Smith"
        self.given_name = "John"
        self.surname = "Smith"
        self.birth_date = "15 May 1970"
        self.birth_place = "Arlington Heights, Cook, Illinois, USA"
        self.death_date = "1 Jan 2020"
        self.death_place = "Boston, Suffolk, Massachusetts, USA"


def draw_position_marker(draw, x, y, label, color="red"):
    """Draw a visible marker at a position with label."""
    # Draw circle
    draw.push()
    draw.fill_color = Color(color)
    draw.stroke_color = Color(color)
    draw.stroke_width = 3
    radius = 20
    draw.circle((x, y), (x + radius, y + radius))

    # Draw cross
    cross_size = 30
    draw.line((x - cross_size, y), (x + cross_size, y))
    draw.line((x, y - cross_size), (x, y + cross_size))
    draw.pop()

    # Draw label
    draw.push()
    draw.fill_color = Color(color)
    draw.font = "Arial"
    draw.font_size = 24
    draw.text(x + 25, y + 10, label)
    draw.pop()


def generate_position_debug_chart():
    """Generate a debug chart showing all position markers."""
    print("\n=== Generating Position Debug Chart ===")

    validated_settings = get_validated_settings({}, DEBUG_SCHEMA, "1gen")

    # Print key positions being used
    print(f"\nKey Positions:")
    print(f"  CENTER_X: {Generation1Constants.CENTER_X}")
    print(f"  CENTER_Y: {Generation1Constants.CENTER_Y}")
    print(f"  Birth Date: base_x=207, base_y=975")
    print(f"  Birth Place: base_y=1875")
    print(f"  Death Date: base_x=975, base_y=207")
    print(f"  Death Place: base_x=1875")
    print(
        f"  Flag: base_x={Generation1Constants.CENTER_X}, base_y={Generation1Constants.CENTER_Y - 50}"
    )

    # Load the HUD preview template
    template_path = os.path.join(
        settings.BASE_DIR,
        "apps/hud/static/hud/images/preview_image_templates",
        "1GEN_PREVIEW.png",
    )

    if not os.path.exists(template_path):
        print(f"ERROR: Template not found: {template_path}")
        return

    print(f"\nUsing template: {template_path}")

    with Image(filename=template_path, resolution=150) as base_img:
        content_img = base_img.clone()

        draw = Drawing()

        # Draw all position markers
        print("\nDrawing position markers:")

        # Name position (CENTER_X, CENTER_Y)
        center_x = Generation1Constants.CENTER_X
        center_y = Generation1Constants.CENTER_Y
        print(f"  NAME: ({center_x}, {center_y})")
        draw_position_marker(draw, center_x, center_y, "NAME", "red")

        # Birth date position
        bd_x = 207
        bd_y = 975
        print(f"  BIRTH DATE: ({bd_x}, {bd_y})")
        draw_position_marker(draw, bd_x, bd_y, "BIRTH DATE", "blue")

        # Death date position
        dd_x = 975
        dd_y = 207
        print(f"  DEATH DATE: ({dd_x}, {dd_y})")
        draw_position_marker(draw, dd_x, dd_y, "DEATH DATE", "green")

        # Birth place position
        # Based on code: birth_place_base_y=1875, with offsets
        bp_x = 0  # Not directly used, uses translate
        bp_y = 1875
        print(f"  BIRTH PLACE: base_y={bp_y}")
        draw_position_marker(draw, 207, bp_y, "BIRTH PLACE", "orange")

        # Death place position
        # Based on code: death_place_base_x=1875
        dep_x = 1875
        dep_y = 1875  # Typical y position
        print(f"  DEATH PLACE: ({dep_x}, {dep_y})")
        draw_position_marker(draw, dep_x, dep_y, "DEATH PLACE", "purple")

        # Flag position
        flag_x = Generation1Constants.CENTER_X
        flag_y = Generation1Constants.CENTER_Y - 50
        print(f"  FLAG: ({flag_x}, {flag_y})")
        draw_position_marker(draw, flag_x, flag_y, "FLAG", "yellow")

        # Apply markers to image
        draw(content_img)

        # Save debug image
        output_path = os.path.join(settings.MEDIA_ROOT, "debug_1gen_positions.png")
        content_img.save(filename=output_path)
        print(f"\nDebug image saved to: {output_path}")
        print(f"Canvas size: {content_img.width}x{content_img.height}")


if __name__ == "__main__":
    generate_position_debug_chart()
    print("\n=== Done ===")
