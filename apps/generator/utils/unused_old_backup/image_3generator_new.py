"""
3-Generation family tree chart generator.

This generator handles 3 generations by overlaying the 2-generation output
and only drawing the grandparents, following the same pattern as the 2-generator.
"""

import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.name_utils import parse_name_parts
from apps.generator.utils.namechart_quadrant_calculator import (
    NameChartQuadrantCalculator,
)
from apps.generator.utils.image_2generator import generate_2gen_preview
from apps.generator.utils.settings_helper import extract_generation_settings

logger = logging.getLogger(__name__)


def generate_3gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 3-generation family tree chart by overlaying 2gen output.

    This generator follows the same pattern as the 2-generator:
    1. Generate 2gen overlay (primary + parents)
    2. Draw only grandparents (A, B, C, D)
    3. Composite overlay for final result

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type ('3gen' for 3-generation chart)
        user_settings: Dictionary of user settings

    Returns:
        BytesIO buffer containing the generated image
    """
    user_settings = user_settings or {}

    try:
        # Extract GRANDPARENT settings for current generation
        gen3_settings = extract_generation_settings(user_settings, "GRANDPARENT")

        # Extract PRIMARY settings for 2gen overlay
        primary_settings = extract_generation_settings(user_settings, "PRIMARY")

        # Generate 2gen overlay (primary + parents)
        gen2_buffer = generate_2gen_preview(
            primary_individual, family_data, "preview", primary_settings
        )

        # Load 3gen template (or use 2gen as base)
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "3GEN_PREVIEW.png",
        )

        # If 3gen template doesn't exist, use 2gen as base
        if not os.path.exists(template_path):
            template_path = os.path.join(
                settings.BASE_DIR,
                "apps/hud/static/hud/images/preview_image_templates",
                "2GEN_PREVIEW.png",
            )

        # Initialize position calculator for 1950px canvas
        position_calculator = NameChartQuadrantCalculator(canvas_size=1950)

        with Image(filename=template_path, resolution=300) as content_img:
            # Apply settings
            settings = apply_3gen_settings(user_settings)

            # First, composite the 2gen overlay
            gen2_buffer.seek(0)
            gen2_bytes = gen2_buffer.getvalue()
            with Image(blob=gen2_bytes) as gen2_overlay:
                # Scale down 2gen overlay for 3gen (make it smaller)
                gen2_overlay.resize(
                    int(gen2_overlay.width * 0.6), int(gen2_overlay.height * 0.6)
                )
                # Center the 2gen overlay
                gen2_x = (content_img.width - gen2_overlay.width) // 2
                gen2_y = (content_img.height - gen2_overlay.height) // 2
                content_img.composite(gen2_overlay, left=gen2_x, top=gen2_y)

            # Draw grandparents on top
            with Drawing() as draw:
                draw.push()

                # Set drawing properties for grandparents
                draw.font = settings["font_family"]
                draw.fill_color = Color(settings["grandparent_font_color"])
                draw.stroke_width = settings["default_stroke_width"]

                # Draw grandparents (A, B, C, D) in their triangular quadrants
                draw_grandparents_only(draw, family_data, settings, position_calculator)

                draw.pop()

            # Apply drawing to image
            draw.draw(content_img)

            # Return appropriate format
            buffer = BytesIO()
            format_type = "png" if template == "preview" else "pdf"
            content_img.save(buffer, format=format_type)
            buffer.seek(0)
            return buffer

    except Exception as e:
        logger.error(f"Error generating 3gen preview: {e}")
        raise


def apply_3gen_settings(user_settings):
    """Apply user settings with defaults for 3gen chart."""
    return {
        # Primary individual settings
        "primary_background_color": user_settings.get(
            "primary_background_color", "#FFFFFF"
        ),
        "primary_stroke_color": user_settings.get("primary_stroke_color", "#000000"),
        "primary_font_color": user_settings.get("primary_font_color", "#000000"),
        "primary_name_font_size": int(user_settings.get("primary_name_font_size", 84)),
        "primary_name_rotate": int(user_settings.get("primary_name_rotate", -45)),
        "font_family": user_settings.get("font_family", "Arial"),
        "default_stroke_width": float(user_settings.get("default_stroke_width", 0.5)),
        # Parent settings
        "parent_font_size": int(user_settings.get("parent_font_size", 72)),
        "parent_font_color": user_settings.get("parent_font_color", "#000000"),
        # Grandparent settings
        "grandparent_font_size": int(user_settings.get("grandparent_font_size", 60)),
        "grandparent_font_color": user_settings.get(
            "grandparent_font_color", "#000000"
        ),
    }


def extract_family_data_3gen(family_data):
    """
    Extract family data organized by generation for 3gen chart.

    Returns:
        Dictionary with naming convention keys
    """
    family_by_generation = {}

    # Generation 0: Primary individual
    family_by_generation["0"] = family_data.primary_individual

    # Generation 1: Parents
    parents = []
    if hasattr(family_data, "father") and family_data.father:
        parents.append(family_data.father)
    if hasattr(family_data, "mother") and family_data.mother:
        parents.append(family_data.mother)

    if parents:
        family_by_generation["1"] = parents[0]  # Father
        family_by_generation["2"] = parents[1] if len(parents) > 1 else None  # Mother

    # Generation 2: Grandparents
    grandparents = get_grandparents(family_data)
    if grandparents:
        family_by_generation["A"] = (
            grandparents[0] if len(grandparents) > 0 else None
        )  # Father's father
        family_by_generation["B"] = (
            grandparents[1] if len(grandparents) > 1 else None
        )  # Father's mother
        family_by_generation["C"] = (
            grandparents[2] if len(grandparents) > 2 else None
        )  # Mother's father
        family_by_generation["D"] = (
            grandparents[3] if len(grandparents) > 3 else None
        )  # Mother's mother

    return family_by_generation

    if mother:
        # Calculate position for mother (2) - top right quadrant
        x, y, rotation = position_calculator._get_quadrant_position("top_right", 1, 0)
        draw_individual_at_position(
            draw, mother, x, y, rotation, settings.get("parent_font_size", 72)
        )


def draw_grandparents_only(draw, family_data, settings, position_calculator):
    """Draw only grandparents (A, B, C, D) in their triangular quadrants."""
    grandparents = get_grandparents(family_data)

    if not grandparents:
        return

    # Quadrant mapping for grandparents
    quadrant_mapping = {
        "A": "top_left",  # Father's father
        "B": "bottom_left",  # Father's mother
        "C": "top_right",  # Mother's father
        "D": "bottom_right",  # Mother's mother
    }

    gp_font_size = settings.get("grandparent_font_size", 60)

    for i, gp_id in enumerate(["A", "B", "C", "D"]):
        if i < len(grandparents) and grandparents[i]:
            gp = grandparents[i]
            quadrant = quadrant_mapping[gp_id]

            # Calculate position for this grandparent
            x, y, rotation = position_calculator._get_quadrant_position(quadrant, 2, 0)
            draw_individual_at_position(draw, gp, x, y, rotation, gp_font_size)


def draw_individual_at_position(draw, individual, x, y, rotation, font_size):
    """Draw a single individual at the specified position."""
    # Parse name using improved logic
    first_name, middle_name, last_name = parse_name_parts(individual.full_name)

    # Build display text
    name_parts_to_display = [
        part for part in [first_name, middle_name, last_name] if part.strip()
    ]
    display_text = "\n".join(name_parts_to_display)

    # Draw individual
    draw.push()
    draw.translate(x, y)
    draw.rotate(rotation)

    draw.font_size = font_size

    # Draw multiline name
    lines = display_text.split("\n")
    line_height = font_size * 1.2
    start_y = -(len(lines) - 1) * line_height / 2

    for j, line in enumerate(lines):
        line_y = start_y + (j * line_height)
        draw.text(0, line_y, line)

    draw.pop()


def get_grandparents(family_data):
    """Extract grandparents from family data."""
    grandparents = []

    # Paternal grandparents
    if (
        hasattr(family_data, "paternal_grandfather")
        and family_data.paternal_grandfather
    ):
        grandparents.append(family_data.paternal_grandfather)
    if (
        hasattr(family_data, "paternal_grandmother")
        and family_data.paternal_grandmother
    ):
        grandparents.append(family_data.paternal_grandmother)

    # Maternal grandparents
    if (
        hasattr(family_data, "maternal_grandfather")
        and family_data.maternal_grandfather
    ):
        grandparents.append(family_data.maternal_grandfather)
    if (
        hasattr(family_data, "maternal_grandmother")
        and family_data.maternal_grandmother
    ):
        grandparents.append(family_data.maternal_grandmother)

    return grandparents
