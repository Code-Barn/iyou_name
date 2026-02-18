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
    BACKGROUND_LEFT = 64
    BACKGROUND_TOP = 64
    BACKGROUND_WIDTH = 1822
    BACKGROUND_HEIGHT = 1822
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
    "primary_background_color": (Color, "#FFFFFF"),
    "primary_font_color": (Color, "black"),
    "primary_stroke_color": (Color, "black"),
    "primary_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "primary_birth_color": (Color, "black"),
    "primary_birth_place_color": (Color, "black"),
    "primary_death_color": (Color, "black"),
    "primary_death_place_color": (Color, "black"),
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

    logger.info(f"Generating prototype 1gen for: {primary_individual.full_name}")

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

                draw.translate(
                    x=Generation1Constants.INITIAL_TRANSLATE_X,
                    y=Generation1Constants.INITIAL_TRANSLATE_Y,
                )

                print_individual(
                    draw=draw,
                    content_img=content_img,
                    individual=primary_individual,
                    settings=validated_settings,
                    center_x=Generation1Constants.CENTER_X,
                    center_y=Generation1Constants.CENTER_Y,
                    rotation=0,
                    name_font_size=validated_settings["primary_name_font_size"],
                    date_font_size=validated_settings["primary_date_info_font_size"],
                    place_font_size=validated_settings["primary_place_info_font_size"],
                    first_name_rotation=validated_settings["primary_name_rotate"],
                    birth_date_base_x=300,
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
                    death_date_base_y=300,
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

                draw.pop()
                draw(content_img)

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
