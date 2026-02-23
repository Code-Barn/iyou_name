"""
Debug test to verify 7gen position placements.
Run via: uv run python manage.py shell < debug_7gen_positions_test.py
"""

import logging
import math
import os
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

            positions = []

            center_x = Generation7Constants.IMAGE_CENTER_X
            center_y = Generation7Constants.IMAGE_CENTER_Y

            def get_sunbeam_rotation(x, y, inward=False):
                """Calculate rotation so text runs ALONG the sunbeam ray (pointing outward from center)."""
                dx = x - center_x
                dy = y - center_y
                angle = math.degrees(math.atan2(dy, dx))
                rotation = int(angle) % 360
                if inward:
                    rotation = (rotation + 180) % 360
                return rotation

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

            bottom_x = [
                125,  # A1111 (-10px)
                241,  # A1112
                357,  # A1121
                473,  # A1122
                577,  # A1211 (-22px)
                693,  # A1212 (-22px)
                809,  # A1221 (-22px)
                925,  # A1222 (-22px)
                993,  # A2111 (+20px, adjusted inward)
                1109,  # A2112 (+20px)
                1225,  # A2121 (+20px)
                1341,  # A2122 (+20px)
                1457,  # A2211 (+10px)
                1573,  # A2212 (+10px)
                1689,  # A2221 (+10px)
                1805,  # A2222 (+10px)
            ]

            a_positions = [(a_labels[i], bottom_x[i], 1875) for i in range(16)]

            # B: right edge, bottom corner going up
            b_y = list(reversed(bottom_x))
            b_positions = [(b_labels[i], 1875, b_y[i]) for i in range(16)]

            # C: top edge, right corner going left
            c_x = list(reversed(bottom_x))
            c_positions = [(c_labels[i], c_x[i], 55) for i in range(16)]

            # D: left edge, top corner going down
            d_positions = [(d_labels[i], 55, bottom_x[i]) for i in range(16)]

            # A = inward (pointing toward center)
            for label, x, y in a_positions:
                rot = get_sunbeam_rotation(x, y, inward=True)
                positions.append((label, x, y, rot))

            # B = inward
            for label, x, y in b_positions:
                rot = get_sunbeam_rotation(x, y, inward=True)
                positions.append((label, x, y, rot))

            # C = inward
            for label, x, y in c_positions:
                rot = get_sunbeam_rotation(x, y, inward=True)
                positions.append((label, x, y, rot))

            # D = inward
            for label, x, y in d_positions:
                rot = get_sunbeam_rotation(x, y, inward=True)
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
    result = generate_7gen_position_debug()
    output_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "debug_7gen_positions.png"
    )
    with open(output_path, "wb") as f:
        f.write(result.getvalue())
    print(f"Saved to {output_path}")
