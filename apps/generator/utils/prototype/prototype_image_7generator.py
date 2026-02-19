"""
Prototype 7-generation family tree chart generator.

This module generates 7-generation ancestor charts using the same modular
approach as the 1-6gen generators, with:
- Generation7Constants for position definitions
- print_individual for rendering
- Composited 6gen overlay in center
"""

import logging
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
from apps.generator.utils.simple_buffer_manager import create_preview_buffer

logger = logging.getLogger(__name__)


class Generation7Constants:
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975

    # 7gen positions follow pattern with 105px spacing (half of 211)
    # Left side (A1111-A1222): 8 positions starting at x=205
    # Right side (A2111-A2222): mirrored across x=975

    # A1111 (outermost-left)
    POSITION_A1111_FIRST_NAME_BASE_X = 205
    POSITION_A1111_FIRST_NAME_BASE_Y = 1885
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
    COMPOSITE_X = 200
    COMPOSITE_Y = 480
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
                base_params = dict(
                    center_x=Generation7Constants.IMAGE_CENTER_X,
                    center_y=Generation7Constants.IMAGE_CENTER_Y,
                    name_font_size=8,
                    date_font_size=6,
                    place_font_size=5,
                    birth_date_offset_x=0,
                    birth_date_offset_y=0,
                    birth_date_rotation=0,
                    birth_date_paired_offset_x=-30,
                    death_date_paired_offset_x=30,
                    paired_dates_base_y=1860,
                    paired_places_base_y=1920,
                    birth_place_paired_offset_x=-30,
                    death_place_paired_offset_x=30,
                    use_display_text=True,
                    use_gravity_center=False,
                    multiline_line_spacing=1.2,
                    multiline_alignment="center",
                )

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

                # Get great-grandparents (gen 3) - for traversal
                def get_parents(person):
                    if not person:
                        return None, None
                    return getattr(person, "father", None), getattr(
                        person, "mother", None
                    )

                # Build gen 3 (great-grandparents) dict for traversal
                gg_parents = {}
                for gp in [
                    paternal_grandfather,
                    paternal_grandmother,
                    maternal_grandfather,
                    maternal_grandmother,
                ]:
                    if gp:
                        fid, mid = get_parents(gp)
                        gg_parents[gp.id] = (
                            individuals.get(fid) if fid else None,
                            individuals.get(mid) if mid else None,
                        )

                # Build gen 4 (great-great-grandparents) dict
                ggg_parents = {}
                for gp_id, (p1, p2) in gg_parents.items():
                    for p in [p1, p2]:
                        if p:
                            fid, mid = get_parents(p)
                            ggg_parents[p.id] = (
                                individuals.get(fid) if fid else None,
                                individuals.get(mid) if mid else None,
                            )

                # Build gen 5 (great-great-great-grandparents) dict
                gggg_parents = {}
                for gp_id, (p1, p2) in ggg_parents.items():
                    for p in [p1, p2]:
                        if p:
                            fid, mid = get_parents(p)
                            gggg_parents[p.id] = (
                                individuals.get(fid) if fid else None,
                                individuals.get(mid) if mid else None,
                            )

                # Build gen 6 (great-great-great-great-grandparents) - these are what we print in 7gen
                great_great_great_grandparents = []

                # Get great-great-great-grandparents and their parents (great-great-great-great-grandparents)
                for gp_id, (g3p1, g3p2) in gggg_parents.items():
                    for parent in [g3p1, g3p2]:
                        if parent:
                            fid, mid = get_parents(parent)
                            child1 = individuals.get(fid) if fid else None
                            child2 = individuals.get(mid) if mid else None

                            # Determine position based on ancestor path
                            # This is complex - we'd need to track the full path
                            # For now, let's just add them to the list
                            if child1:
                                great_great_great_grandparents.append(
                                    (child1, 0, 0, 0, 0, 0, 0, 0)
                                )
                            if child2:
                                great_great_great_grandparents.append(
                                    (child2, 0, 0, 0, 0, 0, 0, 0)
                                )

                # =========================================================================
                # Build great-great-great-great-grandparents (7gen) by traversing 6 levels up
                # =========================================================================
                great_great_great_grandparents = []

                def get_ancestors_at_level(person, target_level, current_level=0):
                    """Recursively get ancestors at a specific level"""
                    if current_level >= target_level or not person:
                        return [person] if current_level == target_level else []

                    father = individuals.get(getattr(person, "father", None))
                    mother = individuals.get(getattr(person, "mother", None))

                    father_ancestors = (
                        get_ancestors_at_level(father, target_level, current_level + 1)
                        if father
                        else []
                    )
                    mother_ancestors = (
                        get_ancestors_at_level(mother, target_level, current_level + 1)
                        if mother
                        else []
                    )

                    return father_ancestors + mother_ancestors

                # Get gen 6 ancestors (great-great-great-great-grandparents) - 6 levels up from primary
                # Primary (0) -> parents (1) -> grandparents (2) -> great-grandparents (3) ->
                # great-great-grandparents (4) -> great-great-great-grandparents (5) -> great-great-great-great-grandparents (6)

                # Get ancestors for each of the 4 grandparents' lines
                # Paternal grandfather's line (A subclade)
                if paternal_grandfather:
                    pgf_line = get_ancestors_at_level(
                        paternal_grandfather, 5
                    )  # 5 more levels from grandparent = gen 6
                    for i, ancestor in enumerate(pgf_line):
                        if ancestor and i < 16:  # Max 16 per subclade
                            pos_idx = i if i < 8 else i - 8
                            pos_x = (
                                [205, 310, 415, 520, 625, 730, 835, 940][pos_idx]
                                if i < 8
                                else [1010, 1115, 1220, 1325, 1430, 1535, 1640, 1745][
                                    pos_idx
                                ]
                            )
                            great_great_great_grandparents.append(
                                (
                                    ancestor,
                                    pos_x,
                                    1885,
                                    pos_x + 40,
                                    1835,
                                    pos_x - 40,
                                    1969,
                                    0,
                                )
                            )

                # Paternal grandmother's line (B subclade - rotation 270)
                if paternal_grandmother:
                    pgm_line = get_ancestors_at_level(paternal_grandmother, 5)
                    for i, ancestor in enumerate(pgm_line):
                        if ancestor and i < 16:
                            pos_idx = i if i < 8 else i - 8
                            pos_x = (
                                [205, 310, 415, 520, 625, 730, 835, 940][pos_idx]
                                if i < 8
                                else [1010, 1115, 1220, 1325, 1430, 1535, 1640, 1745][
                                    pos_idx
                                ]
                            )
                            great_great_great_grandparents.append(
                                (
                                    ancestor,
                                    pos_x,
                                    1885,
                                    pos_x + 40,
                                    1835,
                                    pos_x - 40,
                                    1969,
                                    270,
                                )
                            )

                # Maternal grandfather's line (C subclade - rotation 180)
                if maternal_grandfather:
                    mgf_line = get_ancestors_at_level(maternal_grandfather, 5)
                    for i, ancestor in enumerate(mgf_line):
                        if ancestor and i < 16:
                            pos_idx = i if i < 8 else i - 8
                            pos_x = (
                                [205, 310, 415, 520, 625, 730, 835, 940][pos_idx]
                                if i < 8
                                else [1010, 1115, 1220, 1325, 1430, 1535, 1640, 1745][
                                    pos_idx
                                ]
                            )
                            great_great_great_grandparents.append(
                                (
                                    ancestor,
                                    pos_x,
                                    1885,
                                    pos_x + 40,
                                    1835,
                                    pos_x - 40,
                                    1969,
                                    180,
                                )
                            )

                # Maternal grandmother's line (D subclade - rotation 90)
                if maternal_grandmother:
                    mgm_line = get_ancestors_at_level(maternal_grandmother, 5)
                    for i, ancestor in enumerate(mgm_line):
                        if ancestor and i < 16:
                            pos_idx = i if i < 8 else i - 8
                            pos_x = (
                                [205, 310, 415, 520, 625, 730, 835, 940][pos_idx]
                                if i < 8
                                else [1010, 1115, 1220, 1325, 1430, 1535, 1640, 1745][
                                    pos_idx
                                ]
                            )
                            great_great_great_grandparents.append(
                                (
                                    ancestor,
                                    pos_x,
                                    1885,
                                    pos_x + 40,
                                    1835,
                                    pos_x - 40,
                                    1969,
                                    90,
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
                            birth_date_base_x=birth_date_center_x,
                            birth_date_base_y=birth_date_center_y,
                            birth_place_base_x=birth_place_center_x,
                            birth_place_base_y=birth_place_center_y,
                            death_date_base_x=birth_date_center_x,
                            death_date_base_y=birth_date_center_y,
                            death_place_base_x=birth_place_center_x,
                            death_place_base_y=birth_place_center_y,
                            **base_params,
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
    # For now, just return PNG buffer
    # Full PDF creation would go here
    return create_preview_buffer(content_img)


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
