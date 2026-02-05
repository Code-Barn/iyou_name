"""
3-generation chart generator using square division with diagonal lines.

This generator creates a square divided by diagonal lines from corner to corner,
with grandparents positioned along the edges (not in corners) and a 2gen overlay
in the center.
"""

import logging
import math
from io import BytesIO

from django.conf import settings as django_settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.name_utils import parse_name_parts
from apps.generator.utils.settings_helper import extract_generation_settings

logger = logging.getLogger(__name__)


def calculate_edge_position(edge_percent, square_size):
    """
    Calculate position along a square edge based on percentage.

    Args:
        edge_percent: Percentage (10-90) along the edge from starting corner
        square_size: Size of the square

    Returns:
        tuple: (x, y) coordinates
    """
    # Edge position as fraction of square size
    position = (edge_percent / 100.0) * square_size

    return position


def get_grandparent_edge_coordinates(
    edge_position, edge_type, square_size, distance_from_edge=20
):
    """
    Get coordinates for grandparent positioning along square edges.

    Args:
        edge_position: Position percentage along the edge (10-90)
        edge_type: Type of edge ('top', 'right', 'bottom', 'left')
        square_size: Size of the square
        distance_from_edge: Distance from edge towards center

    Returns:
        tuple: (x, y) coordinates
    """
    half_size = square_size / 2
    position = calculate_edge_position(edge_position, square_size)

    if edge_type == "top":
        # Top edge: left to right
        x = position
        y = distance_from_edge

    elif edge_type == "right":
        # Right edge: top to bottom
        x = square_size - distance_from_edge
        y = position

    elif edge_type == "bottom":
        # Bottom edge: right to left (reversed)
        x = square_size - position
        y = square_size - distance_from_edge

    elif edge_type == "left":
        # Left edge: bottom to top (reversed)
        x = distance_from_edge
        y = square_size - position

    else:
        raise ValueError(f"Invalid edge_type: {edge_type}")

    return (int(x), int(y))


def generate_3gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
    """
    Generate a 3-generation family tree chart with square division.

    Layout:
    - Square divided by diagonal lines from corner to corner
    - Grandparents positioned along the edges of the square
    - 2gen chart (primary + parents) overlaid in center

    Args:
        primary_individual: PersonData object for primary individual
        family_data: Dictionary containing all family data
        template: Template type ('preview' or 'final')
        user_settings: Dictionary of user settings

    Returns:
        BytesIO buffer containing generated image
    """
    user_settings = user_settings or {}

    # Extract 3gen-specific settings
    settings = extract_generation_settings(user_settings, "3gen")

    # Image dimensions (square)
    square_size = 800
    image_size = (square_size, square_size)

    # Create blank white image
    image = Image(width=image_size[0], height=image_size[1], background=Color("white"))
    drawing = Drawing()

    print(
        f"DEBUG 3gen: Generating for {primary_individual.full_name if primary_individual else 'None'}"
    )
    print(f"DEBUG 3gen: Square size: {square_size}x{square_size}")
    print(
        f"DEBUG 3gen: Square divided into 4 triangular sections (conceptual, no lines drawn)"
    )

    # Get family relationships
    father = family_data.get(primary_individual.father_id)
    mother = family_data.get(primary_individual.mother_id)

    paternal_grandfather = family_data.get(father.father_id) if father else None
    paternal_grandmother = family_data.get(father.mother_id) if father else None
    maternal_grandfather = family_data.get(mother.father_id) if mother else None
    maternal_grandmother = family_data.get(mother.mother_id) if mother else None

    print(
        f"DEBUG 3gen: Found {len([g for g in [paternal_grandfather, paternal_grandmother, maternal_grandfather, maternal_grandmother] if g])} grandparents"
    )

    # Grandparent positioning settings
    font_family = get_setting(user_settings, "font_family", "Arial")
    grandparent_name_size = int(
        get_setting(user_settings, "grandparent_name_font_size", 40)
    )
    grandparent_date_size = int(
        get_setting(user_settings, "grandparent_date_info_font_size", 28)
    )
    grandparent_place_size = int(
        get_setting(user_settings, "grandparent_place_info_font_size", 20)
    )
    edge_distance = int(get_setting(user_settings, "grandparent_edge_distance", 20))
    date_distance = int(get_setting(user_settings, "grandparent_date_distance", 15))
    place_distance = int(get_setting(user_settings, "grandparent_place_distance", 10))

    # Position grandparents along edges
    if paternal_grandfather:
        # Top edge (left portion)
        edge_pos = int(
            get_setting(user_settings, "paternal_grandfather_edge_position", 25)
        )
        x, y = get_grandparent_edge_coordinates(
            edge_pos, "top", square_size, edge_distance
        )
        color = Color(
            get_setting(user_settings, "paternal_grandfather_font_color", "#000000")
        )

        drawing.font = font_family
        drawing.font_size = grandparent_name_size
        drawing.fill_color = color
        drawing.text(int(x), int(y), paternal_grandfather.full_name)

        # Add birth date below name
        if paternal_grandfather.birth_date:
            drawing.font_size = grandparent_date_size
            drawing.text(
                int(x), int(y + date_distance), paternal_grandfather.birth_date
            )

        # Add birth place below date
        if paternal_grandfather.birth_place:
            drawing.font_size = grandparent_place_size
            drawing.text(
                int(x),
                int(y + date_distance + place_distance),
                paternal_grandfather.birth_place,
            )

    if maternal_grandfather:
        # Right edge (top portion)
        edge_pos = int(
            get_setting(user_settings, "maternal_grandfather_edge_position", 25)
        )
        x, y = get_grandparent_edge_coordinates(
            edge_pos, "right", square_size, edge_distance
        )
        color = Color(
            get_setting(user_settings, "maternal_grandfather_font_color", "#000000")
        )

        drawing.font = font_family
        drawing.font_size = grandparent_name_size
        drawing.fill_color = color
        drawing.text(int(x), int(y), maternal_grandfather.full_name)

        # Add birth date
        if maternal_grandfather.birth_date:
            drawing.font_size = grandparent_date_size
            drawing.text(
                int(x), int(y + date_distance), maternal_grandfather.birth_date
            )

        # Add birth place
        if maternal_grandfather.birth_place:
            drawing.font_size = grandparent_place_size
            drawing.text(
                int(x),
                int(y + date_distance + place_distance),
                maternal_grandfather.birth_place,
            )

    if paternal_grandmother:
        # Bottom edge (right portion)
        edge_pos = int(
            get_setting(user_settings, "paternal_grandmother_edge_position", 75)
        )
        x, y = get_grandparent_edge_coordinates(
            edge_pos, "bottom", square_size, edge_distance
        )
        color = Color(
            get_setting(user_settings, "paternal_grandmother_font_color", "#000000")
        )

        drawing.font = font_family
        drawing.font_size = grandparent_name_size
        drawing.fill_color = color
        drawing.text(int(x), int(y), paternal_grandmother.full_name)

        # Add birth date
        if paternal_grandmother.birth_date:
            drawing.font_size = grandparent_date_size
            drawing.text(
                int(x), int(y + date_distance), paternal_grandmother.birth_date
            )

        # Add birth place
        if paternal_grandmother.birth_place:
            drawing.font_size = grandparent_place_size
            drawing.text(
                int(x),
                int(y + date_distance + place_distance),
                paternal_grandmother.birth_place,
            )

    if maternal_grandmother:
        # Left edge (bottom portion)
        edge_pos = int(
            get_setting(user_settings, "maternal_grandmother_edge_position", 75)
        )
        x, y = get_grandparent_edge_coordinates(
            edge_pos, "left", square_size, edge_distance
        )
        color = Color(
            get_setting(user_settings, "maternal_grandmother_font_color", "#000000")
        )

        drawing.font = font_family
        drawing.font_size = grandparent_name_size
        drawing.fill_color = color
        drawing.text(int(x), int(y), maternal_grandmother.full_name)

        # Add birth date
        if maternal_grandmother.birth_date:
            drawing.font_size = grandparent_date_size
            drawing.text(
                int(x), int(y + date_distance), maternal_grandmother.birth_date
            )

        # Add birth place
        if maternal_grandmother.birth_place:
            drawing.font_size = grandparent_place_size
            drawing.text(
                int(x),
                int(y + date_distance + place_distance),
                maternal_grandmother.birth_place,
            )

    # Draw the square border
    drawing.stroke_color = Color("black")
    drawing.stroke_width = 1
    drawing.rectangle(left=0, top=0, width=square_size, height=square_size)

    # Apply drawing to image
    drawing(image)

    # Create 2gen overlay for center
    overlay_scale = int(get_setting(user_settings, "composite_2gen_scale", 35))
    overlay_x = int(get_setting(user_settings, "composite_overlay_x", 400))
    overlay_y = int(get_setting(user_settings, "composite_overlay_y", 400))

    print(
        f"DEBUG 3gen: Creating 2gen overlay at scale {overlay_scale}% position ({overlay_x}, {overlay_y})"
    )

    # Generate 2gen chart for overlay
    from apps.generator.utils.image_2generator import generate_2gen_preview

    overlay_buffer = generate_2gen_preview(
        primary_individual, family_data, "preview", user_settings
    )

    # Create overlay image from buffer and resize
    overlay_image = Image(blob=overlay_buffer.getvalue())
    overlay_size = int(square_size * overlay_scale / 100)
    overlay_image.resize(overlay_size, overlay_size)

    # Composite overlay onto main image
    overlay_x_pos = overlay_x - (overlay_size // 2)
    overlay_y_pos = overlay_y - (overlay_size // 2)

    image.composite(overlay_image, left=overlay_x_pos, top=overlay_y_pos)

    print(
        f"DEBUG 3gen: Composite positioned at ({overlay_x_pos}, {overlay_y_pos}) with size {overlay_size}"
    )

    # Convert to PNG buffer
    buffer = BytesIO()
    image.format = "png"
    image.save(buffer)
    buffer.seek(0)

    print(f"DEBUG 3gen: Generated image size: {len(buffer.getvalue())} bytes")

    return buffer


def extract_generation_settings(user_settings, generation_prefix):
    """
    Extract generation-specific settings from user settings.

    Args:
        user_settings: Dictionary of all user settings
        generation_prefix: Type of generation ('1gen', '2gen', '3gen', etc.)

    Returns:
        Dictionary of filtered settings
    """
    if not user_settings:
        return {}

    # Filter settings relevant to this generation type
    generation_settings = {}

    # Common settings
    common_keys = ["font_family", "default_stroke_width"]
    for key in common_keys:
        if key in user_settings:
            generation_settings[key] = user_settings[key]

    # 3gen-specific settings
    if generation_prefix == "3gen":
        gen3_keys = [
            "paternal_grandfather_font_color",
            "paternal_grandmother_font_color",
            "maternal_grandfather_font_color",
            "maternal_grandmother_font_color",
            "grandparent_birth_color",
            "grandparent_death_color",
            "grandparent_birth_place_color",
            "grandparent_death_place_color",
            "grandparent_name_font_size",
            "grandparent_date_info_font_size",
            "grandparent_place_info_font_size",
            "paternal_grandfather_edge_position",
            "paternal_grandmother_edge_position",
            "maternal_grandfather_edge_position",
            "maternal_grandmother_edge_position",
            "grandparent_edge_distance",
            "grandparent_date_distance",
            "grandparent_place_distance",
            "composite_2gen_scale",
            "composite_overlay_x",
            "composite_overlay_y",
            "diagonal_line_color",
            "diagonal_line_width",
        ]

        for key in gen3_keys:
            if key in user_settings:
                generation_settings[key] = user_settings[key]

    return generation_settings


# Helper function for settings access
def get_setting(user_settings, key, default):
    """Helper to get user setting with default."""
    return user_settings.get(key, default)
