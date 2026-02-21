"""
Prototype 7-generation family tree chart generator.

This module generates 7-generation ancestor charts using the same modular
approach as the 1-6gen generators, with:
- Generation7Constants for position definitions
- print_individual for rendering
- Composited 6gen overlay in center
"""

import logging
import math
import os

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.prototype.prototype_image_5generator import (
    generate_prototype_5gen_preview,
)
from apps.generator.utils.prototype.prototype_image_6generator import (
    Generation6Constants,
    generate_prototype_6gen_preview,
)
from apps.generator.utils.prototype.individual_printer import print_individual
from apps.generator.utils.settings_validator import get_validated_settings
from apps.generator.utils.simple_buffer_manager import (
    create_preview_buffer,
    create_pdf_buffer,
)

logger = logging.getLogger(__name__)


class Generation7Constants:
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975

    # 7gen positions follow pattern with 105px spacing (half of 211)
    # Left side (A1111-A1222): 8 positions starting at x=205
    # Right side (A2111-A2222): mirrored across x=975

    # A1111 (outermost-left)
    POSITION_A1111_FIRST_NAME_BASE_X = 105
    POSITION_A1111_FIRST_NAME_BASE_Y = 1785
    POSITION_A1111_BIRTH_DATE_BASE_X = 245
    POSITION_A1111_BIRTH_DATE_BASE_Y = 1835
    POSITION_A1111_BIRTH_PLACE_BASE_X = 165
    POSITION_A1111_BIRTH_PLACE_BASE_Y = 1969

    # A1112
    POSITION_A1112_FIRST_NAME_BASE_X = 310
    POSITION_A1112_FIRST_NAME_BASE_Y = 1885
    POSITION_A1112_BIRTH_DATE_BASE_X = 350
    POSITION_A1112_BIRTH_DATE_BASE_Y = 1835
    POSITION_A1112_BIRTH_PLACE_BASE_X = 270
    POSITION_A1112_BIRTH_PLACE_BASE_Y = 1969

    # A1121
    POSITION_A1121_FIRST_NAME_BASE_X = 415
    POSITION_A1121_FIRST_NAME_BASE_Y = 1885
    POSITION_A1121_BIRTH_DATE_BASE_X = 455
    POSITION_A1121_BIRTH_DATE_BASE_Y = 1835
    POSITION_A1121_BIRTH_PLACE_BASE_X = 375
    POSITION_A1121_BIRTH_PLACE_BASE_Y = 1969

    # A1122
    POSITION_A1122_FIRST_NAME_BASE_X = 520
    POSITION_A1122_FIRST_NAME_BASE_Y = 1885
    POSITION_A1122_BIRTH_DATE_BASE_X = 560
    POSITION_A1122_BIRTH_DATE_BASE_Y = 1835
    POSITION_A1122_BIRTH_PLACE_BASE_X = 480
    POSITION_A1122_BIRTH_PLACE_BASE_Y = 1969

    # A1211
    POSITION_A1211_FIRST_NAME_BASE_X = 625
    POSITION_A1211_FIRST_NAME_BASE_Y = 1885
    POSITION_A1211_BIRTH_DATE_BASE_X = 665
    POSITION_A1211_BIRTH_DATE_BASE_Y = 1835
    POSITION_A1211_BIRTH_PLACE_BASE_X = 585
    POSITION_A1211_BIRTH_PLACE_BASE_Y = 1969

    # A1212
    POSITION_A1212_FIRST_NAME_BASE_X = 730
    POSITION_A1212_FIRST_NAME_BASE_Y = 1885
    POSITION_A1212_BIRTH_DATE_BASE_X = 770
    POSITION_A1212_BIRTH_DATE_BASE_Y = 1835
    POSITION_A1212_BIRTH_PLACE_BASE_X = 690
    POSITION_A1212_BIRTH_PLACE_BASE_Y = 1969

    # A1221
    POSITION_A1221_FIRST_NAME_BASE_X = 835
    POSITION_A1221_FIRST_NAME_BASE_Y = 1885
    POSITION_A1221_BIRTH_DATE_BASE_X = 875
    POSITION_A1221_BIRTH_DATE_BASE_Y = 1835
    POSITION_A1221_BIRTH_PLACE_BASE_X = 795
    POSITION_A1221_BIRTH_PLACE_BASE_Y = 1969

    # A1222
    POSITION_A1222_FIRST_NAME_BASE_X = 940
    POSITION_A1222_FIRST_NAME_BASE_Y = 1885
    POSITION_A1222_BIRTH_DATE_BASE_X = 980
    POSITION_A1222_BIRTH_DATE_BASE_Y = 1835
    POSITION_A1222_BIRTH_PLACE_BASE_X = 900
    POSITION_A1222_BIRTH_PLACE_BASE_Y = 1969

    # Right side - mirrored positions
    # Mirror formula: mirrored_x = 1950 - left_x

    # A2121 (mirrored from A1222)
    POSITION_A2121_FIRST_NAME_BASE_X = 1010
    POSITION_A2121_FIRST_NAME_BASE_Y = 1885
    POSITION_A2121_BIRTH_DATE_BASE_X = 970
    POSITION_A2121_BIRTH_DATE_BASE_Y = 1835
    POSITION_A2121_BIRTH_PLACE_BASE_X = 1050
    POSITION_A2121_BIRTH_PLACE_BASE_Y = 1969

    # A2122 (mirrored from A1221)
    POSITION_A2122_FIRST_NAME_BASE_X = 1115
    POSITION_A2122_FIRST_NAME_BASE_Y = 1885
    POSITION_A2122_BIRTH_DATE_BASE_X = 1075
    POSITION_A2122_BIRTH_DATE_BASE_Y = 1835
    POSITION_A2122_BIRTH_PLACE_BASE_X = 1155
    POSITION_A2122_BIRTH_PLACE_BASE_Y = 1969

    # A2111 (mirrored from A1212)
    POSITION_A2111_FIRST_NAME_BASE_X = 1220
    POSITION_A2111_FIRST_NAME_BASE_Y = 1885
    POSITION_A2111_BIRTH_DATE_BASE_X = 1180
    POSITION_A2111_BIRTH_DATE_BASE_Y = 1835
    POSITION_A2111_BIRTH_PLACE_BASE_X = 1260
    POSITION_A2111_BIRTH_PLACE_BASE_Y = 1969

    # A2112 (mirrored from A1211)
    POSITION_A2112_FIRST_NAME_BASE_X = 1325
    POSITION_A2112_FIRST_NAME_BASE_Y = 1885
    POSITION_A2112_BIRTH_DATE_BASE_X = 1285
    POSITION_A2112_BIRTH_DATE_BASE_Y = 1835
    POSITION_A2112_BIRTH_PLACE_BASE_X = 1365
    POSITION_A2112_BIRTH_PLACE_BASE_Y = 1969

    # A2211 (mirrored from A1122)
    POSITION_A2211_FIRST_NAME_BASE_X = 1430
    POSITION_A2211_FIRST_NAME_BASE_Y = 1885
    POSITION_A2211_BIRTH_DATE_BASE_X = 1390
    POSITION_A2211_BIRTH_DATE_BASE_Y = 1835
    POSITION_A2211_BIRTH_PLACE_BASE_X = 1470
    POSITION_A2211_BIRTH_PLACE_BASE_Y = 1969

    # A2212 (mirrored from A1121)
    POSITION_A2212_FIRST_NAME_BASE_X = 1535
    POSITION_A2212_FIRST_NAME_BASE_Y = 1885
    POSITION_A2212_BIRTH_DATE_BASE_X = 1495
    POSITION_A2212_BIRTH_DATE_BASE_Y = 1835
    POSITION_A2212_BIRTH_PLACE_BASE_X = 1575
    POSITION_A2212_BIRTH_PLACE_BASE_Y = 1969

    # A2221 (mirrored from A1112)
    POSITION_A2221_FIRST_NAME_BASE_X = 1640
    POSITION_A2221_FIRST_NAME_BASE_Y = 1885
    POSITION_A2221_BIRTH_DATE_BASE_X = 1600
    POSITION_A2221_BIRTH_DATE_BASE_Y = 1835
    POSITION_A2221_BIRTH_PLACE_BASE_X = 1680
    POSITION_A2221_BIRTH_PLACE_BASE_Y = 1969

    # A2222 (mirrored from A1111)
    POSITION_A2222_FIRST_NAME_BASE_X = 1745
    POSITION_A2222_FIRST_NAME_BASE_Y = 1885
    POSITION_A2222_BIRTH_DATE_BASE_X = 1705
    POSITION_A2222_BIRTH_DATE_BASE_Y = 1835
    POSITION_A2222_BIRTH_PLACE_BASE_X = 1785
    POSITION_A2222_BIRTH_PLACE_BASE_Y = 1969

    GREAT_GREAT_GREAT_GREAT_GRANDPARENT_NAME_FONT_SIZE = 8
    GREAT_GREAT_GREAT_GREAT_GRANDPARENT_DATE_INFO_FONT_SIZE = 7
    GREAT_GREAT_GREAT_GREAT_GRANDPARENT_PLACE_INFO_FONT_SIZE = 5

    OVERLAY_SCALE = 0.8457
    COMPOSITE_X = 300
    COMPOSITE_Y = 570
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72


GENERATION_7_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    "great_great_great_great_grandparent_stroke_color": (Color, "black"),
    "great_great_great_great_grandparent_font_color": (Color, "black"),
    "great_great_great_great_grandparent_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "overlay_scale": (float, 0.8457),
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
    # Date format settings
    "date_format": (str, "da_mon_year"),
    "date_year_only": (bool, False),  # For compact display in 7gen+
    # Place name formatting settings
    "place_use_country_abbrev": (bool, False),
    "place_use_state_abbrev": (bool, True),
    "place_use_country_abbrev": (bool, True),
    "place_show_county": (bool, False),
    "place_show_country": (bool, True),
    "place_hide_usa_with_state": (bool, True),
    "place_show_township": (bool, True),
    "place_show_flag": (bool, False),
    "place_flag_type": (str, "birth"),
}


def _composite_overlay(content_img, gen6_img_buffer, validated_settings):
    """Composite the 6gen overlay at configured scale in center."""
    try:
        gen6_img_buffer.seek(0)
        gen6_bytes = gen6_img_buffer.getvalue()

        if not gen6_bytes:
            raise BufferError("6gen overlay buffer is empty")

        overlay_scale = validated_settings.get(
            "overlay_scale", Generation7Constants.OVERLAY_SCALE
        )

        with Image(blob=gen6_bytes) as gen6_overlay:
            overlay_size = int(gen6_overlay.width * overlay_scale)
            gen6_overlay.resize(overlay_size, overlay_size)

            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            content_img.composite(gen6_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 6gen overlay at ({overlay_x}, {overlay_y}) scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


class GenerationError(Exception):
    """Custom exception for generation errors."""

    pass


def generate_prototype_7gen_preview(
    primary_individual, family_data=None, template="preview", user_settings=None
):
    """
    Generate 7-gen chart using modular printer.

    7-gen includes great-great-great-great-grandparents (64 positions).
    Each subclade (A, B, C, D) has 16 positions.

    Key principle: Define A subclade positions once, apply rotation for B/C/D.

    A Subclade (paternal grandfather's line): rotation=0 (bottom)
    B Subclade (paternal grandmother's line): rotation=270 (right side)
    C Subclade (maternal grandfather's line): rotation=180 (top)
    D Subclade (maternal grandmother's line): rotation=90 (left side)
    """
    user_settings = user_settings or {}
    validated_settings = get_validated_settings(
        user_settings, GENERATION_7_SETTINGS_SCHEMA, "7gen"
    )

    logger.info(f"Generating prototype 7gen for: {primary_individual.full_name}")

    try:
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "7GEN_PREVIEW.png",
        )

        if not os.path.exists(template_path):
            logger.warning(f"7gen preview template not found, using 6gen template")
            template_path = os.path.join(
                settings.BASE_DIR,
                "apps/hud/static/hud/images/preview_image_templates",
                "6GEN_PREVIEW.png",
            )

        with Image(
            filename=template_path, resolution=Generation7Constants.RESOLUTION
        ) as content_img:
            with Drawing() as draw:
                draw.push()

                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings.get(
                    "great_great_great_great_grandparent_stroke_width", 0.5
                )
                draw.stroke_color = validated_settings.get(
                    "great_great_great_great_grandparent_stroke_color", Color("black")
                )
                draw.fill_color = validated_settings.get(
                    "great_great_great_great_grandparent_font_color", Color("black")
                )

                # Base parameters for great-great-great-great-grandparents
                # Using sunbeam rotation - text points inward toward center
                base_params = dict(
                    center_x=Generation7Constants.IMAGE_CENTER_X,
                    center_y=Generation7Constants.IMAGE_CENTER_Y,
                    name_font_size=4.5,
                    date_font_size=4,
                    place_font_size=4,
                    birth_date_offset_x=0,
                    birth_date_offset_y=0,
                    birth_date_paired_offset_x=-20,
                    death_date_paired_offset_x=20,
                    paired_dates_base_y=1860,
                    paired_places_base_y=1920,
                    birth_place_paired_offset_x=-20,
                    death_place_paired_offset_x=20,
                    use_display_text=True,  # Multiline for full names
                    use_gravity_center=False,
                    multiline_line_spacing=0.8,
                    multiline_alignment="center",
                )

                # Sunbeam rotation helper - text points INWARD toward center
                def get_sunbeam_rotation(
                    x,
                    y,
                    center_x=Generation7Constants.IMAGE_CENTER_X,
                    center_y=Generation7Constants.IMAGE_CENTER_Y,
                    inward=True,
                ):
                    """Calculate rotation so text points toward center (inward) or away (outward)."""
                    dx = x - center_x
                    dy = y - center_y
                    angle = math.degrees(math.atan2(dy, dx))
                    rotation = int(angle) % 360
                    if inward:
                        rotation = (rotation + 180) % 360
                    return rotation

                # Build family relationships
                individuals = family_data.get("individuals", {}) if family_data else {}
                families = family_data.get("families", {}) if family_data else {}

                # Get parents
                father_id = getattr(primary_individual, "father", None)
                mother_id = getattr(primary_individual, "mother", None)

                # Get grandparents (gen 2)
                father = individuals.get(father_id) if father_id else None
                mother = individuals.get(mother_id) if mother_id else None

                paternal_grandfather = (
                    individuals.get(getattr(father, "father", None)) if father else None
                )
                paternal_grandmother = (
                    individuals.get(getattr(father, "mother", None)) if father else None
                )
                maternal_grandfather = (
                    individuals.get(getattr(mother, "father", None)) if mother else None
                )
                maternal_grandmother = (
                    individuals.get(getattr(mother, "mother", None)) if mother else None
                )

                # =========================================================================
                # Build great-great-great-great-grandparents (7gen) - proper lineage traversal
                # =========================================================================
                great_great_great_grandparents = []

                def get_ancestor_by_path(start_person, path_digits):
                    """
                    Get ancestor at a specific position based on a 4-digit path.
                    path_digits: string like "1111", "1112", etc.
                    - Each digit: 1 = father's line, 2 = mother's line
                    - For paternal grandfather's line: start at paternal_grandfather
                    - Example "1111" = father's father's father's father
                    """
                    if not start_person:
                        return None

                    current = start_person
                    for digit in path_digits:
                        if not current:
                            return None
                        if digit == "1":
                            next_id = getattr(current, "father", None)
                        else:  # digit == "2"
                            next_id = getattr(current, "mother", None)

                        if next_id:
                            current = individuals.get(next_id)
                        else:
                            return None

                    return current

                # Position codes for each subclade (4 digits representing father=1/mother=2 path)
                # A subclade: paternal_grandfather's line
                # B subclade: paternal_grandmother's line
                # C subclade: maternal_grandfather's line
                # D subclade: maternal_grandmother's line
                position_codes = [
                    "1111",
                    "1112",
                    "1121",
                    "1122",  # First 4 (father's father line)
                    "1211",
                    "1212",
                    "1221",
                    "1222",  # Next 4 (father's mother line)
                    "2111",
                    "2112",
                    "2121",
                    "2122",  # Next 4 (mother's father line)
                    "2211",
                    "2212",
                    "2221",
                    "2222",  # Last 4 (mother's mother line)
                ]

                # Build positions for each subclade
                # B: right edge (x=1885)
                # C: top edge (y=65-10=55)
                # D: left edge (x=65)

                # A positions: bottom edge (y=1885-10=1875)
                # A1111 moved 10px left, A1 positions keep 116px gap
                # A2 positions adjusted inward
                a_x_positions = [
                    125,  # A1111 (+3px)
                    240,  # A1112
                    355,  # A1121
                    468,  # A1122 (-3px)
                    580,  # A1211
                    692,  # A1212
                    809,  # A1221
                    907,  # A1222 (-10px)
                    1028,  # A2111 (+15px)
                    1143,  # A2112 (new)
                    1251,  # A2121 (+10px)
                    1362,  # A2122 (+8px)
                    1478,  # A2211 (+8px)
                    1590,  # A2212 (+8px)
                    1680,  # A2221 (-3px)
                    1788,  # A2222 (-29px, moved in 25px from 1801)
                ]

                # Use ONLY A positions - sunbeam rotation applied, print_individual handles quadrant rotation
                a_positions = [(a_x_positions[i], 1840) for i in range(16)]

                # Build master position coordinates from A subclade (position only, no ancestor yet)
                # Each tuple: (name_x, name_y, birth_date_x, birth_date_y, birth_place_x, birth_place_y, text_rotation)
                master_positions = []
                for i in range(16):
                    pos_x, pos_y = a_positions[i]
                    text_rot = get_sunbeam_rotation(pos_x, pos_y)
                    master_positions.append(
                        (
                            pos_x,
                            pos_y,
                            pos_x + 25,
                            1825,
                            pos_x - 25,
                            1850,
                            text_rot,
                        )
                    )

                # A subclade (rotation 0) - uses paternal_grandfather lineage
                if paternal_grandfather:
                    for i, path_code in enumerate(position_codes):
                        ancestor = get_ancestor_by_path(paternal_grandfather, path_code)
                        if ancestor:
                            pos = master_positions[i]
                            great_great_great_grandparents.append(
                                (
                                    ancestor,
                                    pos[0],
                                    pos[1],  # name_x, name_y
                                    pos[2],
                                    pos[3],  # birth_date_x, birth_date_y
                                    pos[4],
                                    pos[5],  # birth_place_x, birth_place_y
                                    0,  # A subclade rotation
                                    pos[6],  # text_rotation
                                )
                            )

                # B subclade (rotation 270) - uses paternal_grandmother lineage, reuses A positions
                if paternal_grandmother:
                    for i, path_code in enumerate(position_codes):
                        ancestor = get_ancestor_by_path(paternal_grandmother, path_code)
                        if ancestor:
                            pos = master_positions[i]
                            great_great_great_grandparents.append(
                                (
                                    ancestor,
                                    pos[0],
                                    pos[1],
                                    pos[2],
                                    pos[3],
                                    pos[4],
                                    pos[5],
                                    270,  # B subclade rotation
                                    pos[6],
                                )
                            )

                # C subclade (rotation 180) - uses maternal_grandfather lineage, reuses A positions
                if maternal_grandfather:
                    for i, path_code in enumerate(position_codes):
                        ancestor = get_ancestor_by_path(maternal_grandfather, path_code)
                        if ancestor:
                            pos = master_positions[i]
                            great_great_great_grandparents.append(
                                (
                                    ancestor,
                                    pos[0],
                                    pos[1],
                                    pos[2],
                                    pos[3],
                                    pos[4],
                                    pos[5],
                                    180,  # C subclade rotation
                                    pos[6],
                                )
                            )

                # D subclade (rotation 90) - uses maternal_grandmother lineage, reuses A positions
                if maternal_grandmother:
                    for i, path_code in enumerate(position_codes):
                        ancestor = get_ancestor_by_path(maternal_grandmother, path_code)
                        if ancestor:
                            pos = master_positions[i]
                            great_great_great_grandparents.append(
                                (
                                    ancestor,
                                    pos[0],
                                    pos[1],
                                    pos[2],
                                    pos[3],
                                    pos[4],
                                    pos[5],
                                    90,  # D subclade rotation
                                    pos[6],
                                )
                            )

                # Print all great-great-great-great-grandparents
                for (
                    individual,
                    base_x,
                    base_y,
                    birth_date_center_x,
                    birth_date_center_y,
                    birth_place_center_x,
                    birth_place_center_y,
                    subclade_rotation,
                    sunbeam_rotation,
                ) in great_great_great_grandparents:
                    if individual:
                        print_individual(
                            draw=draw,
                            content_img=content_img,
                            individual=individual,
                            settings=validated_settings,
                            rotation=subclade_rotation,
                            first_name_base_x=base_x,
                            first_name_base_y=base_y,
                            first_name_rotation=sunbeam_rotation,
                            birth_date_base_x=birth_date_center_x,
                            birth_date_base_y=birth_date_center_y,
                            birth_date_rotation=sunbeam_rotation,
                            birth_place_base_x=birth_place_center_x,
                            birth_place_base_y=birth_place_center_y,
                            birth_place_rotation=sunbeam_rotation,
                            death_date_base_x=birth_date_center_x,
                            death_date_base_y=birth_date_center_y,
                            death_date_rotation=sunbeam_rotation,
                            death_place_base_x=birth_place_center_x,
                            death_place_base_y=birth_place_center_y,
                            death_place_rotation=sunbeam_rotation,
                            **base_params,
                            chart_settings=validated_settings,
                            date_year_only=validated_settings.get(
                                "date_year_only", False
                            ),
                        )

                draw.pop()
                draw(content_img)

            # Composite 6gen overlay
            gen6_img_buffer = generate_prototype_6gen_preview(
                primary_individual, family_data, "preview", user_settings
            )
            _composite_overlay(content_img, gen6_img_buffer, validated_settings)

            if template == "preview":
                return create_preview_buffer(content_img)
            elif template == "final":
                return _create_prototype_final_pdf(content_img, validated_settings)
            else:
                raise GenerationError(f"Unknown template type: {template}")

    except (GenerationError, BufferError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prototype 7gen generation: {e}")
        raise GenerationError(f"Prototype 7-gen chart generation failed: {e}")


def _create_prototype_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_7GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation7Constants.RESOLUTION
    ) as base_img:
        base_img.composite(
            content_img,
            left=Generation7Constants.COMPOSITE_X,
            top=Generation7Constants.COMPOSITE_Y,
        )
        return create_pdf_buffer(base_img)


def test_prototype_7gen():
    """Test function for 7-gen prototype generation."""
    from apps.parser.models import PersonData

    # Create test primary individual
    primary = PersonData(
        individual_id="I1",
        full_name="Test Person",
        first_name="Test",
        last_name="Person",
        birth_date="01 JAN 2000",
        birth_place="Test City",
    )
    primary.father = "I2"
    primary.mother = "I3"

    # Create test family data
    family_data = {
        "individuals": {
            "I1": primary,
            "I2": PersonData(
                individual_id="I2",
                full_name="Father",
                first_name="Father",
                last_name="Person",
                father="I4",
                mother="I5",
            ),
            "I3": PersonData(
                individual_id="I3",
                full_name="Mother",
                first_name="Mother",
                last_name="Person",
                father="I6",
                mother="I7",
            ),
        },
        "families": {},
    }

    result = generate_prototype_7gen_preview(primary, family_data, "preview", {})
    with open("prototype_7gen_output.png", "wb") as f:
        f.write(result.getvalue())
    print("Test 7-gen prototype generated: prototype_7gen_output.png")
    return result
