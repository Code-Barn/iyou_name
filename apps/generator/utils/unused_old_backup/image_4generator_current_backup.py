"""
4-generation chart generator using template overlay approach.

This generator creates a 4-generation chart by:
1. Drawing great-grandparents on the 4gen template
2. Overlaying a 3gen chart (primary + parents + grandparents) in the center
3. Using proper session settings inheritance
"""

import logging
import math
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.name_utils import parse_name_parts
from apps.generator.utils.settings_helper import extract_generation_settings
from apps.generator.utils.chart_buffer_manager import buffer_manager

logger = logging.getLogger(__name__)


def generate_4gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 4-generation family tree chart using proven overlay approach.

    This version:
    1. Draws great-grandparents using edge positioning on 4gen template
    2. Generates 3gen overlay with PRIMARY, PARENT, and GRANDPARENT settings
    3. Composites them together like the working 3gen approach

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type ('4gen' for 4-generation chart)
        user_settings: Dictionary of user settings to override hardcoded defaults

    Returns:
        BytesIO buffer containing the generated image (PNG for preview, PDF for final)
    """
    # Get user settings or use empty dict if not provided
    user_settings = user_settings or {}

    print(f"DEBUG: generate_4gen_preview received user_settings: {user_settings}")
    print(f"DEBUG: Generating template type: {template}")

    # Extract GREATGRANDPARENT settings for 4gen-specific drawing
    greatgrandparent_settings = extract_generation_settings(
        user_settings, "GREATGRANDPARENT"
    )
    print(f"DEBUG: Extracted GREATGRANDPARENT settings: {greatgrandparent_settings}")

    print(
        f"DEBUG: Generating 4-generation family tree for: {primary_individual.full_name}"
    )
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    try:
        # Load the 4gen template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "4GEN_PREVIEW.png",
        )

        print(f"DEBUG: Preview template path: {preview_template_path}")
        print(
            f"DEBUG: Preview template exists: {os.path.exists(preview_template_path)}"
        )

        with Image(filename=preview_template_path, resolution=300) as content_img:
            print(f"Content image loaded: {content_img.width}x{content_img.height}")

            # =============================================
            # GREATGRANDPARENT GENERATION DRAWING
            # =============================================

            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                print(f"DEBUG: User settings for preview: {user_settings}")

                # Apply great-grandparent-specific settings with fallback to user_settings
                font_family = greatgrandparent_settings.get(
                    "font_family", user_settings.get("font_family", "Arial")
                )
                draw.font = font_family
                draw.stroke_antialias = True
                draw.stroke_width = greatgrandparent_settings.get(
                    "default_stroke_width",
                    user_settings.get("default_stroke_width", 0.5),
                )

                # Set great-grandparent stroke color
                greatgrandparent_stroke_color = greatgrandparent_settings.get(
                    "primary_stroke_color",
                    user_settings.get("primary_stroke_color", "#000000"),
                )
                draw.stroke_color = Color(greatgrandparent_stroke_color)

                # Get family relationships to find great-grandparents
                great_grandparents = get_great_grandparents(
                    primary_individual, family_data
                )

                print(f"DEBUG: Found {len(great_grandparents)} great-grandparents")

                # Great-grandparent positioning settings
                font_size = greatgrandparent_settings.get(
                    "primary_name_font_size",
                    user_settings.get("primary_name_font_size", 32),
                )
                draw.font_size = font_size
                edge_distance = greatgrandparent_settings.get(
                    "primary_translate_x", user_settings.get("primary_translate_x", 20)
                )
                date_distance = greatgrandparent_settings.get(
                    "primary_birth_translate_y",
                    user_settings.get("primary_birth_translate_y", 12),
                )

                # Draw great-grandparents along edges with proper rotation and centering
                # Canvas center for positioning
                center_x = content_img.width // 2
                center_y = content_img.height // 2
                radius = center_x - edge_distance  # Distance from center to edge

                # Position great-grandparents at 8 compass points
                positions = [
                    (0, 0),  # Bottom
                    (-45, 1),  # Bottom-right
                    (-90, 2),  # Right
                    (-135, 3),  # Top-right
                    (-180, 4),  # Top
                    (-225, 5),  # Top-left
                    (-270, 6),  # Left
                    (-315, 7),  # Bottom-left
                ]

                for rotation, index in positions:
                    if index < len(great_grandparents) and great_grandparents[index]:
                        great_grandparent = great_grandparents[index]
                        gp_type = f"great_grandparent_{index}"

                        print(
                            f"Drawing {gp_type}: {great_grandparent.full_name} at {rotation}° rotation"
                        )

                        # Set great-grandparent font color
                        greatgrandparent_font_color = greatgrandparent_settings.get(
                            "primary_font_color",
                            user_settings.get("primary_font_color", "#000000"),
                        )
                        draw.fill_color = Color(greatgrandparent_font_color)

                        # Calculate position on the edge based on rotation
                        angle_rad = math.radians(rotation)
                        edge_x = center_x + radius * math.cos(angle_rad)
                        edge_y = center_y + radius * math.sin(angle_rad)

                        # Parse name using improved logic
                        first_name, middle_name, last_name = parse_name_parts(
                            great_grandparent.full_name
                        )

                        # Draw great-grandparent name parts centered on edge with rotation
                        if first_name:
                            draw.push()
                            # Translate to edge position
                            draw.translate(int(edge_x), int(edge_y))
                            # Apply rotation (text will be perpendicular to edge)
                            draw.rotate(rotation)
                            # Center the text on the edge
                            draw.text(0, 0, first_name)
                            print(
                                f"Drew {gp_type} first name: '{first_name}' at ({int(edge_x)}, {int(edge_y)}) with {rotation}° rotation"
                            )
                            draw.pop()

                        if last_name:
                            draw.push()
                            # Translate to edge position with offset for last name
                            draw.translate(int(edge_x), int(edge_y) - 25)
                            # Apply rotation
                            draw.rotate(rotation)
                            # Center the text
                            draw.text(0, 0, last_name)
                            print(
                                f"Drew {gp_type} last name: '{last_name}' at ({int(edge_x)}, {int(edge_y) - 25}) with {rotation}° rotation"
                            )
                            draw.pop()

                        # Draw birth date if available
                        if great_grandparent.birth_date:
                            draw.push()
                            # Translate to edge position with offset for date
                            draw.translate(int(edge_x), int(edge_y) + date_distance)
                            # Apply rotation
                            draw.rotate(rotation)
                            # Smaller font for dates
                            draw.font_size = int(font_size * 0.7)
                            # Center the text
                            draw.text(0, 0, great_grandparent.birth_date)
                            print(
                                f"Drew {gp_type} birth date: '{great_grandparent.birth_date}' at ({int(edge_x)}, {int(edge_y)} + {date_distance}) with {rotation}° rotation"
                            )
                            draw.pop()

                # Apply the drawing to the image before destroying the context
                draw(content_img)
                draw.pop()

            # =============================================
            # Generate the 3gen overlay with PRIMARY, PARENT, and GRANDPARENT settings
            # =============================================

            # Extract settings for overlay generation (like 2gen and 3gen do)
            primary_settings = user_settings.get("primary_settings", {})
            if not primary_settings:
                primary_settings = extract_generation_settings(user_settings, "PRIMARY")

            print(
                f"DEBUG: Generating 3gen overlay with primary settings: {primary_settings}"
            )

            # Generate fresh 3gen overlay with current settings (not from cache)
            from apps.generator.utils.image_3generator import generate_3gen_preview

            gen3_img_buffer = generate_3gen_preview(
                primary_individual, family_data, "preview", primary_settings
            )

            if gen3_img_buffer is None:
                print("ERROR: 3gen overlay buffer is None")
                raise Exception("Failed to generate 3gen overlay")

            print(f"DEBUG: Generated 3gen overlay buffer: {type(gen3_img_buffer)}")

            # =============================================
            # Composite the 3gen overlay onto the 4gen image
            # =============================================

            gen3_img_buffer.seek(0)  # Reset buffer position
            gen3_bytes = gen3_img_buffer.getvalue()

            if not gen3_bytes:
                print("ERROR: gen3_bytes is empty")
                raise Exception("3gen overlay buffer is empty")

            # Create image from blob and composite
            overlay_scale = 0.67  # 66.66% scale for 4gen
            with Image(blob=gen3_bytes) as gen3_overlay:
                overlay_size = int(content_img.width * overlay_scale)
                gen3_overlay.resize(overlay_size, overlay_size)

                # Center the overlay
                overlay_x = (content_img.width - overlay_size) // 2
                overlay_y = (content_img.height - overlay_size) // 2

                content_img.composite(gen3_overlay, left=overlay_x, top=overlay_y)
                print(
                    f"DEBUG: Composited 3gen overlay onto 4gen image at ({overlay_x}, {overlay_y}) with size {overlay_size}"
                )

            # =============================================
            # Return the appropriate format
            # =============================================

            if template == "preview":
                print("DEBUG: Returning preview image")
                gen4_image_buffer = BytesIO()
                content_img.save(file=gen4_image_buffer)
                gen4_image_buffer.seek(0)
                return gen4_image_buffer
            else:  # final
                print("DEBUG: Compositing content onto PDF base template")

                # Load the PDF base template
                base_template_path = os.path.join(
                    settings.BASE_DIR,
                    "apps/charts/static/charts/images/base_image_templates",
                    "US_LETTER_4GEN_BW.pdf",
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
        logger.error(f"Error generating 4gen preview: {e}")
        raise


def get_great_grandparents(primary_individual, family_data):
    """
    Get all great-grandparents for the primary individual.

    Returns:
        List of great-grandparent individuals in order
    """
    great_grandparents = []

    # Get parents
    father = None
    mother = None

    if hasattr(primary_individual, "father") and primary_individual.father:
        father = family_data["individuals"].get(primary_individual.father)

    if hasattr(primary_individual, "mother") and primary_individual.mother:
        mother = family_data["individuals"].get(primary_individual.mother)

    # Get grandparents through parents
    grandparents = []

    if father:
        if hasattr(father, "father") and father.father:
            grandparents.append(family_data["individuals"].get(father.father))
        if hasattr(father, "mother") and father.mother:
            grandparents.append(family_data["individuals"].get(father.mother))

    if mother:
        if hasattr(mother, "father") and mother.father:
            grandparents.append(family_data["individuals"].get(mother.father))
        if hasattr(mother, "mother") and mother.mother:
            grandparents.append(family_data["individuals"].get(mother.mother))

    # Get great-grandparents through grandparents
    for grandparent in grandparents:
        if grandparent:
            if hasattr(grandparent, "father") and grandparent.father:
                great_grandparents.append(
                    family_data["individuals"].get(grandparent.father)
                )
            if hasattr(grandparent, "mother") and grandparent.mother:
                great_grandparents.append(
                    family_data["individuals"].get(grandparent.mother)
                )

    # Filter out None values and return
    return [gp for gp in great_grandparents if gp is not None]


def get_name_display_info(full_name):
    """Get name display information (compatibility function)."""
    from apps.generator.utils.name_utils import (
        get_name_display_info as utils_get_display_info,
    )

    return utils_get_display_info(full_name)
