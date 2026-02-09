"""
Scalable high-generation chart generator (4-10 generations).

This generator uses the sunbeam positioning system to handle any number
of generations from 4 to 10, with automatic mathematical positioning
for all individuals.
"""

import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.name_utils import parse_name_parts
from apps.generator.utils.sunbeam_position_calculator import SunbeamPositionCalculator

logger = logging.getLogger(__name__)


def generate_high_gen_preview(
    generation_count,
    primary_individual,
    family_data,
    template="preview",
    user_settings=None,
):
    """
    Generate a high-generation family tree chart (4-10 generations).

    This generator can handle any number of generations from 4 to 10,
    automatically calculating positions for all individuals using
    the sunbeam positioning system.

    Args:
        generation_count: Number of generations to generate (4-10)
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type ('{gen}gen' for generation chart)
        user_settings: Dictionary of user settings

    Returns:
        BytesIO buffer containing the generated image
    """
    user_settings = user_settings or {}

    # Validate generation count
    if generation_count < 4 or generation_count > 10:
        raise ValueError(
            f"Generation count {generation_count} not supported (must be 4-10)"
        )

    # Determine canvas size
    canvas_size = 4700 if generation_count >= 8 else 1950

    try:
        # Load appropriate template
        template_path = get_template_path(generation_count)

        # Initialize position calculator
        position_calculator = SunbeamPositionCalculator(canvas_size=canvas_size)

        with Image(filename=template_path, resolution=300) as content_img:
            # Apply settings
            settings = apply_high_gen_settings(user_settings, generation_count)

            # Extract family data by generation
            family_by_generation = extract_family_by_generation(
                family_data, generation_count
            )

            # Draw the chart
            draw_high_gen_chart(
                draw, content_img, family_by_generation, settings, position_calculator
            )

            # Return appropriate format
            buffer = BytesIO()
            format_type = "png" if template == "preview" else "pdf"
            content_img.save(buffer, format=format_type)
            buffer.seek(0)
            return buffer

    except Exception as e:
        logger.error(f"Error generating {generation_count}gen preview: {e}")
        raise


def get_template_path(generation_count):
    """Get appropriate template path for generation count."""
    template_filename = f"{generation_count}GEN_PREVIEW.png"
    template_path = os.path.join(
        settings.BASE_DIR,
        "apps/hud/static/hud/images/preview_image_templates",
        template_filename,
    )

    # If specific template doesn't exist, use base template
    if not os.path.exists(template_path):
        # Use 2gen as base for higher generations
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "2GEN_PREVIEW.png",
        )

    return template_path


def apply_high_gen_settings(user_settings, generation_count):
    """Apply user settings with defaults for high-generation charts."""
    settings = {
        # Primary individual settings
        "primary_background_color": user_settings.get(
            "primary_background_color", "#FFFFFF"
        ),
        "primary_stroke_color": user_settings.get("primary_stroke_color", "#000000"),
        "primary_font_color": user_settings.get("primary_font_color", "#000000"),
        "primary_name_font_size": int(user_settings.get("primary_name_font_size", 84)),
        "primary_name_rotate": int(user_settings.get("primary_name_rotate", -45)),
        "font_family": user_settings.get("font_family", "Arial"),
        "default_stroke_width": float(user_settings.get("default_stroke_width", 0.5)),
    }

    # Generation-specific font sizes
    base_font_size = 84
    for gen in range(1, generation_count + 1):
        # Decrease font size for higher generations
        gen_font_size = max(18, base_font_size - (gen * 8))
        settings[f"gen_{gen}_font_size"] = int(
            user_settings.get(f"gen_{gen}_font_size", gen_font_size)
        )
        settings[f"gen_{gen}_font_color"] = user_settings.get(
            f"gen_{gen}_font_color", "#000000"
        )

    return settings


def extract_family_by_generation(family_data, generation_count):
    """
    Extract family data organized by generation.

    This is a placeholder - you'll need to implement this based on
    your actual family data structure.
    """
    family_by_generation = {}

    # Generation 0: Primary individual
    family_by_generation[0] = [family_data.primary_individual]

    # Generation 1: Parents
    parents = []
    if hasattr(family_data, "father") and family_data.father:
        parents.append(family_data.father)
    if hasattr(family_data, "mother") and family_data.mother:
        parents.append(family_data.mother)
    if parents:
        family_by_generation[1] = parents

    # Generation 2: Grandparents
    grandparents = get_grandparents(family_data)
    if grandparents:
        family_by_generation[2] = grandparents

    # Higher generations - placeholder implementation
    # You'll need to implement actual family tree traversal
    for gen in range(3, generation_count + 1):
        # For now, create placeholder individuals
        individual_count = 2**gen  # Each generation doubles
        placeholder_individuals = []

        for i in range(individual_count):
            # Create placeholder individual with your data structure
            placeholder_individual = create_placeholder_individual(
                f"Gen{gen}Person{i + 1}"
            )
            placeholder_individuals.append(placeholder_individual)

        if placeholder_individuals:
            family_by_generation[gen] = placeholder_individuals

    return family_by_generation


def draw_high_gen_chart(
    draw, content_img, family_by_generation, settings, position_calculator
):
    """Draw the complete high-generation chart."""
    with Drawing() as draw:
        draw.push()

        # Set base drawing properties
        draw.font = settings["font_family"]
        draw.stroke_width = settings["default_stroke_width"]

        # Draw each generation
        for generation, individuals in family_by_generation.items():
            if individuals and generation <= len(family_by_generation) - 1:
                draw_generation(
                    draw, individuals, generation, settings, position_calculator
                )

        draw.pop()

    # Apply drawing to image
    draw.draw(content_img)


def draw_generation(draw, individuals, generation, settings, position_calculator):
    """Draw all individuals in a specific generation."""
    # Get generation-specific settings
    font_size = settings.get(f"gen_{generation}_font_size", 24)
    font_color = settings.get(f"gen_{generation}_font_color", "#000000")

    draw.font_size = font_size
    draw.fill_color = Color(font_color)

    # Calculate positions for this generation
    positions = position_calculator.calculate_generation_positions(
        generation, len(individuals)
    )

    # Draw each individual
    for i, (x, y, rotation, zone_id) in enumerate(positions):
        if i < len(individuals):
            individual = individuals[i]
            draw_individual_at_position(draw, individual, x, y, rotation, font_size)


def draw_individual_at_position(draw, individual, x, y, rotation, font_size):
    """Draw a single individual at the specified position."""
    # Parse name using improved logic
    first_name, middle_name, last_name = parse_name_parts(individual.full_name)

    # Build display text
    name_parts_to_display = [
        part for part in [first_name, middle_name, last_name] if part.strip()
    ]
    display_text = "\n".join(name_parts_to_display)

    # Draw individual
    draw.push()
    draw.translate(x, y)
    draw.rotate(rotation)

    # Draw multiline name
    lines = display_text.split("\n")
    line_height = font_size * 1.2
    start_y = -(len(lines) - 1) * line_height / 2

    for j, line in enumerate(lines):
        line_y = start_y + (j * line_height)
        draw.push()
        draw.translate(0, line_y)
        draw.text(0, 0, line)
        draw.pop()

    draw.pop()


def get_grandparents(family_data):
    """Extract grandparents from family data."""
    grandparents = []

    # Paternal grandparents
    if (
        hasattr(family_data, "paternal_grandfather")
        and family_data.paternal_grandfather
    ):
        grandparents.append(family_data.paternal_grandfather)
    if (
        hasattr(family_data, "paternal_grandmother")
        and family_data.paternal_grandmother
    ):
        grandparents.append(family_data.paternal_grandmother)

    # Maternal grandparents
    if (
        hasattr(family_data, "maternal_grandfather")
        and family_data.maternal_grandfather
    ):
        grandparents.append(family_data.maternal_grandfather)
    if (
        hasattr(family_data, "maternal_grandmother")
        and family_data.maternal_grandmother
    ):
        grandparents.append(family_data.maternal_grandmother)

    return grandparents


def create_placeholder_individual(name):
    """Create a placeholder individual for testing."""

    class PlaceholderIndividual:
        def __init__(self, name):
            self.full_name = name
            self.id = f"placeholder_{name}"

    return PlaceholderIndividual(name)


# Factory functions for specific generations
def generate_4gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """Generate 4-generation chart."""
    return generate_high_gen_preview(
        4, primary_individual, family_data, template, user_settings
    )


def generate_5gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """Generate 5-generation chart."""
    return generate_high_gen_preview(
        5, primary_individual, family_data, template, user_settings
    )


def generate_6gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """Generate 6-generation chart."""
    return generate_high_gen_preview(
        6, primary_individual, family_data, template, user_settings
    )


def generate_7gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """Generate 7-generation chart."""
    return generate_high_gen_preview(
        7, primary_individual, family_data, template, user_settings
    )


def generate_8gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """Generate 8-generation chart (uses 4700px canvas)."""
    return generate_high_gen_preview(
        8, primary_individual, family_data, template, user_settings
    )


def generate_9gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """Generate 9-generation chart (uses 4700px canvas)."""
    return generate_high_gen_preview(
        9, primary_individual, family_data, template, user_settings
    )


def generate_10gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """Generate 10-generation chart (uses 4700px canvas, 512 individuals)."""
    return generate_high_gen_preview(
        10, primary_individual, family_data, template, user_settings
    )
