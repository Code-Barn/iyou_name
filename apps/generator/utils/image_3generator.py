"""
Working 3-generation chart generator using template overlay approach.

This generator creates a 3-generation chart by:
1. Drawing grandparents on the 3gen template
2. Overlaying a 2gen chart (primary + parents) in the center
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


def generate_3gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 3-generation family tree chart using proven overlay approach.

    This version:
    1. Draws grandparents using edge positioning on 3gen template
    2. Generates 2gen overlay with PRIMARY and PARENT settings
    3. Composites them together like the working 2gen approach

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type ('3gen' for 3-generation chart)
        user_settings: Dictionary of user settings to override hardcoded defaults

    Returns:
        BytesIO buffer containing the generated image (PNG for preview, PDF for final)
    """
    # Get user settings or use empty dict if not provided
    user_settings = user_settings or {}

    print(f"DEBUG: generate_3gen_preview received user_settings: {user_settings}")
    print(f"DEBUG: Generating template type: {template}")

    # Extract GRANDPARENT settings for 3gen-specific drawing
    grandparent_settings = extract_generation_settings(user_settings, "GRANDPARENT")
    print(f"DEBUG: Extracted GRANDPARENT settings: {grandparent_settings}")

    print(
        f"DEBUG: Generating 3-generation family tree for: {primary_individual.full_name}"
    )
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    try:
        # Load the 3gen template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "3GEN_PREVIEW.png",
        )

        print(f"DEBUG: Preview template path: {preview_template_path}")
        print(
            f"DEBUG: Preview template exists: {os.path.exists(preview_template_path)}"
        )

        with Image(filename=preview_template_path, resolution=300) as content_img:
            print(f"Content image loaded: {content_img.width}x{content_img.height}")

            # =============================================
            # GRANDPARENT GENERATION DRAWING
            # =============================================

            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                print(f"DEBUG: User settings for preview: {user_settings}")

                # Apply grandparent-specific settings with fallback to user_settings
                font_family = grandparent_settings.get(
                    "font_family", user_settings.get("font_family", "Arial")
                )
                draw.font = font_family
                draw.stroke_antialias = True
                draw.stroke_width = grandparent_settings.get(
                    "default_stroke_width",
                    user_settings.get("default_stroke_width", 0.5),
                )

                # Set grandparent stroke color
                grandparent_stroke_color = grandparent_settings.get(
                    "primary_stroke_color",
                    user_settings.get("primary_stroke_color", "#000000"),
                )
                draw.stroke_color = Color(grandparent_stroke_color)

                # Get family relationships using correct attribute names
                father = None
                mother = None

                if hasattr(primary_individual, "father") and primary_individual.father:
                    father = family_data["individuals"].get(primary_individual.father)

                if hasattr(primary_individual, "mother") and primary_individual.mother:
                    mother = family_data["individuals"].get(primary_individual.mother)

                # Get grandparents
                paternal_grandfather = None
                paternal_grandmother = None
                maternal_grandfather = None
                maternal_grandmother = None

                if father and hasattr(father, "father") and father.father:
                    paternal_grandfather = family_data["individuals"].get(father.father)

                if father and hasattr(father, "mother") and father.mother:
                    paternal_grandmother = family_data["individuals"].get(father.mother)

                if mother and hasattr(mother, "father") and mother.father:
                    maternal_grandfather = family_data["individuals"].get(mother.father)

                if mother and hasattr(mother, "mother") and mother.mother:
                    maternal_grandmother = family_data["individuals"].get(mother.mother)

                print(
                    f"DEBUG: Found grandparents - PGF: {paternal_grandfather is not None}, PGM: {paternal_grandmother is not None}, MGF: {maternal_grandfather is not None}, MGM: {maternal_grandmother is not None}"
                )

                # Grandparent positioning settings
                font_size = grandparent_settings.get(
                    "primary_name_font_size",
                    user_settings.get("primary_name_font_size", 40),
                )
                draw.font_size = font_size
                edge_distance = grandparent_settings.get(
                    "primary_translate_x", user_settings.get("primary_translate_x", 30)
                )
                date_distance = grandparent_settings.get(
                    "primary_birth_translate_y",
                    user_settings.get("primary_birth_translate_y", 15),
                )

                # Draw grandparents along edges with proper rotation and centering
                # Canvas center for positioning
                center_x = content_img.width // 2
                center_y = content_img.height // 2
                radius = center_x - edge_distance  # Distance from center to edge

                grandparents = [
                    (
                        paternal_grandfather,
                        "paternal_grandfather",
                        0,
                    ),  # Bottom edge - 0 degrees
                    (
                        paternal_grandmother,
                        "paternal_grandmother",
                        -90,
                    ),  # Right edge - -90 degrees
                    (
                        maternal_grandfather,
                        "maternal_grandfather",
                        -180,
                    ),  # Top edge - -180 degrees
                    (
                        maternal_grandmother,
                        "maternal_grandmother",
                        -270,
                    ),  # Left edge - -270 degrees
                ]

                for grandparent, gp_type, rotation in grandparents:
                    if grandparent:
                        print(
                            f"Drawing {gp_type}: {grandparent.full_name} at {rotation}° rotation"
                        )

                        # Set grandparent font color
                        grandparent_font_color = grandparent_settings.get(
                            "primary_font_color",
                            user_settings.get("primary_font_color", "#000000"),
                        )
                        draw.fill_color = Color(grandparent_font_color)

                        # Calculate position on the edge based on rotation
                        angle_rad = math.radians(rotation)
                        edge_x = center_x + radius * math.cos(angle_rad)
                        edge_y = center_y + radius * math.sin(angle_rad)

                        # Parse name using improved logic
                        first_name, middle_name, last_name = parse_name_parts(
                            grandparent.full_name
                        )

                        # Draw grandparent name parts centered on edge with rotation
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
                            draw.translate(int(edge_x), int(edge_y) - 30)
                            # Apply rotation
                            draw.rotate(rotation)
                            # Center the text
                            draw.text(0, 0, last_name)
                            print(
                                f"Drew {gp_type} last name: '{last_name}' at ({int(edge_x)}, {int(edge_y) - 30}) with {rotation}° rotation"
                            )
                            draw.pop()

                        # Draw birth date if available
                        if grandparent.birth_date:
                            draw.push()
                            # Translate to edge position with offset for date
                            draw.translate(int(edge_x), int(edge_y) + date_distance)
                            # Apply rotation
                            draw.rotate(rotation)
                            # Smaller font for dates
                            draw.font_size = int(font_size * 0.7)
                            # Center the text
                            draw.text(0, 0, grandparent.birth_date)
                            print(
                                f"Drew {gp_type} birth date: '{grandparent.birth_date}' at ({int(edge_x)}, {int(edge_y)} + {date_distance}) with {rotation}° rotation"
                            )
                            draw.pop()

                # Apply the drawing to the image before destroying the context
                draw(content_img)
                draw.pop()

            # =============================================
            # Generate the 2gen overlay with PRIMARY and PARENT settings
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
                    f"DEBUG: Using stored primary settings for 2gen overlay: {primary_settings}"
                )

            print(
                f"DEBUG: Getting cached 2gen overlay with settings: {primary_settings}"
            )
            gen2_img_buffer = buffer_manager.get_buffer(2)

            if gen2_img_buffer is None:
                print("WARNING: No cached 2gen buffer found, generating fresh overlay")
                # Fallback: generate fresh 2gen overlay if no cached buffer
                from apps.generator.utils.image_2generator import generate_2gen_preview

                gen2_img_buffer = generate_2gen_preview(
                    primary_individual, family_data, "preview", user_settings
                )

            if gen2_img_buffer is None:
                print("ERROR: 2gen overlay buffer is None")
                raise Exception("Failed to generate 2gen overlay")

            print(f"DEBUG: Generated 2gen overlay buffer: {type(gen2_img_buffer)}")

            # =============================================
            # Composite the 2gen overlay onto the 3gen image
            # =============================================

            gen2_img_buffer.seek(0)  # Reset buffer position
            gen2_bytes = gen2_img_buffer.getvalue()

            if not gen2_bytes:
                print("ERROR: gen2_bytes is empty")
                raise Exception("2gen overlay buffer is empty")

            # Create image from blob and composite
            overlay_scale = 0.5485  # 53.85% scale like the working backup
            with Image(blob=gen2_bytes) as gen2_overlay:
                overlay_size = int(content_img.width * overlay_scale)
                gen2_overlay.resize(overlay_size, overlay_size)

                # Center the overlay
                overlay_x = (content_img.width - overlay_size) // 2
                overlay_y = (content_img.height - overlay_size) // 2

                content_img.composite(gen2_overlay, left=overlay_x, top=overlay_y)
                print(
                    f"DEBUG: Composited 2gen overlay onto 3gen image at ({overlay_x}, {overlay_y}) with size {overlay_size}"
                )

            # =============================================
            # Return the appropriate format
            # =============================================

            if template == "preview":
                print("DEBUG: Returning preview image")
                gen3_image_buffer = BytesIO()
                content_img.save(file=gen3_image_buffer)
                gen3_image_buffer.seek(0)
                return gen3_image_buffer
            else:  # final
                print("DEBUG: Compositing content onto PDF base template")

                # Load the PDF base template
                base_template_path = os.path.join(
                    settings.BASE_DIR,
                    "apps/charts/static/charts/images/base_image_templates",
                    "US_LETTER_3GEN_BW.pdf",
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
        logger.error(f"Error generating 3gen preview: {e}")
        raise


def get_name_display_info(full_name):
    """Get name display information (compatibility function)."""
    from apps.generator.utils.name_utils import (
        get_name_display_info as utils_get_display_info,
    )

    return utils_get_display_info(full_name)
