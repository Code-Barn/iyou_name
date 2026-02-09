import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.image_1generator import generate_1gen_preview
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
class Generation2Constants:
    """Constants for 2-generation chart generation."""

    # Initial translation
    INITIAL_TRANSLATE_X = 350
    INITIAL_TRANSLATE_Y = 350

    # Parent positioning
    FATHER_POSITION_X = 975
    FATHER_POSITION_Y = 1700
    MOTHER_POSITION_X = 0
    MOTHER_POSITION_Y = 0

    # Text positioning for parents
    PARENT_NAME_FONT_SIZE = 72
    PARENT_DATE_INFO_FONT_SIZE = 48
    PARENT_PLACE_INFO_FONT_SIZE = 24

    # Overlay composition
    OVERLAY_SCALE = 0.50

    # PDF compositing
    COMPOSITE_X = 300
    COMPOSITE_Y = 570

    # DPI settings
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72  # Approx 4.1667

    # Text rendering
    MULTILINE_LINE_HEIGHT_RATIO = 1.2


# Settings schema for validation
GENERATION_2_SETTINGS_SCHEMA = {
    # Font settings
    "font_family": (str, "Arial"),
    # Parent generation styling
    "parent_stroke_color": (Color, "black"),
    "parent_font_color": (Color, "black"),
    "parent_stroke_width": (float, 0.5),
    # Father-specific settings
    "father_font_color": (Color, "black"),
    "father_stroke_color": (Color, "black"),
    "father_font_size": (int, 72),
    "father_translate_x": (int, 0),
    "father_translate_y": (int, 0),
    "father_rotate": (int, 0),
    "father_first_translate_x": (int, 0),
    "father_first_translate_y": (int, 0),
    "father_first_rotate": (int, 0),
    "father_middle_translate_x": (int, 0),
    "father_middle_translate_y": (int, 0),
    "father_middle_rotate": (int, 0),
    "father_last_translate_x": (int, 0),
    "father_last_translate_y": (int, 0),
    "father_last_rotate": (int, 0),
    "father_birth_translate_x": (int, 0),
    "father_birth_translate_y": (int, 0),
    "father_birth_rotate": (int, 0),
    "father_birth_place_translate_x": (int, 0),
    "father_birth_place_translate_y": (int, 0),
    "father_birth_place_rotate": (int, 0),
    "father_death_translate_x": (int, 0),
    "father_death_translate_y": (int, 280),
    "father_death_rotate": (int, -90),
    "father_death_place_translate_x": (int, 0),
    "father_death_place_translate_y": (int, 280),
    "father_death_place_rotate": (int, -90),
    # Mother-specific settings
    "mother_font_color": (Color, "black"),
    "mother_stroke_color": (Color, "black"),
    "mother_font_size": (int, 72),
    "mother_translate_x": (int, 0),
    "mother_translate_y": (int, 0),
    "mother_rotate": (int, 0),
    "mother_first_translate_x": (int, 0),
    "mother_first_translate_y": (int, 0),
    "mother_first_rotate": (int, 0),
    "mother_middle_translate_x": (int, 0),
    "mother_middle_translate_y": (int, 0),
    "mother_middle_rotate": (int, 0),
    "mother_last_translate_x": (int, 0),
    "mother_last_translate_y": (int, 0),
    "mother_last_rotate": (int, 0),
    "mother_birth_translate_x": (int, 0),
    "mother_birth_translate_y": (int, 0),
    "mother_birth_rotate": (int, 0),
    "mother_birth_place_translate_x": (int, 0),
    "mother_birth_place_translate_y": (int, 0),
    "mother_birth_place_rotate": (int, 0),
    "mother_death_translate_x": (int, 0),
    "mother_death_translate_y": (int, 280),
    "mother_death_rotate": (int, -90),
    "mother_death_place_translate_x": (int, 0),
    "mother_death_place_translate_y": (int, 280),
    "mother_death_place_rotate": (int, -90),
    # Information styling
    "info_stroke_color": (Color, "gray"),
    "info_stroke_width": (float, 0.25),
    # Overlay settings
    "overlay_scale": (float, 0.50),
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
}


def generate_2gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 2-generation family tree chart using enhanced standardized patterns.

    This enhanced version follows the same standardization patterns as the 1gen generator:
    - Settings validation framework
    - Clean buffer management
    - Consistent logging (no debug prints)
    - Constants extraction
    - Enhanced error handling
    - Robust overlay composition

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
        user_settings, GENERATION_2_SETTINGS_SCHEMA, "2gen"
    )

    logger.info(
        f"Generating 2-generation {template} chart for: {primary_individual.full_name} "
        f"(ID: {primary_individual.id})"
    )

    try:
        # Load the 2gen template
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "2GEN_PREVIEW.png",
        )

        if not os.path.exists(preview_template_path):
            raise GenerationError(
                f"Preview template not found: {preview_template_path}"
            )

        logger.debug(f"Loading preview template: {preview_template_path}")

        with Image(
            filename=preview_template_path, resolution=Generation2Constants.RESOLUTION
        ) as content_img:
            logger.debug(
                f"Content image loaded: {content_img.width}x{content_img.height}"
            )

            # Draw parent generation
            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                draw.font = validated_settings["font_family"]
                draw.stroke_antialias = True
                draw.stroke_width = validated_settings["parent_stroke_width"]
                draw.stroke_color = validated_settings["parent_stroke_color"]

                # Apply initial translation
                draw.translate(
                    x=Generation2Constants.INITIAL_TRANSLATE_X,
                    y=Generation2Constants.INITIAL_TRANSLATE_Y,
                )

                # Draw parents
                _draw_parents(
                    draw,
                    content_img,
                    primary_individual,
                    family_data,
                    validated_settings,
                )

                # Apply drawing to image
                draw(content_img)

            # Generate 1gen overlay with PRIMARY settings
            primary_settings = _extract_primary_settings(user_settings)
            logger.debug(
                f"Generating 1gen overlay with settings: {len(primary_settings)} settings"
            )

            gen1_img_buffer = generate_1gen_preview(
                primary_individual, family_data, "preview", primary_settings
            )

            # Composite the 1gen overlay onto the 2gen image
            _composite_overlay(content_img, gen1_img_buffer, validated_settings)

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
        logger.error(f"Unexpected error in 2gen generation: {e}")
        raise GenerationError(f"2-generation chart generation failed: {e}")


def _draw_parents(
    draw, content_img, primary_individual, family_data, validated_settings
):
    """Draw the parent generation with standardized rendering."""

    # Get parents from family data
    individuals = family_data.get("individuals", {})
    father_id = getattr(primary_individual, "father", None)
    mother_id = getattr(primary_individual, "mother", None)

    father = individuals.get(father_id) if father_id else None
    mother = individuals.get(mother_id) if mother_id else None

    # Draw father if available
    if father:
        _draw_parent(draw, content_img, father, "father", validated_settings)
        logger.debug(f"Drew father: {father.full_name}")
    else:
        logger.debug("No father found in family data")

    # Draw mother if available
    if mother:
        _draw_parent(draw, content_img, mother, "mother", validated_settings)
        logger.debug(f"Drew mother: {mother.full_name}")
    else:
        logger.debug("No mother found in family data")


def _draw_parent(draw, content_img, parent, parent_type, validated_settings):
    """Draw a single parent with standardized positioning and rendering."""

    # Set parent-specific colors and sizes
    prefix = f"{parent_type}_"

    font_color = validated_settings.get(f"{prefix}font_color", Color("black"))
    stroke_color = validated_settings.get(f"{prefix}stroke_color", Color("black"))
    font_size = validated_settings.get(
        f"{prefix}font_size", Generation2Constants.PARENT_NAME_FONT_SIZE
    )

    draw.fill_color = font_color
    draw.stroke_color = stroke_color
    draw.font_size = font_size

    # Get base position
    if parent_type == "father":
        base_x = Generation2Constants.FATHER_POSITION_X
        base_y = Generation2Constants.FATHER_POSITION_Y
    else:  # mother
        base_x = Generation2Constants.MOTHER_POSITION_X
        base_y = Generation2Constants.MOTHER_POSITION_Y

    # Apply parent-specific translations
    translate_x = base_x + validated_settings.get(f"{prefix}translate_x", 0)
    translate_y = base_y + validated_settings.get(f"{prefix}translate_y", 0)

    draw.push()
    draw.translate(translate_x, translate_y)

    # Get name display information
    name_info = get_name_display_info(parent.full_name)
    display_text = name_info["display_text"]

    # Draw name with multiline support using translation
    lines = display_text.split("\n")
    line_height = font_size * Generation2Constants.MULTILINE_LINE_HEIGHT_RATIO
    start_y = -(len(lines) - 1) * line_height / 2

    for i, line in enumerate(lines):
        line_y = start_y + (i * line_height)
        draw.push()
        draw.translate(0, line_y)
        draw.text(0, 0, line)
        draw.pop()

    draw.pop()

    # Draw birth information
    _draw_parent_birth_info(draw, content_img, parent, parent_type, validated_settings)

    # Draw death information
    _draw_parent_death_info(draw, content_img, parent, parent_type, validated_settings)


def _draw_parent_birth_info(draw, content_img, parent, parent_type, validated_settings):
    """Draw birth information for a parent."""

    prefix = f"{parent_type}_"
    birth_color = validated_settings.get(f"{prefix}birth_color", Color("black"))
    birth_place_color = validated_settings.get(
        f"{prefix}birth_place_color", Color("black")
    )

    # Draw birth date
    draw.push()
    draw.font_size = validated_settings.get(
        "primary_date_info_font_size", Generation2Constants.PARENT_DATE_INFO_FONT_SIZE
    )
    draw.fill_color = birth_color

    birth_text = parent.birth_date or " "
    birth_translate_x = validated_settings.get(f"{prefix}birth_translate_x", 0)
    birth_translate_y = validated_settings.get(f"{prefix}birth_translate_y", 0)
    birth_rotate = validated_settings.get(f"{prefix}birth_rotate", 0)

    draw.translate(birth_translate_x, birth_translate_y)
    draw.rotate(birth_rotate)
    draw.text(0, 0, birth_text)
    draw.pop()

    # Draw birth place
    draw.push()
    draw.font_size = validated_settings.get(
        "primary_place_info_font_size", Generation2Constants.PARENT_PLACE_INFO_FONT_SIZE
    )
    draw.fill_color = birth_place_color

    birth_place_text = parent.birth_place or " "
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


def _draw_parent_death_info(draw, content_img, parent, parent_type, validated_settings):
    """Draw death information for a parent."""

    prefix = f"{parent_type}_"
    death_color = validated_settings.get(f"{prefix}death_color", Color("black"))
    death_place_color = validated_settings.get(
        f"{prefix}death_place_color", Color("black")
    )

    # Draw death date
    draw.push()
    draw.font_size = validated_settings.get(
        "primary_date_info_font_size", Generation2Constants.PARENT_DATE_INFO_FONT_SIZE
    )
    draw.fill_color = death_color

    death_text = parent.death_date or " "
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
        "primary_place_info_font_size", Generation2Constants.PARENT_PLACE_INFO_FONT_SIZE
    )
    draw.fill_color = death_place_color

    death_place_text = parent.death_place or " "
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


def _extract_primary_settings(user_settings):
    """Extract PRIMARY settings for 1gen overlay generation."""

    # Check for stored primary settings first (from JavaScript)
    primary_settings = user_settings.get("primary_settings", {})

    if not primary_settings:
        # Fallback: use complete user settings (not extracted subset)
        primary_settings = user_settings
        logger.debug("Using complete user settings for 1gen overlay")
    else:
        logger.debug("Using stored primary settings for 1gen overlay")

    return primary_settings


def _composite_overlay(content_img, gen1_img_buffer, validated_settings):
    """Composite the 1gen overlay onto the 2gen image with enhanced buffer handling."""

    try:
        # Reset buffer position and get bytes
        gen1_img_buffer.seek(0)
        gen1_bytes = gen1_img_buffer.getvalue()

        if not gen1_bytes:
            raise BufferError("1gen overlay buffer is empty")

        # Get overlay settings
        overlay_scale = validated_settings.get(
            "overlay_scale", Generation2Constants.OVERLAY_SCALE
        )
        # Create image from blob and composite
        with Image(blob=gen1_bytes) as gen1_overlay:
            # Scale overlay
            overlay_size = int(gen1_overlay.width * overlay_scale)
            gen1_overlay.resize(overlay_size, overlay_size)

            # Center the overlay
            overlay_x = (content_img.width - overlay_size) // 2
            overlay_y = (content_img.height - overlay_size) // 2

            # Apply position offsets if specified
            overlay_x += validated_settings.get("overlay_position_x", 0)
            overlay_y += validated_settings.get("overlay_position_y", 0)

            # Composite onto content image
            content_img.composite(gen1_overlay, left=overlay_x, top=overlay_y)
            logger.debug(
                f"Composited 1gen overlay at ({overlay_x}, {overlay_y}) with scale {overlay_scale}"
            )

    except Exception as e:
        raise BufferError(f"Failed to composite overlay: {e}")


def _create_final_pdf(content_img, validated_settings):
    """Create final PDF by compositing content onto base template."""

    # Load PDF base template
    base_template_path = os.path.join(
        settings.BASE_DIR,
        "apps/charts/static/charts/images/base_image_templates",
        "US_LETTER_2GEN_BW.pdf",
    )

    if not os.path.exists(base_template_path):
        raise GenerationError(f"PDF base template not found: {base_template_path}")

    logger.debug(f"Loading PDF base template: {base_template_path}")

    with Image(
        filename=base_template_path, resolution=Generation2Constants.RESOLUTION
    ) as base_img:
        logger.debug(f"Base template loaded: {base_img.width}x{base_img.height}")

        # Composite content image onto base template
        base_img.composite(
            content_img,
            left=Generation2Constants.COMPOSITE_X,
            top=Generation2Constants.COMPOSITE_Y,
        )

        logger.debug(
            f"Composited content at ({Generation2Constants.COMPOSITE_X}, {Generation2Constants.COMPOSITE_Y})"
        )

        # Create PDF buffer
        return create_pdf_buffer(base_img)
