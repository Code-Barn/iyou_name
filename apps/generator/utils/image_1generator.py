import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

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
class Generation1Constants:
    """Constants for 1-generation chart generation."""

    # Canvas dimensions
    CANVAS_WIDTH = 1822
    CANVAS_HEIGHT = 1822
    BACKGROUND_LEFT = 64
    BACKGROUND_TOP = 64
    BACKGROUND_WIDTH = 1822
    BACKGROUND_HEIGHT = 1822

    # Initial translation
    INITIAL_TRANSLATE_X = 0
    INITIAL_TRANSLATE_Y = 0

    # Text positioning
    BIRTH_DATE_X = 200
    BIRTH_PLACE_Y = 1875
    DEATH_DATE_Y = 200
    DEATH_PLACE_X = 1875

    # PDF compositing
    COMPOSITE_X = 300
    COMPOSITE_Y = 570

    # DPI settings
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72  # Approx 4.1667


# Settings schema for validation
GENERATION_1_SETTINGS_SCHEMA = {
    # Font settings
    "font_family": (str, "Arial"),
    # Primary individual styling
    "primary_background_color": (Color, "#FFFFFF"),
    "primary_font_color": (Color, "black"),
    "primary_stroke_color": (Color, "black"),
    "primary_stroke_width": (float, 0.5),
    # Information styling
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    # Birth information
    "primary_birth_color": (Color, "black"),
    "primary_birth_place_color": (Color, "black"),
    "primary_birth_translate_x": (int, 0),
    "primary_birth_translate_y": (int, 0),
    "primary_birth_rotate": (int, -90),
    "primary_birth_place_translate_x": (int, 0),
    "primary_birth_place_translate_y": (int, 0),
    "primary_birth_place_rotate": (int, 0),
    # Death information
    "primary_death_color": (Color, "black"),
    "primary_death_place_color": (Color, "black"),
    "primary_death_translate_x": (int, 0),
    "primary_death_translate_y": (int, 0),
    "primary_death_rotate": (int, 0),
    "primary_death_place_translate_x": (int, 0),
    "primary_death_place_translate_y": (int, 0),
    "primary_death_place_rotate": (int, -90),
    # Primary individual positioning
    "primary_translate_x": (int, 0),
    "primary_translate_y": (int, 0),
    "primary_name_rotate": (int, -45),
    # Font sizes
    "primary_name_font_size": (int, 84),
    "primary_date_info_font_size": (int, 60),
    "primary_place_info_font_size": (int, 28),
}


def generate_1gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 1-generation chart using enhanced standardized patterns.

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data (currently unused in 1gen)
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
        user_settings, GENERATION_1_SETTINGS_SCHEMA, "1gen"
    )

    logger.info(
        f"Generating 1-generation {template} chart for: {primary_individual.full_name} "
        f"(ID: {primary_individual.id})"
    )

    try:
        # Load preview template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "1GEN_PREVIEW.png",
        )

        if not os.path.exists(preview_template_path):
            raise GenerationError(
                f"Preview template not found: {preview_template_path}"
            )

        logger.debug(f"Loading preview template: {preview_template_path}")

        # Generate the content image
        with Image(
            filename=preview_template_path, resolution=Generation1Constants.RESOLUTION
        ) as content_img:
            logger.debug(
                f"Content image loaded: {content_img.width}x{content_img.height}"
            )

            # Use validated settings
            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                draw.font = validated_settings["font_family"]
                draw.font_size = validated_settings["primary_name_font_size"]
                draw.stroke_antialias = True

                # Draw background
                draw.fill_color = validated_settings["primary_background_color"]
                draw.rectangle(
                    left=Generation1Constants.BACKGROUND_LEFT,
                    top=Generation1Constants.BACKGROUND_TOP,
                    width=Generation1Constants.BACKGROUND_WIDTH,
                    height=Generation1Constants.BACKGROUND_HEIGHT,
                )

                # Apply initial translation
                draw.translate(
                    x=Generation1Constants.INITIAL_TRANSLATE_X,
                    y=Generation1Constants.INITIAL_TRANSLATE_Y,
                )

                # Draw primary individual
                _draw_primary_individual(
                    draw, content_img, primary_individual, validated_settings
                )

                # Apply drawing to image
                draw(content_img)

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
        logger.error(f"Unexpected error in 1gen generation: {e}")
        raise GenerationError(f"1-generation chart generation failed: {e}")


def _draw_primary_individual(draw, content_img, primary_individual, settings):
    """Draw the primary individual information."""

    # Apply primary individual translation
    draw.translate(x=settings["primary_translate_x"], y=settings["primary_translate_y"])

    # Set stroke properties
    draw.stroke_width = settings["primary_stroke_width"]
    draw.stroke_color = settings["primary_stroke_color"]
    draw.fill_color = settings["primary_font_color"]
    draw.gravity = "center"

    # Draw name with rotation
    draw.rotate(settings["primary_name_rotate"])

    # Parse and draw name
    name_info = get_name_display_info(primary_individual.full_name)
    display_text = name_info["display_text"]

    logger.debug(f"Drawing primary individual name: {display_text}")
    draw.text(0, 0, display_text)
    draw.pop()

    # Set info text properties
    draw.font = settings["font_family"]
    draw.stroke_color = settings["info_stroke_color"]
    draw.stroke_width = settings["info_stroke_width"]
    draw.stroke_antialias = True

    # Draw birth information
    _draw_birth_info(draw, content_img, primary_individual, settings)

    # Draw death information
    _draw_death_info(draw, content_img, primary_individual, settings)


def _draw_birth_info(draw, content_img, primary_individual, settings):
    """Draw birth date and place information."""

    # Draw birth date
    draw.push()
    draw.font_size = settings["primary_date_info_font_size"]
    draw.fill_color = settings["primary_birth_color"]

    birth_text = primary_individual.birth_date or " "
    logger.debug(f"Drawing birth date: {birth_text}")

    # Calculate text metrics and position
    metrics = draw.get_font_metrics(content_img, birth_text, False)
    text_width_px = metrics.text_width * Generation1Constants.PIXEL_RATIO

    translate_x = (
        Generation1Constants.BIRTH_DATE_X + settings["primary_birth_translate_x"]
    )
    translate_y = content_img.height // 2 + settings["primary_birth_translate_y"]

    draw.translate(translate_x, translate_y)
    draw.rotate(settings["primary_birth_rotate"])
    draw.translate(-text_width_px // 2, 0)
    draw.text(0, 0, birth_text)
    draw.pop()

    # Draw birth place
    draw.push()
    draw.font_size = settings["primary_place_info_font_size"]
    draw.fill_color = settings["primary_birth_place_color"]

    birth_place_text = primary_individual.birth_place or " "
    logger.debug(f"Drawing birth place: {birth_place_text}")

    metrics = draw.get_font_metrics(content_img, birth_place_text, False)
    text_width_px = metrics.text_width * Generation1Constants.PIXEL_RATIO

    translate_x = content_img.width // 2 + settings["primary_birth_place_translate_x"]
    translate_y = (
        Generation1Constants.BIRTH_PLACE_Y + settings["primary_birth_place_translate_y"]
    )

    draw.translate(translate_x, translate_y)
    draw.rotate(settings["primary_birth_place_rotate"])
    draw.translate(-text_width_px // 2, 0)
    draw.text(0, 0, birth_place_text)
    draw.pop()


def _draw_death_info(draw, content_img, primary_individual, settings):
    """Draw death date and place information."""

    # Draw death date
    draw.push()
    draw.font_size = settings["primary_date_info_font_size"]
    draw.fill_color = settings["primary_death_color"]

    death_text = primary_individual.death_date or " "
    logger.debug(f"Drawing death date: {death_text}")

    # Calculate text metrics and position
    metrics = draw.get_font_metrics(content_img, death_text, False)
    text_width_px = metrics.text_width * Generation1Constants.PIXEL_RATIO

    translate_x = content_img.width // 2 + settings["primary_death_translate_x"]
    translate_y = (
        Generation1Constants.DEATH_DATE_Y + settings["primary_death_translate_y"]
    )

    draw.translate(translate_x, translate_y)
    draw.rotate(settings["primary_death_rotate"])
    draw.translate(-text_width_px // 2, 0)
    draw.text(0, 0, death_text)
    draw.pop()

    # Draw death place
    draw.push()
    draw.font_size = settings["primary_place_info_font_size"]
    draw.fill_color = settings["primary_death_place_color"]

    death_place_text = primary_individual.death_place or " "
    logger.debug(f"Drawing death place: {death_place_text}")

    metrics = draw.get_font_metrics(content_img, death_place_text, False)
    text_width_px = metrics.text_width * Generation1Constants.PIXEL_RATIO

    translate_x = (
        Generation1Constants.DEATH_PLACE_X + settings["primary_death_place_translate_x"]
    )
    translate_y = content_img.height // 2 + settings["primary_death_place_translate_y"]

    draw.translate(translate_x, translate_y)
    draw.rotate(settings["primary_death_place_rotate"])
    draw.translate(-text_width_px // 2, 0)
    draw.text(0, 0, death_place_text)
    draw.pop()


def _create_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""

    # Load PDF base template
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_1GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    logger.debug(f"Loading PDF base template: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation1Constants.RESOLUTION
    ) as base_img:
        logger.debug(f"Base template loaded: {base_img.width}x{base_img.height}")

        # Composite content image onto base template
        base_img.composite(
            content_img,
            left=Generation1Constants.COMPOSITE_X,
            top=Generation1Constants.COMPOSITE_Y,
        )

        logger.debug(
            f"Composited content at ({Generation1Constants.COMPOSITE_X}, {Generation1Constants.COMPOSITE_Y})"
        )

        # Create PDF buffer
        return create_pdf_buffer(base_img)
