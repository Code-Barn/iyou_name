import logging
import math
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.image_2generator import generate_2gen_preview
from apps.generator.utils.name_utils import get_name_display_info
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


# Constants extracted from magic numbers
class Generation3Constants:
    """Constants for 3-generation chart generation."""

    # Canvas dimensions
    CANVAS_WIDTH = 1923
    CANVAS_HEIGHT = 1923

    # Initial translation
    INITIAL_TRANSLATE_X = 0
    INITIAL_TRANSLATE_Y = 0

    # Grandparent positioning
    CENTER_X = 961  # Canvas center
    CENTER_Y = 961  # Canvas center
    RADIUS = 931  # Distance from center to edge

    # Edge positioning
    EDGE_DISTANCE = 30
    DATE_DISTANCE = 15

    # Font sizes
    GRANDPARENT_NAME_FONT_SIZE = 40
    GRANDPARENT_DATE_INFO_FONT_SIZE = 28
    GRANDPARENT_PLACE_INFO_FONT_SIZE = 20

    # Overlay composition
    OVERLAY_SCALE = 0.60  # 60% scale for 3gen overlay

    # PDF compositing
    COMPOSITE_X = 300
    COMPOSITE_Y = 570

    # DPI settings
    RESOLUTION = 300

    # Text rendering
    MULTILINE_LINE_HEIGHT_RATIO = 1.2
    NAME_OFFSET_Y = 30  # Offset between first and last name


# Settings schema for validation
GENERATION_3_SETTINGS_SCHEMA = {
    # Font settings
    "font_family": (str, "Arial"),
    # Grandparent generation styling
    "grandparent_stroke_color": (Color, "black"),
    "grandparent_font_color": (Color, "black"),
    "grandparent_stroke_width": (float, 0.5),
    # Grandparent-specific settings
    "grandparent_name_font_size": (int, 40),
    "grandparent_date_info_font_size": (int, 28),
    "grandparent_place_info_font_size": (int, 20),
    # Paternal grandfather settings
    "paternal_grandfather_font_color": (Color, "black"),
    "paternal_grandfather_stroke_color": (Color, "black"),
    "paternal_grandfather_font_size": (int, 40),
    "paternal_grandfather_translate_x": (int, 0),
    "paternal_grandfather_translate_y": (int, 0),
    "paternal_grandfather_rotate": (int, 0),
    # Paternal grandmother settings
    "paternal_grandmother_font_color": (Color, "black"),
    "paternal_grandmother_stroke_color": (Color, "black"),
    "paternal_grandmother_font_size": (int, 40),
    "paternal_grandmother_translate_x": (int, 0),
    "paternal_grandmother_translate_y": (int, 0),
    "paternal_grandmother_rotate": (int, 0),
    # Maternal grandfather settings
    "maternal_grandfather_font_color": (Color, "black"),
    "maternal_grandfather_stroke_color": (Color, "black"),
    "maternal_grandfather_font_size": (int, 40),
    "maternal_grandfather_translate_x": (int, 0),
    "maternal_grandfather_translate_y": (int, 0),
    "maternal_grandfather_rotate": (int, 0),
    # Maternal grandmother settings
    "maternal_grandmother_font_color": (Color, "black"),
    "maternal_grandmother_stroke_color": (Color, "black"),
    "maternal_grandmother_font_size": (int, 40),
    "maternal_grandmother_translate_x": (int, 0),
    "maternal_grandmother_translate_y": (int, 0),
    "maternal_grandmother_rotate": (int, 0),
    # Information styling
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    # Birth information
    "grandparent_birth_color": (Color, "black"),
    "grandparent_birth_place_color": (Color, "black"),
    "grandparent_birth_translate_x": (int, 0),
    "grandparent_birth_translate_y": (int, 0),
    "grandparent_birth_rotate": (int, 0),
    "grandparent_birth_place_translate_x": (int, 0),
    "grandparent_birth_place_translate_y": (int, 0),
    "grandparent_birth_place_rotate": (int, 0),
    # Death information
    "grandparent_death_color": (Color, "black"),
    "grandparent_death_place_color": (Color, "black"),
    "grandparent_death_translate_x": (int, 0),
    "grandparent_death_translate_y": (int, 0),
    "grandparent_death_rotate": (int, 0),
    "grandparent_death_place_translate_x": (int, 0),
    "grandparent_death_place_translate_y": (int, 0),
    "grandparent_death_place_rotate": (int, 0),
    # Overlay settings
    "overlay_scale": (float, 0.60),
    "overlay_position_x": (int, 0),  # Will be calculated for centering
    "overlay_position_y": (int, 0),  # Will be calculated for centering
}


def generate_3gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 3-generation family tree chart using enhanced standardized patterns.

    This enhanced version follows the same standardization patterns as the 1gen and 2gen generators:
    - Settings validation framework
    - Clean buffer management
    - Consistent logging (no debug prints)
    - Constants extraction
    - Enhanced error handling
    - Mathematical edge positioning for grandparents
    - 2gen overlay integration

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type ('preview' for PNG preview, 'final' for PDF final chart)
        user_settings: Dictionary of user settings to override hardcoded defaults

    Returns:
        BytesIO buffer containing the generated image (PNG for preview, PDF for final)

    Raises:
        GenerationError: If chart generation fails
        BufferError: If buffer operations fail
    """
    # Validate and process settings
    user_settings = user_settings or {}
    validated_settings = get_validated_settings(
        user_settings, GENERATION_3_SETTINGS_SCHEMA, "3gen"
    )

    logger.info(
        f"Generating 3-generation {template} chart for: {primary_individual.full_name} "
        f"(ID: {primary_individual.id})"
    )

    try:
        # Load the 3gen template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "3GEN_PREVIEW.png",
        )

        if not os.path.exists(preview_template_path):
            raise GenerationError(
                f"Preview template not found: {preview_template_path}"
            )

        logger.debug(f"Loading preview template: {preview_template_path}")

        with Image(
            filename=preview_template_path, resolution=Generation3Constants.RESOLUTION
        ) as content_img:
            logger.debug(
                f"Content image loaded: {content_img.width}x{content_img.height}"
            )

            # Draw grandparent generation
            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings["grandparent_stroke_width"]
                draw.stroke_color = validated_settings["grandparent_stroke_color"]

                # Apply initial translation
                draw.translate(
                    x=Generation3Constants.INITIAL_TRANSLATE_X,
                    y=Generation3Constants.INITIAL_TRANSLATE_Y,
                )

                # Draw grandparents
                _draw_grandparents(
                    draw,
                    content_img,
                    primary_individual,
                    family_data,
                    validated_settings,
                )

                # Apply drawing to image
                draw(content_img)

            # Generate 2gen overlay with enhanced settings
            overlay_settings = _extract_overlay_settings(user_settings)
            logger.debug(
                f"Generating 2gen overlay with settings: {len(overlay_settings)} settings"
            )

            gen2_img_buffer = generate_2gen_preview(
                primary_individual, family_data, "preview", overlay_settings
            )

            # Composite the 2gen overlay onto the 3gen image
            _composite_overlay(content_img, gen2_img_buffer, validated_settings)

            # Generate output based on template type
            if template == "preview":
                return create_preview_buffer(content_img)
            elif template == "final":
                return _create_final_pdf(content_img, validated_settings)
            else:
                raise GenerationError(f"Unknown template type: {template}")

    except (GenerationError, BufferError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in 3gen generation: {e}")
        raise GenerationError(f"3-generation chart generation failed: {e}")


def _draw_grandparents(
    draw, content_img, primary_individual, family_data, validated_settings
):
    """Draw the grandparent generation with mathematical edge positioning."""

    # Get grandparents from family data
    individuals = family_data.get("individuals", {})

    # Get parents first
    father_id = getattr(primary_individual, "father", None)
    mother_id = getattr(primary_individual, "mother", None)

    father = individuals.get(father_id) if father_id else None
    mother = individuals.get(mother_id) if mother_id else None

    # Get grandparents
    paternal_grandfather = None
    paternal_grandmother = None
    maternal_grandfather = None
    maternal_grandmother = None

    if father and hasattr(father, "father") and father.father:
        paternal_grandfather = individuals.get(father.father)
    if father and hasattr(father, "mother") and father.mother:
        paternal_grandmother = individuals.get(father.mother)
    if mother and hasattr(mother, "father") and mother.father:
        maternal_grandfather = individuals.get(mother.father)
    if mother and hasattr(mother, "mother") and mother.mother:
        maternal_grandmother = individuals.get(mother.mother)

    # Define grandparents with mathematical edge positioning
    grandparents = [
        (paternal_grandfather, "paternal_grandfather", 0),  # Bottom edge (0°)
        (paternal_grandmother, "paternal_grandmother", -90),  # Right edge (-90°)
        (maternal_grandfather, "maternal_grandfather", -180),  # Top edge (-180°)
        (maternal_grandmother, "maternal_grandmother", -270),  # Left edge (-270°)
    ]

    # Draw grandparents along edges with mathematical positioning
    for grandparent, gp_type, rotation in grandparents:
        if grandparent:
            logger.debug(
                f"Drawing {gp_type}: {grandparent.full_name} at {rotation}° rotation"
            )

            # Set grandparent-specific colors and sizes
            prefix = f"{gp_type}_"

            font_color = validated_settings.get(f"{prefix}font_color", Color("black"))
            stroke_color = validated_settings.get(
                f"{prefix}stroke_color", Color("black")
            )
            font_size = validated_settings.get(
                f"{prefix}font_size", Generation3Constants.GRANDPARENT_NAME_FONT_SIZE
            )

            draw.fill_color = font_color
            draw.stroke_color = stroke_color
            draw.font_size = font_size

            # Calculate position on the edge using mathematical positioning
            angle_rad = math.radians(rotation)
            edge_distance = validated_settings.get(
                "edge_distance", Generation3Constants.EDGE_DISTANCE
            )
            radius = Generation3Constants.RADIUS - edge_distance

            edge_x = Generation3Constants.CENTER_X + radius * math.cos(angle_rad)
            edge_y = Generation3Constants.CENTER_Y + radius * math.sin(angle_rad)

            # Apply grandparent-specific translations
            translate_x = edge_x + validated_settings.get(f"{prefix}translate_x", 0)
            translate_y = edge_y + validated_settings.get(f"{prefix}translate_y", 0)

            # Draw grandparent with multiline name support
            _draw_grandparent(
                draw,
                grandparent,
                gp_type,
                translate_x,
                translate_y,
                rotation,
                validated_settings,
            )
        else:
            logger.debug(f"No {gp_type} found in family data")


def _draw_grandparent(draw, grandparent, gp_type, x, y, rotation, validated_settings):
    """Draw a single grandparent with standardized rendering."""

    # Apply rotation
    draw.push()
    draw.translate(x, y)
    draw.rotate(rotation)

    # Get name display information
    name_info = get_name_display_info(grandparent.full_name)
    display_text = name_info["display_text"]

    # Draw name with multiline support
    lines = display_text.split("\n")
    line_height = (
        validated_settings.get(
            "grandparent_name_font_size",
            Generation3Constants.GRANDPARENT_NAME_FONT_SIZE,
        )
        * Generation3Constants.MULTILINE_LINE_HEIGHT_RATIO
    )
    start_y = -(len(lines) - 1) * line_height / 2

    for i, line in enumerate(lines):
        line_y = start_y + (i * line_height)
        draw.push()
        draw.translate(0, line_y)
        draw.text(0, 0, line)
        draw.pop()

    draw.pop()

    # Draw birth information
    _draw_grandparent_birth_info(draw, grandparent, gp_type, x, y, validated_settings)

    # Draw death information if available
    if grandparent.death_date:
        _draw_grandparent_death_info(
            draw, grandparent, gp_type, x, y, validated_settings
        )


def _draw_grandparent_birth_info(draw, grandparent, gp_type, x, y, validated_settings):
    """Draw birth information for a grandparent."""

    prefix = f"{gp_type}_"
    birth_color = validated_settings.get(f"{prefix}birth_color", Color("black"))
    birth_place_color = validated_settings.get(
        f"{prefix}birth_place_color", Color("black")
    )

    # Draw birth date
    draw.push()
    draw.font_size = validated_settings.get(
        "grandparent_date_info_font_size",
        Generation3Constants.GRANDPARENT_DATE_INFO_FONT_SIZE,
    )
    draw.fill_color = birth_color

    birth_text = grandparent.birth_date or " "
    birth_translate_x = validated_settings.get(f"{prefix}birth_translate_x", 0)
    birth_translate_y = validated_settings.get(
        f"{prefix}birth_translate_y", Generation3Constants.DATE_DISTANCE
    )
    birth_rotate = validated_settings.get(f"{prefix}birth_rotate", 0)

    draw.translate(birth_translate_x, birth_translate_y)
    draw.rotate(birth_rotate)
    draw.text(0, 0, birth_text)
    draw.pop()

    # Draw birth place
    draw.push()
    draw.font_size = validated_settings.get(
        "grandparent_place_info_font_size",
        Generation3Constants.GRANDPARENT_PLACE_INFO_FONT_SIZE,
    )
    draw.fill_color = birth_place_color

    birth_place_text = grandparent.birth_place or " "
    birth_place_translate_x = validated_settings.get(
        f"{prefix}birth_place_translate_x", 0
    )
    birth_place_translate_y = validated_settings.get(
        f"{prefix}birth_place_translate_y", 0
    )
    birth_place_rotate = validated_settings.get(f"{prefix}birth_place_rotate", 0)

    draw.translate(birth_place_translate_x, birth_place_translate_y)
    draw.rotate(birth_place_rotate)
    draw.text(0, 0, birth_place_text)
    draw.pop()


def _draw_grandparent_death_info(draw, grandparent, gp_type, x, y, validated_settings):
    """Draw death information for a grandparent."""

    prefix = f"{gp_type}_"
    death_color = validated_settings.get(f"{prefix}death_color", Color("black"))
    death_place_color = validated_settings.get(
        f"{prefix}death_place_color", Color("black")
    )

    # Draw death date
    draw.push()
    draw.font_size = validated_settings.get(
        "grandparent_date_info_font_size",
        Generation3Constants.GRANDPARENT_DATE_INFO_FONT_SIZE,
    )
    draw.fill_color = death_color

    death_text = grandparent.death_date or " "
    death_translate_x = validated_settings.get(f"{prefix}death_translate_x", 0)
    death_translate_y = validated_settings.get(f"{prefix}death_translate_y", 0)
    death_rotate = validated_settings.get(f"{prefix}death_rotate", 0)

    draw.translate(death_translate_x, death_translate_y)
    draw.rotate(death_rotate)
    draw.text(0, 0, death_text)
    draw.pop()

    # Draw death place
    draw.push()
    draw.font_size = validated_settings.get(
        "grandparent_place_info_font_size",
        Generation3Constants.GRANDPARENT_PLACE_INFO_FONT_SIZE,
    )
    draw.fill_color = death_place_color

    death_place_text = grandparent.death_place or " "
    death_place_translate_x = validated_settings.get(
        f"{prefix}death_place_translate_x", 0
    )
    death_place_translate_y = validated_settings.get(
        f"{prefix}death_place_translate_y", 0
    )
    death_place_rotate = validated_settings.get(f"{prefix}death_place_rotate", 0)

    draw.translate(death_place_translate_x, death_place_translate_y)
    draw.rotate(death_place_rotate)
    draw.text(0, 0, death_place_text)
    draw.pop()


def _extract_overlay_settings(user_settings):
    """Extract settings for 2gen overlay generation."""

    # Check for stored primary settings first (from JavaScript)
    primary_settings = user_settings.get("primary_settings", {})

    if not primary_settings:
        # Fallback to extracting PRIMARY from current settings
        from apps.generator.utils.settings_helper import extract_generation_settings

        primary_settings = extract_generation_settings(user_settings, "PRIMARY")
        logger.debug("Using fallback PRIMARY settings for 2gen overlay")
    else:
        logger.debug("Using stored primary settings for 2gen overlay")

    return primary_settings


def _composite_overlay(content_img, gen2_img_buffer, validated_settings):
    """Composite the 2gen overlay onto the 3gen image with enhanced buffer handling."""

    try:
        # Reset buffer position and get bytes
        gen2_img_buffer.seek(0)
        gen2_bytes = gen2_img_buffer.getvalue()

        if not gen2_bytes:
            raise BufferError("2gen overlay buffer is empty")

        # Get overlay settings
        overlay_scale = validated_settings.get(
            "overlay_scale", Generation3Constants.OVERLAY_SCALE
        )

        # Create image from blob and composite
        with Image(blob=gen2_bytes) as gen2_overlay:
            # Scale overlay
            overlay_size = int(content_img.width * overlay_scale)
            gen2_overlay.resize(overlay_size, overlay_size)

            # Center the overlay
            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            # Apply position offsets if specified
            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            # Composite onto content image
            content_img.composite(gen2_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 2gen overlay at ({overlay_x}, {overlay_y}) with scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


def _create_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""

    # Load PDF base template
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_3GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    logger.debug(f"Loading PDF base template: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation3Constants.RESOLUTION
    ) as base_img:
        logger.debug(f"Base template loaded: {base_img.width}x{base_img.height}")

        # Composite content image onto base template
        base_img.composite(
            content_img,
            left=Generation3Constants.COMPOSITE_X,
            top=Generation3Constants.COMPOSITE_Y,
        )

        logger.debug(
            f"Composited content at ({Generation3Constants.COMPOSITE_X}, {Generation3Constants.COMPOSITE_Y})"
        )

        # Create PDF buffer
        return create_pdf_buffer(base_img)
