import logging
import math
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.image_4generator import generate_4gen_preview
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
class Generation5Constants:
    """Constants for 5-generation chart generation."""

    # Canvas dimensions
    CANVAS_WIDTH = 1950
    CANVAS_HEIGHT = 1950

    # 2x Great-grandparent positioning
    EDGE_DISTANCE_DEFAULT = 30
    DATE_DISTANCE_DEFAULT = 10

    # 16-point compass positioning for 2x great-grandparents
    COMPASS_POSITIONS = [
        (0, 0),  # Bottom
        (-22.5, 1),  # Bottom-bottom-right
        (-45, 2),  # Bottom-right
        (-67.5, 3),  # Right-bottom-right
        (-90, 4),  # Right
        (-112.5, 5),  # Right-top-right
        (-135, 6),  # Top-right
        (-157.5, 7),  # Top-top-right
        (-180, 8),  # Top
        (-202.5, 9),  # Top-top-left
        (-225, 10),  # Top-left
        (-247.5, 11),  # Left-top-left
        (-270, 12),  # Left
        (-292.5, 13),  # Left-bottom-left
        (-315, 14),  # Bottom-left
        (-337.5, 15),  # Bottom-bottom-left
    ]

    # Overlay composition
    OVERLAY_SCALE = 0.7797  # 74.97% scale for 5gen

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
GENERATION_5_SETTINGS_SCHEMA = {
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
    # 2x Great-grandparent generation styling
    "twoxgreatgrandparent_stroke_color": (Color, "black"),
    "twoxgreatgrandparent_font_color": (Color, "black"),
    "twoxgreatgrandparent_stroke_width": (float, 0.5),
    # 2x Great-grandparent-specific settings
    "twoxgreatgrandparent_font_size": (int, 28),
    "twoxgreatgrandparent_translate_x": (int, 0),
    "twoxgreatgrandparent_translate_y": (int, 0),
    "twoxgreatgrandparent_rotate": (int, 0),
    "twoxgreatgrandparent_edge_distance": (int, 30),
    "twoxgreatgrandparent_date_distance": (int, 10),
    "twoxgreatgrandparent_birth_translate_x": (int, 0),
    "twoxgreatgrandparent_birth_translate_y": (int, 0),
    "twoxgreatgrandparent_birth_rotate": (int, 0),
    "twoxgreatgrandparent_death_translate_x": (int, 0),
    "twoxgreatgrandparent_death_translate_y": (int, 0),
    "twoxgreatgrandparent_death_rotate": (int, 0),
    # Individual 2x great-grandparent settings for 16 compass positions
    "twox_great_grandparent_0_font_color": (Color, "black"),
    "twox_great_grandparent_0_stroke_color": (Color, "black"),
    "twox_great_grandparent_0_font_size": (int, 28),
    "twox_great_grandparent_0_translate_x": (int, 0),
    "twox_great_grandparent_0_translate_y": (int, 0),
    "twox_great_grandparent_0_rotate": (int, 0),
    "twox_great_grandparent_0_birth_translate_x": (int, 0),
    "twox_great_grandparent_0_birth_translate_y": (int, 0),
    "twox_great_grandparent_0_birth_rotate": (int, 0),
    "twox_great_grandparent_0_death_translate_x": (int, 0),
    "twox_great_grandparent_0_death_translate_y": (int, 0),
    "twox_great_grandparent_0_death_rotate": (int, 0),
    "twox_great_grandparent_1_font_color": (Color, "black"),
    "twox_great_grandparent_1_stroke_color": (Color, "black"),
    "twox_great_grandparent_1_font_size": (int, 28),
    "twox_great_grandparent_1_translate_x": (int, 0),
    "twox_great_grandparent_1_translate_y": (int, 0),
    "twox_great_grandparent_1_rotate": (int, 0),
    "twox_great_grandparent_1_birth_translate_x": (int, 0),
    "twox_great_grandparent_1_birth_translate_y": (int, 0),
    "twox_great_grandparent_1_birth_rotate": (int, 0),
    "twox_great_grandparent_1_death_translate_x": (int, 0),
    "twox_great_grandparent_1_death_translate_y": (int, 0),
    "twox_great_grandparent_1_death_rotate": (int, 0),
    "twox_great_grandparent_2_font_color": (Color, "black"),
    "twox_great_grandparent_2_stroke_color": (Color, "black"),
    "twox_great_grandparent_2_font_size": (int, 28),
    "twox_great_grandparent_2_translate_x": (int, 0),
    "twox_great_grandparent_2_translate_y": (int, 0),
    "twox_great_grandparent_2_rotate": (int, 0),
    "twox_great_grandparent_2_birth_translate_x": (int, 0),
    "twox_great_grandparent_2_birth_translate_y": (int, 0),
    "twox_great_grandparent_2_birth_rotate": (int, 0),
    "twox_great_grandparent_2_death_translate_x": (int, 0),
    "twox_great_grandparent_2_death_translate_y": (int, 0),
    "twox_great_grandparent_2_death_rotate": (int, 0),
    "twox_great_grandparent_3_font_color": (Color, "black"),
    "twox_great_grandparent_3_stroke_color": (Color, "black"),
    "twox_great_grandparent_3_font_size": (int, 28),
    "twox_great_grandparent_3_translate_x": (int, 0),
    "twox_great_grandparent_3_translate_y": (int, 0),
    "twox_great_grandparent_3_rotate": (int, 0),
    "twox_great_grandparent_3_birth_translate_x": (int, 0),
    "twox_great_grandparent_3_birth_translate_y": (int, 0),
    "twox_great_grandparent_3_birth_rotate": (int, 0),
    "twox_great_grandparent_3_death_translate_x": (int, 0),
    "twox_great_grandparent_3_death_translate_y": (int, 0),
    "twox_great_grandparent_3_death_rotate": (int, 0),
    "twox_great_grandparent_4_font_color": (Color, "black"),
    "twox_great_grandparent_4_stroke_color": (Color, "black"),
    "twox_great_grandparent_4_font_size": (int, 28),
    "twox_great_grandparent_4_translate_x": (int, 0),
    "twox_great_grandparent_4_translate_y": (int, 0),
    "twox_great_grandparent_4_rotate": (int, 0),
    "twox_great_grandparent_4_birth_translate_x": (int, 0),
    "twox_great_grandparent_4_birth_translate_y": (int, 0),
    "twox_great_grandparent_4_birth_rotate": (int, 0),
    "twox_great_grandparent_4_death_translate_x": (int, 0),
    "twox_great_grandparent_4_death_translate_y": (int, 0),
    "twox_great_grandparent_4_death_rotate": (int, 0),
    "twox_great_grandparent_5_font_color": (Color, "black"),
    "twox_great_grandparent_5_stroke_color": (Color, "black"),
    "twox_great_grandparent_5_font_size": (int, 28),
    "twox_great_grandparent_5_translate_x": (int, 0),
    "twox_great_grandparent_5_translate_y": (int, 0),
    "twox_great_grandparent_5_rotate": (int, 0),
    "twox_great_grandparent_5_birth_translate_x": (int, 0),
    "twox_great_grandparent_5_birth_translate_y": (int, 0),
    "twox_great_grandparent_5_birth_rotate": (int, 0),
    "twox_great_grandparent_5_death_translate_x": (int, 0),
    "twox_great_grandparent_5_death_translate_y": (int, 0),
    "twox_great_grandparent_5_death_rotate": (int, 0),
    "twox_great_grandparent_6_font_color": (Color, "black"),
    "twox_great_grandparent_6_stroke_color": (Color, "black"),
    "twox_great_grandparent_6_font_size": (int, 28),
    "twox_great_grandparent_6_translate_x": (int, 0),
    "twox_great_grandparent_6_translate_y": (int, 0),
    "twox_great_grandparent_6_rotate": (int, 0),
    "twox_great_grandparent_6_birth_translate_x": (int, 0),
    "twox_great_grandparent_6_birth_translate_y": (int, 0),
    "twox_great_grandparent_6_birth_rotate": (int, 0),
    "twox_great_grandparent_6_death_translate_x": (int, 0),
    "twox_great_grandparent_6_death_translate_y": (int, 0),
    "twox_great_grandparent_6_death_rotate": (int, 0),
    "twox_great_grandparent_7_font_color": (Color, "black"),
    "twox_great_grandparent_7_stroke_color": (Color, "black"),
    "twox_great_grandparent_7_font_size": (int, 28),
    "twox_great_grandparent_7_translate_x": (int, 0),
    "twox_great_grandparent_7_translate_y": (int, 0),
    "twox_great_grandparent_7_rotate": (int, 0),
    "twox_great_grandparent_7_birth_translate_x": (int, 0),
    "twox_great_grandparent_7_birth_translate_y": (int, 0),
    "twox_great_grandparent_7_birth_rotate": (int, 0),
    "twox_great_grandparent_7_death_translate_x": (int, 0),
    "twox_great_grandparent_7_death_translate_y": (int, 0),
    "twox_great_grandparent_7_death_rotate": (int, 0),
    "twox_great_grandparent_8_font_color": (Color, "black"),
    "twox_great_grandparent_8_stroke_color": (Color, "black"),
    "twox_great_grandparent_8_font_size": (int, 28),
    "twox_great_grandparent_8_translate_x": (int, 0),
    "twox_great_grandparent_8_translate_y": (int, 0),
    "twox_great_grandparent_8_rotate": (int, 0),
    "twox_great_grandparent_8_birth_translate_x": (int, 0),
    "twox_great_grandparent_8_birth_translate_y": (int, 0),
    "twox_great_grandparent_8_birth_rotate": (int, 0),
    "twox_great_grandparent_8_death_translate_x": (int, 0),
    "twox_great_grandparent_8_death_translate_y": (int, 0),
    "twox_great_grandparent_8_death_rotate": (int, 0),
    "twox_great_grandparent_9_font_color": (Color, "black"),
    "twox_great_grandparent_9_stroke_color": (Color, "black"),
    "twox_great_grandparent_9_font_size": (int, 28),
    "twox_great_grandparent_9_translate_x": (int, 0),
    "twox_great_grandparent_9_translate_y": (int, 0),
    "twox_great_grandparent_9_rotate": (int, 0),
    "twox_great_grandparent_9_birth_translate_x": (int, 0),
    "twox_great_grandparent_9_birth_translate_y": (int, 0),
    "twox_great_grandparent_9_birth_rotate": (int, 0),
    "twox_great_grandparent_9_death_translate_x": (int, 0),
    "twox_great_grandparent_9_death_translate_y": (int, 0),
    "twox_great_grandparent_9_death_rotate": (int, 0),
    "twox_great_grandparent_10_font_color": (Color, "black"),
    "twox_great_grandparent_10_stroke_color": (Color, "black"),
    "twox_great_grandparent_10_font_size": (int, 28),
    "twox_great_grandparent_10_translate_x": (int, 0),
    "twox_great_grandparent_10_translate_y": (int, 0),
    "twox_great_grandparent_10_rotate": (int, 0),
    "twox_great_grandparent_10_birth_translate_x": (int, 0),
    "twox_great_grandparent_10_birth_translate_y": (int, 0),
    "twox_great_grandparent_10_birth_rotate": (int, 0),
    "twox_great_grandparent_10_death_translate_x": (int, 0),
    "twox_great_grandparent_10_death_translate_y": (int, 0),
    "twox_great_grandparent_10_death_rotate": (int, 0),
    "twox_great_grandparent_11_font_color": (Color, "black"),
    "twox_great_grandparent_11_stroke_color": (Color, "black"),
    "twox_great_grandparent_11_font_size": (int, 28),
    "twox_great_grandparent_11_translate_x": (int, 0),
    "twox_great_grandparent_11_translate_y": (int, 0),
    "twox_great_grandparent_11_rotate": (int, 0),
    "twox_great_grandparent_11_birth_translate_x": (int, 0),
    "twox_great_grandparent_11_birth_translate_y": (int, 0),
    "twox_great_grandparent_11_birth_rotate": (int, 0),
    "twox_great_grandparent_11_death_translate_x": (int, 0),
    "twox_great_grandparent_11_death_translate_y": (int, 0),
    "twox_great_grandparent_11_death_rotate": (int, 0),
    "twox_great_grandparent_12_font_color": (Color, "black"),
    "twox_great_grandparent_12_stroke_color": (Color, "black"),
    "twox_great_grandparent_12_font_size": (int, 28),
    "twox_great_grandparent_12_translate_x": (int, 0),
    "twox_great_grandparent_12_translate_y": (int, 0),
    "twox_great_grandparent_12_rotate": (int, 0),
    "twox_great_grandparent_12_birth_translate_x": (int, 0),
    "twox_great_grandparent_12_birth_translate_y": (int, 0),
    "twox_great_grandparent_12_birth_rotate": (int, 0),
    "twox_great_grandparent_12_death_translate_x": (int, 0),
    "twox_great_grandparent_12_death_translate_y": (int, 0),
    "twox_great_grandparent_12_death_rotate": (int, 0),
    "twox_great_grandparent_13_font_color": (Color, "black"),
    "twox_great_grandparent_13_stroke_color": (Color, "black"),
    "twox_great_grandparent_13_font_size": (int, 28),
    "twox_great_grandparent_13_translate_x": (int, 0),
    "twox_great_grandparent_13_translate_y": (int, 0),
    "twox_great_grandparent_13_rotate": (int, 0),
    "twox_great_grandparent_13_birth_translate_x": (int, 0),
    "twox_great_grandparent_13_birth_translate_y": (int, 0),
    "twox_great_grandparent_13_birth_rotate": (int, 0),
    "twox_great_grandparent_13_death_translate_x": (int, 0),
    "twox_great_grandparent_13_death_translate_y": (int, 0),
    "twox_great_grandparent_13_death_rotate": (int, 0),
    "twox_great_grandparent_14_font_color": (Color, "black"),
    "twox_great_grandparent_14_stroke_color": (Color, "black"),
    "twox_great_grandparent_14_font_size": (int, 28),
    "twox_great_grandparent_14_translate_x": (int, 0),
    "twox_great_grandparent_14_translate_y": (int, 0),
    "twox_great_grandparent_14_rotate": (int, 0),
    "twox_great_grandparent_14_birth_translate_x": (int, 0),
    "twox_great_grandparent_14_birth_translate_y": (int, 0),
    "twox_great_grandparent_14_birth_rotate": (int, 0),
    "twox_great_grandparent_14_death_translate_x": (int, 0),
    "twox_great_grandparent_14_death_translate_y": (int, 0),
    "twox_great_grandparent_14_death_rotate": (int, 0),
    "twox_great_grandparent_15_font_color": (Color, "black"),
    "twox_great_grandparent_15_stroke_color": (Color, "black"),
    "twox_great_grandparent_15_font_size": (int, 28),
    "twox_great_grandparent_15_translate_x": (int, 0),
    "twox_great_grandparent_15_translate_y": (int, 0),
    "twox_great_grandparent_15_rotate": (int, 0),
    "twox_great_grandparent_15_birth_translate_x": (int, 0),
    "twox_great_grandparent_15_birth_translate_y": (int, 0),
    "twox_great_grandparent_15_birth_rotate": (int, 0),
    "twox_great_grandparent_15_death_translate_x": (int, 0),
    "twox_great_grandparent_15_death_translate_y": (int, 0),
    "twox_great_grandparent_15_death_rotate": (int, 0),
    # Information styling
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    # Overlay settings
    "overlay_scale": (float, 0.7797),
    "overlay_position_x": (int, 0),  # Centered
    "overlay_position_y": (int, 0),  # Centered
}


def generate_5gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 5-generation family tree chart using enhanced standardized patterns.

    This enhanced version follows the same standardization patterns as the 1gen, 2gen, 3gen, and 4gen generators:
    - Settings validation framework
    - Clean buffer management
    - Consistent logging (no debug prints)
    - Constants extraction
    - Enhanced error handling
    - Mathematical edge positioning
    - 4gen overlay integration

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
        user_settings, GENERATION_5_SETTINGS_SCHEMA, "5gen"
    )

    logger.info(
        f"Generating 5-generation {template} chart for: {primary_individual.full_name} "
        f"(ID: {primary_individual.id})"
    )

    try:
        # Load the 5gen template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "5GEN_PREVIEW.png",
        )

        if not os.path.exists(preview_template_path):
            raise GenerationError(
                f"Preview template not found: {preview_template_path}"
            )

        logger.debug(f"Loading preview template: {preview_template_path}")

        with Image(
            filename=preview_template_path, resolution=Generation5Constants.RESOLUTION
        ) as content_img:
            logger.debug(
                f"Content image loaded: {content_img.width}x{content_img.height}"
            )

            # Draw 2x great-grandparent generation
            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings[
                    "twoxgreatgrandparent_stroke_width"
                ]
                draw.stroke_color = validated_settings[
                    "twoxgreatgrandparent_stroke_color"
                ]

                # Draw 2x great-grandparents
                _draw_twox_great_grandparents(
                    draw,
                    content_img,
                    primary_individual,
                    family_data,
                    validated_settings,
                )

                # Apply drawing to image
                draw(content_img)

            # Generate 4gen overlay with complete user settings
            logger.debug(
                f"Generating 4gen overlay with complete user settings: {len(user_settings) if user_settings else 0} settings"
            )

            gen4_img_buffer = generate_4gen_preview(
                primary_individual, family_data, "preview", user_settings
            )

            # Composite the 4gen overlay onto the 5gen image
            _composite_overlay(content_img, gen4_img_buffer, validated_settings)

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
        logger.error(f"Unexpected error in 5gen generation: {e}")
        raise GenerationError(f"5-generation chart generation failed: {e}")


def _draw_twox_great_grandparents(
    draw, content_img, primary_individual, family_data, validated_settings
):
    """Draw the 2x great-grandparent generation with mathematical edge positioning."""

    # Get 2x great-grandparents from family data
    twox_great_grandparents = get_2x_great_grandparents(primary_individual, family_data)

    if not twox_great_grandparents:
        logger.debug("No 2x great-grandparents found in family data")
        return

    logger.debug(f"Found {len(twox_great_grandparents)} 2x great-grandparents")

    # Set 2x great-grandparent drawing properties
    font_size = validated_settings["twoxgreatgrandparent_font_size"]
    draw.font_size = font_size
    draw.fill_color = validated_settings["twoxgreatgrandparent_font_color"]

    # Get positioning settings
    edge_distance = validated_settings.get(
        "twoxgreatgrandparent_edge_distance", Generation5Constants.EDGE_DISTANCE_DEFAULT
    )
    date_distance = validated_settings.get(
        "twoxgreatgrandparent_date_distance", Generation5Constants.DATE_DISTANCE_DEFAULT
    )

    # Calculate canvas center and radius
    center_x = content_img.width // 2
    center_y = content_img.height // 2
    radius = center_x - edge_distance

    # Draw 2x great-grandparents at 16 compass points
    for rotation, index in Generation5Constants.COMPASS_POSITIONS:
        if index < len(twox_great_grandparents) and twox_great_grandparents[index]:
            twox_great_grandparent = twox_great_grandparents[index]
            gp_type = f"twox_great_grandparent_{index}"

            logger.debug(
                f"Drawing {gp_type}: {twox_great_grandparent.full_name} at {rotation}° rotation"
            )

            # Calculate position on the edge based on rotation
            angle_rad = math.radians(rotation)
            edge_x = center_x + radius * math.cos(angle_rad)
            edge_y = center_y + radius * math.sin(angle_rad)

            # Draw 2x great-grandparent with standardized name rendering
            _draw_twox_great_grandparent_at_position(
                draw,
                twox_great_grandparent,
                index,
                int(edge_x),
                int(edge_y),
                rotation,
                font_size,
                date_distance,
                validated_settings,
            )


def _draw_twox_great_grandparent_at_position(
    draw,
    twox_great_grandparent,
    index,
    edge_x,
    edge_y,
    rotation,
    font_size,
    date_distance,
    validated_settings,
):
    """Draw a single 2x great-grandparent at the specified edge position."""

    # Get individual-specific settings for this 2x great-grandparent
    prefix = f"twox_great_grandparent_{index}_"

    font_color = validated_settings.get(
        f"{prefix}font_color", validated_settings["twoxgreatgrandparent_font_color"]
    )
    stroke_color = validated_settings.get(
        f"{prefix}stroke_color", validated_settings["twoxgreatgrandparent_stroke_color"]
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
    name_info = get_name_display_info(twox_great_grandparent.full_name)
    display_text = name_info["display_text"]

    # Draw name with multiline support using translation
    lines = display_text.split("\n")
    line_height = (
        individual_font_size * Generation5Constants.MULTILINE_LINE_HEIGHT_RATIO
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
    if twox_great_grandparent.birth_date:
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
            individual_font_size * Generation5Constants.DATE_FONT_SIZE_RATIO
        )
        draw.text(0, 0, twox_great_grandparent.birth_date)
        draw.pop()

    # Draw death date if available
    if twox_great_grandparent.death_date:
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
            individual_font_size * Generation5Constants.DATE_FONT_SIZE_RATIO
        )
        draw.text(0, 0, twox_great_grandparent.death_date)
        draw.pop()


def get_2x_great_grandparents(primary_individual, family_data):
    """
    Get all 2x great-grandparents for the primary individual.

    Returns:
        List of 2x great-grandparent individuals in compass point order
    """
    twox_great_grandparents = []

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
    for great_grandparent in great_grandparents:
        if great_grandparent:
            ggp_father_id = getattr(great_grandparent, "father", None)
            ggp_mother_id = getattr(great_grandparent, "mother", None)
            if ggp_father_id:
                twox_great_grandparents.append(individuals.get(ggp_father_id))
            if ggp_mother_id:
                twox_great_grandparents.append(individuals.get(ggp_mother_id))

    # Filter out None values and return
    return [gp for gp in twox_great_grandparents if gp is not None]


def _composite_overlay(content_img, gen4_img_buffer, validated_settings):
    """Composite the 4gen overlay onto the 5gen image with enhanced buffer handling."""

    try:
        # Reset buffer position and get bytes
        gen4_img_buffer.seek(0)
        gen4_bytes = gen4_img_buffer.getvalue()

        if not gen4_bytes:
            raise BufferError("4gen overlay buffer is empty")

        # Get overlay settings
        overlay_scale = validated_settings.get(
            "overlay_scale", Generation5Constants.OVERLAY_SCALE
        )

        # Create image from blob and composite
        with Image(blob=gen4_bytes) as gen4_overlay:
            # Scale overlay
            overlay_size = int(content_img.width * overlay_scale)
            gen4_overlay.resize(overlay_size, overlay_size)

            # Center the overlay
            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            # Apply position offsets if specified
            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            # Composite onto content image
            content_img.composite(gen4_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 4gen overlay at ({overlay_x}, {overlay_y}) with scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


def _create_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""

    # Load PDF base template
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_5GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    logger.debug(f"Loading PDF base template: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation5Constants.RESOLUTION
    ) as base_img:
        logger.debug(f"Base template loaded: {base_img.width}x{base_img.height}")

        # Composite content image onto base template
        base_img.composite(
            content_img,
            left=Generation5Constants.COMPOSITE_X,
            top=Generation5Constants.COMPOSITE_Y,
        )

        logger.debug(
            f"Composited content at ({Generation5Constants.COMPOSITE_X}, {Generation5Constants.COMPOSITE_Y})"
        )

        # Create PDF buffer
        return create_pdf_buffer(base_img)


# Legacy function for backward compatibility
def generate_family_tree(primary_individual, family_data, template="5gen"):
    """Legacy wrapper for backward compatibility."""
    return generate_5gen_preview(primary_individual, family_data, template, None)
