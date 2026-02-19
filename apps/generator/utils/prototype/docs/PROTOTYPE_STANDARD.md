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
| 4gen | A1, A2, B1, B2, C1, C2, D1, D2 | Great-grandparents (8 positions) |
| 5gen | A11-A22, B11-B22, C11-C22, D11-D22 | Great-great-grandparents (16 positions) |
| Ngen | 2^(N-1) positions | All ancestors at rotation intervals |

**Important**: Positions are generation-specific. Position 1 in 2gen has no relationship to Position 1 in 3gen.

## Subclade System (4gen+)

For 4gen and beyond, positions are organized into **subclades**:

- **Subclade A**: Paternal grandfather's line (rotation=0, bottom)
- **Subclade B**: Paternal grandmother's line (rotation=270, right side)
- **Subclade C**: Maternal grandfather's line (rotation=180, top)
- **Subclade D**: Maternal grandmother's line (rotation=90, left side)

**Key Principle**: Define A subclade positions once, then apply rotation for B/C/D subclades.

### 4gen Rotation Values (Counterclockwise from bottom)
- A1, A2: rotation=0 (bottom)
- B1, B2: rotation=270 (right side)
- C1, C2: rotation=180 (top)
- D1, D2: rotation=90 (left side)

### 5gen Rotation Values (Counterclockwise from bottom)
- A11-A22: rotation=0 (bottom)
- B11-B22: rotation=270 (right side)
- C11-C22: rotation=180 (top)
- D11-D22: rotation=90 (left side)

All members within a subclade share the same rotation value.

## Name Printing Modes

The `print_individual()` function supports three name printing modes:

### Mode 1: Gravity Center (1gen only)
```python
use_gravity_center=True  # Uses image center (975, 975)
use_display_text=True    # Multiline with \n
```
Best for: 1gen - single individual at center

### Mode 2: Multiline at Base Position (Recommended for 4gen+)
```python
use_display_text=True   # Uses display_text with \n for multiline
use_gravity_center=False
first_name_base_x=330   # Base position
first_name_base_y=1835
multiline_line_spacing=1.8  # Line spacing multiplier
multiline_alignment="center"  # Center align multiline text
```
Best for: 4gen+ - when space is tight, multiline names with first/middle/last on separate lines

### Mode 3: Single-Line Full Name
```python
full_name=individual.full_name  # Single line, full name
use_display_text=False
use_gravity_center=False
first_name_base_x=975   # Base position (applies to full_name too)
first_name_base_y=1750
```
Best for: 3gen - simple single-line names that rotate around center

## Paired Dates and Places

For 4gen and 5gen, dates and places should print as pairs centered around a point:

```python
birth_date_paired_offset_x=-100,  # Birth goes left of center
death_date_paired_offset_x=100,   # Death goes right of center
paired_dates_base_y=1785,         # Y position for date pair center
paired_places_base_y=1919,         # Y position for place pair center
birth_place_paired_offset_x=-100,
death_place_paired_offset_x=100,
```

## Compositing Order

Lower generation ON TOP of higher generation:
- 1gen draws Position 0 → full output
- 2gen draws Positions 1,2 → composites 1gen ON TOP at reduced scale
- 3gen draws Positions A-D → composites 2gen (with 1gen inside) ON TOP at smaller scale
- 4gen draws A1-D2 → composites 3gen ON TOP at smaller scale
- 5gen draws A11-D22 → composites 4gen ON TOP at smaller scale

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
from apps.generator.utils.prototype.prototype_image_ngen_minus_1 import generate_prototype_ngen_minus_1_preview
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
    
    # A subclade positions (base for all subclades)
    POSITION_A1_FIRST_NAME_BASE_X = 330
    POSITION_A1_FIRST_NAME_BASE_Y = 1835
    # ... define all A positions
    
    FONT_SIZE = 14
    DATE_FONT_SIZE = 10
    PLACE_FONT_SIZE = 8
    
    OVERLAY_SCALE = 0.7779
    COMPOSITE_X = 300
    COMPOSITE_Y = 570
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72


GENERATION_N_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    # Add settings as needed
}


def generate_prototype_ngen_preview(
    primary_individual, family_data=None, template="preview", user_settings=None
):
    """Generate N-gen chart using modular printer."""
    user_settings = user_settings or {}
    validated_settings = get_validated_settings(
        user_settings, GENERATION_N_SETTINGS_SCHEMA, "ngen"
    )
    
    # Load template, create drawing
    # Build great_(great_)grandparents list with positions
    # Use rotation: A=0, B=270, C=180, D=90
    # Call print_individual for each
    
    return create_preview_buffer(content_img)


def test_prototype_ngen():
    """Test the prototype generator."""
    # Create test individuals with complete family tree
    # Call generator
    return result
```

## Core Positioning Principles

### 1. Define A Subclade Once, Rotate for Others

Define A subclade positions, then use rotation to place B/C/D:

```python
# A positions (base)
great_grandparents.append((individual, POSITION_A1_X, POSITION_A1_Y, rotation=0))    # A
great_grandparents.append((individual, POSITION_A1_X, POSITION_A1_Y, rotation=270)) # B
great_grandparents.append((individual, POSITION_A1_X, POSITION_A1_Y, rotation=180)) # C
great_grandparents.append((individual, POSITION_A1_X, POSITION_A1_Y, rotation=90))  # D
```

### 2. Square Chart Rotation (Counterclockwise from Bottom)

For square charts, rotation goes counterclockwise starting from bottom:
- rotation=0: Bottom
- rotation=90: Left side
- rotation=180: Top
- rotation=270: Right side

### 3. All Members of Subclade Share Same Rotation

In 5gen, all 4 positions in subclade A use rotation=0:
```python
# A subclade (all rotation=0)
(A11, ..., 0),  # father's father's father
(A12, ..., 0),  # father's father's mother
(A21, ..., 0),  # father's mother's father
(A22, ..., 0),  # father's mother's mother
```

## Buffer Architecture

```
Buffer[1gen] = 1gen_output
Buffer[2gen] = 2gen_output + Buffer[1gen] composited
Buffer[3gen] = 3gen_output + Buffer[2gen] composited
Buffer[4gen] = 4gen_output + Buffer[3gen] composited
Buffer[5gen] = 5gen_output + Buffer[4gen] composited
```

When user clicks "Apply Settings" at any level:
- Update that generation's buffer
- All buffers above need refresh

## Testing Pattern

```python
def test_prototype_ngen():
    # Create primary individual with all family data
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
    
    # Create complete family tree with birth_date, birth_place, death_date, death_place
    
    result = generate_prototype_ngen_preview(person, family_data, "preview")
    
    # Save to file
    with open('prototype_ngen_output.png', 'wb') as f:
        f.write(result.getvalue())
    
    return result
```

**Important**: Test data must include birth_date, birth_place, death_date, death_place for all individuals to see date/place pairs.

## Key Principles

1. **DRY**: Define A subclade positions once, use rotation for B/C/D
2. **Consistent**: Same positioning pattern for names, dates, places
3. **Scalable**: Loop-based generation for any number of positions
4. **Documented**: Each position has clear naming (A11, B11, etc.)
5. **Testable**: Each generator has test function that outputs PNG
6. **Counterclockwise**: Rotation goes 0→270→180→90 (bottom→right→top→left)

## Generation Reference

### 3gen
- 4 positions: A, B, C, D
- Rotations: 0, 90, 180, 270
- Use single-line names (use_display_text=False)

### 4gen
- 8 positions: A1, A2, B1, B2, C1, C2, D1, D2
- Rotations: A=0, B=270, C=180, D=90
- Use single-line or multiline names

### 5gen
- 16 positions: A11-A22, B11-B22, C11-C22, D11-D22
- Rotations: A=0, B=270, C=180, D=90
- All 4 positions in each subclade share same rotation
- Use multiline names (use_display_text=True) for space efficiency
