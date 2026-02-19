"""
Prototype 3-generation chart generator using modular individual printer.

Position System:
- Position 0: Primary individual (in 1gen overlay at center, reduced scale)
- Position 1, 2: Parents (father/mother at 0°/180°)
- Position A, B, C, D: Grandparents at 0°, 90°, 180°, 270°
  - Position A: rotation=0 (same as Position 1)
  - Position B: rotation=90
  - Position C: rotation=180 (same as Position 2)
  - Position D: rotation=270
"""

import logging
import os

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.parser.models import PersonData
from apps.generator.utils.prototype.individual_printer import print_individual
from apps.generator.utils.prototype.prototype_image_2generator import (
    generate_prototype_2gen_preview,
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


class Generation3Constants:
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975

    POSITION_A_FIRST_NAME_BASE_X = 975
    POSITION_A_FIRST_NAME_BASE_Y = 1800
    POSITION_A_MIDDLE_NAME_BASE_X = 1650
    POSITION_A_MIDDLE_NAME_BASE_Y = 1650
    POSITION_A_MIDDLE_NAME_ROTATION = -45
    POSITION_A_LAST_NAME_BASE_X = 1725
    POSITION_A_LAST_NAME_BASE_Y = 975

    GRANDPARENT_NAME_FONT_SIZE = 30
    GRANDPARENT_DATE_INFO_FONT_SIZE = 20
    GRANDPARENT_PLACE_INFO_FONT_SIZE = 16

    OVERLAY_SCALE = 0.60
    COMPOSITE_X = 300
    COMPOSITE_Y = 570
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72


GENERATION_3_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    "grandparent_stroke_color": (Color, "black"),
    "grandparent_font_color": (Color, "black"),
    "grandparent_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "paternal_grandfather_font_size": (int, 36),
    "paternal_grandfather_translate_x": (int, 0),
    "paternal_grandfather_translate_y": (int, 0),
    "paternal_grandmother_font_size": (int, 36),
    "paternal_grandmother_translate_x": (int, 0),
    "paternal_grandmother_translate_y": (int, 0),
    "maternal_grandmother_font_size": (int, 36),
    "maternal_grandmother_translate_x": (int, 0),
    "maternal_grandmother_translate_y": (int, 0),
    "maternal_grandfather_font_size": (int, 36),
    "maternal_grandfather_translate_x": (int, 0),
    "maternal_grandfather_translate_y": (int, 0),
    "overlay_scale": (float, 0.60),
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
}


def _composite_overlay(content_img, gen2_img_buffer, validated_settings):
    """Composite the 2gen overlay at 60% scale in center."""
    try:
        gen2_img_buffer.seek(0)
        gen2_bytes = gen2_img_buffer.getvalue()

        if not gen2_bytes:
            raise BufferError("2gen overlay buffer is empty")

        overlay_scale = validated_settings.get(
            "overlay_scale", Generation3Constants.OVERLAY_SCALE
        )

        with Image(blob=gen2_bytes) as gen2_overlay:
            overlay_size = int(gen2_overlay.width * overlay_scale)
            gen2_overlay.resize(overlay_size, overlay_size)

            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            content_img.composite(gen2_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 2gen overlay at ({overlay_x}, {overlay_y}) scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


def generate_prototype_3gen_preview(
    primary_individual, family_data=None, template="preview", user_settings=None
):
    """
    Generate 3-gen chart using modular printer.

    Position A: Paternal grandfather (rotation=0)
    Position B: Paternal grandmother (rotation=90)
    Position C: Maternal grandmother (rotation=180)
    Position D: Maternal grandfather (rotation=270)
    """
    user_settings = user_settings or {}
    validated_settings = get_validated_settings(
        user_settings, GENERATION_3_SETTINGS_SCHEMA, "3gen"
    )

    logger.info(f"Generating prototype 3gen for: {primary_individual.full_name}")

    try:
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "3GEN_PREVIEW.png",
        )

        if not os.path.exists(template_path):
            raise GenerationError(f"Preview template not found: {template_path}")

        with Image(
            filename=template_path, resolution=Generation3Constants.RESOLUTION
        ) as content_img:
            with Drawing() as draw:
                draw.push()

                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings["grandparent_stroke_width"]
                draw.stroke_color = validated_settings["grandparent_stroke_color"]

                individuals = family_data.get("individuals", {}) if family_data else {}

                # Get parents by traversing father/mother relationships
                father = individuals.get(getattr(primary_individual, "father", None))
                mother = individuals.get(getattr(primary_individual, "mother", None))

                # Get grandparents by traversing from parents
                paternal_grandfather = None
                paternal_grandmother = None
                maternal_grandfather = None
                maternal_grandmother = None

                if father:
                    paternal_grandfather = individuals.get(
                        getattr(father, "father", None)
                    )
                    paternal_grandmother = individuals.get(
                        getattr(father, "mother", None)
                    )
                if mother:
                    maternal_grandfather = individuals.get(
                        getattr(mother, "father", None)
                    )
                    maternal_grandmother = individuals.get(
                        getattr(mother, "mother", None)
                    )

                positions = [
                    (paternal_grandfather, 0),
                    (maternal_grandfather, 180),
                    (paternal_grandmother, 270),
                    (maternal_grandmother, 90),
                ]

                base_params = dict(
                    center_x=Generation3Constants.IMAGE_CENTER_X,
                    center_y=Generation3Constants.IMAGE_CENTER_Y,
                    name_font_size=Generation3Constants.GRANDPARENT_NAME_FONT_SIZE,
                    date_font_size=Generation3Constants.GRANDPARENT_DATE_INFO_FONT_SIZE,
                    place_font_size=Generation3Constants.GRANDPARENT_PLACE_INFO_FONT_SIZE,
                    first_name_base_x=Generation3Constants.POSITION_A_FIRST_NAME_BASE_X,
                    first_name_base_y=Generation3Constants.POSITION_A_FIRST_NAME_BASE_Y,
                    birth_date_base_x=650,
                    birth_date_base_y=1650,
                    birth_date_offset_x=0,
                    birth_date_offset_y=0,
                    birth_date_rotation=0,
                    birth_date_paired_offset_x=0,
                    death_date_base_x=1300,
                    death_date_base_y=1650,
                    death_date_offset_x=0,
                    death_date_offset_y=0,
                    death_date_rotation=0,
                    death_date_paired_offset_x=0,
                    paired_dates_base_y=1650,
                    paired_places_base_y=1900,
                    birth_place_base_x=650,
                    birth_place_base_y=1900,
                    birth_place_paired_offset_x=0,
                    birth_place_offset_x=0,
                    birth_place_offset_y=0,
                    birth_place_rotation=0,
                    death_place_base_x=1300,
                    death_place_base_y=1900,
                    death_place_paired_offset_x=0,
                    death_place_offset_x=0,
                    death_place_offset_y=0,
                    death_place_rotation=0,
                    use_display_text=False,
                    use_gravity_center=False,
                )

                for individual, rotation in positions:
                    if individual:
                        print_individual(
                            draw=draw,
                            content_img=content_img,
                            individual=individual,
                            settings=validated_settings,
                            rotation=rotation,
                            full_name=individual.full_name,
                            **base_params,
                        )

                draw.pop()
                draw(content_img)

            gen2_img_buffer = generate_prototype_2gen_preview(
                primary_individual, family_data, "preview", user_settings
            )
            _composite_overlay(content_img, gen2_img_buffer, validated_settings)

            if template == "preview":
                return create_preview_buffer(content_img)
            elif template == "final":
                return _create_prototype_final_pdf(content_img, validated_settings)
            else:
                raise GenerationError(f"Unknown template type: {template}")

    except (GenerationError, BufferError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prototype 3gen generation: {e}")
        raise GenerationError(f"Prototype 3-gen chart generation failed: {e}")


def _create_prototype_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_3GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation3Constants.RESOLUTION
    ) as base_img:
        base_img.composite(
            content_img,
            left=Generation3Constants.COMPOSITE_X,
            top=Generation3Constants.COMPOSITE_Y,
        )
        return create_pdf_buffer(base_img)


def test_prototype_3gen():
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

    paternal_grandfather = PersonData(
        id="I4",
        full_name="William Robert Smith",
        given_name="William",
        surname="Smith",
        birth_date="1920-01-15",
        birth_place="Philadelphia, PA",
        death_date="1990-06-10",
        death_place="Chicago, IL",
    )

    paternal_grandmother = PersonData(
        id="I5",
        full_name="Helen Marie Smith",
        given_name="Helen",
        surname="Smith",
        birth_date="1923-04-20",
        birth_place="Detroit, MI",
        death_date="2000-11-25",
        death_place="Chicago, IL",
    )

    maternal_grandmother = PersonData(
        id="I6",
        full_name="Patricia Ann Johnson",
        given_name="Patricia",
        surname="Johnson",
        birth_date="1925-08-12",
        birth_place="Brooklyn, NY",
        death_date="2012-03-18",
        death_place="Boston, MA",
    )

    maternal_grandfather = PersonData(
        id="I7",
        full_name="Thomas Edward Johnson",
        given_name="Thomas",
        surname="Johnson",
        birth_date="1922-11-30",
        birth_place="Queens, NY",
        death_date="2005-09-05",
        death_place="New York, NY",
    )

    family_data = {
        "individuals": {
            "I2": father,
            "I3": mother,
            "I4": paternal_grandfather,
            "I5": paternal_grandmother,
            "I6": maternal_grandmother,
            "I7": maternal_grandfather,
        }
    }

    person.father = "I2"
    person.mother = "I3"
    father.father = "I4"
    father.mother = "I5"
    mother.father = "I7"
    mother.mother = "I6"

    person.paternal_grandfather = "I4"
    person.paternal_grandmother = "I5"
    person.maternal_grandmother = "I6"
    person.maternal_grandfather = "I7"

    print(f"Testing prototype 3gen for: {person.full_name}")

    result = generate_prototype_3gen_preview(person, family_data, "preview")

    print(f"Generated {result.getbuffer().nbytes} bytes")
    print("Output via buffer")

    return result


if __name__ == "__main__":
    test_prototype_3gen()
