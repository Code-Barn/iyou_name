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
)
from apps.generator.utils.prototype.individual_printer import print_individual
from apps.generator.utils.settings_validator import get_validated_settings
from apps.generator.utils.simple_buffer_manager import (
    create_preview_buffer,
    create_pdf_buffer,
    get_chart_buffer,
)

logger = logging.getLogger(__name__)


class Generation7Constants:
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975

    # 7gen positions follow pattern with 105px spacing (half of 211)
    # Left side (A1111-A1222): 8 positions starting at x=205
    # Right side (A2111-A2222): mirrored across x=975

    # A1111 (outermost-left)
    POSITION_A1111_FIRST_NAME_BASE_X = 115
    POSITION_A1111_FIRST_NAME_BASE_Y = 1788
    POSITION_A1111_BIRTH_DATE_BASE_X = 300
    POSITION_A1111_BIRTH_DATE_BASE_Y = 1795
    POSITION_A1111_BIRTH_PLACE_BASE_X = 184
    POSITION_A1111_BIRTH_PLACE_BASE_Y = 1969

    # A1112
    POSITION_A1112_FIRST_NAME_BASE_X = 310
    POSITION_A1112_FIRST_NAME_BASE_Y = 1885
    POSITION_A1112_BIRTH_DATE_BASE_X = 400
    POSITION_A1112_BIRTH_DATE_BASE_Y = 1795
    POSITION_A1112_BIRTH_PLACE_BASE_X = 297
    POSITION_A1112_BIRTH_PLACE_BASE_Y = 1969

    # A1121
    POSITION_A1121_FIRST_NAME_BASE_X = 415
    POSITION_A1121_FIRST_NAME_BASE_Y = 1885
    POSITION_A1121_BIRTH_DATE_BASE_X = 495
    POSITION_A1121_BIRTH_DATE_BASE_Y = 1795
    POSITION_A1121_BIRTH_PLACE_BASE_X = 375
    POSITION_A1121_BIRTH_PLACE_BASE_Y = 1969

    # A1122
    POSITION_A1122_FIRST_NAME_BASE_X = 520
    POSITION_A1122_FIRST_NAME_BASE_Y = 1885
    POSITION_A1122_BIRTH_DATE_BASE_X = 590
    POSITION_A1122_BIRTH_DATE_BASE_Y = 1795
    POSITION_A1122_BIRTH_PLACE_BASE_X = 480
    POSITION_A1122_BIRTH_PLACE_BASE_Y = 1969

    # A1211
    POSITION_A1211_FIRST_NAME_BASE_X = 625
    POSITION_A1211_FIRST_NAME_BASE_Y = 1885
    POSITION_A1211_BIRTH_DATE_BASE_X = 675
    POSITION_A1211_BIRTH_DATE_BASE_Y = 1795
    POSITION_A1211_BIRTH_PLACE_BASE_X = 590
    POSITION_A1211_BIRTH_PLACE_BASE_Y = 1969

    # A1212
    POSITION_A1212_FIRST_NAME_BASE_X = 732
    POSITION_A1212_FIRST_NAME_BASE_Y = 1885
    POSITION_A1212_BIRTH_DATE_BASE_X = 769
    POSITION_A1212_BIRTH_DATE_BASE_Y = 1795
    POSITION_A1212_BIRTH_PLACE_BASE_X = 710
    POSITION_A1212_BIRTH_PLACE_BASE_Y = 1969

    # A1221
    POSITION_A1221_FIRST_NAME_BASE_X = 835
    POSITION_A1221_FIRST_NAME_BASE_Y = 1885
    POSITION_A1221_BIRTH_DATE_BASE_X = 875
    POSITION_A1221_BIRTH_DATE_BASE_Y = 1795
    POSITION_A1221_BIRTH_PLACE_BASE_X = 795
    POSITION_A1221_BIRTH_PLACE_BASE_Y = 1969

    # A1222
    POSITION_A1222_FIRST_NAME_BASE_X = 940
    POSITION_A1222_FIRST_NAME_BASE_Y = 1885
    POSITION_A1222_BIRTH_DATE_BASE_X = 970
    POSITION_A1222_BIRTH_DATE_BASE_Y = 1795
    POSITION_A1222_BIRTH_PLACE_BASE_X = 900
    POSITION_A1222_BIRTH_PLACE_BASE_Y = 1969

    # Right side - mirrored positions
    # Mirror formula: mirrored_x = 1950 - left_x

    # A2121 (mirrored from A1222)
    POSITION_A2121_FIRST_NAME_BASE_X = 1010
    POSITION_A2121_FIRST_NAME_BASE_Y = 1885
    POSITION_A2121_BIRTH_DATE_BASE_X = 980
    POSITION_A2121_BIRTH_DATE_BASE_Y = 1795
    POSITION_A2121_BIRTH_PLACE_BASE_X = 1050
    POSITION_A2121_BIRTH_PLACE_BASE_Y = 1969

    # A2122 (mirrored from A1221)
    POSITION_A2122_FIRST_NAME_BASE_X = 1115
    POSITION_A2122_FIRST_NAME_BASE_Y = 1885
    POSITION_A2122_BIRTH_DATE_BASE_X = 1075
    POSITION_A2122_BIRTH_DATE_BASE_Y = 1795
    POSITION_A2122_BIRTH_PLACE_BASE_X = 1155
    POSITION_A2122_BIRTH_PLACE_BASE_Y = 1969

    # A2111 (mirrored from A1212)
    POSITION_A2111_FIRST_NAME_BASE_X = 1220
    POSITION_A2111_FIRST_NAME_BASE_Y = 1885
    POSITION_A2111_BIRTH_DATE_BASE_X = 1180
    POSITION_A2111_BIRTH_DATE_BASE_Y = 1795
    POSITION_A2111_BIRTH_PLACE_BASE_X = 1260
    POSITION_A2111_BIRTH_PLACE_BASE_Y = 1969

    # A2112 (mirrored from A1211)
    POSITION_A2112_FIRST_NAME_BASE_X = 1325
    POSITION_A2112_FIRST_NAME_BASE_Y = 1885
    POSITION_A2112_BIRTH_DATE_BASE_X = 1285
    POSITION_A2112_BIRTH_DATE_BASE_Y = 1795
    POSITION_A2112_BIRTH_PLACE_BASE_X = 1365
    POSITION_A2112_BIRTH_PLACE_BASE_Y = 1969

    # A2211 (mirrored from A1122)
    POSITION_A2211_FIRST_NAME_BASE_X = 1430
    POSITION_A2211_FIRST_NAME_BASE_Y = 1885
    POSITION_A2211_BIRTH_DATE_BASE_X = 1390
    POSITION_A2211_BIRTH_DATE_BASE_Y = 1795
    POSITION_A2211_BIRTH_PLACE_BASE_X = 1470
    POSITION_A2211_BIRTH_PLACE_BASE_Y = 1969

    # A2212 (mirrored from A1121)
    POSITION_A2212_FIRST_NAME_BASE_X = 1535
    POSITION_A2212_FIRST_NAME_BASE_Y = 1885
    POSITION_A2212_BIRTH_DATE_BASE_X = 1495
    POSITION_A2212_BIRTH_DATE_BASE_Y = 1795
    POSITION_A2212_BIRTH_PLACE_BASE_X = 1575
    POSITION_A2212_BIRTH_PLACE_BASE_Y = 1969

    # A2221 (mirrored from A1112)
    POSITION_A2221_FIRST_NAME_BASE_X = 1640
    POSITION_A2221_FIRST_NAME_BASE_Y = 1885
    POSITION_A2221_BIRTH_DATE_BASE_X = 1600
    POSITION_A2221_BIRTH_DATE_BASE_Y = 1795
    POSITION_A2221_BIRTH_PLACE_BASE_X = 1680
    POSITION_A2221_BIRTH_PLACE_BASE_Y = 1969

    # A2222 (mirrored from A1111)
    POSITION_A2222_FIRST_NAME_BASE_X = 1745
    POSITION_A2222_FIRST_NAME_BASE_Y = 1885
    POSITION_A2222_BIRTH_DATE_BASE_X = 1705
    POSITION_A2222_BIRTH_DATE_BASE_Y = 1795
    POSITION_A2222_BIRTH_PLACE_BASE_X = 1785
    POSITION_A2222_BIRTH_PLACE_BASE_Y = 1969

    # Date pair and place pair offsets (can be tuned per-position below)
    DATE_PAIR_OFFSET_X = 25  # Birth date center offset from name
    PLACE_PAIR_OFFSET_X = 25  # Birth place center offset from name

    # Per-position fine-tuning: dict of {index: (name_y_adjust, date_y_adjust, place_y_adjust, date_x_adjust, place_x_adjust)}
    # Use None for no adjustment, or specific pixel values
    # Index corresponds to position in a_x_positions (0=A1111, 1=A1112, ... 15=A2222)
    POSITION_FINE_TUNE = {
        # index: (name_y, birth_date_y, birth_place_y, birth_date_x, birth_place_x)
        0: (0, -10, 0, 33, 0),  # A1111
        1: (0, 10, 0, 29, -5),  # A1112
        2: (0, 5, 0, 20, -5),  # A1121
        3: (0, 5, 0, 15, -10),  # A1122
        4: (0, 10, 0, 5, -15),  # A1211
        5: (0, 15, 0, 0, -25),  # A1212
        6: (0, 15, 0, -5, -25),  # A1221
        7: (6, 20, 0, -5, -40),  # A1222
        8: (6, 20, -10, -18, -40),  # A2111
        9: (7, 25, -10, -25, -45),  # A2112
        10: (9, 25, 0, -30, -50),  # A2121
        11: (10, 30, 0, -37, -55),  # A2122
        12: (10, 30, -10, -45, -60),  # A2211
        13: (8, 35, -5, -50, -65),  # A2212
        14: (13, 35, 0, -50, -70),  # A2221
        15: (15, -50, 0, -55, -75),  # A2222
        # Add more fine-tuning as needed
    }

    GREAT_GREAT_GREAT_GREAT_GRANDPARENT_NAME_FONT_SIZE = 8
    GREAT_GREAT_GREAT_GREAT_GRANDPARENT_DATE_INFO_FONT_SIZE = 7
    GREAT_GREAT_GREAT_GREAT_GRANDPARENT_PLACE_INFO_FONT_SIZE = 5

    # Flag positions - centered on date pair (y=1823), 16 positions
    FLAG_A1111_BASE_X = -794
    FLAG_A1111_BASE_Y = 848
    FLAG_A1112_BASE_X = -675
    FLAG_A1112_BASE_Y = 848
    FLAG_A1121_BASE_X = -585
    FLAG_A1121_BASE_Y = 848
    FLAG_A1122_BASE_X = -480
    FLAG_A1122_BASE_Y = 848
    FLAG_A1211_BASE_X = -350
    FLAG_A1211_BASE_Y = 848
    FLAG_A1212_BASE_X = -243
    FLAG_A1212_BASE_Y = 848
    FLAG_A1221_BASE_X = -140
    FLAG_A1221_BASE_Y = 848
    FLAG_A1222_BASE_X = -35
    FLAG_A1222_BASE_Y = 848
    FLAG_A2111_BASE_X = 35
    FLAG_A2111_BASE_Y = 848
    FLAG_A2112_BASE_X = 140
    FLAG_A2112_BASE_Y = 848
    FLAG_A2121_BASE_X = 243
    FLAG_A2121_BASE_Y = 848
    FLAG_A2122_BASE_X = 350
    FLAG_A2122_BASE_Y = 848
    FLAG_A2211_BASE_X = 480
    FLAG_A2211_BASE_Y = 848
    FLAG_A2212_BASE_X = 585
    FLAG_A2212_BASE_Y = 848
    FLAG_A2221_BASE_X = 675
    FLAG_A2221_BASE_Y = 848
    FLAG_A2222_BASE_X = 794
    FLAG_A2222_BASE_Y = 848

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
    "place_show_flag": (bool, True),
    "place_flag_type": (str, "birth"),
    "gen7_flag_size": (int, 77),  # Generation-specific flag size
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
                    birth_date_paired_offset_x=-38,
                    death_date_paired_offset_x=38,
                    paired_dates_base_y=1823,
                    paired_places_base_y=1910,
                    birth_place_paired_offset_x=-40,
                    death_place_paired_offset_x=40,
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
                    131,  # A1111 (+3px)
                    241,  # A1112
                    355,  # A1121
                    468,  # A1122 (-3px)
                    578,  # A1211
                    692,  # A1212
                    805,  # A1221
                    907,  # A1222 (-10px)
                    1028,  # A2111 (+15px)
                    1140,  # A2112 (new)
                    1249,  # A2121 (+10px)
                    1360,  # A2122 (+8px)
                    1473,  # A2211 (+8px)
                    1585,  # A2212 (+8px)
                    1695,  # A2221 (-3px)
                    1807,  # A2222 (-29px, moved in 25px from 1801)
                ]

                # Use ONLY A positions - sunbeam rotation applied, print_individual handles quadrant rotation
                a_positions = [(a_x_positions[i], 1842) for i in range(16)]

                # Build master position coordinates from A subclade (position only, no ancestor yet)
                # Each tuple: (name_x, name_y, birth_date_x, birth_date_y, birth_place_x, birth_place_y, text_rotation)
                # Apply fine-tuning from Generation7Constants.POSITION_FINE_TUNE
                master_positions = []
                for i in range(16):
                    pos_x, pos_y = a_positions[i]
                    text_rot = get_sunbeam_rotation(pos_x, pos_y)

                    # Get fine-tune adjustments if defined
                    tune = Generation7Constants.POSITION_FINE_TUNE.get(i)
                    if tune:
                        name_y_adj, date_y_adj, place_y_adj, date_x_adj, place_x_adj = (
                            tune
                        )
                        # Apply adjustments (check for None, not for falsy 0)
                        final_name_y = pos_y + (
                            name_y_adj if name_y_adj is not None else 0
                        )
                        final_date_y = 1825 + (
                            date_y_adj if date_y_adj is not None else 0
                        )
                        final_place_y = 1850 + (
                            place_y_adj if place_y_adj is not None else 0
                        )
                        final_date_x = (
                            pos_x
                            + Generation7Constants.DATE_PAIR_OFFSET_X
                            + (date_x_adj if date_x_adj is not None else 0)
                        )
                        final_place_x = (
                            pos_x
                            - Generation7Constants.PLACE_PAIR_OFFSET_X
                            - (place_x_adj if place_x_adj is not None else 0)
                        )
                    else:
                        final_name_y = pos_y
                        final_date_y = 1825
                        final_place_y = 1850
                        final_date_x = pos_x + Generation7Constants.DATE_PAIR_OFFSET_X
                        final_place_x = pos_x - Generation7Constants.PLACE_PAIR_OFFSET_X

                    master_positions.append(
                        (
                            pos_x,
                            final_name_y,
                            final_date_x,
                            final_date_y,
                            final_place_x,
                            final_place_y,
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
                        # Determine flag position based on base_x (16 master positions)
                        # Using actual a_x_positions values: [131, 241, 355, 468, 578, 692, 805, 907, 1028, 1140, 1249, 1360, 1473, 1585, 1695, 1807]
                        if base_x == 131:  # A1111
                            flag_base_x = Generation7Constants.FLAG_A1111_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A1111_BASE_Y
                        elif base_x == 241:  # A1112
                            flag_base_x = Generation7Constants.FLAG_A1112_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A1112_BASE_Y
                        elif base_x == 355:  # A1121
                            flag_base_x = Generation7Constants.FLAG_A1121_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A1121_BASE_Y
                        elif base_x == 468:  # A1122
                            flag_base_x = Generation7Constants.FLAG_A1122_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A1122_BASE_Y
                        elif base_x == 578:  # A1211
                            flag_base_x = Generation7Constants.FLAG_A1211_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A1211_BASE_Y
                        elif base_x == 692:  # A1212
                            flag_base_x = Generation7Constants.FLAG_A1212_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A1212_BASE_Y
                        elif base_x == 805:  # A1221
                            flag_base_x = Generation7Constants.FLAG_A1221_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A1221_BASE_Y
                        elif base_x == 907:  # A1222
                            flag_base_x = Generation7Constants.FLAG_A1222_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A1222_BASE_Y
                        elif base_x == 1028:  # A2111
                            flag_base_x = Generation7Constants.FLAG_A2111_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A2111_BASE_Y
                        elif base_x == 1140:  # A2112
                            flag_base_x = Generation7Constants.FLAG_A2112_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A2112_BASE_Y
                        elif base_x == 1249:  # A2121
                            flag_base_x = Generation7Constants.FLAG_A2121_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A2121_BASE_Y
                        elif base_x == 1360:  # A2122
                            flag_base_x = Generation7Constants.FLAG_A2122_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A2122_BASE_Y
                        elif base_x == 1473:  # A2211
                            flag_base_x = Generation7Constants.FLAG_A2211_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A2211_BASE_Y
                        elif base_x == 1585:  # A2212
                            flag_base_x = Generation7Constants.FLAG_A2212_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A2212_BASE_Y
                        elif base_x == 1695:  # A2221
                            flag_base_x = Generation7Constants.FLAG_A2221_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A2221_BASE_Y
                        elif base_x == 1807:  # A2222
                            flag_base_x = Generation7Constants.FLAG_A2222_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A2222_BASE_Y
                        else:
                            flag_base_x = Generation7Constants.FLAG_A1111_BASE_X
                            flag_base_y = Generation7Constants.FLAG_A1111_BASE_Y

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
                            flag_base_x=flag_base_x,
                            flag_base_y=flag_base_y,
                            flag_size=validated_settings.get("gen7_flag_size", 90),
                            **base_params,
                            chart_settings=validated_settings,
                            date_year_only=validated_settings.get(
                                "date_year_only", False
                            ),
                        )

                draw.pop()
                draw(content_img)

            # Composite 6gen overlay using BUFFER MANAGER (not direct call)
            # IMPORTANT: Don't pass place_flag_size to lower generations - each uses its own genX_flag_size
            gen6_settings = {k: v for k, v in user_settings.items()}
            logger.info("[7gen] Getting 6gen overlay from buffer manager")
            gen6_img_buffer = get_chart_buffer(
                primary_individual, family_data, gen6_settings, generation=6
            )
            if not gen6_img_buffer:
                raise GenerationError("Failed to get 6gen overlay buffer")
            logger.info("[7gen] Got 6gen overlay buffer successfully")

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
