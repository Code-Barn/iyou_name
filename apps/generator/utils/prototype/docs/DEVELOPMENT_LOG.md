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
