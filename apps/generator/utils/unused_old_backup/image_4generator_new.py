"""
4-Generation family tree chart generator.

This generator handles 4 generations by overlaying the 3-generation output
and only drawing the great-grandparents, following the same pattern as the 2-generator.
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
from apps.generator.utils.image_3generator_new import generate_3gen_preview
from apps.generator.utils.settings_helper import extract_generation_settings


def generate_4gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 4-generation family tree chart by overlaying 3gen output.

    This generator follows the same pattern as the 2-generator:
    1. Generate 3gen overlay (primary + parents + grandparents)
    2. Draw only great-grandparents (A11, A12, B11, B12, C11, C12, D11, D12)
    3. Composite overlay for final result

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type ('4gen' for 4-generation chart)
        user_settings: Dictionary of user settings

    Returns:
        BytesIO buffer containing the generated image
    """
    user_settings = user_settings or {}

    try:
        # Extract GREATGRANDPARENT settings for current generation
        gen4_settings = extract_generation_settings(user_settings, "GREATGRANDPARENT")

        # Extract PRIMARY settings for 3gen overlay
        primary_settings = extract_generation_settings(user_settings, "PRIMARY")

        # Generate 3gen overlay (primary + parents + grandparents)
        gen3_buffer = generate_3gen_preview(
            primary_individual, family_data, "preview", primary_settings
        )

        # Load 4gen template (or use 3gen as base)
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "4GEN_PREVIEW.png",
        )

        # If 4gen template doesn't exist, use 3gen as base
        if not os.path.exists(template_path):
            template_path = os.path.join(
                settings.BASE_DIR,
                "apps/hud/static/hud/images/preview_image_templates",
                "3GEN_PREVIEW.png",
            )

        # Initialize position calculator for 1950px canvas
        position_calculator = NameChartQuadrantCalculator(canvas_size=1950)

        with Image(filename=template_path, resolution=300) as content_img:
            # Apply settings
            settings = apply_4gen_settings(user_settings)

            # First, composite the 3gen overlay
            gen3_buffer.seek(0)
            gen3_bytes = gen3_buffer.getvalue()
            with Image(blob=gen3_bytes) as gen3_overlay:
                # Scale down 3gen overlay for 4gen (make it smaller)
                gen3_overlay.resize(
                    int(gen3_overlay.width * 0.5), int(gen3_overlay.height * 0.5)
                )
                # Center the 3gen overlay
                gen3_x = (content_img.width - gen3_overlay.width) // 2
                gen3_y = (content_img.height - gen3_overlay.height) // 2
                content_img.composite(gen3_overlay, left=gen3_x, top=gen3_y)

            # Draw great-grandparents on top
            with Drawing() as draw:
                draw.push()

                # Set drawing properties for great-grandparents
                draw.font = settings["font_family"]
                draw.fill_color = Color(settings["greatgrandparent_font_color"])
                draw.stroke_width = settings["default_stroke_width"]

                # Draw great-grandparents (A11, A12, B11, B12, C11, C12, D11, D12)
                draw_great_grandparents_only(
                    draw, family_data, settings, position_calculator
                )

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
        logger.error(f"Error generating 4gen preview: {e}")
        raise


def apply_4gen_settings(user_settings):
    """Apply user settings with defaults for 4gen chart."""
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
        # Great-grandparent settings
        "greatgrandparent_font_size": int(
            user_settings.get("greatgrandparent_font_size", 48)
        ),
        "greatgrandparent_font_color": user_settings.get(
            "greatgrandparent_font_color", "#000000"
        ),
    }


def draw_great_grandparents_only(draw, family_data, settings, position_calculator):
    """Draw only great-grandparents (A11, A12, B11, B12, C11, C12, D11, D12) in their triangular quadrants."""
    great_grandparents = get_great_grandparents(family_data)

    if not great_grandparents:
        return

    # Quadrant mapping for great-grandparents
    quadrant_mapping = {
        "A11": "top_left",  # Father's father's father
        "A12": "top_left",  # Father's father's mother
        "B11": "bottom_left",  # Father's mother's father
        "B12": "bottom_left",  # Father's mother's mother
        "C11": "top_right",  # Mother's father's father
        "C12": "top_right",  # Mother's father's mother
        "D11": "bottom_right",  # Mother's mother's father
        "D12": "bottom_right",  # Mother's mother's mother
    }

    gg_font_size = settings.get("greatgrandparent_font_size", 48)

    for i, gg_id in enumerate(["A11", "A12", "B11", "B12", "C11", "C12", "D11", "D12"]):
        if i < len(great_grandparents) and great_grandparents[i]:
            gg = great_grandparents[i]
            quadrant = quadrant_mapping[gg_id]

            # Calculate position for this great-grandparent
            x, y, rotation = position_calculator._get_quadrant_position(quadrant, 3, 0)
            draw_individual_at_position(draw, gg, x, y, rotation, gg_font_size)


def get_great_grandparents(family_data):
    """Extract great-grandparents from family data."""
    great_grandparents = []

    # Paternal great-grandparents
    if (
        hasattr(family_data, "paternal_grandfather")
        and family_data.paternal_grandfather
    ):
        great_grandparents.append(family_data.paternal_grandfather)
    if (
        hasattr(family_data, "paternal_grandmother")
        and family_data.paternal_grandmother
    ):
        great_grandparents.append(family_data.paternal_grandmother)
    if (
        hasattr(family_data, "paternal_great_grandfather")
        and family_data.paternal_great_grandfather
    ):
        great_grandparents.append(family_data.paternal_great_grandfather)
    if (
        hasattr(family_data, "paternal_great_grandmother")
        and family_data.paternal_great_grandmother
    ):
        great_grandparents.append(family_data.paternal_great_grandmother)

    # Maternal great-grandparents
    if (
        hasattr(family_data, "maternal_grandfather")
        and family_data.maternal_grandfather
    ):
        great_grandparents.append(family_data.maternal_grandfather)
    if (
        hasattr(family_data, "maternal_grandmother")
        and family_data.maternal_grandmother
    ):
        great_grandparents.append(family_data.maternal_grandmother)
    if (
        hasattr(family_data, "maternal_great_grandfather")
        and family_data.maternal_great_grandfather
    ):
        great_grandparents.append(family_data.maternal_great_grandfather)
    if (
        hasattr(family_data, "maternal_great_grandmother")
        and family_data.maternal_great_grandmother
    ):
        great_grandparents.append(family_data.maternal_great_grandmother)

    return great_grandparents


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
