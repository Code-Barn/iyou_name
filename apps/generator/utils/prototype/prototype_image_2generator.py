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
    _render_flag_overlay,
)
from apps.generator.utils.settings_validator import (
    get_validated_settings,
    GenerationError,
)
from apps.generator.utils.simple_buffer_manager import (
    create_preview_buffer,
    create_pdf_buffer,
    BufferError,
    get_chart_buffer,
)

logger = logging.getLogger(__name__)


class Generation2Constants:
    # Image center - rotation point for positions
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975

    # Position 1 (Base position - use for ALL positions, rotation handles placement)
    # First name: centered at bottom
    POSITION_1_FIRST_NAME_BASE_Y = 1759

    # Middle name: at (1650, 1650), -45° angle
    POSITION_1_MIDDLE_NAME_BASE_X = 1625
    POSITION_1_MIDDLE_NAME_BASE_Y = 1625
    POSITION_1_MIDDLE_NAME_ROTATION = -45

    # Last name: centered on right
    POSITION_1_LAST_NAME_BASE_X = 1759
    POSITION_1_LAST_NAME_BASE_Y = 975

    # Birth/Death info positions - single base, rotation handles placement
    POSITION_1_BIRTH_DATE_BASE_Y = 1565

    POSITION_1_BIRTH_PLACE_BASE_Y = 1890

    POSITION_1_DEATH_DATE_BASE_X = 1565
    POSITION_1_DEATH_DATE_BASE_Y = 975

    POSITION_1_DEATH_PLACE_BASE_X = 1890
    POSITION_1_DEATH_PLACE_BASE_Y = 975

    PARENT_NAME_FONT_SIZE = 44
    PARENT_DATE_INFO_FONT_SIZE = 28
    PARENT_PLACE_INFO_FONT_SIZE = 24

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
    "father_font_size": (int, 44),
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
    "mother_font_size": (int, 44),
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
    # Date format settings
    "date_format": (str, "da_mon_year"),
    "date_year_only": (bool, True),
    # Place name formatting settings
    "place_use_country_abbrev": (bool, True),
    "place_use_state_abbrev": (bool, True),
    "place_show_county": (bool, False),
    "place_show_country": (bool, True),
    "place_hide_usa_with_state": (bool, True),
    "place_show_township": (bool, True),
    "place_show_flag": (bool, True),
    "place_flag_type": (str, "birth"),
    "place_flag_format": (str, "png"),
    "gen2_flag_size": (int, 333),  # Generation-specific flag size
    "place_flag_layer": (str, "bottom"),
    "place_flag_in_overlay": (bool, False),
    "flag_font": (str, "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf"),
    # Name formatting settings
    "name_use_first_middle_only": (bool, True),
    "name_hide_hyphenated_surname": (bool, True),
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
    logger.info(
        f"[2gen DEBUG] Received user_settings keys: {list(user_settings.keys())}"
    )
    logger.info(
        f"[2gen DEBUG] primary_background_color in user_settings: {user_settings.get('primary_background_color', 'NOT FOUND')}"
    )

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

                positions = [
                    (father, 0, "father_translate_x", "father_translate_y"),
                    (mother, 180, "mother_translate_x", "mother_translate_y"),
                ]

                base_params = dict(
                    center_x=Generation2Constants.IMAGE_CENTER_X,
                    center_y=Generation2Constants.IMAGE_CENTER_Y,
                    date_font_size=Generation2Constants.PARENT_DATE_INFO_FONT_SIZE,
                    place_font_size=Generation2Constants.PARENT_PLACE_INFO_FONT_SIZE,
                    # Name positions
                    first_name_base_x=None,
                    first_name_base_y=Generation2Constants.POSITION_1_FIRST_NAME_BASE_Y,
                    first_name_rotation=0,
                    middle_name_base_x=Generation2Constants.POSITION_1_MIDDLE_NAME_BASE_X,
                    middle_name_base_y=Generation2Constants.POSITION_1_MIDDLE_NAME_BASE_Y,
                    middle_name_rotation=Generation2Constants.POSITION_1_MIDDLE_NAME_ROTATION,
                    # Last name - rotated -90° for vertical text at specified position
                    last_name_base_x=Generation2Constants.POSITION_1_LAST_NAME_BASE_X,
                    last_name_base_y=Generation2Constants.POSITION_1_LAST_NAME_BASE_Y,
                    last_name_rotation=-90,
                    # Birth date - auto-centered at center_x
                    birth_date_base_x=None,
                    birth_date_base_y=Generation2Constants.POSITION_1_BIRTH_DATE_BASE_Y,
                    birth_date_offset_y=0,
                    birth_date_rotation=0,
                    # Death date - rotated -90° at specified position
                    death_date_base_x=Generation2Constants.POSITION_1_DEATH_DATE_BASE_X,
                    death_date_base_y=Generation2Constants.POSITION_1_DEATH_DATE_BASE_Y,
                    death_date_offset_x=0,
                    death_date_rotation=-90,
                    # Birth place - auto-centered at center_x
                    birth_place_base_x=None,
                    birth_place_base_y=Generation2Constants.POSITION_1_BIRTH_PLACE_BASE_Y,
                    # Death place - rotated -90° at specified position
                    death_place_base_x=Generation2Constants.POSITION_1_DEATH_PLACE_BASE_X,
                    death_place_base_y=Generation2Constants.POSITION_1_DEATH_PLACE_BASE_Y,
                    death_place_rotation=-90,
                    use_display_text=False,
                    use_gravity_center=False,
                )

                for idx, (
                    individual,
                    rotation,
                    translate_x_key,
                    translate_y_key,
                ) in enumerate(positions):
                    if individual:
                        translate_x = validated_settings.get(translate_x_key, 0)
                        translate_y = validated_settings.get(translate_y_key, 0)

                        print_individual(
                            draw=draw,
                            content_img=content_img,
                            individual=individual,
                            settings=validated_settings,
                            chart_settings=validated_settings,
                            rotation=rotation,
                            name_font_size=validated_settings.get(
                                f"{'father' if rotation == 0 else 'mother'}_font_size",
                                Generation2Constants.PARENT_NAME_FONT_SIZE,
                            ),
                            first_name_offset_x=translate_x,
                            first_name_offset_y=translate_y,
                            middle_name_offset_x=translate_x,
                            middle_name_offset_y=translate_y,
                            last_name_offset_x=translate_x,
                            last_name_offset_y=translate_y,
                            birth_date_offset_x=translate_x,
                            death_date_offset_y=translate_y,
                            flag_base_x=760,
                            flag_base_y=760,
                            flag_rotation=-45,
                            flag_size=validated_settings.get("gen2_flag_size", 333),
                            **base_params,
                        )

                draw.pop()
                draw(content_img)

            # Generate 1gen overlay using BUFFER MANAGER (not direct call)
            # This uses the cached 1gen buffer if settings match, or regenerates if needed
            # IMPORTANT: Don't pass place_flag_size to 1gen - each generation uses its own genX_flag_size
            # This ensures 1gen overlay renders with 1gen's flag size (666), then gets scaled to 50%
            gen1_settings = {k: v for k, v in user_settings.items()}
            logger.info("[2gen] Getting 1gen overlay from buffer manager")
            gen1_img_buffer = get_chart_buffer(
                primary_individual, family_data, gen1_settings, generation=1
            )
            if not gen1_img_buffer:
                raise GenerationError("Failed to get 1gen overlay buffer")
            logger.info("[2gen] Got 1gen overlay buffer successfully")

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
    import math

    person = PersonData(
        id="I1",
        full_name="John Michael Smith",
        given_name="John",
        surname="Smith",
        birth_date="1970-05-15",
        birth_place="Chicago, Illinois, USA",
        death_date="2020-01-01",
        death_place="Chicago, Illinois, USA",
    )

    father = PersonData(
        id="I2",
        full_name="Robert James Smith",
        given_name="Robert",
        surname="Smith",
        birth_date="1945-03-20",
        birth_place="New York, New York, USA",
        death_date="2010-08-15",
        death_place="New York, New York, USA",
    )

    mother = PersonData(
        id="I3",
        full_name="Mary Elizabeth Johnson",
        given_name="Mary",
        surname="Johnson",
        birth_date="1948-07-25",
        birth_place="Los Angeles, California, USA",
        death_date="2015-12-01",
        death_place="Los Angeles, California, USA",
    )

    family_data = {
        "individuals": {
            "I1": person,
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


def debug_2gen_flag_positions():
    """Debug test to show expected vs actual flag positions."""
    import math
    from wand.drawing import Drawing
    from wand.image import Image
    from django.conf import settings as django_settings
    import os

    # Constants
    CENTER_X = 975
    CENTER_Y = 975
    FLAG_OFFSET_X = 679
    FLAG_OFFSET_Y = 679
    FLAG_SIZE = 200

    print("=" * 60)
    print("2GEN FLAG POSITION DEBUG")
    print("=" * 60)
    print(f"Center: ({CENTER_X}, {CENTER_Y})")
    print(f"Flag offset (master position): ({FLAG_OFFSET_X}, {FLAG_OFFSET_Y})")
    print()

    # Calculate expected positions for each rotation
    rotations = [0, 180]
    for rotation in rotations:
        angle_rad = math.radians(rotation)
        rotated_x = FLAG_OFFSET_X * math.cos(angle_rad) - FLAG_OFFSET_Y * math.sin(
            angle_rad
        )
        rotated_y = FLAG_OFFSET_X * math.sin(angle_rad) + FLAG_OFFSET_Y * math.cos(
            angle_rad
        )

        final_x = CENTER_X + rotated_x
        final_y = CENTER_Y + rotated_y

        # Expected if we just rotate the offset
        print(f"Rotation {rotation}:")
        print(f"  Rotated offset: ({rotated_x:.1f}, {rotated_y:.1f})")
        print(f"  Final position: ({final_x:.1f}, {final_y:.1f})")
        print()

        # Calculate distance from center
        dist_from_center = math.sqrt(
            (final_x - CENTER_X) ** 2 + (final_y - CENTER_Y) ** 2
        )
        print(f"  Distance from center: {dist_from_center:.1f}px")
        print()

    # Now test what print_individual does
    print("=" * 60)
    print("Simulating print_individual flag positioning:")
    print("=" * 60)

    # Simulate what happens in print_individual
    # With flag_base_x=609, flag_base_y=609, center=975,975
    flag_base_x = 609
    flag_base_y = 609

    dx = flag_base_x  # 609
    dy = flag_base_y  # 609

    for rotation in [0, 180]:
        angle_rad = math.radians(rotation)
        rotated_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        rotated_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)

        base_x = CENTER_X + rotated_x
        base_y = CENTER_Y + rotated_y

        # After rotation, flag_rotation = -45 + rotation
        final_flag_rotation = -45 + rotation

        print(f"\nRotation {rotation}:")
        print(f"  Position after rotation: ({base_x:.1f}, {base_y:.1f})")
        print(f"  Flag rotation: {final_flag_rotation} degrees")

        # Simulate what ImageMagick does when rotating
        # After rotate, dimensions change
        print(f"  Note: After {final_flag_rotation}° rotation, image dimensions change")
        print(f"  Centering on ({base_x}, {base_y}) using POST-rotation dimensions")


if __name__ == "__main__":
    debug_2gen_flag_positions()
