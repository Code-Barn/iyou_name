"""
Debug test to verify position placements in 5gen chart.
Prints position labels (A11, A12, A21, A22, B11, etc.) instead of actual names.
"""

import logging
import os

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.parser.models import PersonData
from apps.generator.utils.prototype.prototype_image_4generator import (
    generate_prototype_4gen_preview,
)
from apps.generator.utils.prototype.prototype_image_5generator import (
    Generation5Constants,
    generate_prototype_5gen_preview,
)
from apps.generator.utils.settings_validator import get_validated_settings
from apps.generator.utils.simple_buffer_manager import create_preview_buffer

logger = logging.getLogger(__name__)

GENERATION_5_DEBUG_SCHEMA = {
    "font_family": (str, "Arial"),
    "great_great_grandparent_stroke_color": (Color, "black"),
    "great_great_grandparent_font_color": (Color, "black"),
    "great_great_grandparent_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "overlay_scale": (float, 0.7779),
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
}


def _composite_overlay_debug(content_img, gen4_img_buffer, validated_settings):
    """Composite the 4gen overlay at 77.79% scale in center."""
    try:
        gen4_img_buffer.seek(0)
        gen4_bytes = gen4_img_buffer.getvalue()

        if not gen4_bytes:
            return

        overlay_scale = validated_settings.get("overlay_scale", 0.7779)

        with Image(blob=gen4_bytes) as gen4_overlay:
            overlay_size = int(gen4_overlay.width * overlay_scale)
            gen4_overlay.resize(overlay_size, overlay_size)

            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            content_img.composite(gen4_overlay, left=overlay_x, top=overlay_y)

    except Exception as e:
        logger.error(f"Failed to composite overlay: {e}")


def generate_position_debug_preview():
    """Generate a debug chart showing position labels."""
    validated_settings = get_validated_settings({}, GENERATION_5_DEBUG_SCHEMA, "5gen")

    template_path = os.path.join(
        settings.BASE_DIR,
        "apps/hud/static/hud/images/preview_image_templates",
        "5GEN_PREVIEW.png",
    )

    if not os.path.exists(template_path):
        logger.warning("5gen preview template not found, using 4gen template")
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "4GEN_PREVIEW.png",
        )

    with Image(filename=template_path, resolution=300) as content_img:
        with Drawing() as draw:
            draw.push()
            draw.font = "Arial"
            draw.font_size = 14
            draw.fill_color = Color("red")
            draw.stroke_color = Color("black")
            draw.stroke_width = 0.5

            positions_to_print = [
                (
                    "A11",
                    Generation5Constants.POSITION_A11_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A11_FIRST_NAME_BASE_Y,
                    0,
                ),
                (
                    "A12",
                    Generation5Constants.POSITION_A12_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A12_FIRST_NAME_BASE_Y,
                    0,
                ),
                (
                    "A21",
                    Generation5Constants.POSITION_A21_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A21_FIRST_NAME_BASE_Y,
                    0,
                ),
                (
                    "A22",
                    Generation5Constants.POSITION_A22_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A22_FIRST_NAME_BASE_Y,
                    0,
                ),
                (
                    "B11",
                    Generation5Constants.POSITION_A11_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A11_FIRST_NAME_BASE_Y,
                    270,
                ),
                (
                    "B12",
                    Generation5Constants.POSITION_A12_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A12_FIRST_NAME_BASE_Y,
                    270,
                ),
                (
                    "B21",
                    Generation5Constants.POSITION_A21_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A21_FIRST_NAME_BASE_Y,
                    270,
                ),
                (
                    "B22",
                    Generation5Constants.POSITION_A22_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A22_FIRST_NAME_BASE_Y,
                    270,
                ),
                (
                    "C11",
                    Generation5Constants.POSITION_A11_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A11_FIRST_NAME_BASE_Y,
                    180,
                ),
                (
                    "C12",
                    Generation5Constants.POSITION_A12_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A12_FIRST_NAME_BASE_Y,
                    180,
                ),
                (
                    "C21",
                    Generation5Constants.POSITION_A21_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A21_FIRST_NAME_BASE_Y,
                    180,
                ),
                (
                    "C22",
                    Generation5Constants.POSITION_A22_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A22_FIRST_NAME_BASE_Y,
                    180,
                ),
                (
                    "D11",
                    Generation5Constants.POSITION_A11_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A11_FIRST_NAME_BASE_Y,
                    90,
                ),
                (
                    "D12",
                    Generation5Constants.POSITION_A12_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A12_FIRST_NAME_BASE_Y,
                    90,
                ),
                (
                    "D21",
                    Generation5Constants.POSITION_A21_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A21_FIRST_NAME_BASE_Y,
                    90,
                ),
                (
                    "D22",
                    Generation5Constants.POSITION_A22_FIRST_NAME_BASE_X,
                    Generation5Constants.POSITION_A22_FIRST_NAME_BASE_Y,
                    90,
                ),
            ]

            center_x = 975
            center_y = 975

            for label, base_x, base_y, rotation in positions_to_print:
                import math

                rad = math.radians(rotation)
                x = (
                    center_x
                    + (base_x - center_x) * math.cos(rad)
                    - (base_y - center_y) * math.sin(rad)
                )
                y = (
                    center_y
                    + (base_x - center_x) * math.sin(rad)
                    + (base_y - center_y) * math.cos(rad)
                )

                draw.text(int(x), int(y), f"{label}({rotation}°)")
                logger.debug(f"{label} at ({x:.0f}, {y:.0f}) rotation={rotation}")

            draw.pop()
            draw(content_img)

        return create_preview_buffer(content_img)


def generate_4gen_position_debug():
    """Generate a debug chart showing 4gen position labels."""
    from apps.generator.utils.prototype.prototype_image_4generator import (
        Generation4Constants,
    )

    template_path = os.path.join(
        settings.BASE_DIR,
        "apps/hud/static/hud/images/preview_image_templates",
        "4GEN_PREVIEW.png",
    )

    with Image(filename=template_path, resolution=300) as content_img:
        with Drawing() as draw:
            draw.push()
            draw.font = "Arial"
            draw.font_size = 16
            draw.fill_color = Color("red")
            draw.stroke_color = Color("black")
            draw.stroke_width = 0.5

            center_x = 975
            center_y = 975

            positions_to_print = [
                (
                    "A1",
                    Generation4Constants.POSITION_A1_FIRST_NAME_BASE_X,
                    Generation4Constants.POSITION_A1_FIRST_NAME_BASE_Y,
                    0,
                ),
                (
                    "A2",
                    Generation4Constants.POSITION_A2_FIRST_NAME_BASE_X,
                    Generation4Constants.POSITION_A2_FIRST_NAME_BASE_Y,
                    0,
                ),
                (
                    "B1",
                    Generation4Constants.POSITION_A1_FIRST_NAME_BASE_X,
                    Generation4Constants.POSITION_A1_FIRST_NAME_BASE_Y,
                    270,
                ),
                (
                    "B2",
                    Generation4Constants.POSITION_A2_FIRST_NAME_BASE_X,
                    Generation4Constants.POSITION_A2_FIRST_NAME_BASE_Y,
                    270,
                ),
                (
                    "C1",
                    Generation4Constants.POSITION_A1_FIRST_NAME_BASE_X,
                    Generation4Constants.POSITION_A1_FIRST_NAME_BASE_Y,
                    180,
                ),
                (
                    "C2",
                    Generation4Constants.POSITION_A2_FIRST_NAME_BASE_X,
                    Generation4Constants.POSITION_A2_FIRST_NAME_BASE_Y,
                    180,
                ),
                (
                    "D1",
                    Generation4Constants.POSITION_A1_FIRST_NAME_BASE_X,
                    Generation4Constants.POSITION_A1_FIRST_NAME_BASE_Y,
                    90,
                ),
                (
                    "D2",
                    Generation4Constants.POSITION_A2_FIRST_NAME_BASE_X,
                    Generation4Constants.POSITION_A2_FIRST_NAME_BASE_Y,
                    90,
                ),
            ]

            import math

            for label, base_x, base_y, rotation in positions_to_print:
                rad = math.radians(rotation)
                x = (
                    center_x
                    + (base_x - center_x) * math.cos(rad)
                    - (base_y - center_y) * math.sin(rad)
                )
                y = (
                    center_y
                    + (base_x - center_x) * math.sin(rad)
                    + (base_y - center_y) * math.cos(rad)
                )

                draw.text(int(x), int(y), f"{label}({rotation}°)")
                print(
                    f"{label}: base=({base_x},{base_y}) -> rotated=({x:.0f},{y:.0f}) rot={rotation}"
                )

            draw.pop()
            draw(content_img)

        return create_preview_buffer(content_img)


if __name__ == "__main__":
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    django.setup()

    print("=== 4GEN Position Debug ===")
    result = generate_4gen_position_debug()
    with open("debug_4gen_positions.png", "wb") as f:
        f.write(result.getvalue())
    print("Saved to debug_4gen_positions.png")

    print("\n=== 5GEN Position Debug ===")
    result = generate_position_debug_preview()
    with open("debug_5gen_positions.png", "wb") as f:
        f.write(result.getvalue())
    print("Saved to debug_5gen_positions.png")
