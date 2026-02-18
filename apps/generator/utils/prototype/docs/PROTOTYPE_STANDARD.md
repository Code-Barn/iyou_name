# Prototype Implementation Standards

## Overview

This document defines the standardized approach for implementing family tree chart generators using the modular `print_individual()` function.

## Position Naming Convention

Each generation uses uniquely named positions that cannot be reused across generations:

| Generation | Positions | Description |
|------------|-----------|-------------|
| 1gen | Position 0 | Primary individual (100% output, becomes overlay) |
| 2gen | Position 1, 2 | Parents (father/mother at 0°/180°) |
| 3gen | Position A, B, C, D | Grandparents (at 0°, 90°, 180°, 270°) |
| Ngen | 2^(N-1) positions | All ancestors at rotation intervals |

**Important**: Positions are generation-specific. Position 1 in 2gen has no relationship to Position 1 in 3gen.

## Name Printing Modes

The `print_individual()` function supports three name printing modes:

### Mode 1: Gravity Center (1gen only)
```python
use_gravity_center=True  # Uses image center (975, 975)
use_display_text=True    # Multiline with \n
```
Best for: 1gen - single individual at center

### Mode 2: Multiline at Base Position
```python
use_display_text=True   # Uses display_text with \n for multiline
use_gravity_center=False
first_name_base_x=975   # Base position
first_name_base_y=1500
```
Best for: When you want multiline names at specific positions

### Mode 3: Single-Line Full Name (Recommended for 3gen+)
```python
full_name=individual.full_name  # Single line, full name
use_display_text=False
use_gravity_center=False
first_name_base_x=975   # Base position (applies to full_name too)
first_name_base_y=1750
```
Best for: 3gen+ - simple single-line names that rotate around center

## Compositing Order

Lower generation ON TOP of higher generation:
- 1gen draws Position 0 → full output
- 2gen draws Positions 1,2 → composites 1gen ON TOP at reduced scale
- 3gen draws Positions A-D → composites 2gen (with 1gen inside) ON TOP at smaller scale

## Standard File Structure

Each generator follows this pattern:

```python
"""
Prototype N-generation chart generator using modular individual printer.
"""

import logging
import os

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.parser.models import PersonData
from apps.generator.utils.prototype.individual_printer import print_individual
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


class GenerationNConstants:
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975
    
    # Position 1 (Base position - use for ALL positions, rotation handles placement)
    POSITION_1_FIRST_NAME_BASE_X = 975
    POSITION_1_FIRST_NAME_BASE_Y = 1725
    POSITION_1_LAST_NAME_BASE_X = 1725
    POSITION_1_LAST_NAME_BASE_Y = 975
    
    FONT_SIZE = 48
    DATE_FONT_SIZE = 36
    PLACE_FONT_SIZE = 20
    
    OVERLAY_SCALE = 0.50
    COMPOSITE_X = 300
    COMPOSITE_Y = 570
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72


GENERATION_N_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    # Add settings with GEN_POSITION_* prefix for each position
}


def generate_prototype_ngen_preview(
    primary_individual, family_data=None, template="preview", user_settings=None
):
    """Generate N-gen chart using modular printer."""
    user_settings = user_settings or {}
    validated_settings = get_validated_settings(
        user_settings, GENERATION_N_SETTINGS_SCHEMA, "ngen"
    )
    
    # Load template, create drawing, render each position
    # Use rotation parameter to position each individual
    
    return create_preview_buffer(content_img)


def test_prototype_ngen():
    """Test the prototype generator."""
    # Create test individuals
    # Call generator
    return result
```

## Core Positioning Principles

### 1. Single Base Position for All

Define ONE set of base positions, then use `rotation` parameter to place individuals:

```python
# All positions use these base coordinates
first_name_base_x = GenerationNConstants.POSITION_1_FIRST_NAME_BASE_X
first_name_base_y = GenerationNConstants.POSITION_1_FIRST_NAME_BASE_Y

# Position 1: rotation=0
# Position 2: rotation=180
# Position A (3gen): rotation=0
# Position B (3gen): rotation=90
# etc.
print_individual(
    individual=person,
    rotation=rotation,  # Only this differs!
    first_name_base_x=first_name_base_x,
    first_name_base_y=first_name_base_y,
    # ... other params same
)
```

### 2. Birth/Death Info Positioning

Follows exact same pattern as name positioning:

```python
# Birth date: same position as first name, offset to avoid overlap
birth_date_base_x=POSITION_1_FIRST_NAME_BASE_X,
birth_date_base_y=POSITION_1_FIRST_NAME_BASE_Y,
birth_date_offset_y=-150,  # Move away from name

# Death date: same position as last name, offset to avoid overlap
death_date_base_x=POSITION_1_LAST_NAME_BASE_X,
death_date_base_base_y=POSITION_1_LAST_NAME_BASE_Y,
death_date_offset_x=-150,  # Move away from name

# Birth/Death places: similar pattern
```

### 3. Rotation Transformation

The `print_individual()` function handles rotation automatically. Apply 180° rotation for Position 2, 90° for Position B, etc.

## Settings Schema Pattern

Use prefix for each position:

```python
GENERATION_2_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    # Shared settings
    "parent_font_size": (int, 48),
    
    # Position 1 (Father) - use "2GEN_POSITION_1_*" prefix
    "2GEN_POSITION_1_translate_x": (int, 0),
    "2GEN_POSITION_1_translate_y": (int, 0),
    
    # Position 2 (Mother) - use "2GEN_POSITION_2_*" prefix  
    "2GEN_POSITION_2_translate_x": (int, 0),
    "2GEN_POSITION_2_translate_y": (int, 0),
}

# For 3gen:
# "3GEN_POSITION_A_*", "3GEN_POSITION_B_*", etc.
```

## Buffer Architecture

```
Buffer[1gen] = 1gen_output
Buffer[2gen] = 2gen_output + Buffer[1gen] composited
Buffer[3gen] = 3gen_output + Buffer[2gen] composited
```

When user clicks "Apply Settings" at any level:
- Update that generation's buffer
- All buffers above need refresh

## Testing Pattern

```python
def test_prototype_ngen():
    # Create primary individual
    person = PersonData(
        id="I1",
        full_name="Test Person",
        given_name="Test",
        surname="Person",
        birth_date="1970-05-15",
        birth_place="Test City",
        death_date="2020-01-01",
        death_place="Test Place",
    )
    
    # Create family data as needed
    
    result = generate_prototype_ngen_preview(person, family_data, "preview")
    
    # Save to file
    with open('prototype_ngen_output.png', 'wb') as f:
        f.write(result.getvalue())
    
    return result
```

## Key Principles

1. **DRY**: Define base positions once, use rotation for placement
2. **Consistent**: Same positioning pattern for names, dates, places
3. **Scalable**: Loop-based generation for any number of positions
4. **Documented**: Each position has clear naming (1,2 or A,B,C,D)
5. **Testable**: Each generator has test function that outputs PNG

## 3gen Planning

3gen adds 4 positions (A, B, C, D) at 90° intervals:
- Position A: rotation=0 (same as Position 1 in 2gen)
- Position B: rotation=90
- Position C: rotation=180 (same as Position 2 in 2gen)
- Position D: rotation=270

This creates the grandparent layer with:
- Paternal grandfather (A)
- Paternal grandmother (B)
- Maternal grandmother (C)
- Maternal grandfather (D)

All four use identical positioning logic, just with different rotation values.
