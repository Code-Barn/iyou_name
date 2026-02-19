"""
Debug test to verify 6gen position placements.
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

from apps.generator.utils.prototype.prototype_image_6generator import (
    Generation6Constants,
)
from apps.generator.utils.prototype.prototype_image_5generator import (
    generate_prototype_5gen_preview,
)
from apps.generator.utils.prototype.individual_printer import print_individual
from apps.generator.utils.settings_validator import get_validated_settings
from apps.generator.utils.simple_buffer_manager import create_preview_buffer

logger = logging.getLogger(__name__)

GENERATION_6_DEBUG_SCHEMA = {
    "font_family": (str, "Arial"),
    "great_great_great_grandparent_stroke_color": (Color, "black"),
    "great_great_great_grandparent_font_color": (Color, "black"),
    "great_great_great_grandparent_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "overlay_scale": (float, 0.8179),
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
}


def _composite_overlay_debug(content_img, gen5_img_buffer, validated_settings):
    """Composite the 5gen overlay at 81.79% scale in center."""
    try:
        gen5_img_buffer.seek(0)
        gen5_bytes = gen5_img_buffer.getvalue()

        if not gen5_bytes:
            return

        overlay_scale = validated_settings.get("overlay_scale", 0.8179)

        with Image(blob=gen5_bytes) as gen5_overlay:
            overlay_size = int(gen5_overlay.width * overlay_scale)
            gen5_overlay.resize(overlay_size, overlay_size)

            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            content_img.composite(gen5_overlay, left=overlay_x, top=overlay_y)

    except Exception as e:
        logger.error(f"Failed to composite overlay: {e}")


class PositionLabel:
    """Simple class to hold position label for printing."""

    def __init__(self, full_name):
        self.full_name = full_name
        self.birth_date = ""
        self.birth_place = ""
        self.death_date = ""
        self.death_place = ""


def generate_6gen_position_debug():
    """Generate a debug chart showing position labels using print_individual."""
    validated_settings = get_validated_settings({}, GENERATION_6_DEBUG_SCHEMA, "6gen")

    template_path = os.path.join(
        settings.BASE_DIR,
        "apps/hud/static/hud/images/preview_image_templates",
        "6GEN_PREVIEW.png",
    )

    if not os.path.exists(template_path):
        logger.warning("6gen preview template not found, using 5gen template")
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "5GEN_PREVIEW.png",
        )

    with Image(filename=template_path, resolution=300) as content_img:
        with Drawing() as draw:
            draw.push()

            draw.font = validated_settings["font_family"]
            draw.stroke_antialias = True
            draw.stroke_width = 0.5
            draw.stroke_color = Color("black")

            # All 32 positions for 6gen (A111-A222, B111-B222, C111-C222, D111-D222)
            # Each position tuple: (label, base_x, base_y, rotation)
            positions = []

            # A subclade (rotation=0, bottom)
            a_positions = [
                (
                    "A111",
                    Generation6Constants.POSITION_A111_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A111_FIRST_NAME_BASE_Y,
                ),
                (
                    "A112",
                    Generation6Constants.POSITION_A112_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A112_FIRST_NAME_BASE_Y,
                ),
                (
                    "A121",
                    Generation6Constants.POSITION_A121_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A121_FIRST_NAME_BASE_Y,
                ),
                (
                    "A122",
                    Generation6Constants.POSITION_A122_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A122_FIRST_NAME_BASE_Y,
                ),
                (
                    "A211",
                    Generation6Constants.POSITION_A211_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A211_FIRST_NAME_BASE_Y,
                ),
                (
                    "A212",
                    Generation6Constants.POSITION_A212_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A212_FIRST_NAME_BASE_Y,
                ),
                (
                    "A221",
                    Generation6Constants.POSITION_A221_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A221_FIRST_NAME_BASE_Y,
                ),
                (
                    "A222",
                    Generation6Constants.POSITION_A222_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A222_FIRST_NAME_BASE_Y,
                ),
            ]

            for label, x, y in a_positions:
                positions.append((label, x, y, 0))

            # B subclade (rotation=270, right side)
            b_positions = [
                (
                    "B111",
                    Generation6Constants.POSITION_A111_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A111_FIRST_NAME_BASE_Y,
                ),
                (
                    "B112",
                    Generation6Constants.POSITION_A112_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A112_FIRST_NAME_BASE_Y,
                ),
                (
                    "B121",
                    Generation6Constants.POSITION_A121_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A121_FIRST_NAME_BASE_Y,
                ),
                (
                    "B122",
                    Generation6Constants.POSITION_A122_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A122_FIRST_NAME_BASE_Y,
                ),
                (
                    "B211",
                    Generation6Constants.POSITION_A211_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A211_FIRST_NAME_BASE_Y,
                ),
                (
                    "B212",
                    Generation6Constants.POSITION_A212_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A212_FIRST_NAME_BASE_Y,
                ),
                (
                    "B221",
                    Generation6Constants.POSITION_A221_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A221_FIRST_NAME_BASE_Y,
                ),
                (
                    "B222",
                    Generation6Constants.POSITION_A222_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A222_FIRST_NAME_BASE_Y,
                ),
            ]

            for label, x, y in b_positions:
                positions.append((label, x, y, 270))

            # C subclade (rotation=180, top)
            c_positions = [
                (
                    "C111",
                    Generation6Constants.POSITION_A111_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A111_FIRST_NAME_BASE_Y,
                ),
                (
                    "C112",
                    Generation6Constants.POSITION_A112_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A112_FIRST_NAME_BASE_Y,
                ),
                (
                    "C121",
                    Generation6Constants.POSITION_A121_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A121_FIRST_NAME_BASE_Y,
                ),
                (
                    "C122",
                    Generation6Constants.POSITION_A122_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A122_FIRST_NAME_BASE_Y,
                ),
                (
                    "C211",
                    Generation6Constants.POSITION_A211_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A211_FIRST_NAME_BASE_Y,
                ),
                (
                    "C212",
                    Generation6Constants.POSITION_A212_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A212_FIRST_NAME_BASE_Y,
                ),
                (
                    "C221",
                    Generation6Constants.POSITION_A221_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A221_FIRST_NAME_BASE_Y,
                ),
                (
                    "C222",
                    Generation6Constants.POSITION_A222_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A222_FIRST_NAME_BASE_Y,
                ),
            ]

            for label, x, y in c_positions:
                positions.append((label, x, y, 180))

            # D subclade (rotation=90, left side)
            d_positions = [
                (
                    "D111",
                    Generation6Constants.POSITION_A111_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A111_FIRST_NAME_BASE_Y,
                ),
                (
                    "D112",
                    Generation6Constants.POSITION_A112_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A112_FIRST_NAME_BASE_Y,
                ),
                (
                    "D121",
                    Generation6Constants.POSITION_A121_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A121_FIRST_NAME_BASE_Y,
                ),
                (
                    "D122",
                    Generation6Constants.POSITION_A122_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A122_FIRST_NAME_BASE_Y,
                ),
                (
                    "D211",
                    Generation6Constants.POSITION_A211_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A211_FIRST_NAME_BASE_Y,
                ),
                (
                    "D212",
                    Generation6Constants.POSITION_A212_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A212_FIRST_NAME_BASE_Y,
                ),
                (
                    "D221",
                    Generation6Constants.POSITION_A221_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A221_FIRST_NAME_BASE_Y,
                ),
                (
                    "D222",
                    Generation6Constants.POSITION_A222_FIRST_NAME_BASE_X,
                    Generation6Constants.POSITION_A222_FIRST_NAME_BASE_Y,
                ),
            ]

            for label, x, y in d_positions:
                positions.append((label, x, y, 90))

            # Use print_individual to print each position label
            base_params = dict(
                center_x=Generation6Constants.IMAGE_CENTER_X,
                center_y=Generation6Constants.IMAGE_CENTER_Y,
                name_font_size=10,
                date_font_size=8,
                place_font_size=6,
                birth_date_offset_x=0,
                birth_date_offset_y=0,
                birth_date_rotation=0,
                birth_date_paired_offset_x=-100,
                death_date_paired_offset_x=100,
                paired_dates_base_y=1785,
                paired_places_base_y=1919,
                birth_place_paired_offset_x=-100,
                death_place_paired_offset_x=100,
                use_display_text=False,  # Use full_name mode
                use_gravity_center=False,
                multiline_line_spacing=1.8,
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

        # Skip overlay for position debugging
        # gen5_img_buffer = generate_prototype_5gen_preview(None, None, "preview", {})
        # _composite_overlay_debug(content_img, gen5_img_buffer, validated_settings)

        return create_preview_buffer(content_img)


if __name__ == "__main__":
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    logging.basicConfig(level=logging.DEBUG)

    result = generate_6gen_position_debug()
    with open("debug_6gen_positions.png", "wb") as f:
        f.write(result.getvalue())
    print("Saved to debug_6gen_positions.png")
