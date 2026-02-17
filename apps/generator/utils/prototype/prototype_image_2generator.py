"""
Prototype 2-generation chart generator using modular individual printer.

Position System:
- Position 0: Primary individual (in 1gen overlay at center, 50% scale)
- Position 1: Father (bottom-left quadrant, 0° rotation)
  - First name: centered horizontally at bottom
  - Last name: -90° rotated, centered vertically along right side
- Position 2: Mother (top-right quadrant, 180° rotation)
  - First name: centered horizontally at top
  - Last name: 90° rotated, centered vertically along left side

The positions are rotated around the center point (975, 975).
"""

import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.parser.models import PersonData
from apps.generator.utils.prototype.individual_printer import print_individual
from apps.generator.utils.prototype.prototype_image_1generator import (
    generate_prototype_1gen_preview,
)
from apps.generator.utils.settings_validator import (
    get_validated_settings,
    GenerationError,
)
from apps.generator.utils.simple_buffer_manager import (
    create_preview_buffer,
    create_pdf_buffer,
    BufferError,
)

logger = logging.getLogger(__name__)


class Generation2Constants:
    # Image center - rotation point for positions
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975

    # Position 1 (Father): base positions before any rotation
    # First name: centered at bottom, 150px from edge
    POSITION_1_FIRST_NAME_BASE_X = 975
    POSITION_1_FIRST_NAME_BASE_Y = 1725  # 1875 - 150

    # Middle name: at (1650, 1650), -45° angle
    POSITION_1_MIDDLE_NAME_BASE_X = 1650
    POSITION_1_MIDDLE_NAME_BASE_Y = 1650
    POSITION_1_MIDDLE_NAME_ROTATION = -45

    # Last name: centered on right, 150px from edge
    POSITION_1_LAST_NAME_BASE_X = 1725  # 1875 - 150
    POSITION_1_LAST_NAME_BASE_Y = 975

    # Position 1 (Father): Birth/Death info positions
    # Image is 1950x1950, center is (975, 975), border is 32px from edge
    # Birth date: left side (x=200), near first name at bottom (y=1700)
    POSITION_1_BIRTH_DATE_BASE_X = 200
    POSITION_1_BIRTH_DATE_BASE_Y = 1700

    # Birth place: bottom area, 50px from edge (y=1900)
    POSITION_1_BIRTH_PLACE_BASE_X = 975
    POSITION_1_BIRTH_PLACE_BASE_Y = 1900

    # Death date: top area (y=225), near center/first name area
    POSITION_1_DEATH_DATE_BASE_X = 975
    POSITION_1_DEATH_DATE_BASE_Y = 225

    # Death place: right side, 50px from edge (x=1900)
    POSITION_1_DEATH_PLACE_BASE_X = 1900
    POSITION_1_DEATH_PLACE_BASE_Y = 975

    # Position 2 (Mother): 180° mirrored positions from Position 1
    # Birth date: (200, 1700) mirrored → (1750, 225)
    POSITION_2_BIRTH_DATE_BASE_X = 1750
    POSITION_2_BIRTH_DATE_BASE_Y = 225

    # Birth place: (975, 1900) mirrored → (975, 50)
    POSITION_2_BIRTH_PLACE_BASE_X = 975
    POSITION_2_BIRTH_PLACE_BASE_Y = 50

    # Death date: (975, 200) mirrored → (975, 1750)
    POSITION_2_DEATH_DATE_BASE_X = 975
    POSITION_2_DEATH_DATE_BASE_Y = 1750

    # Death place: (1900, 975) mirrored → (50, 975)
    POSITION_2_DEATH_PLACE_BASE_X = 50
    POSITION_2_DEATH_PLACE_BASE_Y = 975

    PARENT_NAME_FONT_SIZE = 48
    PARENT_DATE_INFO_FONT_SIZE = 36
    PARENT_PLACE_INFO_FONT_SIZE = 20

    OVERLAY_SCALE = 0.50
    COMPOSITE_X = 300
    COMPOSITE_Y = 570
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72


GENERATION_2_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    "parent_stroke_color": (Color, "black"),
    "parent_font_color": (Color, "black"),
    "parent_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "father_font_color": (Color, "black"),
    "father_stroke_color": (Color, "black"),
    "father_font_size": (int, 48),
    "father_translate_x": (int, 0),
    "father_translate_y": (int, 0),
    "father_rotate": (int, 0),
    "father_birth_translate_x": (int, 0),
    "father_birth_translate_y": (int, 0),
    "father_birth_rotate": (int, 0),
    "father_birth_place_translate_y": (int, 0),
    "father_birth_place_rotate": (int, 0),
    "father_death_translate_x": (int, 0),
    "father_death_translate_y": (int, 0),
    "father_death_rotate": (int, 0),
    "father_death_place_translate_x": (int, 0),
    "father_death_place_translate_y": (int, 0),
    "father_death_place_rotate": (int, -90),
    "mother_font_color": (Color, "black"),
    "mother_stroke_color": (Color, "black"),
    "mother_font_size": (int, 48),
    "mother_translate_x": (int, 0),
    "mother_translate_y": (int, 0),
    "mother_rotate": (int, 180),
    "mother_birth_translate_x": (int, 0),
    "mother_birth_translate_y": (int, 0),
    "mother_birth_rotate": (int, 0),
    "mother_birth_place_translate_y": (int, 0),
    "mother_birth_place_rotate": (int, 0),
    "mother_death_translate_x": (int, 0),
    "mother_death_translate_y": (int, 0),
    "mother_death_rotate": (int, -90),
    "mother_death_place_translate_x": (int, 0),
    "mother_death_place_translate_y": (int, 0),
    "mother_death_place_rotate": (int, -90),
    "overlay_scale": (float, 0.50),
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
}


def _composite_overlay(content_img, gen1_img_buffer, validated_settings):
    """Composite the 1gen overlay at 50% scale in center."""
    try:
        gen1_img_buffer.seek(0)
        gen1_bytes = gen1_img_buffer.getvalue()

        if not gen1_bytes:
            raise BufferError("1gen overlay buffer is empty")

        overlay_scale = validated_settings.get(
            "overlay_scale", Generation2Constants.OVERLAY_SCALE
        )

        with Image(blob=gen1_bytes) as gen1_overlay:
            overlay_size = int(gen1_overlay.width * overlay_scale)
            gen1_overlay.resize(overlay_size, overlay_size)

            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            content_img.composite(gen1_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 1gen overlay at ({overlay_x}, {overlay_y}) scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


def generate_prototype_2gen_preview(
    primary_individual, family_data=None, template="preview", user_settings=None
):
    """
    Generate 2-gen chart using modular printer.

    Position 0: Father (bottom, 0° rotation)
    Position 1: Mother (center, 180° rotation - flipped)
    """
    user_settings = user_settings or {}
    validated_settings = get_validated_settings(
        user_settings, GENERATION_2_SETTINGS_SCHEMA, "2gen"
    )

    logger.info(f"Generating prototype 2gen for: {primary_individual.full_name}")

    try:
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "2GEN_PREVIEW.png",
        )

        if not os.path.exists(template_path):
            raise GenerationError(f"Preview template not found: {template_path}")

        with Image(
            filename=template_path, resolution=Generation2Constants.RESOLUTION
        ) as content_img:
            with Drawing() as draw:
                draw.push()

                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings["parent_stroke_width"]
                draw.stroke_color = validated_settings["parent_stroke_color"]

                # No initial translate - use absolute positions

                individuals = family_data.get("individuals", {}) if family_data else {}
                father_id = getattr(primary_individual, "father", None)
                mother_id = getattr(primary_individual, "mother", None)

                father = individuals.get(father_id) if father_id else None
                mother = individuals.get(mother_id) if mother_id else None

                # Draw father (Position 1: bottom, 0° rotation)
                # Base positions: first name at bottom, last name on right
                if father:
                    print_individual(
                        draw=draw,
                        content_img=content_img,
                        individual=father,
                        settings=validated_settings,
                        center_x=Generation2Constants.IMAGE_CENTER_X,
                        center_y=Generation2Constants.IMAGE_CENTER_Y,
                        rotation=0,  # Position 1: no rotation
                        name_font_size=validated_settings.get(
                            "father_font_size",
                            Generation2Constants.PARENT_NAME_FONT_SIZE,
                        ),
                        date_font_size=Generation2Constants.PARENT_DATE_INFO_FONT_SIZE,
                        place_font_size=Generation2Constants.PARENT_PLACE_INFO_FONT_SIZE,
                        # First name: centered at bottom, 150px from edge
                        first_name_base_x=Generation2Constants.POSITION_1_FIRST_NAME_BASE_X,
                        first_name_base_y=Generation2Constants.POSITION_1_FIRST_NAME_BASE_Y,
                        first_name_offset_x=validated_settings.get(
                            "father_translate_x", 0
                        ),
                        first_name_offset_y=validated_settings.get(
                            "father_translate_y", 0
                        ),
                        first_name_rotation=0,
                        # Middle name: at (1750, 1750), -45° angle
                        middle_name_base_x=Generation2Constants.POSITION_1_MIDDLE_NAME_BASE_X,
                        middle_name_base_y=Generation2Constants.POSITION_1_MIDDLE_NAME_BASE_Y,
                        middle_name_offset_x=validated_settings.get(
                            "father_translate_x", 0
                        ),
                        middle_name_offset_y=validated_settings.get(
                            "father_translate_y", 0
                        ),
                        middle_name_rotation=Generation2Constants.POSITION_1_MIDDLE_NAME_ROTATION,
                        # Last name: centered on right, 150px from edge, vertical (-90°)
                        last_name_base_x=Generation2Constants.POSITION_1_LAST_NAME_BASE_X,
                        last_name_base_y=Generation2Constants.POSITION_1_LAST_NAME_BASE_Y,
                        last_name_offset_x=validated_settings.get(
                            "father_translate_x", 0
                        ),
                        last_name_offset_y=validated_settings.get(
                            "father_translate_y", 0
                        ),
                        last_name_rotation=-90,  # Vertical text
                        # Birth date: same position as first name, moved up 150px
                        birth_date_base_x=Generation2Constants.POSITION_1_FIRST_NAME_BASE_X,
                        birth_date_base_y=Generation2Constants.POSITION_1_FIRST_NAME_BASE_Y,
                        birth_date_offset_x=validated_settings.get(
                            "father_translate_x", 0
                        ),
                        birth_date_offset_y=-150,
                        birth_date_rotation=0,
                        # Death date: same position as last name, moved left 150px
                        death_date_base_x=Generation2Constants.POSITION_1_LAST_NAME_BASE_X,
                        death_date_base_y=Generation2Constants.POSITION_1_LAST_NAME_BASE_Y,
                        death_date_offset_x=-150,
                        death_date_offset_y=validated_settings.get(
                            "father_translate_y", 0
                        ),
                        death_date_rotation=-90,
                        birth_place_base_x=Generation2Constants.POSITION_1_BIRTH_PLACE_BASE_X,
                        birth_place_base_y=Generation2Constants.POSITION_1_BIRTH_PLACE_BASE_Y,
                        birth_place_offset_x=validated_settings.get(
                            "father_birth_place_translate_x", 0
                        ),
                        birth_place_offset_y=validated_settings.get(
                            "father_birth_place_translate_y", 0
                        ),
                        birth_place_rotation=validated_settings.get(
                            "father_birth_place_rotate", 0
                        ),
                        death_place_base_x=Generation2Constants.POSITION_1_DEATH_PLACE_BASE_X,
                        death_place_base_y=Generation2Constants.POSITION_1_DEATH_PLACE_BASE_Y,
                        death_place_offset_x=validated_settings.get(
                            "father_death_place_translate_x", 0
                        ),
                        death_place_offset_y=validated_settings.get(
                            "father_death_place_translate_y", 0
                        ),
                        death_place_rotation=validated_settings.get(
                            "father_death_place_rotate", -90
                        ),
                        use_display_text=False,
                        use_gravity_center=False,
                    )

                # Draw mother (Position 2: top, 180° rotation)
                # Same base positions as father, but rotated 180° around image center
                # This mirrors to: first name at top, last name on left
                if mother:
                    print_individual(
                        draw=draw,
                        content_img=content_img,
                        individual=mother,
                        settings=validated_settings,
                        center_x=Generation2Constants.IMAGE_CENTER_X,
                        center_y=Generation2Constants.IMAGE_CENTER_Y,
                        rotation=180,  # Position 2: 180° rotation around image center
                        name_font_size=validated_settings.get(
                            "mother_font_size",
                            Generation2Constants.PARENT_NAME_FONT_SIZE,
                        ),
                        date_font_size=Generation2Constants.PARENT_DATE_INFO_FONT_SIZE,
                        place_font_size=Generation2Constants.PARENT_PLACE_INFO_FONT_SIZE,
                        # First name: same base position, will be rotated to top
                        first_name_base_x=Generation2Constants.POSITION_1_FIRST_NAME_BASE_X,
                        first_name_base_y=Generation2Constants.POSITION_1_FIRST_NAME_BASE_Y,
                        first_name_offset_x=validated_settings.get(
                            "mother_translate_x", 0
                        ),
                        first_name_offset_y=validated_settings.get(
                            "mother_translate_y", 0
                        ),
                        first_name_rotation=0,
                        # Middle name: same base (1750,1750), rotated 180° → appears at (200,200)
                        middle_name_base_x=Generation2Constants.POSITION_1_MIDDLE_NAME_BASE_X,
                        middle_name_base_y=Generation2Constants.POSITION_1_MIDDLE_NAME_BASE_Y,
                        middle_name_offset_x=validated_settings.get(
                            "mother_translate_x", 0
                        ),
                        middle_name_offset_y=validated_settings.get(
                            "mother_translate_y", 0
                        ),
                        middle_name_rotation=Generation2Constants.POSITION_1_MIDDLE_NAME_ROTATION,  # -45° + 180° = 135°
                        # Last name: same base position, will be rotated to left
                        last_name_base_x=Generation2Constants.POSITION_1_LAST_NAME_BASE_X,
                        last_name_base_y=Generation2Constants.POSITION_1_LAST_NAME_BASE_Y,
                        last_name_offset_x=validated_settings.get(
                            "mother_translate_x", 0
                        ),
                        last_name_offset_y=validated_settings.get(
                            "mother_translate_y", 0
                        ),
                        last_name_rotation=-90,  # Vertical text (becomes +90° after 180° flip)
                        # Birth date: same position as first name, moved up 150px
                        birth_date_base_x=Generation2Constants.POSITION_1_FIRST_NAME_BASE_X,
                        birth_date_base_y=Generation2Constants.POSITION_1_FIRST_NAME_BASE_Y,
                        birth_date_offset_x=validated_settings.get(
                            "mother_translate_x", 0
                        ),
                        birth_date_offset_y=-150,
                        birth_date_rotation=0,
                        # Death date: same position as last name, moved left 150px
                        death_date_base_x=Generation2Constants.POSITION_1_LAST_NAME_BASE_X,
                        death_date_base_y=Generation2Constants.POSITION_1_LAST_NAME_BASE_Y,
                        death_date_offset_x=-150,
                        death_date_offset_y=validated_settings.get(
                            "mother_translate_y", 0
                        ),
                        death_date_rotation=-90,
                        birth_place_offset_x=validated_settings.get(
                            "mother_birth_place_translate_x", 0
                        ),
                        birth_place_offset_y=validated_settings.get(
                            "mother_birth_place_translate_y", 0
                        ),
                        birth_place_rotation=validated_settings.get(
                            "mother_birth_place_rotate", 0
                        ),
                        death_place_base_x=Generation2Constants.POSITION_1_DEATH_PLACE_BASE_X,
                        death_place_base_y=Generation2Constants.POSITION_1_DEATH_PLACE_BASE_Y,
                        death_place_offset_x=validated_settings.get(
                            "mother_death_place_translate_x", 0
                        ),
                        death_place_offset_y=validated_settings.get(
                            "mother_death_place_translate_y", 0
                        ),
                        death_place_rotation=validated_settings.get(
                            "mother_death_place_rotate", -90
                        ),
                        use_display_text=False,
                        use_gravity_center=False,
                    )

                draw.pop()
                draw(content_img)

            # Generate 1gen overlay and composite at 50% scale in center
            gen1_img_buffer = generate_prototype_1gen_preview(
                primary_individual, family_data, "preview", user_settings
            )
            _composite_overlay(content_img, gen1_img_buffer, validated_settings)

            if template == "preview":
                return create_preview_buffer(content_img)
            elif template == "final":
                return _create_prototype_final_pdf(content_img, validated_settings)
            else:
                raise GenerationError(f"Unknown template type: {template}")

    except (GenerationError, BufferError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prototype 2gen generation: {e}")
        raise GenerationError(f"Prototype 2-gen chart generation failed: {e}")


def _create_prototype_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_2GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation2Constants.RESOLUTION
    ) as base_img:
        base_img.composite(
            content_img,
            left=Generation2Constants.COMPOSITE_X,
            top=Generation2Constants.COMPOSITE_Y,
        )
        return create_pdf_buffer(base_img)


def test_prototype_2gen():
    """Test the prototype generator."""

    # Primary individual
    person = PersonData(
        id="I1",
        full_name="John Michael Smith",
        given_name="John",
        surname="Smith",
        birth_date="1970-05-15",
        birth_place="New York, NY",
        death_date="2020-01-01",
        death_place="Boston, MA",
    )

    # Father
    father = PersonData(
        id="I2",
        full_name="Robert James Smith",
        given_name="Robert",
        surname="Smith",
        birth_date="1945-03-10",
        birth_place="Chicago, IL",
        death_date="2010-08-20",
        death_place="Boston, MA",
    )

    # Mother
    mother = PersonData(
        id="I3",
        full_name="Mary Elizabeth Johnson",
        given_name="Mary",
        surname="Johnson",
        birth_date="1948-07-22",
        birth_place="Boston, MA",
        death_date="2015-12-01",
        death_place="New York, NY",
    )

    family_data = {
        "individuals": {
            "I2": father,
            "I3": mother,
        }
    }

    # Link parents to child
    person.father = "I2"
    person.mother = "I3"

    print(f"Testing prototype 2gen for: {person.full_name}")

    result = generate_prototype_2gen_preview(person, family_data, "preview")

    print(f"Generated {result.getbuffer().nbytes} bytes")
    print("Output via buffer")

    return result


if __name__ == "__main__":
    test_prototype_2gen()
