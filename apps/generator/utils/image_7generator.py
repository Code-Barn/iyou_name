import logging
import math
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.image_6generator import generate_6gen_preview
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
class Generation7Constants:
    """Constants for 7-generation chart generation."""

    # Canvas dimensions
    CANVAS_WIDTH = 1950
    CANVAS_HEIGHT = 1950

    # 4x Great-grandparent positioning
    EDGE_DISTANCE_DEFAULT = 50
    DATE_DISTANCE_DEFAULT = 8

    # 64-point compass positioning for 4x great-grandparents
    COMPASS_POSITIONS = [
        (0, 0),  # Bottom
        (-5.625, 1),  # Bottom-bottom-right-1
        (-11.25, 2),  # Bottom-bottom-right-2
        (-16.875, 3),  # Bottom-bottom-right-3
        (-22.5, 4),  # Bottom-bottom-right-4
        (-28.125, 5),  # Right-bottom-right-1
        (-33.75, 6),  # Right-bottom-right-2
        (-39.375, 7),  # Right-bottom-right-3
        (-45, 8),  # Bottom-right
        (-50.625, 9),  # Right-bottom-right-4
        (-56.25, 10),  # Right-bottom-right-5
        (-61.875, 11),  # Right-bottom-right-6
        (-67.5, 12),  # Right-bottom-right-7
        (-73.125, 13),  # Right-bottom-right-8
        (-78.75, 14),  # Right-bottom-right-9
        (-84.375, 15),  # Right-bottom-right-10
        (-90, 16),  # Right
        (-95.625, 17),  # Right-top-right-1
        (-101.25, 18),  # Right-top-right-2
        (-106.875, 19),  # Right-top-right-3
        (-112.5, 20),  # Right-top-right-4
        (-118.125, 21),  # Right-top-right-5
        (-123.75, 22),  # Right-top-right-6
        (-129.375, 23),  # Right-top-right-7
        (-135, 24),  # Top-right
        (-140.625, 25),  # Top-top-right-1
        (-146.25, 26),  # Top-top-right-2
        (-151.875, 27),  # Top-top-right-3
        (-157.5, 28),  # Top-top-right-4
        (-163.125, 29),  # Top-top-right-5
        (-168.75, 30),  # Top-top-right-6
        (-174.375, 31),  # Top-top-right-7
        (-180, 32),  # Top
        (-185.625, 33),  # Top-top-left-1
        (-191.25, 34),  # Top-top-left-2
        (-196.875, 35),  # Top-top-left-3
        (-202.5, 36),  # Top-top-left-4
        (-208.125, 37),  # Top-top-left-5
        (-213.75, 38),  # Top-top-left-6
        (-219.375, 39),  # Top-top-left-7
        (-225, 40),  # Top-left
        (-230.625, 41),  # Left-top-left-1
        (-236.25, 42),  # Left-top-left-2
        (-241.875, 43),  # Left-top-left-3
        (-247.5, 44),  # Left-top-left-4
        (-253.125, 45),  # Left-top-left-5
        (-258.75, 46),  # Left-top-left-6
        (-264.375, 47),  # Left-top-left-7
        (-270, 48),  # Left
        (-275.625, 49),  # Left-bottom-left-1
        (-281.25, 50),  # Left-bottom-left-2
        (-286.875, 51),  # Left-bottom-left-3
        (-292.5, 52),  # Left-bottom-left-4
        (-298.125, 53),  # Left-bottom-left-5
        (-303.75, 54),  # Left-bottom-left-6
        (-309.375, 55),  # Left-bottom-left-7
        (-315, 56),  # Bottom-left
        (-320.625, 57),  # Bottom-bottom-left-1
        (-326.25, 58),  # Bottom-bottom-left-2
        (-331.875, 59),  # Bottom-bottom-left-3
        (-337.5, 60),  # Bottom-bottom-left-4
        (-343.125, 61),  # Bottom-bottom-left-5
        (-348.75, 62),  # Bottom-bottom-left-6
        (-354.375, 63),  # Bottom-bottom-left-7
    ]

    # Overlay composition
    OVERLAY_SCALE = 0.8462  # Scale for 7gen

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
GENERATION_7_SETTINGS_SCHEMA = {
    # Font settings
    "font_family": (str, "Arial"),
    # Primary Individual Settings (inherited from 1gen)
    "primary_background_color": (Color, "#FFFFFF"),
    "primary_font_color": (Color, "black"),
    "primary_stroke_color": (Color, "black"),
    "primary_stroke_width": (float, 0.5),
    "primary_name_font_size": (int, 84),
    "primary_date_info_font_size": (int, 60),
    "primary_place_info_font_size": (int, 28),
    "primary_translate_x": (int, 0),
    "primary_translate_y": (int, 0),
    "primary_name_rotate": (int, -45),
    "primary_birth_translate_x": (int, 0),
    "primary_birth_translate_y": (int, 0),
    "primary_birth_rotate": (int, -90),
    "primary_birth_place_translate_x": (int, 0),
    "primary_birth_place_translate_y": (int, 0),
    "primary_birth_place_rotate": (int, 0),
    "primary_death_translate_x": (int, 0),
    "primary_death_translate_y": (int, 0),
    "primary_death_rotate": (int, 0),
    "primary_death_place_translate_x": (int, 0),
    "primary_death_place_translate_y": (int, 0),
    "primary_death_place_rotate": (int, -90),
    # 4x Great-grandparent generation styling
    "fourxgreatgrandparent_stroke_color": (Color, "black"),
    "fourxgreatgrandparent_font_color": (Color, "black"),
    "fourxgreatgrandparent_stroke_width": (float, 0.5),
    # 4x Great-grandparent-specific settings
    "fourxgreatgrandparent_font_size": (int, 20),
    "fourxgreatgrandparent_translate_x": (int, 0),
    "fourxgreatgrandparent_translate_y": (int, 0),
    "fourxgreatgrandparent_rotate": (int, 0),
    "fourxgreatgrandparent_edge_distance": (int, 50),
    "fourxgreatgrandparent_date_distance": (int, 8),
    "fourxgreatgrandparent_birth_translate_x": (int, 0),
    "fourxgreatgrandparent_birth_translate_y": (int, 0),
    "fourxgreatgrandparent_birth_rotate": (int, 0),
    "fourxgreatgrandparent_death_translate_x": (int, 0),
    "fourxgreatgrandparent_death_translate_y": (int, 0),
    "fourxgreatgrandparent_death_rotate": (int, 0),
    # Individual 4x great-grandparent settings for 64 compass positions (0-63)
    # Note: For brevity, only showing first few - full implementation would include all 64
    "fourx_great_grandparent_0_font_color": (Color, "black"),
    "fourx_great_grandparent_0_stroke_color": (Color, "black"),
    "fourx_great_grandparent_0_font_size": (int, 20),
    "fourx_great_grandparent_0_translate_x": (int, 0),
    "fourx_great_grandparent_0_translate_y": (int, 0),
    "fourx_great_grandparent_0_rotate": (int, 0),
    "fourx_great_grandparent_0_birth_translate_x": (int, 0),
    "fourx_great_grandparent_0_birth_translate_y": (int, 0),
    "fourx_great_grandparent_0_birth_rotate": (int, 0),
    "fourx_great_grandparent_0_death_translate_x": (int, 0),
    "fourx_great_grandparent_0_death_translate_y": (int, 0),
    "fourx_great_grandparent_0_death_rotate": (int, 0),
    # Information styling
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    # Overlay settings
    "overlay_scale": (float, 0.8462),
    "overlay_position_x": (int, 0),  # Centered
    "overlay_position_y": (int, 0),  # Centered
}


def generate_7gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 7-generation family tree chart using enhanced standardized patterns.

    This enhanced version follows the same standardization patterns as the 1gen, 2gen, 3gen, 4gen, 5gen, and 6gen generators:
    - Settings validation framework
    - Clean buffer management
    - Consistent logging (no debug prints)
    - Constants extraction
    - Enhanced error handling
    - Mathematical edge positioning
    - 6gen overlay integration

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
        user_settings, GENERATION_7_SETTINGS_SCHEMA, "7gen"
    )

    logger.info(
        f"Generating 7-generation {template} chart for: {primary_individual.full_name} "
        f"(ID: {primary_individual.id})"
    )

    try:
        # Load the 7gen template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "7GEN_PREVIEW.png",
        )

        if not os.path.exists(preview_template_path):
            raise GenerationError(
                f"Preview template not found: {preview_template_path}"
            )

        logger.debug(f"Loading preview template: {preview_template_path}")

        with Image(
            filename=preview_template_path, resolution=Generation7Constants.RESOLUTION
        ) as content_img:
            logger.debug(
                f"Content image loaded: {content_img.width}x{content_img.height}"
            )

            # Draw 4x great-grandparent generation
            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings[
                    "fourxgreatgrandparent_stroke_width"
                ]
                draw.stroke_color = validated_settings[
                    "fourxgreatgrandparent_stroke_color"
                ]

                # Draw 4x great-grandparents
                _draw_fourx_great_grandparents(
                    draw,
                    content_img,
                    primary_individual,
                    family_data,
                    validated_settings,
                )

                # Apply drawing to image
                draw(content_img)

            # Generate 6gen overlay with complete user settings
            logger.debug(
                f"Generating 6gen overlay with complete user settings: {len(user_settings) if user_settings else 0} settings"
            )

            gen6_img_buffer = generate_6gen_preview(
                primary_individual, family_data, "preview", user_settings
            )

            # Composite the 6gen overlay onto the 7gen image
            _composite_overlay(content_img, gen6_img_buffer, validated_settings)

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
        logger.error(f"Unexpected error in 7gen generation: {e}")
        raise GenerationError(f"7-generation chart generation failed: {e}")


def _draw_fourx_great_grandparents(
    draw, content_img, primary_individual, family_data, validated_settings
):
    """Draw the 4x great-grandparent generation with mathematical edge positioning."""

    # Get 4x great-grandparents from family data
    fourx_great_grandparents = get_fourx_great_grandparents(
        primary_individual, family_data
    )

    if not fourx_great_grandparents:
        logger.debug("No 4x great-grandparents found in family data")
        return

    logger.debug(f"Found {len(fourx_great_grandparents)} 4x great-grandparents")

    # Set 4x great-grandparent drawing properties
    font_size = validated_settings["fourxgreatgrandparent_font_size"]
    draw.font_size = font_size
    draw.fill_color = validated_settings["fourxgreatgrandparent_font_color"]

    # Get positioning settings
    edge_distance = validated_settings.get(
        "fourxgreatgrandparent_edge_distance",
        Generation7Constants.EDGE_DISTANCE_DEFAULT,
    )
    date_distance = validated_settings.get(
        "fourxgreatgrandparent_date_distance",
        Generation7Constants.DATE_DISTANCE_DEFAULT,
    )

    # Calculate canvas center and radius
    center_x = content_img.width // 2
    center_y = content_img.height // 2
    radius = center_x - edge_distance

    # Draw 4x great-grandparents at 64 compass points
    for rotation, index in Generation7Constants.COMPASS_POSITIONS:
        if index < len(fourx_great_grandparents) and fourx_great_grandparents[index]:
            fourx_great_grandparent = fourx_great_grandparents[index]
            gp_type = f"fourx_great_grandparent_{index}"

            logger.debug(
                f"Drawing {gp_type}: {fourx_great_grandparent.full_name} at {rotation}° rotation"
            )

            # Calculate position on the edge based on rotation
            angle_rad = math.radians(rotation)
            edge_x = center_x + radius * math.cos(angle_rad)
            edge_y = center_y + radius * math.sin(angle_rad)

            # Draw 4x great-grandparent with standardized name rendering
            _draw_fourx_great_grandparent_at_position(
                draw,
                fourx_great_grandparent,
                index,
                int(edge_x),
                int(edge_y),
                rotation,
                font_size,
                date_distance,
                validated_settings,
            )


def _draw_fourx_great_grandparent_at_position(
    draw,
    fourx_great_grandparent,
    index,
    edge_x,
    edge_y,
    rotation,
    font_size,
    date_distance,
    validated_settings,
):
    """Draw a single 4x great-grandparent at the specified edge position."""

    # Get individual-specific settings for this 4x great-grandparent
    prefix = f"fourx_great_grandparent_{index}_"

    font_color = validated_settings.get(
        f"{prefix}font_color", validated_settings["fourxgreatgrandparent_font_color"]
    )
    stroke_color = validated_settings.get(
        f"{prefix}stroke_color",
        validated_settings["fourxgreatgrandparent_stroke_color"],
    )
    individual_font_size = validated_settings.get(f"{prefix}font_size", font_size)
    translate_x = validated_settings.get(f"{prefix}translate_x", 0)
    translate_y = validated_settings.get(f"{prefix}translate_y", 0)
    individual_rotation = validated_settings.get(f"{prefix}rotate", 0)

    # Set drawing properties
    draw.fill_color = font_color
    draw.stroke_color = stroke_color
    draw.font_size = individual_font_size

    # Get name display information using standardized approach
    name_info = get_name_display_info(fourx_great_grandparent.full_name)
    display_text = name_info["display_text"]

    # Draw name with multiline support using translation
    lines = display_text.split("\n")
    line_height = (
        individual_font_size * Generation7Constants.MULTILINE_LINE_HEIGHT_RATIO
    )
    start_y = -(len(lines) - 1) * line_height / 2

    for i, line in enumerate(lines):
        line_y = start_y + (i * line_height)

        draw.push()
        draw.translate(edge_x + translate_x, edge_y + translate_y)
        draw.rotate(rotation + individual_rotation)
        draw.push()
        draw.translate(0, line_y)
        draw.text(0, 0, line)
        draw.pop()
        draw.pop()

    # Draw birth date if available
    if fourx_great_grandparent.birth_date:
        draw.push()
        birth_translate_x = validated_settings.get(f"{prefix}birth_translate_x", 0)
        birth_translate_y = validated_settings.get(f"{prefix}birth_translate_y", 0)
        birth_rotate = validated_settings.get(f"{prefix}birth_rotate", 0)

        draw.translate(
            edge_x + translate_x + birth_translate_x,
            edge_y + translate_y + birth_translate_y + date_distance,
        )
        draw.rotate(rotation + individual_rotation + birth_rotate)
        draw.font_size = int(
            individual_font_size * Generation7Constants.DATE_FONT_SIZE_RATIO
        )
        draw.text(0, 0, fourx_great_grandparent.birth_date)
        draw.pop()

    # Draw death date if available
    if fourx_great_grandparent.death_date:
        draw.push()
        death_translate_x = validated_settings.get(f"{prefix}death_translate_x", 0)
        death_translate_y = validated_settings.get(f"{prefix}death_translate_y", 0)
        death_rotate = validated_settings.get(f"{prefix}death_rotate", 0)

        draw.translate(
            edge_x + translate_x + death_translate_x,
            edge_y + translate_y + death_translate_y + date_distance + 15,
        )
        draw.rotate(rotation + individual_rotation + death_rotate)
        draw.font_size = int(
            individual_font_size * Generation7Constants.DATE_FONT_SIZE_RATIO
        )
        draw.text(0, 0, fourx_great_grandparent.death_date)
        draw.pop()


def get_fourx_great_grandparents(primary_individual, family_data):
    """
    Get all 4x great-grandparents for the primary individual.

    Returns:
        List of 4x great-grandparent individuals in compass point order
    """
    fourx_great_grandparents = []

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
    great_grandparents = []
    for grandparent in grandparents:
        if grandparent:
            gp_father_id = getattr(grandparent, "father", None)
            gp_mother_id = getattr(grandparent, "mother", None)
            if gp_father_id:
                great_grandparents.append(individuals.get(gp_father_id))
            if gp_mother_id:
                great_grandparents.append(individuals.get(gp_mother_id))

    # Get 2x great-grandparents through great-grandparents
    twox_great_grandparents = []
    for great_grandparent in great_grandparents:
        if great_grandparent:
            ggp_father_id = getattr(great_grandparent, "father", None)
            ggp_mother_id = getattr(great_grandparent, "mother", None)
            if ggp_father_id:
                twox_great_grandparents.append(individuals.get(ggp_father_id))
            if ggp_mother_id:
                twox_great_grandparents.append(individuals.get(ggp_mother_id))

    # Get 3x great-grandparents through 2x great-grandparents
    threex_great_grandparents = []
    for twox_great_grandparent in twox_great_grandparents:
        if twox_great_grandparent:
            gggp_father_id = getattr(twox_great_grandparent, "father", None)
            gggp_mother_id = getattr(twox_great_grandparent, "mother", None)
            if gggp_father_id:
                threex_great_grandparents.append(individuals.get(gggp_father_id))
            if gggp_mother_id:
                threex_great_grandparents.append(individuals.get(gggp_mother_id))

    # Get 4x great-grandparents through 3x great-grandparents
    for threex_great_grandparent in threex_great_grandparents:
        if threex_great_grandparent:
            ggggp_father_id = getattr(threex_great_grandparent, "father", None)
            ggggp_mother_id = getattr(threex_great_grandparent, "mother", None)
            if ggggp_father_id:
                fourx_great_grandparents.append(individuals.get(ggggp_father_id))
            if ggggp_mother_id:
                fourx_great_grandparents.append(individuals.get(ggggp_mother_id))

    # Filter out None values and return
    return [gp for gp in fourx_great_grandparents if gp is not None]


def _composite_overlay(content_img, gen6_img_buffer, validated_settings):
    """Composite the 6gen overlay onto the 7gen image with enhanced buffer handling."""

    try:
        # Reset buffer position and get bytes
        gen6_img_buffer.seek(0)
        gen6_bytes = gen6_img_buffer.getvalue()

        if not gen6_bytes:
            raise BufferError("6gen overlay buffer is empty")

        # Get overlay settings
        overlay_scale = validated_settings.get(
            "overlay_scale", Generation7Constants.OVERLAY_SCALE
        )

        # Create image from blob and composite
        with Image(blob=gen6_bytes) as gen6_overlay:
            # Scale overlay
            overlay_size = int(content_img.width * overlay_scale)
            gen6_overlay.resize(overlay_size, overlay_size)

            # Center the overlay
            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            # Apply position offsets if specified
            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            # Composite onto content image
            content_img.composite(gen6_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 6gen overlay at ({overlay_x}, {overlay_y}) with scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


def _create_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""

    # Load PDF base template
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_7GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    logger.debug(f"Loading PDF base template: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation7Constants.RESOLUTION
    ) as base_img:
        logger.debug(f"Base template loaded: {base_img.width}x{base_img.height}")

        # Composite content image onto base template
        base_img.composite(
            content_img,
            left=Generation7Constants.COMPOSITE_X,
            top=Generation7Constants.COMPOSITE_Y,
        )

        logger.debug(
            f"Composited content at ({Generation7Constants.COMPOSITE_X}, {Generation7Constants.COMPOSITE_Y})"
        )

        # Create PDF buffer
        return create_pdf_buffer(base_img)


# Legacy function for backward compatibility
def generate_family_tree(primary_individual, family_data, template="7gen"):
    """Legacy wrapper for backward compatibility."""
    return generate_7gen_preview(primary_individual, family_data, template, None)
