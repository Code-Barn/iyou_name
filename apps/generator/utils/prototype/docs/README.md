# Individual Printer Prototype Documentation

## Overview

This prototype implements a modular approach to family tree chart generation, providing a standardized way to print individuals at any position with any rotation across all generation charts (1-10+).

## Current Status

### ✅ Working Implementations
- **1gen**: Single individual with gravity center or base position placement
- **2gen**: Two individuals (father/mother) rotated 180° apart with names, dates, places

### 🎯 Current Focus
- 2gen complete with standardized positioning
- Planning for 3gen (4 positions: A, B, C, D)

## Position Naming

| Generation | Positions | Rotation |
|------------|-----------|----------|
| 1gen | Position 0 | N/A |
| 2gen | Position 1, 2 | 0°, 180° |
| 3gen | Position A, B, C, D | 0°, 90°, 180°, 270° |

## Core Concept: Standardized Centering

The key insight from 1gen is the exact centering technique used for all text:

```python
# Pattern: translate → rotate → center → draw
draw.translate(x, y)                    # 1. Move to position
draw.rotate(degrees)                     # 2. Rotate context  
draw.translate(-text_width // 2, 0)      # 3. Center horizontally
draw.text(0, 0, text)                   # 4. Draw at origin
```

This pattern is used for ALL text elements (first name, last name, dates, places).

## Generation Structure

Each generation positions individuals around the image center:

| Generation | People | Rotation Intervals |
|------------|--------|-------------------|
| 1gen | 1 | N/A |
| 2gen | 2 | 0°, 180° |
| 3gen | 4 | 0°, 90°, 180°, 270° |
| 4gen | 8 | 0°, 45°, 90°, ... |
| Ngen | 2^(N-1) | 360°/2^(N-1) intervals |

## The `print_individual()` Function

### Key Parameters for Name Positioning

```python
def print_individual(
    draw,
    content_img,
    individual,
    settings,
    # Image center for rotation
    center_x=975,
    center_y=975,
    rotation=0,  # 0, 90, 180, 270
    
    name_font_size=72,
    date_font_size=48,
    place_font_size=24,
    
    # Name positions - base_x/base_y support
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
    
    # Birth/death info (original style)
    birth_date_base_x=0,
    birth_date_base_y=None,
    birth_date_offset_x=0,
    birth_date_offset_y=0,
    birth_date_rotation=0,
    # ... similar for birth_place, death_date, death_place
    
    # Options
    use_display_text=True,
    use_gravity_center=False,
):
```

### Important: name_drawn Flag

When using `use_gravity_center=True` or `use_display_text=True`, the full name is drawn as multiline. The middle_name and last_name blocks must be skipped:

```python
name_drawn = False

if use_gravity_center and display_text:
    draw.text(0, 0, display_text)
    name_drawn = True
# ...

if middle_name and not name_drawn:
    # draw middle name...
```

## 2gen Implementation

### Position System

The 2gen chart uses two positions:
- **Position 1 (Father)**: rotation=0
- **Position 2 (Mother)**: rotation=180

### Base Positions (before rotation)

```python
class Generation2Constants:
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975
    
    # First name: centered at bottom, 150px from edge
    POSITION_1_FIRST_NAME_BASE_X = 975
    POSITION_1_FIRST_NAME_BASE_Y = 1725  # 1875 - 150
    
    # Middle name: at (1650, 1650), -45° angle
    POSITION_1_MIDDLE_NAME_BASE_X = 1650
    POSITION_1_MIDDLE_NAME_BASE_Y = 1650
    POSITION_1_MIDDLE_NAME_ROTATION = -45
    
    # Last name: centered on right, 150px from edge
    POSITION_1_LAST_NAME_BASE_X = 1725  # 1875 - 150
    POSITION_1_LAST_NAME_BASE_Y = 975
```

### Rotation Handling

When rotation is applied, base positions are transformed around the image center:

```python
if rotation == 180:
    # Flip both X and Y around center
    final_base_x = 2 * center_x - base_x
    final_base_y = 2 * center_y - base_y
elif rotation == 90:
    # Swap X/Y with flip
    final_base_x = 2 * center_x - base_y
    final_base_y = base_x
# etc.
```

## File Structure

```
apps/generator/utils/prototype/
├── docs/
│   ├── README.md              # This file
│   ├── QUICK_REFERENCE.md    # Quick lookup
│   ├── DEVELOPMENT_LOG.md    # Today's progress
│   └── PROJECT_ANALYSIS.md   # SWOT analysis
├── individual_printer.py      # Core modular printing function
├── prototype_image_1generator.py
├── prototype_image_2generator.py
└── progress_prompts.txt
```

## Key Learnings

1. **Never use `elif` for middle_name/last_name** - must be independent `if` blocks
2. **Always set name_drawn flag** after gravity_center and use_display_text paths  
3. **Base positions + rotation = scalable** - same code works for any generation
4. **Pixels, not points** - all coordinates are in pixels at 300 DPI

## ⚠️ Avoiding Parameter Explosion (3gen+)

As generations increase, hardcoding each position becomes unwieldy. Use **loop-based generation**:

```python
# Define base positions ONCE
BASE_PARAMS = dict(
    center_x=975, center_y=975,
    first_name_base_x=975, first_name_base_y=1725,
    # ... all params same for every position
)

# For each generation, just add to positions list
positions = [
    (father, 0),
    (mother, 180),
    # 3gen: add more (grandparent, 90), etc.
]

for individual, rotation in positions:
    print_individual(
        individual=individual,
        **BASE_PARAMS,
        rotation=rotation,  # Only this differs!
    )
```

This scales to any generation - just add individuals to the list!

## Future: 10gen Scale

At 10gen, we need 512 positions. The approach scales naturally:

1. Calculate position index (0-511)
2. Compute rotation angle: `angle = index * (360 / 512)`
3. Transform base positions by rotation around center
4. Render all individuals identically except for rotation
