"""
Modular individual printer for chart generation.

This module provides a standardized way to print an individual's
name and birth/death information at any position with any rotation.

Used by image_1generator through image_7generator scripts.
"""

import logging
import math

from wand.color import Color
from wand.image import Image

from apps.generator.utils.name_utils import (
    get_name_display_info,
    get_name_display_info_with_settings,
)
from apps.generator.utils.prototype.date_utils import (
    format_date_from_settings,
)
from apps.generator.utils.prototype.place_name_utils import (
    format_place_from_settings,
    get_flag_from_place,
    get_flag_image_path,
)

logger = logging.getLogger(__name__)

# Default PIXEL_RATIO for 300 DPI
PIXEL_RATIO = 300 / 72  # ~4.167


def get_text_width_px(draw, content_img, text):
    """Get text width in pixels for centering with PIXEL_RATIO."""
    if not text:
        return 0
    metrics = draw.get_font_metrics(content_img, text, False)
    return metrics.text_width * PIXEL_RATIO


def get_text_height_px(draw, content_img, text):
    """Get text height in pixels using font metrics for accurate centering."""
    if not text:
        return 0
    metrics = draw.get_font_metrics(content_img, text, False)
    return metrics.text_height * PIXEL_RATIO


def get_text_bounding_box(draw, content_img, text):
    """
    Get the actual text bounding box dimensions using font metrics.
    Returns (width, height) in pixels.
    """
    if not text:
        return (0, 0)
    metrics = draw.get_font_metrics(content_img, text, True)
    width = (
        (metrics.x1 - metrics.x0) * PIXEL_RATIO
        if hasattr(metrics, "x1")
        else metrics.text_width * PIXEL_RATIO
    )
    height = (
        (metrics.y1 - metrics.y0) * PIXEL_RATIO
        if hasattr(metrics, "y1")
        else metrics.text_height * PIXEL_RATIO
    )
    return (width, height)


def print_individual(
    draw,
    content_img,
    individual,
    settings,
    # Position parameters
    center_x=0,
    center_y=0,
    rotation=0,
    # Font sizes
    name_font_size=72,
    date_font_size=48,
    place_font_size=24,
    # Individual date/place font sizes (for paired text)
    birth_date_font_size=None,
    death_date_font_size=None,
    birth_place_font_size=None,
    death_place_font_size=None,
    # Paired dates helper: set both on same row
    paired_dates_base_y=None,
    birth_date_paired_offset_x=0,
    death_date_paired_offset_x=0,
    paired_places_base_y=None,
    birth_place_paired_offset_x=0,
    death_place_paired_offset_x=0,
    # Name positions - base position (like dates/places in 1gen)
    full_name=None,  # Simple single-line full name override
    first_name_base_x=None,
    first_name_base_y=None,
    first_name_offset_x=0,
    first_name_offset_y=0,
    first_name_rotation=0,
    middle_name_base_x=None,
    middle_name_base_y=None,
    middle_name_offset_x=0,
    middle_name_offset_y=0,
    middle_name_rotation=0,
    last_name_base_x=None,
    last_name_base_y=None,
    last_name_offset_x=0,
    last_name_offset_y=0,
    last_name_rotation=0,
    # Birth info - absolute base positions (user translate adjusts from there)
    birth_date_base_x=0,
    birth_date_base_y=None,
    birth_date_offset_x=0,
    birth_date_offset_y=0,
    birth_date_rotation=0,
    birth_place_base_x=None,
    birth_place_base_y=0,
    birth_place_offset_x=0,
    birth_place_offset_y=0,
    birth_place_rotation=0,
    # Death info
    death_date_base_x=None,
    death_date_base_y=0,
    death_date_offset_x=0,
    death_date_offset_y=0,
    death_date_rotation=0,
    death_place_base_x=0,
    death_place_base_y=None,
    death_place_offset_x=0,
    death_place_offset_y=0,
    death_place_rotation=0,
    # Flag options
    birth_flag="",
    death_flag="",
    flag_base_x=None,
    flag_base_y=None,
    flag_offset_x=0,
    flag_offset_y=0,
    flag_rotation=0,
    flag_size=None,
    flag_font_size=None,
    flag_font=None,
    # Options
    use_display_text=True,
    use_gravity_center=False,
    multiline_line_spacing=1.2,
    multiline_alignment="center",
    chart_settings=None,
    date_year_only=False,
    outside_stroke=False,
    outside_stroke_width=5,
    outside_stroke_color=None,
):
    """
    Print an individual's name and birth/death info at a given position.

    For name: uses either gravity center or offset-based positioning.
    For info text: uses absolute base positions + user offsets + centering.

    Args:
        draw: Wand Drawing object
        content_img: Wand Image object (for font metrics)
        individual: PersonData object
        settings: Validated settings dictionary
        center_x/y: Image center for offset-based positioning
        rotation: Base rotation for 180/90/270 positioning
        name_font_size: Font size for name
        date_font_size: Font size for dates
        place_font_size: Font size for places
        *_offset_x/y: User adjustment from base position
        *_base_x/y: Absolute base position (None = use center)
        *_rotation: Rotation angle
        use_display_text: Use display_text with newlines
        use_gravity_center: Use gravity="center" for name
        chart_settings: Settings dict for date and name formatting (from settings_validator)
        date_year_only: If True, print only year for dates (for compact display)
        outside_stroke: If True, render text twice - first with white fill for border, then normal
    """
    import logging

    logger = logging.getLogger(__name__)

    # Determine stroke color for outside stroke
    stroke_color = outside_stroke_color if outside_stroke_color else Color("white")

    # Read line spacing from settings - check generation-specific first, then fall back to generic
    # This ensures each generation uses its own setting without inheriting from other gens
    if settings:
        # Check for generation-specific prefixed setting first
        if "gen5_name_line_spacing" in settings:
            multiline_line_spacing = settings["gen5_name_line_spacing"]
            logger.info(
                f"[print_individual] Using gen5_name_line_spacing: {multiline_line_spacing}"
            )
        elif "gen6_name_line_spacing" in settings:
            multiline_line_spacing = settings["gen6_name_line_spacing"]
            logger.info(
                f"[print_individual] Using gen6_name_line_spacing: {multiline_line_spacing}"
            )
        elif "gen7_name_line_spacing" in settings:
            multiline_line_spacing = settings["gen7_name_line_spacing"]
            logger.info(
                f"[print_individual] Using gen7_name_line_spacing: {multiline_line_spacing}"
            )
        elif "name_line_spacing" in settings:
            multiline_line_spacing = settings["name_line_spacing"]
            logger.info(
                f"[print_individual] Using name_line_spacing from settings: {multiline_line_spacing}"
            )
        elif "multiline_line_spacing" in settings:
            multiline_line_spacing = settings["multiline_line_spacing"]

    # Handle outside stroke by running twice
    if outside_stroke:
        logger.info(
            f"[print_individual] outside_stroke=True, width={outside_stroke_width}, color={stroke_color}"
        )
        # First pass: draw with contrasting fill + contrasting stroke to create border
        _settings_border = settings.copy() if settings else {}
        _settings_border["primary_font_color"] = stroke_color
        _settings_border["primary_birth_color"] = stroke_color
        _settings_border["primary_death_color"] = stroke_color
        _settings_border["primary_birth_place_color"] = stroke_color
        _settings_border["primary_death_place_color"] = stroke_color
        _settings_border["primary_stroke_color"] = stroke_color
        _settings_border["primary_stroke_width"] = outside_stroke_width
        _settings_border["primary_birth_stroke_color"] = stroke_color
        _settings_border["primary_death_stroke_color"] = stroke_color
        _settings_border["primary_birth_place_stroke_color"] = stroke_color
        _settings_border["primary_death_place_stroke_color"] = stroke_color
        # Generation-specific stroke settings
        _settings_border["great_grandparent_stroke_color"] = stroke_color
        _settings_border["great_grandparent_stroke_width"] = outside_stroke_width
        _settings_border["great_great_grandparent_stroke_color"] = stroke_color
        _settings_border["great_great_grandparent_stroke_width"] = outside_stroke_width
        _settings_border["great_great_great_grandparent_stroke_color"] = Color("white")
        _settings_border["great_great_great_grandparent_stroke_width"] = (
            outside_stroke_width
        )
        _settings_border["great_great_great_great_grandparent_stroke_color"] = (
            stroke_color
        )
        _settings_border["great_great_great_great_grandparent_stroke_width"] = (
            outside_stroke_width
        )
        _settings_border["info_stroke_color"] = stroke_color
        _settings_border["info_stroke_width"] = outside_stroke_width

        # Recursive call with border settings
        print_individual(
            draw,
            content_img,
            individual,
            _settings_border,
            center_x=center_x,
            center_y=center_y,
            rotation=rotation,
            name_font_size=name_font_size,
            date_font_size=date_font_size,
            place_font_size=place_font_size,
            birth_date_font_size=birth_date_font_size,
            death_date_font_size=death_date_font_size,
            birth_place_font_size=birth_place_font_size,
            death_place_font_size=death_place_font_size,
            paired_dates_base_y=paired_dates_base_y,
            birth_date_paired_offset_x=birth_date_paired_offset_x,
            death_date_paired_offset_x=death_date_paired_offset_x,
            paired_places_base_y=paired_places_base_y,
            birth_place_paired_offset_x=birth_place_paired_offset_x,
            death_place_paired_offset_x=death_place_paired_offset_x,
            full_name=full_name,
            first_name_base_x=first_name_base_x,
            first_name_base_y=first_name_base_y,
            first_name_offset_x=first_name_offset_x,
            first_name_offset_y=first_name_offset_y,
            first_name_rotation=first_name_rotation,
            middle_name_base_x=middle_name_base_x,
            middle_name_base_y=middle_name_base_y,
            middle_name_offset_x=middle_name_offset_x,
            middle_name_offset_y=middle_name_offset_y,
            middle_name_rotation=middle_name_rotation,
            last_name_base_x=last_name_base_x,
            last_name_base_y=last_name_base_y,
            last_name_offset_x=last_name_offset_x,
            last_name_offset_y=last_name_offset_y,
            last_name_rotation=last_name_rotation,
            birth_date_base_x=birth_date_base_x,
            birth_date_base_y=birth_date_base_y,
            birth_date_offset_x=birth_date_offset_x,
            birth_date_offset_y=birth_date_offset_y,
            birth_date_rotation=birth_date_rotation,
            birth_place_base_x=birth_place_base_x,
            birth_place_base_y=birth_place_base_y,
            birth_place_offset_x=birth_place_offset_x,
            birth_place_offset_y=birth_place_offset_y,
            birth_place_rotation=birth_place_rotation,
            death_date_base_x=death_date_base_x,
            death_date_base_y=death_date_base_y,
            death_date_offset_x=death_date_offset_x,
            death_date_offset_y=death_date_offset_y,
            death_date_rotation=death_date_rotation,
            death_place_base_x=death_place_base_x,
            death_place_base_y=death_place_base_y,
            death_place_offset_x=death_place_offset_x,
            death_place_offset_y=death_place_offset_y,
            death_place_rotation=death_place_rotation,
            birth_flag=birth_flag,
            death_flag=death_flag,
            flag_base_x=flag_base_x,
            flag_base_y=flag_base_y,
            flag_offset_x=flag_offset_x,
            flag_offset_y=flag_offset_y,
            flag_rotation=flag_rotation,
            flag_size=flag_size,
            flag_font_size=flag_font_size,
            flag_font=flag_font,
            use_display_text=use_display_text,
            use_gravity_center=use_gravity_center,
            multiline_line_spacing=multiline_line_spacing,
            multiline_alignment=multiline_alignment,
            chart_settings=chart_settings,
            date_year_only=date_year_only,
            outside_stroke=False,  # Prevent infinite recursion
            outside_stroke_color=outside_stroke_color,
        )
        # Second pass: draw with normal settings but NO stroke (0 width)
        _settings_no_stroke = settings.copy() if settings else {}
        _settings_no_stroke["primary_stroke_width"] = 0
        _settings_no_stroke["primary_birth_stroke_width"] = 0
        _settings_no_stroke["primary_death_stroke_width"] = 0
        _settings_no_stroke["primary_birth_place_stroke_width"] = 0
        _settings_no_stroke["primary_death_place_stroke_width"] = 0
        _settings_no_stroke["great_grandparent_stroke_width"] = 0
        _settings_no_stroke["great_great_grandparent_stroke_width"] = 0
        _settings_no_stroke["great_great_great_grandparent_stroke_width"] = 0
        _settings_no_stroke["great_great_great_great_grandparent_stroke_width"] = 0
        _settings_no_stroke["info_stroke_width"] = 0
        return print_individual(
            draw,
            content_img,
            individual,
            _settings_no_stroke,
            center_x=center_x,
            center_y=center_y,
            rotation=rotation,
            name_font_size=name_font_size,
            date_font_size=date_font_size,
            place_font_size=place_font_size,
            birth_date_font_size=birth_date_font_size,
            death_date_font_size=death_date_font_size,
            birth_place_font_size=birth_place_font_size,
            death_place_font_size=death_place_font_size,
            paired_dates_base_y=paired_dates_base_y,
            birth_date_paired_offset_x=birth_date_paired_offset_x,
            death_date_paired_offset_x=death_date_paired_offset_x,
            paired_places_base_y=paired_places_base_y,
            birth_place_paired_offset_x=birth_place_paired_offset_x,
            death_place_paired_offset_x=death_place_paired_offset_x,
            full_name=full_name,
            first_name_base_x=first_name_base_x,
            first_name_base_y=first_name_base_y,
            first_name_offset_x=first_name_offset_x,
            first_name_offset_y=first_name_offset_y,
            first_name_rotation=first_name_rotation,
            middle_name_base_x=middle_name_base_x,
            middle_name_base_y=middle_name_base_y,
            middle_name_offset_x=middle_name_offset_x,
            middle_name_offset_y=middle_name_offset_y,
            middle_name_rotation=middle_name_rotation,
            last_name_base_x=last_name_base_x,
            last_name_base_y=last_name_base_y,
            last_name_offset_x=last_name_offset_x,
            last_name_offset_y=last_name_offset_y,
            last_name_rotation=last_name_rotation,
            birth_date_base_x=birth_date_base_x,
            birth_date_base_y=birth_date_base_y,
            birth_date_offset_x=birth_date_offset_x,
            birth_date_offset_y=birth_date_offset_y,
            birth_date_rotation=birth_date_rotation,
            birth_place_base_x=birth_place_base_x,
            birth_place_base_y=birth_place_base_y,
            birth_place_offset_x=birth_place_offset_x,
            birth_place_offset_y=birth_place_offset_y,
            birth_place_rotation=birth_place_rotation,
            death_date_base_x=death_date_base_x,
            death_date_base_y=death_date_base_y,
            death_date_offset_x=death_date_offset_x,
            death_date_offset_y=death_date_offset_y,
            death_date_rotation=death_date_rotation,
            death_place_base_x=death_place_base_x,
            death_place_base_y=death_place_base_y,
            death_place_offset_x=death_place_offset_x,
            death_place_offset_y=death_place_offset_y,
            death_place_rotation=death_place_rotation,
            birth_flag=birth_flag,
            death_flag=death_flag,
            flag_base_x=flag_base_x,
            flag_base_y=flag_base_y,
            flag_offset_x=flag_offset_x,
            flag_offset_y=flag_offset_y,
            flag_rotation=flag_rotation,
            flag_size=flag_size,
            flag_font_size=flag_font_size,
            flag_font=flag_font,
            use_display_text=use_display_text,
            use_gravity_center=use_gravity_center,
            multiline_line_spacing=multiline_line_spacing,
            multiline_alignment=multiline_alignment,
            chart_settings=chart_settings,
            date_year_only=date_year_only,
            outside_stroke=False,
            outside_stroke_width=outside_stroke_width,
            outside_stroke_color=outside_stroke_color,
        )

    # Get settings with optional chart settings
    chart_settings = chart_settings or {}

    # Check if name formatting settings are provided
    name_settings = {}
    if "name_use_first_middle_only" in chart_settings:
        name_settings["name_use_first_middle_only"] = chart_settings.get(
            "name_use_first_middle_only", False
        )
    if "name_hide_hyphenated_surname" in chart_settings:
        name_settings["name_hide_hyphenated_surname"] = chart_settings.get(
            "name_hide_hyphenated_surname", False
        )

    if name_settings:
        name_info = get_name_display_info_with_settings(
            individual.full_name, name_settings
        )
    else:
        name_info = get_name_display_info(individual.full_name)

    first_name = name_info.get("first_name", "")
    middle_name = name_info.get("middle_name", "")
    last_name = name_info.get("last_name", "")
    display_text = name_info.get("display_text", "")

    # Override with full_name if provided (simple single-line mode)
    if full_name:
        first_name = full_name
        middle_name = ""
        last_name = ""
        display_text = ""

    # Get text info
    birth_date = individual.birth_date or ""
    birth_place = individual.birth_place or ""
    death_date = individual.death_date or ""
    death_place = individual.death_place or ""

    # Apply date formatting if settings provided
    if birth_date:
        birth_date = format_date_from_settings(
            birth_date, chart_settings, year_only=date_year_only
        )
    if death_date:
        death_date = format_date_from_settings(
            death_date, chart_settings, year_only=date_year_only
        )

    # Apply place formatting if settings provided
    if birth_place:
        birth_place = format_place_from_settings(birth_place, chart_settings)
    if death_place:
        death_place = format_place_from_settings(death_place, chart_settings)

    # Handle flags if enabled in settings
    # Skip flag rendering in print_individual if using overlay approach (flag rendered separately in generator)
    show_flag = chart_settings.get("place_show_flag", False)
    flag_type = chart_settings.get("place_flag_type", "birth")
    flag_format = chart_settings.get("place_flag_format", "png")
    # New: if flag is rendered in generator's overlay stage, skip in print_individual
    flag_in_overlay = chart_settings.get("place_flag_in_overlay", False)

    birth_flag = ""
    death_flag = ""
    birth_flag_path = ""
    death_flag_path = ""
    # Skip flag rendering in print_individual if using overlay approach
    if show_flag and not flag_in_overlay:
        if flag_type == "birth":
            birth_flag = get_flag_from_place(individual.birth_place or "")
            birth_flag_path = get_flag_image_path(individual.birth_place or "")
        elif flag_type == "death":
            death_flag = get_flag_from_place(individual.death_place or "")
            death_flag_path = get_flag_image_path(individual.death_place or "")

    # Track if name has been drawn (to avoid duplicates)
    name_drawn = False

    # Set common font properties
    draw.font = settings.get("font_family", "Arial")
    draw.stroke_color = settings.get("info_stroke_color", Color("gray"))
    draw.stroke_width = settings.get("info_stroke_width", 0.25)
    draw.stroke_antialias = True

    # Stroke settings for primary name
    primary_stroke_color = settings.get("primary_stroke_color", Color("black"))
    primary_stroke_width = settings.get("primary_stroke_width", 0.5)

    # Calculate effective rotation for this individual (base + element-specific)
    # For 180° rotation (mother in 2gen), we flip both X and Y offsets

    # Draw name - mutually exclusive options
    # Option 1: gravity center (1gen only - uses image center)
    if use_gravity_center and display_text:
        draw.push()
        draw.fill_color = settings.get("primary_font_color", Color("black"))
        draw.stroke_color = primary_stroke_color
        draw.stroke_width = primary_stroke_width
        draw.font_size = name_font_size
        draw.gravity = "center"
        draw.rotate(first_name_rotation)
        draw.text(0, 0, display_text)
        draw.pop()
        name_drawn = True

    # Option 2: multiline display_text at base position (with \n between parts)
    elif use_display_text and display_text:
        draw.push()
        draw.fill_color = settings.get("primary_font_color", Color("black"))
        draw.stroke_color = primary_stroke_color
        draw.stroke_width = primary_stroke_width
        draw.font_size = name_font_size

        # Determine base position - use base_x/base_y if provided, else use center
        if first_name_base_x is not None:
            base_x = first_name_base_x
        else:
            base_x = center_x
        if first_name_base_y is not None:
            base_y = first_name_base_y
        else:
            base_y = center_y

        # Handle rotation - transform base position around center
        if rotation == 180:
            final_base_x = 2 * center_x - base_x
            final_base_y = 2 * center_y - base_y
            offset_x = -first_name_offset_x
            offset_y = -first_name_offset_y
            rot = rotation + first_name_rotation
        elif rotation == 90:
            final_base_x = 2 * center_x - base_y
            final_base_y = base_x
            offset_x = -first_name_offset_y
            offset_y = first_name_offset_x
            rot = rotation + first_name_rotation
        elif rotation == 270:
            final_base_x = base_y
            final_base_y = 2 * center_y - base_x
            offset_x = first_name_offset_y
            offset_y = -first_name_offset_x
            rot = rotation + first_name_rotation
        else:
            final_base_x = base_x
            final_base_y = base_y
            offset_x = first_name_offset_x
            offset_y = first_name_offset_y
            rot = rotation + first_name_rotation

        # Multiline centering: use actual font metrics for vertical centering only
        # (horizontal centering is handled by text_alignment="center" when drawing)
        lines = display_text.split("\n")

        if lines:
            # Use font metrics for line height (includes ascenders and descenders)
            line_height = name_font_size * PIXEL_RATIO * multiline_line_spacing
            # Calculate vertical centering offset based on FIXED 3-line reference
            # This ensures all positions align consistently regardless of actual line count
            # (most names have 1-3 lines, we use 3 as the reference for symmetry)
            total_height_reference = 3 * line_height
            centering_offset = total_height_reference // 2

            # For 2-line names, add offset to push them down to match 3-line center
            # (difference between 3-line center and 2-line center = 0.5 * line_height)
            if len(lines) == 2:
                centering_offset += line_height // 2
            # For 1-line names, add more offset to push them down to match 3-line center
            # (difference between 3-line center and 1-line center = 1.0 * line_height)
            elif len(lines) == 1:
                centering_offset += line_height
        else:
            centering_offset = 0
            line_height = name_font_size * PIXEL_RATIO

        # Apply centering offset AFTER rotation - translation is in rotated coordinate space
        # In rotated space: for 90°, rotated x points in original -y, rotated y points in original x
        # To center vertically in original space, we need to offset appropriately
        if rotation == 180:
            # For 180°, both x and y flip - offset goes in rotated y (original -y)
            final_x = final_base_x + offset_x
            final_y = final_base_y + offset_y - centering_offset
        elif rotation == 90:
            # For 90°, rotated x points in original -y direction
            final_x = final_base_x + offset_x - centering_offset
            final_y = final_base_y + offset_y
        elif rotation == 270:
            # For 270°, rotated y points in original -x direction (offset_y becomes offset_x after swap)
            # centering goes in rotated x which maps to original +y
            final_x = final_base_x + offset_x + centering_offset
            final_y = final_base_y + offset_y
        else:
            # No rotation - normal vertical centering on base position
            final_x = final_base_x + offset_x
            final_y = final_base_y + offset_y + centering_offset

        draw.translate(final_x, final_y)
        draw.rotate(rot)

        # Draw each line centered horizontally
        draw.text_alignment = "center"
        for i, line in enumerate(lines):
            line_y = i * line_height
            draw.push()
            draw.translate(0, line_y)
            draw.text(0, 0, line)
            draw.pop()
        draw.pop()
        name_drawn = True

    elif first_name:
        # Draw individual name parts (first, middle, last)
        draw.push()
        draw.fill_color = settings.get("primary_font_color", Color("black"))
        draw.stroke_color = primary_stroke_color
        draw.stroke_width = primary_stroke_width
        draw.font_size = name_font_size

        text_width = get_text_width_px(draw, content_img, first_name)

        # Determine base position
        if first_name_base_x is not None:
            base_x = first_name_base_x
        else:
            base_x = center_x
        if first_name_base_y is not None:
            base_y = first_name_base_y
        else:
            base_y = center_y

        # Handle rotation - transform base position around center
        if rotation == 180:
            # 180°: flip both X and Y around center
            final_base_x = 2 * center_x - base_x
            final_base_y = 2 * center_y - base_y
            offset_x = -first_name_offset_x
            offset_y = -first_name_offset_y
            rot = rotation + first_name_rotation
        elif rotation == 90:
            # 90°: swap X/Y with flip
            final_base_x = 2 * center_x - base_y
            final_base_y = base_x
            offset_x = -first_name_offset_y
            offset_y = first_name_offset_x
            rot = rotation + first_name_rotation
        elif rotation == 270:
            # 270°: swap X/Y
            final_base_x = base_y
            final_base_y = 2 * center_y - base_x
            offset_x = first_name_offset_y
            offset_y = -first_name_offset_x
            rot = rotation + first_name_rotation
        else:
            # No rotation
            final_base_x = base_x
            final_base_y = base_y
            offset_x = first_name_offset_x
            offset_y = first_name_offset_y
            rot = rotation + first_name_rotation

        # Apply offset
        final_x = final_base_x + offset_x
        final_y = final_base_y + offset_y

        # 1gen pattern: translate, rotate, then center
        draw.translate(final_x, final_y)
        draw.rotate(rot)
        # Center horizontally
        draw.translate(-text_width // 2, 0)
        draw.text(0, 0, first_name)
        draw.pop()

    # Draw middle name (skip if name was already drawn via gravity_center or use_display_text)
    if middle_name and not name_drawn:
        draw.push()
        draw.fill_color = settings.get("primary_font_color", Color("black"))
        draw.stroke_color = primary_stroke_color
        draw.stroke_width = primary_stroke_width
        draw.font_size = name_font_size

        text_width = get_text_width_px(draw, content_img, middle_name)

        # Determine base position
        if middle_name_base_x is not None:
            base_x = middle_name_base_x
        else:
            base_x = center_x
        if middle_name_base_y is not None:
            base_y = middle_name_base_y
        else:
            base_y = center_y

        # Handle rotation - transform base position around center
        if rotation == 180:
            final_base_x = 2 * center_x - base_x
            final_base_y = 2 * center_y - base_y
            offset_x = -middle_name_offset_x
            offset_y = -middle_name_offset_y
            rot = rotation + middle_name_rotation
        elif rotation == 90:
            final_base_x = 2 * center_x - base_y
            final_base_y = base_x
            offset_x = -middle_name_offset_y
            offset_y = middle_name_offset_x
            rot = rotation + middle_name_rotation
        elif rotation == 270:
            final_base_x = base_y
            final_base_y = 2 * center_y - base_x
            offset_x = middle_name_offset_y
            offset_y = -middle_name_offset_x
            rot = rotation + middle_name_rotation
        else:
            final_base_x = base_x
            final_base_y = base_y
            offset_x = middle_name_offset_x
            offset_y = middle_name_offset_y
            rot = rotation + middle_name_rotation

        # Apply offset
        final_x = final_base_x + offset_x
        final_y = final_base_y + offset_y

        # 1gen pattern: translate, rotate, then center
        draw.translate(final_x, final_y)
        draw.rotate(rot)
        draw.translate(-text_width // 2, 0)
        draw.text(0, 0, middle_name)
        draw.pop()

    # Draw last name (skip if name was already drawn via gravity_center or use_display_text)
    if last_name and not name_drawn:
        draw.push()
        draw.fill_color = settings.get("primary_font_color", Color("black"))
        draw.stroke_color = primary_stroke_color
        draw.stroke_width = primary_stroke_width
        draw.font_size = name_font_size

        text_width = get_text_width_px(draw, content_img, last_name)

        # Determine base position
        if last_name_base_x is not None:
            base_x = last_name_base_x
        else:
            base_x = center_x
        if last_name_base_y is not None:
            base_y = last_name_base_y
        else:
            base_y = center_y

        # Handle rotation - transform base position around center
        if rotation == 180:
            # 180°: flip both X and Y around center
            final_base_x = 2 * center_x - base_x
            final_base_y = 2 * center_y - base_y
            offset_x = -last_name_offset_x
            offset_y = -last_name_offset_y
            rot = rotation + last_name_rotation
        elif rotation == 90:
            # 90°: swap X/Y with flip
            final_base_x = 2 * center_x - base_y
            final_base_y = base_x
            offset_x = -last_name_offset_y
            offset_y = last_name_offset_x
            rot = rotation + last_name_rotation
        elif rotation == 270:
            # 270°: swap X/Y
            final_base_x = base_y
            final_base_y = 2 * center_y - base_x
            offset_x = last_name_offset_y
            offset_y = -last_name_offset_x
            rot = rotation + last_name_rotation
        else:
            # No rotation
            final_base_x = base_x
            final_base_y = base_y
            offset_x = last_name_offset_x
            offset_y = last_name_offset_y
            rot = rotation + last_name_rotation

        # Apply offset
        final_x = final_base_x + offset_x
        final_y = final_base_y + offset_y

        # 1gen pattern: translate, rotate, then center
        draw.translate(final_x, final_y)
        draw.rotate(rot)
        # After rotation, translate by -text_width//2 to center
        # For vertical text (-90°), this centers along the vertical line
        # For horizontal text (0°), this centers horizontally
        draw.translate(-text_width // 2, 0)
        draw.text(0, 0, last_name)
        draw.pop()

    # Reset to info stroke settings for birth/death info
    draw.stroke_color = settings.get("info_stroke_color", Color("gray"))
    draw.stroke_width = settings.get("info_stroke_width", 0.25)

    # Draw birth date
    # Pattern: translate to (base_x + offset_x, center_y + offset_y), rotate, center, draw
    if birth_date:
        draw.push()
        draw.fill_color = settings.get("primary_birth_color", Color("black"))
        # Use individual font size if provided, otherwise use shared date_font_size
        draw.font_size = (
            birth_date_font_size if birth_date_font_size is not None else date_font_size
        )

        text_width = get_text_width_px(draw, content_img, birth_date)

        # Base X: use provided base_x, or center if None
        base_x = birth_date_base_x if birth_date_base_x is not None else center_x
        # Base Y: use paired_dates_base_y if provided, otherwise use birth_date_base_y or center_y
        if paired_dates_base_y is not None:
            base_y = paired_dates_base_y
        else:
            base_y = birth_date_base_y if birth_date_base_y is not None else center_y

        # Apply paired offset if provided
        effective_offset_x = birth_date_offset_x + birth_date_paired_offset_x

        # Apply rotation transformation around center
        if rotation == 180:
            final_base_x = 2 * center_x - base_x
            final_base_y = 2 * center_y - base_y
            offset_x = -effective_offset_x
            offset_y = -birth_date_offset_y
            rot = rotation + birth_date_rotation
        elif rotation == 90:
            final_base_x = 2 * center_x - base_y
            final_base_y = base_x
            offset_x = -birth_date_offset_y
            offset_y = effective_offset_x
            rot = rotation + birth_date_rotation
        elif rotation == 270:
            final_base_x = base_y
            final_base_y = 2 * center_y - base_x
            offset_x = birth_date_offset_y
            offset_y = -effective_offset_x
            rot = rotation + birth_date_rotation
        else:
            final_base_x = base_x
            final_base_y = base_y
            offset_x = effective_offset_x
            offset_y = birth_date_offset_y
            rot = birth_date_rotation

        translate_x = final_base_x + offset_x
        translate_y = final_base_y + offset_y

        draw.translate(translate_x, translate_y)
        draw.rotate(rot)
        draw.translate(-text_width // 2, 0)
        draw.text(0, 0, birth_date)
        draw.pop()

    # Draw birth place
    # Pattern: translate to (center_x + offset_x, base_y + offset_y), rotate, center, draw
    if birth_place:
        draw.push()
        draw.fill_color = settings.get("primary_birth_place_color", Color("black"))
        draw.font_size = place_font_size

        text_width = get_text_width_px(draw, content_img, birth_place)

        # Base X: use center if not specified
        base_x = birth_place_base_x if birth_place_base_x is not None else center_x
        # Base Y: use paired_places_base_y if provided, otherwise use birth_place_base_y or center_y
        if paired_places_base_y is not None:
            base_y = paired_places_base_y
        else:
            base_y = birth_place_base_y if birth_place_base_y is not None else center_y

        # Apply paired offset if provided
        effective_offset_x = birth_place_offset_x + birth_place_paired_offset_x

        # Apply rotation transformation around center
        if rotation == 180:
            final_base_x = 2 * center_x - base_x
            final_base_y = 2 * center_y - base_y
            offset_x = -effective_offset_x
            offset_y = -birth_place_offset_y
            rot = rotation + birth_place_rotation
        elif rotation == 90:
            final_base_x = 2 * center_x - base_y
            final_base_y = base_x
            offset_x = -birth_place_offset_y
            offset_y = effective_offset_x
            rot = rotation + birth_place_rotation
        elif rotation == 270:
            final_base_x = base_y
            final_base_y = 2 * center_y - base_x
            offset_x = birth_place_offset_y
            offset_y = -effective_offset_x
            rot = rotation + birth_place_rotation
        else:
            final_base_x = base_x
            final_base_y = base_y
            offset_x = effective_offset_x
            offset_y = birth_place_offset_y
            rot = birth_place_rotation

        translate_x = final_base_x + offset_x
        translate_y = final_base_y + offset_y

        draw.translate(translate_x, translate_y)
        draw.rotate(rot)
        draw.translate(-text_width // 2, 0)
        draw.text(0, 0, birth_place)
        draw.pop()

    # Draw death date
    # Pattern: translate to (center_x + offset_x, base_y + offset_y), rotate, center, draw
    if death_date:
        draw.push()
        draw.fill_color = settings.get("primary_death_color", Color("black"))
        # Use individual font size if provided, otherwise use shared date_font_size
        draw.font_size = (
            death_date_font_size if death_date_font_size is not None else date_font_size
        )

        text_width = get_text_width_px(draw, content_img, death_date)

        # Base X: use center if not specified
        base_x = death_date_base_x if death_date_base_x is not None else center_x
        # Base Y: use paired_dates_base_y if provided, otherwise use death_date_base_y or center_y
        if paired_dates_base_y is not None:
            base_y = paired_dates_base_y
        else:
            base_y = death_date_base_y if death_date_base_y is not None else center_y

        # Apply paired offset if provided
        effective_offset_x = death_date_offset_x + death_date_paired_offset_x

        # Apply rotation transformation around center
        if rotation == 180:
            final_base_x = 2 * center_x - base_x
            final_base_y = 2 * center_y - base_y
            offset_x = -effective_offset_x
            offset_y = -death_date_offset_y
            rot = rotation + death_date_rotation
        elif rotation == 90:
            final_base_x = 2 * center_x - base_y
            final_base_y = base_x
            offset_x = -death_date_offset_y
            offset_y = effective_offset_x
            rot = rotation + death_date_rotation
        elif rotation == 270:
            final_base_x = base_y
            final_base_y = 2 * center_y - base_x
            offset_x = death_date_offset_y
            offset_y = -effective_offset_x
            rot = rotation + death_date_rotation
        else:
            final_base_x = base_x
            final_base_y = base_y
            offset_x = effective_offset_x
            offset_y = death_date_offset_y
            rot = death_date_rotation

        translate_x = final_base_x + offset_x
        translate_y = final_base_y + offset_y

        draw.translate(translate_x, translate_y)
        draw.rotate(rot)
        draw.translate(-text_width // 2, 0)
        draw.text(0, 0, death_date)
        draw.pop()

    # Draw death place
    # Pattern: translate to (base_x + offset_x, center_y + offset_y), rotate, center, draw
    if death_place:
        draw.push()
        draw.fill_color = settings.get("primary_death_place_color", Color("black"))
        draw.font_size = place_font_size

        text_width = get_text_width_px(draw, content_img, death_place)

        # Base X: use provided base_x, or center if None
        base_x = death_place_base_x if death_place_base_x is not None else center_x
        # Base Y: use paired_places_base_y if provided, otherwise use death_place_base_y or center_y
        if paired_places_base_y is not None:
            base_y = paired_places_base_y
        else:
            base_y = death_place_base_y if death_place_base_y is not None else center_y

        # Apply paired offset if provided
        effective_offset_x = death_place_offset_x + death_place_paired_offset_x

        # Apply rotation transformation around center
        if rotation == 180:
            final_base_x = 2 * center_x - base_x
            final_base_y = 2 * center_y - base_y
            offset_x = -effective_offset_x
            offset_y = -death_place_offset_y
            rot = rotation + death_place_rotation
        elif rotation == 90:
            final_base_x = 2 * center_x - base_y
            final_base_y = base_x
            offset_x = -death_place_offset_y
            offset_y = effective_offset_x
            rot = rotation + death_place_rotation
        elif rotation == 270:
            final_base_x = base_y
            final_base_y = 2 * center_y - base_x
            offset_x = death_place_offset_y
            offset_y = -effective_offset_x
            rot = rotation + death_place_rotation
        else:
            final_base_x = base_x
            final_base_y = base_y
            offset_x = effective_offset_x
            offset_y = death_place_offset_y
            rot = death_place_rotation

        translate_x = final_base_x + offset_x
        translate_y = final_base_y + offset_y

        draw.translate(translate_x, translate_y)
        draw.rotate(rot)
        draw.translate(-text_width // 2, 0)
        draw.text(0, 0, death_place)
        draw.pop()

    # Draw flags - separate positioned elements aligned to name
    if (
        (birth_flag and flag_format == "emoji")
        or (birth_flag_path and flag_format == "png")
        or (death_flag and flag_format == "emoji")
        or (death_flag_path and flag_format == "png")
    ):
        import math

        draw.fill_color = settings.get("primary_birth_place_color", Color("black"))

        # Calculate flag position with rotational translation
        # flag_base_x/flag_base_y are OFFSETS from center (like overlay approach)
        dx = flag_base_x if flag_base_x is not None else 0
        dy = flag_base_y if flag_base_y is not None else -50

        # Apply rotation to offset
        angle_rad = math.radians(rotation)
        rotated_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        rotated_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)

        base_x = center_x + rotated_x
        base_y = center_y + rotated_y

        # Use emoji-compatible font for flags (when using emoji format)
        flag_font = (
            flag_font
            or settings.get("flag_font")
            or "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf"
        )

        # Get flag size from parameter or use a sensible default
        # Note: Each generation should pass flag_size explicitly via genX_flag_size
        flag_size = flag_size or 48

        # Combine flag's own rotation with position rotation
        final_flag_rotation = flag_rotation + rotation

        if flag_format == "png" and content_img:
            from django.conf import settings as django_settings
            import os

            if birth_flag_path:
                flag_img_path = os.path.join(
                    django_settings.BASE_DIR,
                    "apps",
                    "charts",
                    "static",
                    birth_flag_path,
                )
                if os.path.exists(flag_img_path):
                    with Image(filename=flag_img_path) as flag_img:
                        # Resize flag to desired size
                        flag_img.resize(
                            flag_size, int(flag_size * flag_img.height / flag_img.width)
                        )
                        # Apply rotation BEFORE positioning (ImageMagick recenters after rotate)
                        if final_flag_rotation != 0:
                            flag_img.rotate(final_flag_rotation)
                        # Calculate position AFTER rotation (dimensions may have changed)
                        pos_x = int(base_x + flag_offset_x - flag_img.width // 2)
                        pos_y = int(base_y + flag_offset_y - flag_img.height // 2)
                        content_img.composite(flag_img, pos_x, pos_y)

            if death_flag_path:
                flag_img_path = os.path.join(
                    django_settings.BASE_DIR,
                    "apps",
                    "charts",
                    "static",
                    death_flag_path,
                )
                if os.path.exists(flag_img_path):
                    with Image(filename=flag_img_path) as flag_img:
                        flag_img.resize(
                            flag_size, int(flag_size * flag_img.height / flag_img.width)
                        )
                        if final_flag_rotation != 0:
                            flag_img.rotate(final_flag_rotation)
                        pos_x = int(base_x + flag_offset_x - flag_img.width // 2)
                        pos_y = int(base_y + flag_offset_y + 50 - flag_img.height // 2)
                        content_img.composite(flag_img, pos_x, pos_y)
        else:
            # Original emoji/text rendering
            if birth_flag:
                draw.push()
                draw.font = flag_font
                draw.font_size = (
                    flag_font_size if flag_font_size is not None else place_font_size
                )
                text_width = get_text_width_px(draw, content_img, birth_flag)
                draw.translate(base_x + flag_offset_x, base_y + flag_offset_y)
                draw.rotate(final_flag_rotation)
                draw.translate(-text_width // 2, 0)
                draw.text(0, 0, birth_flag)
                draw.pop()

            if death_flag:
                draw.push()
                draw.font = flag_font
                draw.font_size = (
                    flag_font_size if flag_font_size is not None else place_font_size
                )
                text_width = get_text_width_px(draw, content_img, death_flag)
                draw.translate(base_x + flag_offset_x, base_y + flag_offset_y + 50)
                draw.rotate(final_flag_rotation)
                draw.translate(-text_width // 2, 0)
                draw.text(0, 0, death_flag)
                draw.pop()


def print_individual_simple(
    draw,
    content_img,
    individual,
    settings,
    # Simplified parameters for basic use
    x,
    y,
    rotation=0,
    font_size=72,
    text=None,
):
    """
    Simple version - print a single text at a position with rotation.

    Args:
        draw: Wand Drawing object
        content_img: Wand Image object
        individual: PersonData object (or None if using text param)
        settings: Validated settings dictionary
        x: X position
        y: Y position
        rotation: Rotation in degrees
        font_size: Font size
        text: Optional text to print (if None, uses individual's full_name)
    """
    if text is None:
        text = individual.full_name if individual else ""

    if not text:
        return

    draw.push()
    draw.font = settings.get("font_family", "Arial")
    draw.font_size = font_size
    draw.fill_color = settings.get("primary_font_color", Color("black"))

    text_width = get_text_width_px(draw, content_img, text)

    draw.translate(x, y)
    draw.rotate(rotation)
    draw.translate(-text_width // 2, 0)
    draw.text(0, 0, text)
    draw.pop()
