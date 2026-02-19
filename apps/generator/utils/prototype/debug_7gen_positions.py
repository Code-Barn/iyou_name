"""
Debug test to verify 7gen position placements.
Uses the actual print_individual function to show position labels.
"""

import logging
import os
import sys

# Add project root to path
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.prototype.prototype_image_7generator import (
    Generation7Constants,
)
from apps.generator.utils.prototype.individual_printer import print_individual
from apps.generator.utils.settings_validator import get_validated_settings
from apps.generator.utils.simple_buffer_manager import create_preview_buffer

logger = logging.getLogger(__name__)

GENERATION_7_DEBUG_SCHEMA = {
    "font_family": (str, "Arial"),
    "great_great_great_great_grandparent_stroke_color": (Color, "black"),
    "great_great_great_great_grandparent_font_color": (Color, "black"),
    "great_great_great_great_grandparent_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "overlay_scale": (float, 0.8560),
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
}


class PositionLabel:
    """Simple class to hold position label for printing."""

    def __init__(self, full_name):
        self.full_name = full_name
        self.birth_date = ""
        self.birth_place = ""
        self.death_date = ""
        self.death_place = ""


def generate_7gen_position_debug():
    """Generate a debug chart showing position labels for 7gen."""
    validated_settings = get_validated_settings({}, GENERATION_7_DEBUG_SCHEMA, "7gen")

    template_path = os.path.join(
        settings.BASE_DIR,
        "apps/hud/static/hud/images/preview_image_templates",
        "7GEN_PREVIEW.png",
    )

    if not os.path.exists(template_path):
        logger.warning("7gen preview template not found, using 6gen template")
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "6GEN_PREVIEW.png",
        )

    with Image(filename=template_path, resolution=300) as content_img:
        with Drawing() as draw:
            draw.push()
            draw.font = validated_settings["font_family"]
            draw.stroke_antialias = True
            draw.stroke_width = 0.5
            draw.stroke_color = Color("black")

            # All 64 positions for 7gen (A1111-A2222 and their B/C/D counterparts)
            positions = []

            # A subclade (rotation=0, bottom) - 16 positions
            a_positions = [
                # Left side (closest to center going outward)
                (
                    "A1111",
                    Generation7Constants.POSITION_A1111_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A1111_FIRST_NAME_BASE_Y,
                ),
                (
                    "A1112",
                    Generation7Constants.POSITION_A1112_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A1112_FIRST_NAME_BASE_Y,
                ),
                (
                    "A1121",
                    Generation7Constants.POSITION_A1121_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A1121_FIRST_NAME_BASE_Y,
                ),
                (
                    "A1122",
                    Generation7Constants.POSITION_A1122_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A1122_FIRST_NAME_BASE_Y,
                ),
                (
                    "A1211",
                    Generation7Constants.POSITION_A1211_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A1211_FIRST_NAME_BASE_Y,
                ),
                (
                    "A1212",
                    Generation7Constants.POSITION_A1212_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A1212_FIRST_NAME_BASE_Y,
                ),
                (
                    "A1221",
                    Generation7Constants.POSITION_A1221_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A1221_FIRST_NAME_BASE_Y,
                ),
                (
                    "A1222",
                    Generation7Constants.POSITION_A1222_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A1222_FIRST_NAME_BASE_Y,
                ),
                # Right side (mirrored, closest to center going outward)
                (
                    "A2121",
                    Generation7Constants.POSITION_A2121_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A2121_FIRST_NAME_BASE_Y,
                ),
                (
                    "A2122",
                    Generation7Constants.POSITION_A2122_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A2122_FIRST_NAME_BASE_Y,
                ),
                (
                    "A2111",
                    Generation7Constants.POSITION_A2111_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A2111_FIRST_NAME_BASE_Y,
                ),
                (
                    "A2112",
                    Generation7Constants.POSITION_A2112_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A2112_FIRST_NAME_BASE_Y,
                ),
                (
                    "A2211",
                    Generation7Constants.POSITION_A2211_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A2211_FIRST_NAME_BASE_Y,
                ),
                (
                    "A2212",
                    Generation7Constants.POSITION_A2212_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A2212_FIRST_NAME_BASE_Y,
                ),
                (
                    "A2221",
                    Generation7Constants.POSITION_A2221_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A2221_FIRST_NAME_BASE_Y,
                ),
                (
                    "A2222",
                    Generation7Constants.POSITION_A2222_FIRST_NAME_BASE_X,
                    Generation7Constants.POSITION_A2222_FIRST_NAME_BASE_Y,
                ),
            ]

            for label, x, y in a_positions:
                positions.append((label, x, y, 0))

            # B subclade (rotation=270, right side)
            for label, x, y in a_positions:
                positions.append((label.replace("A", "B"), x, y, 270))

            # C subclade (rotation=180, top)
            for label, x, y in a_positions:
                positions.append((label.replace("A", "C"), x, y, 180))

            # D subclade (rotation=90, left side)
            for label, x, y in a_positions:
                positions.append((label.replace("A", "D"), x, y, 90))

            base_params = dict(
                center_x=Generation7Constants.IMAGE_CENTER_X,
                center_y=Generation7Constants.IMAGE_CENTER_Y,
                name_font_size=8,
                date_font_size=6,
                place_font_size=5,
                birth_date_offset_x=0,
                birth_date_offset_y=0,
                birth_date_rotation=0,
                birth_date_paired_offset_x=-40,
                death_date_paired_offset_x=40,
                paired_dates_base_y=1835,
                paired_places_base_y=1969,
                birth_place_paired_offset_x=-40,
                death_place_paired_offset_x=40,
                use_display_text=False,
                use_gravity_center=False,
                multiline_line_spacing=1.5,
                multiline_alignment="center",
            )

            for label, base_x, base_y, rotation in positions:
                label_person = PositionLabel(label)
                print_individual(
                    draw=draw,
                    content_img=content_img,
                    individual=label_person,
                    settings=validated_settings,
                    rotation=rotation,
                    first_name_base_x=base_x,
                    first_name_base_y=base_y,
                    birth_date_base_x=base_x,
                    birth_date_base_y=base_y,
                    birth_place_base_x=base_x,
                    birth_place_base_y=base_y,
                    death_date_base_x=base_x,
                    death_date_base_y=base_y,
                    death_place_base_x=base_x,
                    death_place_base_y=base_y,
                    **base_params,
                )
                logger.debug(
                    f"Printed {label} at ({base_x}, {base_y}) rotation={rotation}"
                )

            draw.pop()
            draw(content_img)

        return create_preview_buffer(content_img)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    result = generate_7gen_position_debug()
    with open("debug_7gen_positions.png", "wb") as f:
        f.write(result.getvalue())
    print("Saved to debug_7gen_positions.png")
