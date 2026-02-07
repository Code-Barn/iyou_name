"""
7-generation chart generator using template overlay approach.

This generator creates a 7-generation chart by:
1. Drawing 4x great-grandparents on the 7gen template
2. Overlaying a 6gen chart (primary + parents + grandparents + great-grandparents + 2x great-grandparents + 3x great-grandparents) in the center
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


def generate_7gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 7-generation family tree chart using proven overlay approach.

    This version:
    1. Draws 4x great-grandparents using edge positioning on 7gen template
    2. Generates 6gen overlay with all previous generation settings
    3. Composites them together like the working 6gen approach

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type ('7gen' for 7-generation chart)
        user_settings: Dictionary of user settings to override hardcoded defaults

    Returns:
        BytesIO buffer containing the generated image (PNG for preview, PDF for final)
    """
    # Get user settings or use empty dict if not provided
    user_settings = user_settings or {}

    print(f"DEBUG: generate_7gen_preview received user_settings: {user_settings}")
    print(f"DEBUG: Generating template type: {template}")

    # Extract 4XGREATGRANDPARENT settings for 7gen-specific drawing
    fourx_greatgrandparent_settings = extract_generation_settings(
        user_settings, "4XGREATGRANDPARENT"
    )
    print(
        f"DEBUG: Extracted 4XGREATGRANDPARENT settings: {fourx_greatgrandparent_settings}"
    )

    print(
        f"DEBUG: Generating 7-generation family tree for: {primary_individual.full_name}"
    )
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    try:
        # Load the 7gen template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "7GEN_PREVIEW.png",
        )

        print(f"DEBUG: Preview template path: {preview_template_path}")
        print(
            f"DEBUG: Preview template exists: {os.path.exists(preview_template_path)}"
        )

        with Image(filename=preview_template_path, resolution=300) as content_img:
            print(f"Content image loaded: {content_img.width}x{content_img.height}")

            # =============================================
            # 4X GREAT-GRANDPARENT GENERATION DRAWING
            # =============================================

            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                print(f"DEBUG: User settings for preview: {user_settings}")

                # Apply 4x great-grandparent-specific settings with fallback to user_settings
                font_family = fourx_greatgrandparent_settings.get(
                    "font_family", user_settings.get("font_family", "Arial")
                )
                draw.font = font_family
                draw.stroke_antialias = True
                draw.stroke_width = fourx_greatgrandparent_settings.get(
                    "default_stroke_width",
                    user_settings.get("default_stroke_width", 0.5),
                )

                # Set 4x great-grandparent stroke color
                fourx_greatgrandparent_stroke_color = (
                    fourx_greatgrandparent_settings.get(
                        "primary_stroke_color",
                        user_settings.get("primary_stroke_color", "#000000"),
                    )
                )
                draw.stroke_color = Color(fourx_greatgrandparent_stroke_color)

                # Get family relationships to find 4x great-grandparents
                fourx_great_grandparents = get_4x_great_grandparents(
                    primary_individual, family_data
                )

                print(
                    f"DEBUG: Found {len(fourx_great_grandparents)} 4x great-grandparents"
                )

                # 4x Great-grandparent positioning settings
                font_size = fourx_greatgrandparent_settings.get(
                    "primary_name_font_size",
                    user_settings.get("primary_name_font_size", 16),
                )
                draw.font_size = font_size
                edge_distance = fourx_greatgrandparent_settings.get(
                    "primary_translate_x", user_settings.get("primary_translate_x", 8)
                )
                date_distance = fourx_greatgrandparent_settings.get(
                    "primary_birth_translate_y",
                    user_settings.get("primary_birth_translate_y", 6),
                )

                # Draw 4x great-grandparents along edges with proper rotation and centering
                # Canvas center for positioning
                center_x = content_img.width // 2
                center_y = content_img.height // 2
                radius = center_x - edge_distance  # Distance from center to edge

                # Position 4x great-grandparents at 64 compass points (for 128 individuals)
                positions = []
                for i in range(64):
                    angle = -i * 5.625  # 360/64 = 5.625 degrees between positions
                    positions.append((angle, i))

                for rotation, index in positions:
                    if (
                        index < len(fourx_great_grandparents)
                        and fourx_great_grandparents[index]
                    ):
                        fourx_great_grandparent = fourx_great_grandparents[index]
                        gp_type = f"4x_great_grandparent_{index}"

                        print(
                            f"Drawing {gp_type}: {fourx_great_grandparent.full_name} at {rotation}° rotation"
                        )

                        # Set 4x great-grandparent font color
                        fourx_greatgrandparent_font_color = (
                            fourx_greatgrandparent_settings.get(
                                "primary_font_color",
                                user_settings.get("primary_font_color", "#000000"),
                            )
                        )
                        draw.fill_color = Color(fourx_greatgrandparent_font_color)

                        # Calculate position on the edge based on rotation
                        angle_rad = math.radians(rotation)
                        edge_x = center_x + radius * math.cos(angle_rad)
                        edge_y = center_y + radius * math.sin(angle_rad)

                        # Parse name using improved logic
                        first_name, middle_name, last_name = parse_name_parts(
                            fourx_great_grandparent.full_name
                        )

                        # Draw 4x great-grandparent name parts centered on edge with rotation
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
                            draw.translate(int(edge_x), int(edge_y) - 16)
                            # Apply rotation
                            draw.rotate(rotation)
                            # Center the text
                            draw.text(0, 0, last_name)
                            print(
                                f"Drew {gp_type} last name: '{last_name}' at ({int(edge_x)}, {int(edge_y) - 16}) with {rotation}° rotation"
                            )
                            draw.pop()

                        # Draw birth date if available
                        if fourx_great_grandparent.birth_date:
                            draw.push()
                            # Translate to edge position with offset for date
                            draw.translate(int(edge_x), int(edge_y) + date_distance)
                            # Apply rotation
                            draw.rotate(rotation)
                            # Smaller font for dates
                            draw.font_size = int(font_size * 0.5)
                            # Center the text
                            draw.text(0, 0, fourx_great_grandparent.birth_date)
                            print(
                                f"Drew {gp_type} birth date: '{fourx_great_grandparent.birth_date}' at ({int(edge_x)}, {int(edge_y)} + {date_distance}) with {rotation}° rotation"
                            )
                            draw.pop()

                # Apply the drawing to the image before destroying the context
                draw(content_img)
                draw.pop()

            # =============================================
            # Generate the 6gen overlay with all previous generation settings
            # =============================================

            # Extract settings for overlay generation (like 2gen and 3gen do)
            primary_settings = user_settings.get("primary_settings", {})
            if not primary_settings:
                primary_settings = extract_generation_settings(user_settings, "PRIMARY")

            print(
                f"DEBUG: Generating 6gen overlay with primary settings: {primary_settings}"
            )

            # Generate fresh 6gen overlay with current settings (not from cache)
            from apps.generator.utils.image_6generator import generate_6gen_preview

            gen6_img_buffer = generate_6gen_preview(
                primary_individual, family_data, "preview", primary_settings
            )

            if gen6_img_buffer is None:
                print("ERROR: 6gen overlay buffer is None")
                raise Exception("Failed to generate 6gen overlay")

            print(f"DEBUG: Generated 6gen overlay buffer: {type(gen6_img_buffer)}")

            # =============================================
            # Composite the 6gen overlay onto the 7gen image - VITAL COMPOSITE FUNCTION
            # =============================================

            gen6_img_buffer.seek(0)  # Reset buffer position
            gen6_bytes = gen6_img_buffer.getvalue()

            if not gen6_bytes:
                print("ERROR: gen6_bytes is empty")
                raise Exception("6gen overlay buffer is empty")

            # Create image from blob and composite
            overlay_scale = 0.8333  # 83.33% scale for 7gen
            with Image(blob=gen6_bytes) as gen6_overlay:
                overlay_size = int(content_img.width * overlay_scale)
                gen6_overlay.resize(overlay_size, overlay_size)

                # Center the overlay
                overlay_x = (content_img.width - overlay_size) // 2
                overlay_y = (content_img.height - overlay_size) // 2

                content_img.composite(gen6_overlay, left=overlay_x, top=overlay_y)
                print(
                    f"DEBUG: Composited 6gen overlay onto 7gen image at ({overlay_x}, {overlay_y}) with size {overlay_size}"
                )

            # =============================================
            # Return the appropriate format
            # =============================================

            if template == "preview":
                print("DEBUG: Returning preview image")
                gen7_image_buffer = BytesIO()
                content_img.save(file=gen7_image_buffer)
                gen7_image_buffer.seek(0)
                return gen7_image_buffer
            else:  # final
                print("DEBUG: Compositing content onto PDF base template")

                # Load the PDF base template
                base_template_path = os.path.join(
                    settings.BASE_DIR,
                    "apps/charts/static/charts/images/base_image_templates",
                    "US_LETTER_7GEN_BW.pdf",
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
        logger.error(f"Error generating 7gen preview: {e}")
        raise


def get_4x_great_grandparents(primary_individual, family_data):
    """
    Get all 4x great-grandparents for the primary individual.

    Returns:
        List of 4x great-grandparent individuals in order
    """
    fourx_great_grandparents = []

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
    great_grandparents = []
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

    # Get 2x great-grandparents through great-grandparents
    twox_great_grandparents = []
    for great_grandparent in great_grandparents:
        if great_grandparent:
            if hasattr(great_grandparent, "father") and great_grandparent.father:
                twox_great_grandparents.append(
                    family_data["individuals"].get(great_grandparent.father)
                )
            if hasattr(great_grandparent, "mother") and great_grandparent.mother:
                twox_great_grandparents.append(
                    family_data["individuals"].get(great_grandparent.mother)
                )

    # Get 3x great-grandparents through 2x great-grandparents
    threex_great_grandparents = []
    for twox_great_grandparent in twox_great_grandparents:
        if twox_great_grandparent:
            if (
                hasattr(twox_great_grandparent, "father")
                and twox_great_grandparent.father
            ):
                threex_great_grandparents.append(
                    family_data["individuals"].get(twox_great_grandparent.father)
                )
            if (
                hasattr(twox_great_grandparent, "mother")
                and twox_great_grandparent.mother
            ):
                threex_great_grandparents.append(
                    family_data["individuals"].get(twox_great_grandparent.mother)
                )

    # Get 4x great-grandparents through 3x great-grandparents
    for threex_great_grandparent in threex_great_grandparents:
        if threex_great_grandparent:
            if (
                hasattr(threex_great_grandparent, "father")
                and threex_great_grandparent.father
            ):
                fourx_great_grandparents.append(
                    family_data["individuals"].get(threex_great_grandparent.father)
                )
            if (
                hasattr(threex_great_grandparent, "mother")
                and threex_great_grandparent.mother
            ):
                fourx_great_grandparents.append(
                    family_data["individuals"].get(threex_great_grandparent.mother)
                )

    # Filter out None values and return
    return [gp for gp in fourx_great_grandparents if gp is not None]


def get_name_display_info(full_name):
    """Get name display information (compatibility function)."""
    from apps.generator.utils.name_utils import (
        get_name_display_info as utils_get_display_info,
    )

    return utils_get_display_info(full_name)


# Legacy function for backward compatibility
def generate_family_tree(primary_individual, family_data, template="7gen"):
    """Legacy wrapper for backward compatibility."""
    return generate_7gen_preview(primary_individual, family_data, template, None)
