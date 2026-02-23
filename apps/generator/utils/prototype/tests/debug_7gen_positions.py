"""
Debug test to verify 7gen position placements.
Uses the actual print_individual function to show position labels.
Calculates sunbeam-style rotation based on position angle from center.
"""

import logging
import math
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

            # Calculate sunbeam rotation based on position angle from center
            center_x = Generation7Constants.IMAGE_CENTER_X
            center_y = Generation7Constants.IMAGE_CENTER_Y

            def get_sunbeam_rotation(x, y):
                """Calculate rotation so text runs ALONG the sunbeam ray (pointing outward from center)"""
                dx = x - center_x
                dy = y - center_y
                angle = math.degrees(math.atan2(dy, dx))
                # Rotation makes text point ALONG the ray away from center
                # Currently we have angle-90 (perpendicular), change to just angle
                rotation = int(angle)
                # Normalize to 0-360
                rotation = rotation % 360
                return rotation

            # Position labels following father(1)/mother(2) binary pattern
            # A1111 = father's father's father's father, A1112 = father's father's father's mother, etc.
            a_labels = [
                "A1111",
                "A1112",
                "A1121",
                "A1122",
                "A1211",
                "A1212",
                "A1221",
                "A1222",
                "A2111",
                "A2112",
                "A2121",
                "A2122",
                "A2211",
                "A2212",
                "A2221",
                "A2222",
            ]
            b_labels = [
                "B1111",
                "B1112",
                "B1121",
                "B1122",
                "B1211",
                "B1212",
                "B1221",
                "B1222",
                "B2111",
                "B2112",
                "B2121",
                "B2122",
                "B2211",
                "B2212",
                "B2221",
                "B2222",
            ]
            c_labels = [
                "C1111",
                "C1112",
                "C1121",
                "C1122",
                "C1211",
                "C1212",
                "C1221",
                "C1222",
                "C2111",
                "C2112",
                "C2121",
                "C2122",
                "C2211",
                "C2212",
                "C2221",
                "C2222",
            ]
            d_labels = [
                "D1111",
                "D1112",
                "D1121",
                "D1122",
                "D1211",
                "D1212",
                "D1221",
                "D1222",
                "D2111",
                "D2112",
                "D2121",
                "D2122",
                "D2211",
                "D2212",
                "D2221",
                "D2222",
            ]

            # Square edge positions - 116px spacing starting at x=135
            bottom_x = [
                135,
                251,
                367,
                483,
                599,
                715,
                831,
                947,
                1003,
                1119,
                1235,
                1351,
                1467,
                1583,
                1699,
                1815,
            ]

            # Square positions - 16 per edge
            # A: bottom edge, left corner (x=135) going inward to center (x=975), then to right corner (x=1815)
            a_positions = [(a_labels[i], bottom_x[i], 1885) for i in range(16)]

            # B: right edge, bottom corner (y=1815) going upward to top corner (y=135)
            # Uses bottom_x for y values reversed so B0 is at corner where A ends
            b_y = list(reversed(bottom_x))
            b_positions = [(b_labels[i], 1885, b_y[i]) for i in range(16)]

            # C: top edge, right corner (x=1815) going leftward to left corner (x=135)
            c_x = list(reversed(bottom_x))
            c_positions = [(c_labels[i], c_x[i], 65) for i in range(16)]

            # D: left edge, top corner (y=135) going downward to bottom corner (y=1815)
            d_positions = [(d_labels[i], 65, bottom_x[i]) for i in range(16)]

            # All subclades with sunbeam rotation
            for label, x, y in a_positions:
                rot = get_sunbeam_rotation(x, y)
                positions.append((label, x, y, rot))

            for label, x, y in b_positions:
                rot = get_sunbeam_rotation(x, y)
                positions.append((label, x, y, rot))

            for label, x, y in c_positions:
                rot = get_sunbeam_rotation(x, y)
                positions.append((label, x, y, rot))

            for label, x, y in d_positions:
                rot = get_sunbeam_rotation(x, y)
                positions.append((label, x, y, rot))

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
