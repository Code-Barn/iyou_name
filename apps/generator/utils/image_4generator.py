import logging
import math
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.image_3generator import generate_3gen_preview
from apps.generator.utils.name_utils import get_name_display_info
from apps.generator.utils.settings_validator import (
    get_validated_settings,
    GenerationError,
)
from apps.generator.utils.buffer_manager import (
    create_preview_buffer,
    create_pdf_buffer,
    BufferError,
)

logger = logging.getLogger(__name__)


# Constants extracted from magic numbers
class Generation4Constants:
    """Constants for 4-generation chart generation."""

    # Canvas dimensions
    CANVAS_WIDTH = 1950
    CANVAS_HEIGHT = 1950

    # Great-grandparent positioning
    EDGE_DISTANCE_DEFAULT = 20
    DATE_DISTANCE_DEFAULT = 12
    LAST_NAME_OFFSET = 25

    # 8-point compass positioning
    COMPASS_POSITIONS = [
        (0, 0),  # Bottom
        (-45, 1),  # Bottom-right
        (-90, 2),  # Right
        (-135, 3),  # Top-right
        (-180, 4),  # Top
        (-225, 5),  # Top-left
        (-270, 6),  # Left
        (-315, 7),  # Bottom-left
    ]

    # Overlay composition
    OVERLAY_SCALE = 0.67  # 66.66% scale for 4gen

    # PDF compositing
    COMPOSITE_X = 300
    COMPOSITE_Y = 570

    # DPI settings
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72  # Approx 4.1667

    # Text rendering
    MULTILINE_LINE_HEIGHT_RATIO = 1.2
    DATE_FONT_SIZE_RATIO = 0.7


# Settings schema for validation
GENERATION_4_SETTINGS_SCHEMA = {
    # Font settings
    "font_family": (str, "Arial"),
    # Great-grandparent generation styling
    "greatgrandparent_stroke_color": (Color, "black"),
    "greatgrandparent_font_color": (Color, "black"),
    "greatgrandparent_stroke_width": (float, 0.5),
    # Great-grandparent-specific settings
    "greatgrandparent_font_size": (int, 32),
    "greatgrandparent_translate_x": (int, 0),
    "greatgrandparent_translate_y": (int, 0),
    "greatgrandparent_rotate": (int, 0),
    "greatgrandparent_edge_distance": (int, 20),
    "greatgrandparent_date_distance": (int, 12),
    "greatgrandparent_birth_translate_x": (int, 0),
    "greatgrandparent_birth_translate_y": (int, 0),
    "greatgrandparent_birth_rotate": (int, 0),
    "greatgrandparent_death_translate_x": (int, 0),
    "greatgrandparent_death_translate_y": (int, 0),
    "greatgrandparent_death_rotate": (int, 0),
    # Information styling
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    # Overlay settings
    "overlay_scale": (float, 0.67),
    "overlay_position_x": (int, 0),  # Centered
    "overlay_position_y": (int, 0),  # Centered
}


def generate_4gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 4-generation family tree chart using enhanced standardized patterns.

    This enhanced version follows the same standardization patterns as the 1gen, 2gen, and 3gen generators:
    - Settings validation framework
    - Clean buffer management
    - Consistent logging (no debug prints)
    - Constants extraction
    - Enhanced error handling
    - Mathematical edge positioning
    - 3gen overlay integration

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
        user_settings, GENERATION_4_SETTINGS_SCHEMA, "4gen"
    )

    logger.info(
        f"Generating 4-generation {template} chart for: {primary_individual.full_name} "
        f"(ID: {primary_individual.id})"
    )

    try:
        # Load the 4gen template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "4GEN_PREVIEW.png",
        )

        if not os.path.exists(preview_template_path):
            raise GenerationError(
                f"Preview template not found: {preview_template_path}"
            )

        logger.debug(f"Loading preview template: {preview_template_path}")

        with Image(
            filename=preview_template_path, resolution=Generation4Constants.RESOLUTION
        ) as content_img:
            logger.debug(
                f"Content image loaded: {content_img.width}x{content_img.height}"
            )

            # Draw great-grandparent generation
            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings["greatgrandparent_stroke_width"]
                draw.stroke_color = validated_settings["greatgrandparent_stroke_color"]

                # Draw great-grandparents
                _draw_great_grandparents(
                    draw,
                    content_img,
                    primary_individual,
                    family_data,
                    validated_settings,
                )

                # Apply drawing to image
                draw(content_img)

            # Generate 3gen overlay with PRIMARY settings
            primary_settings = _extract_primary_settings(user_settings)
            logger.debug(
                f"Generating 3gen overlay with settings: {len(primary_settings)} settings"
            )

            gen3_img_buffer = generate_3gen_preview(
                primary_individual, family_data, "preview", primary_settings
            )

            # Composite the 3gen overlay onto the 4gen image
            _composite_overlay(content_img, gen3_img_buffer, validated_settings)

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
        logger.error(f"Unexpected error in 4gen generation: {e}")
        raise GenerationError(f"4-generation chart generation failed: {e}")


def _draw_great_grandparents(
    draw, content_img, primary_individual, family_data, validated_settings
):
    """Draw the great-grandparent generation with mathematical edge positioning."""

    # Get great-grandparents from family data
    great_grandparents = get_great_grandparents(primary_individual, family_data)

    if not great_grandparents:
        logger.debug("No great-grandparents found in family data")
        return

    logger.debug(f"Found {len(great_grandparents)} great-grandparents")

    # Set great-grandparent drawing properties
    font_size = validated_settings["greatgrandparent_font_size"]
    draw.font_size = font_size
    draw.fill_color = validated_settings["greatgrandparent_font_color"]

    # Get positioning settings
    edge_distance = validated_settings.get(
        "greatgrandparent_edge_distance", Generation4Constants.EDGE_DISTANCE_DEFAULT
    )
    date_distance = validated_settings.get(
        "greatgrandparent_date_distance", Generation4Constants.DATE_DISTANCE_DEFAULT
    )

    # Calculate canvas center and radius
    center_x = content_img.width // 2
    center_y = content_img.height // 2
    radius = center_x - edge_distance

    # Draw great-grandparents at 8 compass points
    for rotation, index in Generation4Constants.COMPASS_POSITIONS:
        if index < len(great_grandparents) and great_grandparents[index]:
            great_grandparent = great_grandparents[index]
            gp_type = f"great_grandparent_{index}"

            logger.debug(
                f"Drawing {gp_type}: {great_grandparent.full_name} at {rotation}° rotation"
            )

            # Calculate position on the edge based on rotation
            angle_rad = math.radians(rotation)
            edge_x = center_x + radius * math.cos(angle_rad)
            edge_y = center_y + radius * math.sin(angle_rad)

            # Draw great-grandparent with standardized name rendering
            _draw_great_grandparent_at_position(
                draw,
                great_grandparent,
                int(edge_x),
                int(edge_y),
                rotation,
                font_size,
                date_distance,
                validated_settings,
            )


def _draw_great_grandparent_at_position(
    draw,
    great_grandparent,
    edge_x,
    edge_y,
    rotation,
    font_size,
    date_distance,
    validated_settings,
):
    """Draw a single great-grandparent at the specified edge position."""

    # Get name display information using standardized approach
    name_info = get_name_display_info(great_grandparent.full_name)
    display_text = name_info["display_text"]

    # Draw name with multiline support using translation
    lines = display_text.split("\n")
    line_height = font_size * Generation4Constants.MULTILINE_LINE_HEIGHT_RATIO
    start_y = -(len(lines) - 1) * line_height / 2

    for i, line in enumerate(lines):
        line_y = start_y + (i * line_height)

        draw.push()
        draw.translate(edge_x, edge_y)
        draw.rotate(rotation)
        draw.text(0, int(round(line_y)), line)
        draw.pop()

    # Draw birth date if available
    if great_grandparent.birth_date:
        draw.push()
        draw.translate(edge_x, edge_y + date_distance)
        draw.rotate(rotation)
        draw.font_size = int(font_size * Generation4Constants.DATE_FONT_SIZE_RATIO)
        draw.text(0, 0, great_grandparent.birth_date)
        draw.pop()

    # Draw death date if available
    if great_grandparent.death_date:
        draw.push()
        draw.translate(edge_x, edge_y + date_distance + 15)
        draw.rotate(rotation)
        draw.font_size = int(font_size * Generation4Constants.DATE_FONT_SIZE_RATIO)
        draw.text(0, 0, great_grandparent.death_date)
        draw.pop()


def get_great_grandparents(primary_individual, family_data):
    """
    Get all great-grandparents for the primary individual.

    Returns:
        List of great-grandparent individuals in compass point order
    """
    great_grandparents = []

    # Get parents
    individuals = family_data.get("individuals", {})
    father_id = getattr(primary_individual, "father", None)
    mother_id = getattr(primary_individual, "mother", None)

    father = individuals.get(father_id) if father_id else None
    mother = individuals.get(mother_id) if mother_id else None

    # Get grandparents through parents
    grandparents = []

    if father:
        father_father_id = getattr(father, "father", None)
        father_mother_id = getattr(father, "mother", None)
        if father_father_id:
            grandparents.append(individuals.get(father_father_id))
        if father_mother_id:
            grandparents.append(individuals.get(father_mother_id))

    if mother:
        mother_father_id = getattr(mother, "father", None)
        mother_mother_id = getattr(mother, "mother", None)
        if mother_father_id:
            grandparents.append(individuals.get(mother_father_id))
        if mother_mother_id:
            grandparents.append(individuals.get(mother_mother_id))

    # Get great-grandparents through grandparents
    for grandparent in grandparents:
        if grandparent:
            gp_father_id = getattr(grandparent, "father", None)
            gp_mother_id = getattr(grandparent, "mother", None)
            if gp_father_id:
                great_grandparents.append(individuals.get(gp_father_id))
            if gp_mother_id:
                great_grandparents.append(individuals.get(gp_mother_id))

    # Filter out None values and return
    return [gp for gp in great_grandparents if gp is not None]


def _extract_primary_settings(user_settings):
    """Extract PRIMARY settings for 3gen overlay generation."""

    # Check for stored primary settings first (from JavaScript)
    primary_settings = user_settings.get("primary_settings", {})

    if not primary_settings:
        # Fallback to extracting PRIMARY from current settings
        from apps.generator.utils.settings_helper import extract_generation_settings

        primary_settings = extract_generation_settings(user_settings, "PRIMARY")
        logger.debug("Using fallback PRIMARY settings for 3gen overlay")
    else:
        logger.debug("Using stored primary settings for 3gen overlay")

    return primary_settings


def _composite_overlay(content_img, gen3_img_buffer, validated_settings):
    """Composite the 3gen overlay onto the 4gen image with enhanced buffer handling."""

    try:
        # Reset buffer position and get bytes
        gen3_img_buffer.seek(0)
        gen3_bytes = gen3_img_buffer.getvalue()

        if not gen3_bytes:
            raise BufferError("3gen overlay buffer is empty")

        # Get overlay settings
        overlay_scale = validated_settings.get(
            "overlay_scale", Generation4Constants.OVERLAY_SCALE
        )

        # Create image from blob and composite
        with Image(blob=gen3_bytes) as gen3_overlay:
            # Scale overlay
            overlay_size = int(content_img.width * overlay_scale)
            gen3_overlay.resize(overlay_size, overlay_size)

            # Center the overlay
            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            # Apply position offsets if specified
            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            # Composite onto content image
            content_img.composite(gen3_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 3gen overlay at ({overlay_x}, {overlay_y}) with scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


def _create_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""

    # Load PDF base template
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_4GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    logger.debug(f"Loading PDF base template: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation4Constants.RESOLUTION
    ) as base_img:
        logger.debug(f"Base template loaded: {base_img.width}x{base_img.height}")

        # Composite content image onto base template
        base_img.composite(
            content_img,
            left=Generation4Constants.COMPOSITE_X,
            top=Generation4Constants.COMPOSITE_Y,
        )

        logger.debug(
            f"Composited content at ({Generation4Constants.COMPOSITE_X}, {Generation4Constants.COMPOSITE_Y})"
        )

        # Create PDF buffer
        return create_pdf_buffer(base_img)
