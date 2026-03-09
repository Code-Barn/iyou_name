"""
Prototype 1-generation chart generator using modular individual printer.

This is a test implementation to verify the individual_printer module
produces the same output as the original image_1generator.py
"""

import logging
import os

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.parser.models import PersonData
from apps.generator.utils.prototype.individual_printer import print_individual
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


class Generation1Constants:
    CANVAS_WIDTH = 1822
    CANVAS_HEIGHT = 1822
    BACKGROUND_LEFT = 0
    BACKGROUND_TOP = 0
    BACKGROUND_WIDTH = 1950
    BACKGROUND_HEIGHT = 1950
    INITIAL_TRANSLATE_X = 0
    INITIAL_TRANSLATE_Y = 0
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72

    COMPOSITE_X = 300
    COMPOSITE_Y = 570

    CENTER_X = 975
    CENTER_Y = 975


GENERATION_1_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    "primary_background_color": (Color, "#000000"),
    "primary_font_color": (Color, "white"),
    "primary_stroke_color": (Color, "white"),
    "primary_stroke_width": (float, 0.5),
    "primary_info_stroke_color": (Color, "#888888"),
    "primary_info_stroke_width": (float, 0.25),
    "primary_birth_color": (Color, "white"),
    "primary_birth_place_color": (Color, "white"),
    "primary_death_color": (Color, "white"),
    "primary_death_place_color": (Color, "white"),
    "primary_name_font_size": (int, 84),
    "primary_date_info_font_size": (int, 52),
    "primary_place_info_font_size": (int, 36),
    "primary_translate_x": (int, 0),
    "primary_translate_y": (int, 0),
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
    # Date format settings
    "date_format": (str, "da_mon_year"),
    # Place name formatting settings
    "place_use_country_abbrev": (bool, True),
    "place_use_state_abbrev": (bool, True),
    "place_hide_us_counties": (bool, True),
    "place_show_country": (bool, True),
    "place_hide_usa_with_state": (bool, True),
    "place_show_township": (bool, False),
    "place_auto_shorten": (bool, False),
    "place_abbreviate_uk_counties": (bool, False),
    "place_show_uk_flag": (bool, False),
    "place_show_flag": (bool, True),
    "place_flag_type": (str, "birth"),
    "place_flag_format": (str, "png"),
    "gen1_flag_size": (int, 666),  # Generation-specific flag size
    "place_flag_layer": (str, "bottom"),
    "place_flag_in_overlay": (bool, True),
    "flag_font": (str, "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf"),
    # Name formatting settings
    "name_use_first_middle_only": (bool, True),
    "name_hide_hyphenated_surname": (bool, True),
}


def generate_prototype_1gen_preview(
    primary_individual, family_data=None, template="preview", user_settings=None
):
    """
    Generate 1-gen chart using modular printer.

    Args:
        primary_individual: PersonData object
        family_data: Not used in 1gen
        template: 'preview' or 'final'
        user_settings: Optional settings overrides

    Returns:
        BytesIO buffer containing the image
    """
    user_settings = user_settings or {}
    validated_settings = get_validated_settings(
        user_settings, GENERATION_1_SETTINGS_SCHEMA, "1gen"
    )

    # Map 1gen-specific info stroke settings to generic names for print_individual
    # This allows 1gen to have its own info stroke settings separate from other generations
    validated_settings["info_stroke_color"] = validated_settings.get(
        "primary_info_stroke_color", Color("#888888")
    )
    validated_settings["info_stroke_width"] = validated_settings.get(
        "primary_info_stroke_width", 0.25
    )

    logger.info(f"Generating prototype 1gen for: {primary_individual.full_name}")
    logger.info(
        f"[1gen DEBUG] Received user_settings keys: {list(user_settings.keys())}"
    )
    logger.info(
        f"[1gen DEBUG] primary_background_color in user_settings: {user_settings.get('primary_background_color', 'NOT FOUND')}"
    )
    logger.info(
        f"[1gen DEBUG] validated primary_background_color: {validated_settings.get('primary_background_color')}"
    )

    try:
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "1GEN_PREVIEW.png",
        )

        if not os.path.exists(template_path):
            raise GenerationError(f"Preview template not found: {template_path}")

        with Image(
            filename=template_path, resolution=Generation1Constants.RESOLUTION
        ) as content_img:
            with Drawing() as draw:
                draw.push()

                draw.font = validated_settings["font_family"]
                draw.font_size = validated_settings["primary_name_font_size"]
                draw.stroke_antialias = True

                draw.fill_color = validated_settings["primary_background_color"]
                draw.rectangle(
                    left=Generation1Constants.BACKGROUND_LEFT,
                    top=Generation1Constants.BACKGROUND_TOP,
                    width=Generation1Constants.BACKGROUND_WIDTH,
                    height=Generation1Constants.BACKGROUND_HEIGHT,
                )

                # Apply background to image
                draw(content_img)

                # Render flag AFTER background, BEFORE text (on background)
                # Position: 1584, 1584 = offset (609, 609) from center (975, 975)
                # Flag size comes from settings (place_flag_size)
                _render_flag_overlay(
                    content_img,
                    primary_individual,
                    validated_settings,
                    flag_base_x=609,
                    flag_base_y=609,
                    flag_rotation=-45,
                    rotation=0,
                )

                # Now draw text on a new Drawing layer
                text_draw = Drawing()
                text_draw.font = validated_settings["font_family"]
                text_draw.font_size = validated_settings["primary_name_font_size"]
                text_draw.stroke_antialias = True
                text_draw.stroke_color = validated_settings["primary_stroke_color"]
                text_draw.stroke_width = validated_settings["primary_stroke_width"]
                text_draw.fill_color = validated_settings["primary_font_color"]

                text_draw.translate(
                    x=Generation1Constants.INITIAL_TRANSLATE_X,
                    y=Generation1Constants.INITIAL_TRANSLATE_Y,
                )

                print_individual(
                    draw=text_draw,
                    content_img=content_img,
                    individual=primary_individual,
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
                    birth_place_offset_x=validated_settings[
                        "primary_birth_place_translate_x"
                    ],
                    birth_place_offset_y=validated_settings[
                        "primary_birth_place_translate_y"
                    ],
                    birth_place_rotation=validated_settings[
                        "primary_birth_place_rotate"
                    ],
                    death_date_base_x=975,
                    death_date_base_y=207,
                    death_date_offset_x=validated_settings["primary_death_translate_x"],
                    death_date_offset_y=validated_settings["primary_death_translate_y"],
                    death_date_rotation=validated_settings["primary_death_rotate"],
                    death_place_base_x=1875,
                    death_place_offset_x=validated_settings[
                        "primary_death_place_translate_x"
                    ],
                    death_place_offset_y=validated_settings[
                        "primary_death_place_translate_y"
                    ],
                    death_place_rotation=validated_settings[
                        "primary_death_place_rotate"
                    ],
                    use_display_text=True,
                    use_gravity_center=True,
                )

                text_draw(content_img)

                draw.pop()

            if template == "preview":
                return create_preview_buffer(content_img)
            elif template == "final":
                return _create_prototype_final_pdf(content_img, validated_settings)
            else:
                raise GenerationError(f"Unknown template type: {template}")

    except (GenerationError, BufferError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prototype 1gen generation: {e}")
        raise GenerationError(f"Prototype 1-gen chart generation failed: {e}")


def _render_flag_overlay(
    content_img,
    individual,
    validated_settings,
    flag_base_x=None,
    flag_base_y=None,
    flag_rotation=0,
    flag_size=None,
    rotation=0,
    center_x=None,
    center_y=None,
):
    """Render flag as final overlay - composites AFTER all text drawing is complete.

    This ensures the flag appears ON TOP of all text, not behind it.
    Supports rotational translation for multi-gen charts.

    Args:
        content_img: The Wand image to composite onto
        individual: The PersonData object with birth_place/death_place
        validated_settings: Settings dictionary
        flag_base_x: X offset from center for flag (default: center_x)
        flag_base_y: Y offset from center for flag (default: center_y - 50)
        flag_rotation: Rotation of the flag itself in degrees (default: 0)
        flag_size: Size in pixels (default: from settings or 48)
        rotation: Rotational position (0, 90, 180, 270) - applies same translation as text
        center_x: Center X for rotation (default: 975)
        center_y: Center Y for rotation (default: 975)
    """
    import math
    from apps.generator.utils.prototype.place_name_utils import get_flag_image_path

    show_flag = validated_settings.get("place_show_flag", False)
    if not show_flag:
        return

    flag_type = validated_settings.get("place_flag_type", "birth")
    flag_format = validated_settings.get("place_flag_format", "png")

    if flag_format != "png":
        return

    place = ""
    if flag_type == "birth":
        place = individual.birth_place or ""
    elif flag_type == "death":
        place = individual.death_place or ""

    flag_path = get_flag_image_path(place)
    if not flag_path:
        return

    flag_full_path = os.path.join(
        settings.BASE_DIR, "apps", "charts", "static", flag_path
    )

    if not os.path.exists(flag_full_path):
        logger.warning(f"Flag image not found: {flag_full_path}")
        return

    size = (
        flag_size
        if flag_size is not None
        else validated_settings.get("gen1_flag_size", 666)
    )

    # Default center
    cx = center_x if center_x is not None else Generation1Constants.CENTER_X
    cy = center_y if center_y is not None else Generation1Constants.CENTER_Y

    # Base offset from center
    dx = flag_base_x if flag_base_x is not None else 0
    dy = flag_base_y if flag_base_y is not None else -50

    # Apply rotational translation (same as text positioning)
    # Convert rotation to radians
    angle_rad = math.radians(rotation)

    # Rotate the offset around center
    rotated_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
    rotated_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)

    # Final position
    x = int(cx + rotated_x)
    y = int(cy + rotated_y)

    # Flag's own rotation = base rotation + position rotation
    final_rotation = flag_rotation + rotation

    try:
        with Image(filename=flag_full_path) as flag_img:
            new_height = int(size * flag_img.height / flag_img.width)
            flag_img.resize(size, new_height)

            if final_rotation != 0:
                flag_img.rotate(final_rotation)

            pos_x = int(x - flag_img.width // 2)
            pos_y = int(y - flag_img.height // 2)

            content_img.composite(flag_img, pos_x, pos_y)
            logger.info(
                f"Rendered flag at ({pos_x}, {pos_y}) rotation={final_rotation}: {flag_path}"
            )
    except Exception as e:
        logger.warning(f"Failed to render flag overlay: {e}")


def _create_prototype_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_1GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation1Constants.RESOLUTION
    ) as base_img:
        base_img.composite(
            content_img,
            left=Generation1Constants.COMPOSITE_X,
            top=Generation1Constants.COMPOSITE_Y,
        )
        return create_pdf_buffer(base_img)


def test_prototype_1gen():
    """Test the prototype generator."""

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

    print(f"Testing prototype 1gen for: {person.full_name}")

    result = generate_prototype_1gen_preview(person, None, "preview")

    print(f"Generated {result.getbuffer().nbytes} bytes")
    print("Output via buffer")

    return result


if __name__ == "__main__":
    test_prototype_1gen()
