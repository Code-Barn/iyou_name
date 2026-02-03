"""
3-generation chart generator using sunbeam positioning system.

This generator places the primary individual and parents in traditional
layout, with grandparents (4 people) in sunbeam pattern.
"""

import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.name_utils import parse_name_parts
from apps.generator.utils.settings_helper import extract_generation_settings
from apps.generator.utils.sunbeam_position_calculator import SunbeamPositionCalculator

logger = logging.getLogger(__name__)


def generate_3gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 3-generation family tree chart.

    Layout:
    - Primary individual at center (existing 1gen positioning)
    - Parents at inner positions (enhanced 2gen positioning)
    - Grandparents (4 people) in sunbeam pattern at outer positions

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
        # Load 3gen template (or create one if needed)
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "3GEN_PREVIEW.png",
        )

        # If template doesn't exist, use 2gen as base
        if not os.path.exists(template_path):
            template_path = os.path.join(
                settings.BASE_DIR,
                "apps/hud/static/hud/images/preview_image_templates",
                "2GEN_PREVIEW.png",
            )

        # Initialize position calculator
        position_calculator = SunbeamPositionCalculator(canvas_size=1950)

        with Image(filename=template_path, resolution=300) as content_img:
            # Apply settings
            settings = apply_3gen_settings(user_settings)

            # Calculate positions for all generations
            all_positions = calculate_all_positions(family_data, position_calculator)

            with Drawing() as draw:
                draw.push()

                # Set drawing properties
                draw.font = settings["font_family"]
                draw.fill_color = Color(settings["primary_font_color"])
                draw.stroke_width = settings["default_stroke_width"]

                # Draw each generation
                draw_primary_individual(draw, primary_individual, settings)
                draw_parents(draw, family_data, settings, position_calculator)
                draw_grandparents(draw, family_data, settings, position_calculator)

                draw.pop()

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
        "parent_font_size": int(user_settings.get("parent_name_font_size", 72)),
        "parent_font_color": user_settings.get("parent_font_color", "#000000"),
        # Grandparent settings
        "grandparent_font_size": int(
            user_settings.get("grandparent_name_font_size", 60)
        ),
        "grandparent_font_color": user_settings.get(
            "grandparent_font_color", "#000000"
        ),
    }


def calculate_all_positions(family_data, position_calculator):
    """Calculate positions for all individuals in 3-generation chart."""
    all_positions = {}

    # Primary individual (use existing positioning)
    all_positions["primary"] = (975, 975, -45, family_data.primary_individual)

    # Parents (generation 1)
    parent_positions = position_calculator.calculate_generation_positions(1, 2)
    father = getattr(family_data, "father", None)
    mother = getattr(family_data, "mother", None)

    parents = [father, mother]
    for i, (x, y, rotation, zone_id) in enumerate(parent_positions):
        if i < len(parents) and parents[i]:
            all_positions[f"parent_{i}"] = (x, y, rotation, parents[i])

    # Grandparents (generation 2) - 4 people in sunbeam pattern
    grandparents = get_grandparents(family_data)
    if grandparents:
        gp_positions = position_calculator.calculate_generation_positions(2, 4)
        for i, (x, y, rotation, zone_id) in enumerate(gp_positions):
            if i < len(grandparents) and grandparents[i]:
                all_positions[f"grandparent_{i}"] = (x, y, rotation, grandparents[i])

    return all_positions


def draw_primary_individual(draw, primary_individual, settings):
    """Draw primary individual using existing 1gen positioning."""
    from apps.generator.utils.name_utils import get_name_display_info

    primary_x = 975
    primary_y = 975
    primary_rotation = settings.get("primary_name_rotate", -45)

    name_info = get_name_display_info(primary_individual.full_name)

    draw.push()
    draw.translate(primary_x, primary_y)
    draw.rotate(primary_rotation)

    draw.font_size = settings.get("primary_name_font_size", 84)
    draw.fill_color = Color(settings.get("primary_font_color", "#000000"))

    # Draw multiline name
    lines = name_info["display_text"].split("\n")
    line_height = draw.font_size * 1.2
    start_y = -(len(lines) - 1) * line_height / 2

    for i, line in enumerate(lines):
        line_y = start_y + (i * line_height)
        draw.text(0, line_y, line)

    draw.pop()


def draw_parents(draw, family_data, settings, position_calculator):
    """Draw parents using enhanced 2gen positioning."""
    parent_positions = position_calculator.calculate_generation_positions(1, 2)

    father = getattr(family_data, "father", None)
    mother = getattr(family_data, "mother", None)

    parents = [father, mother]
    parent_font_size = settings.get("parent_font_size", 72)

    draw.font_size = parent_font_size
    draw.fill_color = Color(settings.get("parent_font_color", "#000000"))

    for i, (x, y, rotation, zone_id) in enumerate(parent_positions):
        if i < len(parents) and parents[i]:
            parent = parents[i]
            first_name, middle_name, last_name = parse_name_parts(parent.full_name)

            # Build display text
            name_parts_to_display = [
                part for part in [first_name, middle_name, last_name] if part.strip()
            ]
            display_text = "\n".join(name_parts_to_display)

            # Draw parent
            draw.push()
            draw.translate(x, y)
            draw.rotate(rotation)

            # Draw multiline name
            lines = display_text.split("\n")
            line_height = parent_font_size * 1.2
            start_y = -(len(lines) - 1) * line_height / 2

            for j, line in enumerate(lines):
                line_y = start_y + (j * line_height)
                draw.text(0, line_y, line)

            draw.pop()


def draw_grandparents(draw, family_data, settings, position_calculator):
    """Draw grandparents (4 people) in sunbeam pattern."""
    grandparents = get_grandparents(family_data)

    if not grandparents:
        return

    # Calculate positions for 4 grandparents in sunbeam pattern
    gp_positions = position_calculator.calculate_generation_positions(2, 4)
    gp_font_size = settings.get("grandparent_font_size", 60)

    draw.font_size = gp_font_size
    draw.fill_color = Color(settings.get("grandparent_font_color", "#000000"))

    for i, (x, y, rotation, zone_id) in enumerate(gp_positions):
        if i < len(grandparents) and grandparents[i]:
            gp = grandparents[i]
            first_name, middle_name, last_name = parse_name_parts(gp.full_name)

            # Build display text
            name_parts_to_display = [
                part for part in [first_name, middle_name, last_name] if part.strip()
            ]
            display_text = "\n".join(name_parts_to_display)

            # Draw grandparent
            draw.push()
            draw.translate(x, y)
            draw.rotate(rotation)

            # Draw multiline name
            lines = display_text.split("\n")
            line_height = gp_font_size * 1.2
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
