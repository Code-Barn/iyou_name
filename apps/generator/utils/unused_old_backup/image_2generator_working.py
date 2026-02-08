"""
Working 2-generation chart generator that combines the mathematical positioning
with the proven overlay approach from the working backup.

This version maintains compatibility with the existing 1gen system while adding
proper parent generation positioning.
"""

import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils. import generate_1gen_preview
from apps.generator.utils.name_utils import parse_name_parts
from apps.generator.utils.settings_helper import extract_generation_settings
from apps.generator.utils.sunbeam_position_calculator import SunbeamPositionCalculator

logger = logging.getLogger(__name__)


def generate_2gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 2-generation family tree chart using proven overlay approach.

    This version:
    1. Generates parent drawing using mathematical positioning
    2. Generates 1gen overlay with PRIMARY settings
    3. Composites them together like the working backup

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

        with Image(filename=preview_template_path, resolution=300) as content_img:
            print(f"Content image loaded: {content_img.width}x{content_img.height}")

            # =============================================
            # PARENT GENERATION DRAWING (using mathematical positioning)
            # =============================================

            # Initialize position calculator for 1950px canvas
            position_calculator = SunbeamPositionCalculator(canvas_size=1950)

            # Calculate positions for parents using mathematical system
            parent_positions = calculate_parent_positions(
                family_data, position_calculator
            )

            print(f"DEBUG: Calculated parent positions: {parent_positions}")

            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                print(f"DEBUG: User settings for preview: {user_settings}")

                # Apply parent-specific settings with fallback to user_settings
                font_family = parent_settings.get(
                    "font_family", user_settings.get("font_family", "Arial")
                )
                draw.font = font_family
                draw.stroke_antialias = True
                draw.stroke_width = parent_settings.get(
                    "default_stroke_width",
                    user_settings.get("default_stroke_width", 0.5),
                )

                # Initial translation (from working backup)
                INITIAL_TRANSLATE_X = 350
                INITIAL_TRANSLATE_Y = 350
                draw.translate(x=INITIAL_TRANSLATE_X, y=INITIAL_TRANSLATE_Y)

                # Set parent stroke color
                parent_stroke_color = parent_settings.get(
                    "primary_stroke_color",
                    user_settings.get("primary_stroke_color", "#000000"),
                )
                draw.stroke_color = Color(parent_stroke_color)

                # Draw parents if we have positions
                if parent_positions:
                    for i, (parent_type, x, y, rotation, individual) in enumerate(
                        parent_positions
                    ):
                        if individual:
                            print(f"Drawing {parent_type}: {individual.full_name}")

                            # Set parent font color
                            parent_font_color = parent_settings.get(
                                "primary_font_color",
                                user_settings.get("primary_font_color", "#000000"),
                            )
                            draw.fill_color = Color(parent_font_color)

                            # Set parent font size
                            parent_font_size = parent_settings.get(
                                "primary_name_font_size",
                                user_settings.get("primary_name_font_size", 72),
                            )
                            draw.font_size = parent_font_size

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

            # Apply the drawing to the image
            draw(content_img)

            # =============================================
            # Generate the 1gen overlay with PRIMARY settings
            # =============================================

            # Check for stored primary settings first (from JavaScript)
            primary_settings = user_settings.get("primary_settings", {})
            print(f"DEBUG: user_settings keys: {list(user_settings.keys())}")
            print(f"DEBUG: primary_settings from user_settings: {primary_settings}")

            if not primary_settings:
                # Fallback to extracting PRIMARY from current settings
                primary_settings = extract_generation_settings(user_settings, "PRIMARY")
                print(
                    f"DEBUG: No stored primary settings, using fallback PRIMARY settings: {primary_settings}"
                )
            else:
                print(
                    f"DEBUG: Using stored primary settings for 1gen overlay: {primary_settings}"
                )

            print(f"DEBUG: Generating 1gen overlay with settings: {primary_settings}")
            gen1_img_buffer = generate_1gen_preview(
                primary_individual, family_data, "preview", primary_settings
            )
            print(f"DEBUG: Generated 1gen overlay buffer")

            # =============================================
            # Composite the 1gen overlay onto the 2gen image
            # =============================================

            gen1_img_buffer.seek(0)  # Reset buffer position
            gen1_bytes = gen1_img_buffer.getvalue()

            # Create image from blob and composite
            with Image(blob=gen1_bytes) as gen1_overlay:
                gen1_overlay.resize(
                    int(gen1_overlay.width * 0.48), int(gen1_overlay.height * 0.48)
                )
                content_img.composite(gen1_overlay, left=508, top=508)
                print(f"DEBUG: Composited 1gen overlay onto 2gen image")

            # =============================================
            # Return the appropriate format
            # =============================================

            if template == "preview":
                print("DEBUG: Returning preview image")
                gen2_image_buffer = BytesIO()
                content_img.save(file=gen2_image_buffer)
                gen2_image_buffer.seek(0)
                return gen2_image_buffer
            else:  # final
                print("DEBUG: Compositing content onto PDF base template")

                # Load the PDF base template
                base_template_path = os.path.join(
                    settings.BASE_DIR,
                    "apps/charts/static/charts/images/base_image_templates",
                    "US_LETTER_2GEN_BW.pdf",
                )
                print(f"DEBUG: Base template path: {base_template_path}")
                print(
                    f"DEBUG: Base template exists: {os.path.exists(base_template_path)}"
                )

                with Image(filename=base_template_path, resolution=300) as base_img:
                    print(f"Base template loaded: {base_img.width}x{base_img.height}")

                    # Composite the content image onto the base template
                    composite_x = 300
                    composite_y = 570

                    print(
                        f"DEBUG: Compositing content image at position ({composite_x}, {composite_y})"
                    )
                    base_img.composite(content_img, left=composite_x, top=composite_y)

                    # Save the final result as PDF
                    pdf_buffer = BytesIO()
                    base_img.save(file=pdf_buffer)
                    pdf_buffer.seek(0)

                    return pdf_buffer

    except Exception as e:
        logger.error(f"Error generating 2gen preview: {e}")
        raise


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
