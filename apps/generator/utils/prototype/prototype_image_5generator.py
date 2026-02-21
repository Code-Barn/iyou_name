"""
Prototype 5-generation chart generator using modular individual printer.

Position System:
- Position 0: Primary individual (in 1gen overlay at center, reduced scale)
- Position 1, 2: Parents (father/mother at 0°/180°)
- Position A, B, C, D: Grandparents at 0°, 90°, 180°, 270°
- Position A1, A2, B1, B2, C1, C2, D1, D2: Great-grandparents at 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°
- Position A11, A12, A21, A22: Great-great-grandparents from paternal grandfather's line (base positions)
- Position B11, B12, B21, B22: Same as A positions, rotated 270° (right side)
- Position C11, C12, C21, C22: Same as A positions, rotated 180° (top)
- Position D11, D12, D21, D22: Same as A positions, rotated 90° (left side)
"""

import logging
import os

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.parser.models import PersonData
from apps.generator.utils.prototype.individual_printer import print_individual
from apps.generator.utils.prototype.place_name_utils import (
    format_place_from_settings,
    get_flag_from_place,
)
from apps.generator.utils.prototype.prototype_image_4generator import (
    generate_prototype_4gen_preview,
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


class Generation5Constants:
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975

    # A11 position (base for all positions in A subclade)
    POSITION_A11_FIRST_NAME_BASE_X = 330
    POSITION_A11_FIRST_NAME_BASE_Y = 1735
    POSITION_A11_BIRTH_DATE_BASE_X = 390
    POSITION_A11_BIRTH_DATE_BASE_Y = 1735
    POSITION_A11_BIRTH_PLACE_BASE_X = 267
    POSITION_A11_BIRTH_PLACE_BASE_Y = 1869

    # A12 position (base for all positions in A subclade)
    POSITION_A12_FIRST_NAME_BASE_X = 760
    POSITION_A12_FIRST_NAME_BASE_Y = 1735
    POSITION_A12_BIRTH_DATE_BASE_X = 780
    POSITION_A12_BIRTH_DATE_BASE_Y = 1735
    POSITION_A12_BIRTH_PLACE_BASE_X = 739
    POSITION_A12_BIRTH_PLACE_BASE_Y = 1869

    # A21 position (mirrors A12 over x=975)
    POSITION_A21_FIRST_NAME_BASE_X = 1190
    POSITION_A21_FIRST_NAME_BASE_Y = 1735
    POSITION_A21_BIRTH_DATE_BASE_X = 1560
    POSITION_A21_BIRTH_DATE_BASE_Y = 1735
    POSITION_A21_BIRTH_PLACE_BASE_X = 1683
    POSITION_A21_BIRTH_PLACE_BASE_Y = 1869

    # A22 position (mirrors A11 over x=975)
    POSITION_A22_FIRST_NAME_BASE_X = 1620
    POSITION_A22_FIRST_NAME_BASE_Y = 1735
    POSITION_A22_BIRTH_DATE_BASE_X = 1170
    POSITION_A22_BIRTH_DATE_BASE_Y = 1735
    POSITION_A22_BIRTH_PLACE_BASE_X = 1211
    POSITION_A22_BIRTH_PLACE_BASE_Y = 1869

    GREAT_GREAT_GRANDPARENT_NAME_FONT_SIZE = 14
    GREAT_GREAT_GRANDPARENT_DATE_INFO_FONT_SIZE = 10
    GREAT_GREAT_GRANDPARENT_PLACE_INFO_FONT_SIZE = 8

    OVERLAY_SCALE = 0.7778
    COMPOSITE_X = 300
    COMPOSITE_Y = 570
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72


GENERATION_5_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    "great_great_grandparent_stroke_color": (Color, "black"),
    "great_great_grandparent_font_color": (Color, "black"),
    "great_great_grandparent_stroke_width": (float, 0.5),
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    "overlay_scale": (float, 0.7778),
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
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


def _composite_overlay(content_img, gen4_img_buffer, validated_settings):
    """Composite the 4gen overlay at 77.79% scale in center."""
    try:
        gen4_img_buffer.seek(0)
        gen4_bytes = gen4_img_buffer.getvalue()

        if not gen4_bytes:
            raise BufferError("4gen overlay buffer is empty")

        overlay_scale = validated_settings.get(
            "overlay_scale", Generation5Constants.OVERLAY_SCALE
        )

        with Image(blob=gen4_bytes) as gen4_overlay:
            overlay_size = int(gen4_overlay.width * overlay_scale)
            gen4_overlay.resize(overlay_size, overlay_size)

            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            content_img.composite(gen4_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 4gen overlay at ({overlay_x}, {overlay_y}) scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


def generate_prototype_5gen_preview(
    primary_individual, family_data=None, template="preview", user_settings=None
):
    """
    Generate 5-gen chart using modular printer.

    Key principle: Define A subclade positions once, apply rotation for B/C/D.

    A Subclade (paternal grandfather's line): rotation=0 (bottom)
    B Subclade (paternal grandmother's line): rotation=270 (right side)
    C Subclade (maternal grandfather's line): rotation=180 (top)
    D Subclade (maternal grandmother's line): rotation=90 (left side)
    """
    user_settings = user_settings or {}
    validated_settings = get_validated_settings(
        user_settings, GENERATION_5_SETTINGS_SCHEMA, "5gen"
    )

    logger.info(f"Generating prototype 5gen for: {primary_individual.full_name}")

    try:
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "5GEN_PREVIEW.png",
        )

        if not os.path.exists(template_path):
            logger.warning(f"5gen preview template not found, using 4gen template")
            template_path = os.path.join(
                settings.BASE_DIR,
                "apps/hud/static/hud/images/preview_image_templates",
                "4GEN_PREVIEW.png",
            )

        with Image(
            filename=template_path, resolution=Generation5Constants.RESOLUTION
        ) as content_img:
            with Drawing() as draw:
                draw.push()

                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings.get(
                    "great_great_grandparent_stroke_width", 0.5
                )
                draw.stroke_color = validated_settings.get(
                    "great_great_grandparent_stroke_color", Color("black")
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

                great_great_grandparents = []

                # =========================================================================
                # A SUBCLADE (paternal grandfather's line) - rotation = 0 (bottom)
                # =========================================================================
                if paternal_grandfather:
                    pgf_father_id = getattr(paternal_grandfather, "father", None)
                    pgf_mother_id = getattr(paternal_grandfather, "mother", None)

                    if pgf_father_id:
                        pgf_father = individuals.get(pgf_father_id)
                        if pgf_father:
                            pgf_father_father_id = getattr(pgf_father, "father", None)
                            pgf_father_mother_id = getattr(pgf_father, "mother", None)

                            if pgf_father_father_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(pgf_father_father_id),
                                        Generation5Constants.POSITION_A11_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A11_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A11_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A11_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A11_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A11_BIRTH_PLACE_BASE_Y,
                                        0,
                                    )
                                )
                            if pgf_father_mother_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(pgf_father_mother_id),
                                        Generation5Constants.POSITION_A12_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A12_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A12_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A12_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A12_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A12_BIRTH_PLACE_BASE_Y,
                                        0,
                                    )
                                )

                    if pgf_mother_id:
                        pgf_mother = individuals.get(pgf_mother_id)
                        if pgf_mother:
                            pgf_mother_father_id = getattr(pgf_mother, "father", None)
                            pgf_mother_mother_id = getattr(pgf_mother, "mother", None)

                            if pgf_mother_father_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(pgf_mother_father_id),
                                        Generation5Constants.POSITION_A21_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A21_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A21_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A21_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A21_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A21_BIRTH_PLACE_BASE_Y,
                                        0,
                                    )
                                )
                            if pgf_mother_mother_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(pgf_mother_mother_id),
                                        Generation5Constants.POSITION_A22_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A22_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A22_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A22_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A22_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A22_BIRTH_PLACE_BASE_Y,
                                        0,
                                    )
                                )

                # =========================================================================
                # B SUBCLADE (paternal grandmother's line) - rotation = 270 (right side)
                # Uses SAME positions as A, just with rotation applied
                # =========================================================================
                if paternal_grandmother:
                    pgm_father_id = getattr(paternal_grandmother, "father", None)
                    pgm_mother_id = getattr(paternal_grandmother, "mother", None)

                    if pgm_father_id:
                        pgm_father = individuals.get(pgm_father_id)
                        if pgm_father:
                            pgm_father_father_id = getattr(pgm_father, "father", None)
                            pgm_father_mother_id = getattr(pgm_father, "mother", None)

                            if pgm_father_father_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(pgm_father_father_id),
                                        Generation5Constants.POSITION_A11_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A11_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A11_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A11_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A11_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A11_BIRTH_PLACE_BASE_Y,
                                        270,
                                    )
                                )
                            if pgm_father_mother_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(pgm_father_mother_id),
                                        Generation5Constants.POSITION_A12_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A12_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A12_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A12_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A12_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A12_BIRTH_PLACE_BASE_Y,
                                        270,
                                    )
                                )

                    if pgm_mother_id:
                        pgm_mother = individuals.get(pgm_mother_id)
                        if pgm_mother:
                            pgm_mother_father_id = getattr(pgm_mother, "father", None)
                            pgm_mother_mother_id = getattr(pgm_mother, "mother", None)

                            if pgm_mother_father_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(pgm_mother_father_id),
                                        Generation5Constants.POSITION_A21_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A21_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A21_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A21_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A21_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A21_BIRTH_PLACE_BASE_Y,
                                        270,
                                    )
                                )
                            if pgm_mother_mother_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(pgm_mother_mother_id),
                                        Generation5Constants.POSITION_A22_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A22_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A22_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A22_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A22_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A22_BIRTH_PLACE_BASE_Y,
                                        270,
                                    )
                                )

                # =========================================================================
                # C SUBCLADE (maternal grandfather's line) - rotation = 180 (top)
                # Uses SAME positions as A, just with rotation applied
                # =========================================================================
                if maternal_grandfather:
                    mgf_father_id = getattr(maternal_grandfather, "father", None)
                    mgf_mother_id = getattr(maternal_grandfather, "mother", None)

                    if mgf_father_id:
                        mgf_father = individuals.get(mgf_father_id)
                        if mgf_father:
                            mgf_father_father_id = getattr(mgf_father, "father", None)
                            mgf_father_mother_id = getattr(mgf_father, "mother", None)

                            if mgf_father_father_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(mgf_father_father_id),
                                        Generation5Constants.POSITION_A11_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A11_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A11_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A11_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A11_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A11_BIRTH_PLACE_BASE_Y,
                                        180,
                                    )
                                )
                            if mgf_father_mother_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(mgf_father_mother_id),
                                        Generation5Constants.POSITION_A12_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A12_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A12_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A12_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A12_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A12_BIRTH_PLACE_BASE_Y,
                                        180,
                                    )
                                )

                    if mgf_mother_id:
                        mgf_mother = individuals.get(mgf_mother_id)
                        if mgf_mother:
                            mgf_mother_father_id = getattr(mgf_mother, "father", None)
                            mgf_mother_mother_id = getattr(mgf_mother, "mother", None)

                            if mgf_mother_father_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(mgf_mother_father_id),
                                        Generation5Constants.POSITION_A21_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A21_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A21_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A21_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A21_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A21_BIRTH_PLACE_BASE_Y,
                                        180,
                                    )
                                )
                            if mgf_mother_mother_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(mgf_mother_mother_id),
                                        Generation5Constants.POSITION_A22_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A22_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A22_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A22_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A22_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A22_BIRTH_PLACE_BASE_Y,
                                        180,
                                    )
                                )

                # =========================================================================
                # D SUBCLADE (maternal grandmother's line) - rotation = 90 (left side)
                # Uses SAME positions as A, just with rotation applied
                # =========================================================================
                if maternal_grandmother:
                    mgm_father_id = getattr(maternal_grandmother, "father", None)
                    mgm_mother_id = getattr(maternal_grandmother, "mother", None)

                    if mgm_father_id:
                        mgm_father = individuals.get(mgm_father_id)
                        if mgm_father:
                            mgm_father_father_id = getattr(mgm_father, "father", None)
                            mgm_father_mother_id = getattr(mgm_father, "mother", None)

                            if mgm_father_father_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(mgm_father_father_id),
                                        Generation5Constants.POSITION_A11_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A11_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A11_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A11_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A11_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A11_BIRTH_PLACE_BASE_Y,
                                        90,
                                    )
                                )
                            if mgm_father_mother_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(mgm_father_mother_id),
                                        Generation5Constants.POSITION_A12_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A12_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A12_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A12_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A12_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A12_BIRTH_PLACE_BASE_Y,
                                        90,
                                    )
                                )

                    if mgm_mother_id:
                        mgm_mother = individuals.get(mgm_mother_id)
                        if mgm_mother:
                            mgm_mother_father_id = getattr(mgm_mother, "father", None)
                            mgm_mother_mother_id = getattr(mgm_mother, "mother", None)

                            if mgm_mother_father_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(mgm_mother_father_id),
                                        Generation5Constants.POSITION_A21_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A21_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A21_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A21_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A21_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A21_BIRTH_PLACE_BASE_Y,
                                        90,
                                    )
                                )
                            if mgm_mother_mother_id:
                                great_great_grandparents.append(
                                    (
                                        individuals.get(mgm_mother_mother_id),
                                        Generation5Constants.POSITION_A22_FIRST_NAME_BASE_X,
                                        Generation5Constants.POSITION_A22_FIRST_NAME_BASE_Y,
                                        Generation5Constants.POSITION_A22_BIRTH_DATE_BASE_X,
                                        Generation5Constants.POSITION_A22_BIRTH_DATE_BASE_Y,
                                        Generation5Constants.POSITION_A22_BIRTH_PLACE_BASE_X,
                                        Generation5Constants.POSITION_A22_BIRTH_PLACE_BASE_Y,
                                        90,
                                    )
                                )

                base_params = dict(
                    center_x=Generation5Constants.IMAGE_CENTER_X,
                    center_y=Generation5Constants.IMAGE_CENTER_Y,
                    name_font_size=Generation5Constants.GREAT_GREAT_GRANDPARENT_NAME_FONT_SIZE,
                    date_font_size=Generation5Constants.GREAT_GREAT_GRANDPARENT_DATE_INFO_FONT_SIZE,
                    place_font_size=Generation5Constants.GREAT_GREAT_GRANDPARENT_PLACE_INFO_FONT_SIZE,
                    birth_date_offset_x=0,
                    birth_date_offset_y=0,
                    birth_date_rotation=0,
                    birth_date_paired_offset_x=-100,
                    death_date_paired_offset_x=100,
                    paired_dates_base_y=1785,
                    paired_places_base_y=1919,
                    birth_place_paired_offset_x=-100,
                    death_place_paired_offset_x=100,
                    use_display_text=True,
                    use_gravity_center=False,
                    multiline_line_spacing=0.8,
                    multiline_alignment="center",
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
                ) in great_great_grandparents:
                    if individual:
                        # Format places based on settings
                        formatted_birth_place = format_place_from_settings(
                            getattr(individual, "birth_place", "") or "",
                            validated_settings,
                        )
                        formatted_death_place = format_place_from_settings(
                            getattr(individual, "death_place", "") or "",
                            validated_settings,
                        )

                        # Create a modified individual with formatted places
                        class FormattedIndividual:
                            def __init__(self, original, birth_place, death_place):
                                self.__dict__.update(original.__dict__)
                                self.birth_place = birth_place
                                self.death_place = death_place

                        formatted_individual = FormattedIndividual(
                            individual, formatted_birth_place, formatted_death_place
                        )

                        print_individual(
                            draw=draw,
                            content_img=content_img,
                            individual=formatted_individual,
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

            gen4_img_buffer = generate_prototype_4gen_preview(
                primary_individual, family_data, "preview", user_settings
            )
            _composite_overlay(content_img, gen4_img_buffer, validated_settings)

            if template == "preview":
                return create_preview_buffer(content_img)
            elif template == "final":
                return _create_prototype_final_pdf(content_img, validated_settings)
            else:
                raise GenerationError(f"Unknown template type: {template}")

    except (GenerationError, BufferError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prototype 5gen generation: {e}")
        raise GenerationError(f"Prototype 5-gen chart generation failed: {e}")


def _create_prototype_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_5GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation5Constants.RESOLUTION
    ) as base_img:
        base_img.composite(
            content_img,
            left=Generation5Constants.COMPOSITE_X,
            top=Generation5Constants.COMPOSITE_Y,
        )
        return create_pdf_buffer(base_img)


def test_prototype_5gen():
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

    great_great_grandfather_1 = PersonData(
        id="I16",
        full_name="Arthur James Anderson",
        given_name="Arthur",
        surname="Anderson",
        birth_date="1880-01-10",
        birth_place="Boston, MA",
        death_date="1960-05-20",
        death_place="Philadelphia, PA",
    )

    great_great_grandmother_1 = PersonData(
        id="I17",
        full_name="Mary Ann Thompson",
        given_name="Mary",
        surname="Thompson",
        birth_date="1882-06-15",
        birth_place="New York, NY",
        death_date="1955-11-30",
        death_place="Boston, MA",
    )

    great_great_grandfather_2 = PersonData(
        id="I18",
        full_name="William Henry Clark",
        given_name="William",
        surname="Clark",
        birth_date="1878-09-22",
        birth_place="Chicago, IL",
        death_date="1958-02-14",
        death_place="Detroit, MI",
    )

    great_great_grandmother_2 = PersonData(
        id="I19",
        full_name="Emma Louise Lewis",
        given_name="Emma",
        surname="Lewis",
        birth_date="1880-12-05",
        birth_place="Philadelphia, PA",
        death_date="1962-08-18",
        death_place="Chicago, IL",
    )

    great_great_grandfather_3 = PersonData(
        id="I20",
        full_name="Joseph Paul Walker",
        given_name="Joseph",
        surname="Walker",
        birth_date="1875-03-18",
        birth_place="Boston, MA",
        death_date="1955-07-22",
        death_place="Brooklyn, NY",
    )

    great_great_grandmother_3 = PersonData(
        id="I21",
        full_name="Sarah Jane Hall",
        given_name="Sarah",
        surname="Hall",
        birth_date="1877-08-30",
        birth_place="Queens, NY",
        death_date="1953-12-10",
        death_place="Boston, MA",
    )

    great_great_grandfather_4 = PersonData(
        id="I22",
        full_name="Frank Benjamin Young",
        given_name="Frank",
        surname="Young",
        birth_date="1872-11-12",
        birth_place="Chicago, IL",
        death_date="1950-04-05",
        death_place="New York, NY",
    )

    great_great_grandmother_4 = PersonData(
        id="I23",
        full_name="Grace Elizabeth King",
        given_name="Grace",
        surname="King",
        birth_date="1874-05-25",
        birth_place="Philadelphia, PA",
        death_date="1948-09-15",
        death_place="Boston, MA",
    )

    great_great_grandfather_5 = PersonData(
        id="I24",
        full_name="Michael David Scott",
        given_name="Michael",
        surname="Scott",
        birth_date="1876-02-14",
        birth_place="Boston, MA",
        death_date="1952-06-18",
        death_place="Brooklyn, NY",
    )

    great_great_grandmother_5 = PersonData(
        id="I25",
        full_name="Jennifer Lynn Taylor",
        given_name="Jennifer",
        surname="Taylor",
        birth_date="1878-07-22",
        birth_place="Queens, NY",
        death_date="1950-10-05",
        death_place="Boston, MA",
    )

    great_great_grandfather_6 = PersonData(
        id="I26",
        full_name="Richard Alan Moore",
        given_name="Richard",
        surname="Moore",
        birth_date="1873-09-08",
        birth_place="Chicago, IL",
        death_date="1948-12-20",
        death_place="New York, NY",
    )

    great_great_grandmother_6 = PersonData(
        id="I27",
        full_name="Patricia Sue White",
        given_name="Patricia",
        surname="White",
        birth_date="1875-12-30",
        birth_place="Philadelphia, PA",
        death_date="1946-04-12",
        death_place="Boston, MA",
    )

    great_great_grandfather_7 = PersonData(
        id="I28",
        full_name="Daniel James Harris",
        given_name="Daniel",
        surname="Harris",
        birth_date="1870-04-05",
        birth_place="Boston, MA",
        death_date="1945-08-25",
        death_place="New York, NY",
    )

    great_great_grandmother_7 = PersonData(
        id="I29",
        full_name="Nancy Marie Clark",
        given_name="Nancy",
        surname="Clark",
        birth_date="1872-10-18",
        birth_place="Brooklyn, NY",
        death_date="1943-02-14",
        death_place="Boston, MA",
    )

    great_great_grandfather_8 = PersonData(
        id="I30",
        full_name="Christopher Lee Lewis",
        given_name="Christopher",
        surname="Lewis",
        birth_date="1868-06-12",
        birth_place="Chicago, IL",
        death_date="1942-11-30",
        death_place="Philadelphia, PA",
    )

    great_great_grandmother_8 = PersonData(
        id="I31",
        full_name="Michelle Anne Robinson",
        given_name="Michelle",
        surname="Robinson",
        birth_date="1870-01-25",
        birth_place="Detroit, MI",
        death_date="1940-07-08",
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
            "I16": great_great_grandfather_1,
            "I17": great_great_grandmother_1,
            "I18": great_great_grandfather_2,
            "I19": great_great_grandmother_2,
            "I20": great_great_grandfather_3,
            "I21": great_great_grandmother_3,
            "I22": great_great_grandfather_4,
            "I23": great_great_grandmother_4,
            "I24": great_great_grandfather_5,
            "I25": great_great_grandmother_5,
            "I26": great_great_grandfather_6,
            "I27": great_great_grandmother_6,
            "I28": great_great_grandfather_7,
            "I29": great_great_grandmother_7,
            "I30": great_great_grandfather_8,
            "I31": great_great_grandmother_8,
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

    great_grandfather_1.father = "I16"
    great_grandfather_1.mother = "I17"
    great_grandmother_1.father = "I18"
    great_grandmother_1.mother = "I19"
    great_grandfather_2.father = "I20"
    great_grandfather_2.mother = "I21"
    great_grandmother_2.father = "I22"
    great_grandmother_2.mother = "I23"

    great_grandfather_3.father = "I24"
    great_grandfather_3.mother = "I25"
    great_grandmother_3.father = "I26"
    great_grandmother_3.mother = "I27"
    great_grandfather_4.father = "I28"
    great_grandfather_4.mother = "I29"
    great_grandmother_4.father = "I30"
    great_grandmother_4.mother = "I31"

    print(f"Testing prototype 5gen for: {person.full_name}")

    result = generate_prototype_5gen_preview(person, family_data, "preview")

    print(f"Generated {result.getbuffer().nbytes} bytes")
    print("Output via buffer")

    return result


if __name__ == "__main__":
    test_prototype_5gen()
