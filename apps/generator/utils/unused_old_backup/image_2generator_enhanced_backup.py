"""
Enhanced 2-generation chart generator using mathematical positioning.

This generator uses the new sunbeam positioning system for the parents
while maintaining compatibility with the existing 1gen system.
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


def generate_2gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 2-generation family tree chart using mathematical positioning.

    This version uses the new sunbeam positioning system for parents
    while maintaining the existing 1gen primary individual positioning.

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type ('2gen' for 2-generation chart)
        user_settings: Dictionary of user settings to override hardcoded defaults

    Returns:
        BytesIO buffer containing the generated image (PNG for preview, PDF for final)
    """
    # Get user settings or use empty dict if not provided
    user_settings = user_settings or {}

    print(f"DEBUG: generate_2gen_preview received user_settings: {user_settings}")
    print(f"DEBUG: Generating template type: {template}")

    # Extract PARENT settings for 2gen-specific drawing
    parent_settings = extract_generation_settings(user_settings, "PARENT")
    print(f"DEBUG: Extracted PARENT settings: {parent_settings}")

    print(
        f"DEBUG: Generating 2-generation family tree for: {primary_individual.full_name}"
    )
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    try:
        # Load the 2gen template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "2GEN_PREVIEW.png",
        )

        print(f"DEBUG: Preview template path: {preview_template_path}")
        print(
            f"DEBUG: Preview template exists: {os.path.exists(preview_template_path)}"
        )

        # Initialize position calculator for 1950px canvas
        position_calculator = SunbeamPositionCalculator(canvas_size=1950)

        with Image(filename=preview_template_path, resolution=300) as content_img:
            print(f"Content image loaded: {content_img.width}x{content_img.height}")

            # Apply user settings with defaults
            settings = apply_2gen_settings(user_settings)

            # Calculate positions for parents using mathematical system
            parent_positions = calculate_parent_positions(
                family_data, position_calculator
            )

            print(f"DEBUG: Calculated parent positions: {parent_positions}")

            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                print(f"DEBUG: User settings for preview: {user_settings}")

                draw.font = settings["font_family"]
                draw.fill_color = Color(settings["primary_font_color"])
                draw.stroke_antialias = True
                draw.stroke_width = settings["default_stroke_width"]

                # =============================================
                # DRAW PRIMARY INDIVIDUAL (using existing 1gen logic)
                # =============================================

                # Use your existing 1gen positioning for primary individual
                primary_x = 975  # Center of 1950px canvas
                primary_y = 975
                primary_rotation = settings.get("primary_name_rotate", -45)

                # Get primary individual name info
                primary_name_info = get_name_display_info(primary_individual.full_name)

                # Draw primary individual
                draw.push()
                draw.translate(primary_x, primary_y)
                draw.rotate(primary_rotation)

                # Set primary individual styling
                draw.font_size = settings.get("primary_name_font_size", 84)
                draw.fill_color = Color(settings.get("primary_font_color", "#000000"))

                # Draw name (multiline)
                lines = primary_name_info["display_text"].split("\n")
                line_height = draw.font_size * 1.2
                start_y = -(len(lines) - 1) * line_height / 2

                for i, line in enumerate(lines):
                    line_y = start_y + (i * line_height)
                    draw.text(0, line_y, line)
                    print(f"Drew primary individual line {i + 1}: '{line}'")

                draw.pop()

                # =============================================
                # DRAW PARENTS (using new mathematical positioning)
                # =============================================

                if parent_positions:
                    # Set parent styling
                    parent_font_size = parent_settings.get("father_name_font_size", 72)
                    draw.font_size = parent_font_size
                    draw.fill_color = Color(
                        parent_settings.get("father_font_color", "#000000")
                    )

                    for i, (parent_type, x, y, rotation, individual) in enumerate(
                        parent_positions
                    ):
                        if individual:
                            print(f"Drawing {parent_type}: {individual.full_name}")

                            # Parse name using improved logic
                            first_name, middle_name, last_name = parse_name_parts(
                                individual.full_name
                            )

                            # Build display text - only include non-empty parts
                            name_parts_to_display = [
                                part
                                for part in [first_name, middle_name, last_name]
                                if part.strip()
                            ]
                            display_text = "\n".join(name_parts_to_display)

                            # Draw parent
                            draw.push()
                            draw.translate(x, y)
                            draw.rotate(rotation)

                            # Draw name (multiline)
                            lines = display_text.split("\n")
                            line_height = parent_font_size * 1.2
                            start_y = -(len(lines) - 1) * line_height / 2

                            for j, line in enumerate(lines):
                                line_y = start_y + (j * line_height)
                                draw.text(0, line_y, line)
                                print(f"Drew {parent_type} line {j + 1}: '{line}'")

                            draw.pop()
                        else:
                            print(f"No {parent_type} found in family data")

                draw.pop()

            # Convert to appropriate format
            if template == "preview":
                buffer = BytesIO()
                content_img.save(buffer, format="png")
                buffer.seek(0)
                return buffer
            else:  # final
                buffer = BytesIO()
                content_img.save(buffer, format="pdf")
                buffer.seek(0)
                return buffer

    except Exception as e:
        logger.error(f"Error generating 2gen preview: {e}")
        raise


def apply_2gen_settings(user_settings):
    """Apply user settings with defaults for 2gen chart."""
    settings = {
        # Primary individual settings (keep your existing defaults)
        "primary_background_color": user_settings.get(
            "primary_background_color", "#FFFFFF"
        ),
        "primary_stroke_color": user_settings.get("primary_stroke_color", "#000000"),
        "primary_font_color": user_settings.get("primary_font_color", "#000000"),
        "primary_name_font_size": int(user_settings.get("primary_name_font_size", 84)),
        "primary_name_rotate": int(user_settings.get("primary_name_rotate", -45)),
        "font_family": user_settings.get("font_family", "Arial"),
        "default_stroke_width": float(user_settings.get("default_stroke_width", 0.5)),
    }

    return settings


def calculate_parent_positions(family_data, position_calculator):
    """
    Calculate positions for parents using the mathematical positioning system.

    Args:
        family_data: Family data dictionary
        position_calculator: SunbeamPositionCalculator instance

    Returns:
        List of tuples: (parent_type, x, y, rotation, individual)
    """
    parent_positions = []

    # Calculate positions for 2 parents (generation 1)
    positions = position_calculator.calculate_generation_positions(1, 2)

    # Map positions to parents
    father = getattr(family_data, "father", None)
    mother = getattr(family_data, "mother", None)

    parents = [father, mother]
    parent_types = ["father", "mother"]

    for i, (x, y, rotation, zone_id) in enumerate(positions):
        if i < len(parents) and parents[i]:
            parent_positions.append((parent_types[i], x, y, rotation, parents[i]))

    return parent_positions


def get_name_display_info(full_name):
    """Get name display information (compatibility function)."""
    from apps.generator.utils.name_utils import (
        get_name_display_info as utils_get_display_info,
    )

    return utils_get_display_info(full_name)
