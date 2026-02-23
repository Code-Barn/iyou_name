"""
Prototype 4-generation chart generator using modular individual printer.

Position System:
- Position 0: Primary individual (in 1gen overlay at center, reduced scale)
- Position 1, 2: Parents (father/mother at 0°/180°)
- Position A, B, C, D: Grandparents at 0°, 90°, 180°, 270°
- Position A1, A2, B1, B2, C1, C2, D1, D2: Great-grandparents at 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°
  - A1 (Paternal grandfather's father): rotation=0
  - A2 (Paternal grandfather's mother): rotation=45
  - B1 (Paternal grandmother's father): rotation=270
  - B2 (Paternal grandmother's mother): rotation=315
  - C1 (Maternal grandfather's father): rotation=180
  - C2 (Maternal grandfather's mother): rotation=225
  - D1 (Maternal grandmother's father): rotation=90
  - D2 (Maternal grandmother's mother): rotation=135
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
    get_chart_buffer,
)
from apps.generator.utils.name_utils import parse_name_parts_with_settings

logger = logging.getLogger(__name__)


class Generation4Constants:
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975

    POSITION_A1_FIRST_NAME_BASE_X = 560
    POSITION_A1_FIRST_NAME_BASE_Y = 1834
    POSITION_A1_BIRTH_DATE_BASE_X = 613
    POSITION_A1_BIRTH_DATE_BASE_Y = 1725
    POSITION_A1_BIRTH_PLACE_BASE_X = 518
    POSITION_A1_BIRTH_PLACE_BASE_Y = 1888

    POSITION_A2_FIRST_NAME_BASE_X = 1390
    POSITION_A2_FIRST_NAME_BASE_Y = 1834
    POSITION_A2_BIRTH_DATE_BASE_X = 1337
    POSITION_A2_BIRTH_DATE_BASE_Y = 1725
    POSITION_A2_BIRTH_PLACE_BASE_X = 1432
    POSITION_A2_BIRTH_PLACE_BASE_Y = 1888

    GREAT_GRANDPARENT_NAME_FONT_SIZE = 18
    GREAT_GRANDPARENT_DATE_INFO_FONT_SIZE = 12
    GREAT_GRANDPARENT_PLACE_INFO_FONT_SIZE = 10

    OVERLAY_SCALE = 0.7143
    COMPOSITE_X = 300
    COMPOSITE_Y = 570
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72


GENERATION_4_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    "great_grandparent_stroke_color": (Color, "black"),
    "great_grandparent_font_color": (Color, "black"),
    "great_grandparent_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "overlay_scale": (float, 0.7143),
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
    # Date format settings
    "date_format": (str, "da_mon_year"),
    # Place name formatting settings
    "place_use_country_abbrev": (bool, True),
    "place_use_state_abbrev": (bool, True),
    "place_show_county": (bool, False),
    "place_show_country": (bool, True),
    "place_hide_usa_with_state": (bool, True),
    "place_show_township": (bool, False),
    "place_show_flag": (bool, True),
    "place_flag_type": (str, "birth"),
    "place_flag_format": (str, "png"),
    "place_flag_size": (int, 48),
    "flag_font": (str, "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf"),
    # Name formatting settings
    "name_use_first_middle_only": (bool, True),
    "name_hide_hyphenated_surname": (bool, True),
}


def _composite_overlay(content_img, gen3_img_buffer, validated_settings):
    """Composite the 3gen overlay at 45% scale in center."""
    try:
        gen3_img_buffer.seek(0)
        gen3_bytes = gen3_img_buffer.getvalue()

        if not gen3_bytes:
            raise BufferError("3gen overlay buffer is empty")

        overlay_scale = validated_settings.get(
            "overlay_scale", Generation4Constants.OVERLAY_SCALE
        )

        with Image(blob=gen3_bytes) as gen3_overlay:
            overlay_size = int(gen3_overlay.width * overlay_scale)
            gen3_overlay.resize(overlay_size, overlay_size)

            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            content_img.composite(gen3_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 3gen overlay at ({overlay_x}, {overlay_y}) scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


def generate_prototype_4gen_preview(
    primary_individual, family_data=None, template="preview", user_settings=None
):
    """
    Generate 4-gen chart using modular printer.

    Positions (8 great-grandparents at 45° intervals):
    - A1: Paternal grandfather's father (rotation=0)
    - A2: Paternal grandfather's mother (rotation=45)
    - B1: Paternal grandmother's father (rotation=270)
    - B2: Paternal grandmother's mother (rotation=315)
    - C1: Maternal grandfather's father (rotation=180)
    - C2: Maternal grandfather's mother (rotation=225)
    - D1: Maternal grandmother's father (rotation=90)
    - D2: Maternal grandmother's mother (rotation=135)
    """
    user_settings = user_settings or {}
    validated_settings = get_validated_settings(
        user_settings, GENERATION_4_SETTINGS_SCHEMA, "4gen"
    )

    logger.info(f"Generating prototype 4gen for: {primary_individual.full_name}")

    try:
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "4GEN_PREVIEW.png",
        )

        if not os.path.exists(template_path):
            logger.warning(f"4gen preview template not found, using 3gen template")
            template_path = os.path.join(
                settings.BASE_DIR,
                "apps/hud/static/hud/images/preview_image_templates",
                "3GEN_PREVIEW.png",
            )

        with Image(
            filename=template_path, resolution=Generation4Constants.RESOLUTION
        ) as content_img:
            with Drawing() as draw:
                draw.push()

                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings.get(
                    "great_grandparent_stroke_width", 0.5
                )
                draw.stroke_color = validated_settings.get(
                    "great_grandparent_stroke_color", Color("black")
                )

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

                great_grandparents = []

                if paternal_grandfather:
                    pg_father_id = getattr(paternal_grandfather, "father", None)
                    pg_mother_id = getattr(paternal_grandfather, "mother", None)
                    if pg_father_id:
                        great_grandparents.append(
                            (
                                individuals.get(pg_father_id),
                                Generation4Constants.POSITION_A1_FIRST_NAME_BASE_X,
                                Generation4Constants.POSITION_A1_FIRST_NAME_BASE_Y,
                                Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_X,
                                Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_Y,
                                Generation4Constants.POSITION_A1_BIRTH_PLACE_BASE_X,
                                Generation4Constants.POSITION_A1_BIRTH_PLACE_BASE_Y,
                                0,
                            )
                        )
                    if pg_mother_id:
                        great_grandparents.append(
                            (
                                individuals.get(pg_mother_id),
                                Generation4Constants.POSITION_A2_FIRST_NAME_BASE_X,
                                Generation4Constants.POSITION_A2_FIRST_NAME_BASE_Y,
                                Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_X,
                                Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_Y,
                                Generation4Constants.POSITION_A2_BIRTH_PLACE_BASE_X,
                                Generation4Constants.POSITION_A2_BIRTH_PLACE_BASE_Y,
                                0,
                            )
                        )

                if paternal_grandmother:
                    pmg_father_id = getattr(paternal_grandmother, "father", None)
                    pmg_mother_id = getattr(paternal_grandmother, "mother", None)
                    if pmg_father_id:
                        great_grandparents.append(
                            (
                                individuals.get(pmg_father_id),
                                Generation4Constants.POSITION_A1_FIRST_NAME_BASE_X,
                                Generation4Constants.POSITION_A1_FIRST_NAME_BASE_Y,
                                Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_X,
                                Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_Y,
                                Generation4Constants.POSITION_A1_BIRTH_PLACE_BASE_X,
                                Generation4Constants.POSITION_A1_BIRTH_PLACE_BASE_Y,
                                270,
                            )
                        )
                    if pmg_mother_id:
                        great_grandparents.append(
                            (
                                individuals.get(pmg_mother_id),
                                Generation4Constants.POSITION_A2_FIRST_NAME_BASE_X,
                                Generation4Constants.POSITION_A2_FIRST_NAME_BASE_Y,
                                Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_X,
                                Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_Y,
                                Generation4Constants.POSITION_A2_BIRTH_PLACE_BASE_X,
                                Generation4Constants.POSITION_A2_BIRTH_PLACE_BASE_Y,
                                270,
                            )
                        )

                if maternal_grandfather:
                    mg_father_id = getattr(maternal_grandfather, "father", None)
                    mg_mother_id = getattr(maternal_grandfather, "mother", None)
                    if mg_father_id:
                        great_grandparents.append(
                            (
                                individuals.get(mg_father_id),
                                Generation4Constants.POSITION_A1_FIRST_NAME_BASE_X,
                                Generation4Constants.POSITION_A1_FIRST_NAME_BASE_Y,
                                Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_X,
                                Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_Y,
                                Generation4Constants.POSITION_A1_BIRTH_PLACE_BASE_X,
                                Generation4Constants.POSITION_A1_BIRTH_PLACE_BASE_Y,
                                180,
                            )
                        )
                    if mg_mother_id:
                        great_grandparents.append(
                            (
                                individuals.get(mg_mother_id),
                                Generation4Constants.POSITION_A2_FIRST_NAME_BASE_X,
                                Generation4Constants.POSITION_A2_FIRST_NAME_BASE_Y,
                                Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_X,
                                Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_Y,
                                Generation4Constants.POSITION_A2_BIRTH_PLACE_BASE_X,
                                Generation4Constants.POSITION_A2_BIRTH_PLACE_BASE_Y,
                                180,
                            )
                        )

                if maternal_grandmother:
                    mmg_father_id = getattr(maternal_grandmother, "father", None)
                    mmg_mother_id = getattr(maternal_grandmother, "mother", None)
                    if mmg_father_id:
                        great_grandparents.append(
                            (
                                individuals.get(mmg_father_id),
                                Generation4Constants.POSITION_A1_FIRST_NAME_BASE_X,
                                Generation4Constants.POSITION_A1_FIRST_NAME_BASE_Y,
                                Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_X,
                                Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_Y,
                                Generation4Constants.POSITION_A1_BIRTH_PLACE_BASE_X,
                                Generation4Constants.POSITION_A1_BIRTH_PLACE_BASE_Y,
                                90,
                            )
                        )
                    if mmg_mother_id:
                        great_grandparents.append(
                            (
                                individuals.get(mmg_mother_id),
                                Generation4Constants.POSITION_A2_FIRST_NAME_BASE_X,
                                Generation4Constants.POSITION_A2_FIRST_NAME_BASE_Y,
                                Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_X,
                                Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_Y,
                                Generation4Constants.POSITION_A2_BIRTH_PLACE_BASE_X,
                                Generation4Constants.POSITION_A2_BIRTH_PLACE_BASE_Y,
                                90,
                            )
                        )

                base_params = dict(
                    center_x=Generation4Constants.IMAGE_CENTER_X,
                    center_y=Generation4Constants.IMAGE_CENTER_Y,
                    name_font_size=Generation4Constants.GREAT_GRANDPARENT_NAME_FONT_SIZE,
                    date_font_size=Generation4Constants.GREAT_GRANDPARENT_DATE_INFO_FONT_SIZE,
                    place_font_size=Generation4Constants.GREAT_GRANDPARENT_PLACE_INFO_FONT_SIZE,
                    birth_date_offset_x=0,
                    birth_date_offset_y=0,
                    birth_date_rotation=0,
                    birth_date_paired_offset_x=-200,
                    death_date_paired_offset_x=200,
                    paired_dates_base_y=1725,
                    paired_places_base_y=1925,
                    birth_place_paired_offset_x=-200,
                    death_place_paired_offset_x=200,
                    use_display_text=False,
                    use_gravity_center=False,
                )

                for (
                    individual,
                    base_x,
                    base_y,
                    birth_date_center_x,
                    birth_date_center_y,
                    birth_place_center_x,
                    birth_place_center_y,
                    subclade_rotation,
                ) in great_grandparents:
                    if individual:
                        name_settings = {
                            "name_use_first_middle_only": validated_settings.get(
                                "name_use_first_middle_only", True
                            ),
                            "name_hide_hyphenated_surname": validated_settings.get(
                                "name_hide_hyphenated_surname", True
                            ),
                        }
                        first, middle, last = parse_name_parts_with_settings(
                            individual.full_name, name_settings
                        )
                        formatted_name = " ".join(
                            [p for p in [first, middle, last] if p]
                        )

                        print_individual(
                            draw=draw,
                            content_img=content_img,
                            individual=individual,
                            settings=validated_settings,
                            rotation=subclade_rotation,
                            full_name=formatted_name,
                            first_name_base_x=base_x,
                            first_name_base_y=base_y,
                            birth_date_base_x=birth_date_center_x,
                            birth_date_base_y=birth_date_center_y,
                            birth_place_base_x=birth_place_center_x,
                            birth_place_base_y=birth_place_center_y,
                            death_date_base_x=birth_date_center_x,
                            death_date_base_y=birth_date_center_y,
                            death_place_base_x=birth_place_center_x,
                            death_place_base_y=birth_place_center_y,
                            **base_params,
                            chart_settings=validated_settings,
                        )

                draw.pop()
                draw(content_img)

            # Generate 3gen overlay using BUFFER MANAGER (not direct call)
            logger.info("[4gen] Getting 3gen overlay from buffer manager")
            gen3_img_buffer = get_chart_buffer(
                primary_individual, family_data, user_settings, generation=3
            )
            if not gen3_img_buffer:
                raise GenerationError("Failed to get 3gen overlay buffer")
            logger.info("[4gen] Got 3gen overlay buffer successfully")

            _composite_overlay(content_img, gen3_img_buffer, validated_settings)

            if template == "preview":
                return create_preview_buffer(content_img)
            elif template == "final":
                return _create_prototype_final_pdf(content_img, validated_settings)
            else:
                raise GenerationError(f"Unknown template type: {template}")

    except (GenerationError, BufferError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prototype 4gen generation: {e}")
        raise GenerationError(f"Prototype 4-gen chart generation failed: {e}")


def _create_prototype_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_4GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation4Constants.RESOLUTION
    ) as base_img:
        base_img.composite(
            content_img,
            left=Generation4Constants.COMPOSITE_X,
            top=Generation4Constants.COMPOSITE_Y,
        )
        return create_pdf_buffer(base_img)


def test_prototype_4gen():
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

    great_grandfather_1 = PersonData(
        id="I8",
        full_name="James William Smith Sr",
        given_name="James",
        surname="Smith",
        birth_date="1900-05-10",
        birth_place="Boston, MA",
        death_date="1980-12-25",
        death_place="Philadelphia, PA",
    )

    great_grandmother_1 = PersonData(
        id="I9",
        full_name="Rose Mary O'Brien",
        given_name="Rose",
        surname="O'Brien",
        birth_date="1902-03-15",
        birth_place="New York, NY",
        death_date="1975-08-30",
        death_place="Boston, MA",
    )

    great_grandfather_2 = PersonData(
        id="I10",
        full_name="Robert John Williams",
        given_name="Robert",
        surname="Williams",
        birth_date="1901-07-20",
        birth_place="Chicago, IL",
        death_date="1978-04-15",
        death_place="Detroit, MI",
    )

    great_grandmother_2 = PersonData(
        id="I11",
        full_name="Margaret Anne White",
        given_name="Margaret",
        surname="White",
        birth_date="1903-11-25",
        birth_place="Philadelphia, PA",
        death_date="1982-09-10",
        death_place="Chicago, IL",
    )

    great_grandfather_3 = PersonData(
        id="I12",
        full_name="Charles Edward Brown",
        given_name="Charles",
        surname="Brown",
        birth_date="1898-02-14",
        birth_place="Boston, MA",
        death_date="1970-06-22",
        death_place="Brooklyn, NY",
    )

    great_grandmother_3 = PersonData(
        id="I13",
        full_name="Elizabeth Grace Davis",
        given_name="Elizabeth",
        surname="Davis",
        birth_date="1900-09-05",
        birth_place="Queens, NY",
        death_date="1968-12-30",
        death_place="Boston, MA",
    )

    great_grandfather_4 = PersonData(
        id="I14",
        full_name="George Thomas Miller",
        given_name="George",
        surname="Miller",
        birth_date="1895-04-18",
        birth_place="Chicago, IL",
        death_date="1965-03-12",
        death_place="New York, NY",
    )

    great_grandmother_4 = PersonData(
        id="I15",
        full_name="Catherine Marie Wilson",
        given_name="Catherine",
        surname="Wilson",
        birth_date="1897-12-08",
        birth_place="Philadelphia, PA",
        death_date="1972-07-25",
        death_place="Boston, MA",
    )

    family_data = {
        "individuals": {
            "I2": father,
            "I3": mother,
            "I4": paternal_grandfather,
            "I5": paternal_grandmother,
            "I6": maternal_grandmother,
            "I7": maternal_grandfather,
            "I8": great_grandfather_1,
            "I9": great_grandmother_1,
            "I10": great_grandfather_2,
            "I11": great_grandmother_2,
            "I12": great_grandfather_3,
            "I13": great_grandmother_3,
            "I14": great_grandfather_4,
            "I15": great_grandmother_4,
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

    paternal_grandfather.father = "I8"
    paternal_grandfather.mother = "I9"
    paternal_grandmother.father = "I10"
    paternal_grandmother.mother = "I11"
    maternal_grandfather.father = "I12"
    maternal_grandfather.mother = "I13"
    maternal_grandmother.father = "I14"
    maternal_grandmother.mother = "I15"

    print(f"Testing prototype 4gen for: {person.full_name}")

    result = generate_prototype_4gen_preview(person, family_data, "preview")

    print(f"Generated {result.getbuffer().nbytes} bytes")
    print("Output via buffer")

    return result


if __name__ == "__main__":
    test_prototype_4gen()
