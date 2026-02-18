# Individual Printer Prototype - Development Log

## Session Date: 2026-02-16

## Major Accomplishments

### 1. Fixed Duplicate Name Bug
**Problem**: Names were being printed twice in 1gen and middle names weren't showing in 2gen.

**Solution**: Added `name_drawn` flag tracking. When using `use_gravity_center=True` or `use_display_text=True`, the full name is already drawn as multiline, so middle_name and last_name blocks must be skipped.

```python
# Track if name has been drawn
name_drawn = False

# Set flag after drawing full name
if use_gravity_center and display_text:
    draw.text(0, 0, display_text)
    name_drawn = True

# Skip individual parts if full name was drawn
if middle_name and not name_drawn:
    # draw middle name...
```

### 2. Standardized Centering Pattern
**Key Insight**: All text centering follows the exact same pattern from 1gen:

```python
# Pattern: translate → rotate → center → draw
draw.translate(x, y)                    # 1. Move to position
draw.rotate(degrees)                   # 2. Rotate context
draw.translate(-text_width // 2, 0)    # 3. Center horizontally
draw.text(0, 0, text)                 # 4. Draw at origin
```

This works for both horizontal (0°) and vertical (-90°) text.

### 3. Base Position System with Rotation

**Concept**: Define positions once, rotate around image center:

```python
# Base positions (father, rotation=0)
POSITION_1_FIRST_NAME_BASE_X = 975    # Center X
POSITION_1_FIRST_NAME_BASE_Y = 1725   # Bottom - 150px

POSITION_1_MIDDLE_NAME_BASE_X = 1650 # Diagonal in
POSITION_1_MIDDLE_NAME_BASE_Y = 1650

POSITION_1_LAST_NAME_BASE_X = 1725   # Right - 150px
POSITION_1_LAST_NAME_BASE_Y = 975    # Center Y
```

**Rotation Math** (applied to base positions):
```python
if rotation == 180:
    final_base_x = 2 * center_x - base_x  # Flip around center
    final_base_y = 2 * center_y - base_y
```

### 4. 2gen Default Positions

| Element | Position 1 (Father) | Position 2 (Mother) |
|---------|---------------------|---------------------|
| First Name | (975, 1725), 0° | Rotated 180° → top |
| Middle Name | (1650, 1650), -45° | Rotated 180° → (300, 300) |
| Last Name | (1725, 975), -90° vertical | Rotated 180° → left side |

## Current Status

### ✅ Working
- 1gen: Full functionality with gravity center
- 2gen: Two positions with rotation, middle names, proper centering

### 📋 To Do
- Add birth/death info to 2gen
- Test 3gen+ implementations
- Add user-adjustable offset settings

## Key Learnings

1. **Never use `elif` for middle_name/last_name** - they must be independent `if` blocks
2. **Always set name_drawn flag** after gravity_center and use_display_text paths
3. **Base positions + rotation = scalable** - same code works for any generation
4. **Pixels, not points** - all coordinates are in pixels at 300 DPI

## Avoiding Parameter Explosion (3gen+)

As generations increase, hardcoding each position becomes unwieldy (7gen = 64 positions!).

### Recommended: Loop-Based Generation

Instead of hardcoding each position, iterate programmatically:

```python
# Define base positions ONCE
BASE_PARAMS = dict(
    center_x=975, center_y=975,
    first_name_base_x=975, first_name_base_y=1725,
    middle_name_base_x=1650, middle_name_base_y=1650,
    last_name_base_x=1725, last_name_base_y=975,
    # ... all other params same for every position
)

# For each generation, calculate positions dynamically
positions = [
    (father, 0),
    (mother, 180),
    # 3gen adds:
    # (grandfather1, 0),
    # (grandfather2, 90),
    # ...
]

for individual, rotation in positions:
    print_individual(
        individual=individual,
        **BASE_PARAMS,
        rotation=rotation,  # Only this differs per position!
    )
```

### Why This Works

- **90% of parameters are IDENTICAL** across all positions
- Only rotation changes per position
- Adding 3gen+ just means adding to the positions list
- No code changes needed to individual_printer

### Future: Mathematical Position Generation

For 10gen (512 positions), calculate automatically:

```python
def get_positions_for_generation(gen_number, family_data):
    num_positions = 2 ** (gen_number - 1)
    angle_step = 360 / num_positions
    
    positions = []
    for i in range(num_positions):
        rotation = i * angle_step
        individual = get_individual_for_position(i, family_data)
        positions.append((individual, rotation))
    return positions
```

---

## Session Date: 2026-02-17

### Major Accomplishments

### 1. Three Name Printing Modes

The `print_individual()` function now supports three modes:

#### Mode 1: Gravity Center (1gen only)
```python
use_gravity_center=True   # Uses image center (975, 975)
use_display_text=True    # Multiline with \n
```
Best for: 1gen - single individual at center

#### Mode 2: Multiline at Base Position
```python
use_display_text=True    # Uses display_text with \n for multiline
use_gravity_center=False
first_name_base_x=975   # Base position
first_name_base_y=1500
```
Best for: When you want multiline names at specific positions

#### Mode 3: Single-Line Full Name (Recommended for 3gen+)
```python
full_name=individual.full_name  # Single line, full name
use_display_text=False
use_gravity_center=False
first_name_base_x=975   # Base position (applies to full_name too)
first_name_base_y=1750
```
Best for: 3gen+ - simple single-line names that rotate around center

### 2. Fixed use_display_text Base Position Bug

**Problem**: `use_display_text=True` was using image center instead of base positions.

**Solution**: Updated `print_individual()` to check for `first_name_base_x/first_name_base_y` and apply rotation transform:

```python
# Determine base position - use base_x/base_y if provided, else use center
if first_name_base_x is not None:
    base_x = first_name_base_base_x
else:
    base_x = center_x

# Apply rotation transformation
if rotation == 180:
    final_base_x = 2 * center_x - base_x
    final_base_y = 2 * center_y - base_y
# ... other rotations
```

### 3. Added full_name Parameter

New parameter to override name parsing for simple single-line printing:

```python
full_name=None,  # Simple single-line full name override

# In function body:
if full_name:
    first_name = full_name
    middle_name = ""
    last_name = ""
    display_text = ""
```

### 4. Refactored 2gen to Standard Pattern

**Before**: Separate hardcoded constants for Position 1 and Position 2

**After**: Single base positions + loop with rotation:

```python
positions = [
    (father, 0, "father_translate_x", "father_translate_y"),
    (mother, 180, "mother_translate_x", "mother_translate_y"),
]

base_params = dict(
    center_x=Generation2Constants.IMAGE_CENTER_X,
    center_y=Generation2Constants.IMAGE_CENTER_Y,
    first_name_base_x=Generation2Constants.POSITION_1_FIRST_NAME_BASE_X,
    # ... all common params
)

for individual, rotation, translate_x_key, translate_y_key in positions:
    print_individual(
        individual=individual,
        rotation=rotation,
        **base_params,
    )
```

### Current Status

### ✅ Working
- 1gen: Gravity center with multiline
- 2gen: Loop-based with rotation, separate name parts (complex case)
- 3gen: Loop-based with rotation, full_name single-line

### 📋 4gen Planning
- 8 positions: A1, A2, B1, B2, C1, C2, D1, D2
- Rotation intervals: 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°
- Uses same pattern as 3gen (full_name single-line)

---

## Generation Naming Convention

| Generation | Positions | Rotation Intervals |
|------------|-----------|-------------------|
| 1gen | Position 0 | N/A |
| 2gen | Position 1, 2 | 0°, 180° |
| 3gen | Position A, B, C, D | 0°, 90°, 180°, 270° |
| 4gen | A1, A2, B1, B2, C1, C2, D1, D2 | 0°, 45°, 90°, ... |
