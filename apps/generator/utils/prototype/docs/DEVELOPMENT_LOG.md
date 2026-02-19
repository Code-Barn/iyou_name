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

## Session Date: 2026-02-18

### Major Accomplishments

### 1. 4gen Implementation

**Key Insight**: Since the chart is square (not circular), simple rotation doesn't work for all positions. The solution is to:
1. Define A1 and A2 base positions (father/mother pair in bottom-left quadrant)
2. Apply 90° rotation to get B1/B2, 180° for C1/C2, 270° for D1/D2

```python
# Define A1/A2 base positions once
POSITION_A1_FIRST_NAME_BASE_X = 560
POSITION_A1_FIRST_NAME_BASE_Y = 1825

POSITION_A2_FIRST_NAME_BASE_X = 1390
POSITION_A2_FIRST_NAME_BASE_Y = 1825

# For each subclade, use A1/A2 base + rotation
great_grandparents = [
    (paternal_grandfather_father, A1_X, A1_Y, 0),      # A1 - rotation 0
    (paternal_grandfather_mother, A2_X, A2_Y, 0),      # A2 - rotation 0
    (paternal_grandmother_father, A1_X, A1_Y, 90),    # B1 - rotation 90
    (paternal_grandmother_mother, A2_X, A2_Y, 90),    # B2 - rotation 90
    # ... etc
]
```

### 2. Fixed Paired Offset Bug for Rotation 0

**Problem**: Birth/death date pairs and birth/death place pairs were printing on top of each other for rotation=0 positions (A1, A2).

**Root Cause**: The rotation 0 case in `print_individual()` was using `offset_x` instead of `effective_offset_x` (which includes paired offset).

**Fix**: Updated all four date/place blocks in individual_printer.py:
```python
# Before (broken for rotation 0):
else:
    offset_x = birth_date_offset_x  # Missing paired offset!

# After (works for all rotations):
else:
    effective_offset_x = birth_date_offset_x + birth_date_paired_offset_x
    offset_x = effective_offset_x
```

### 3. Paired Offsets Pattern

For centering pairs of dates/places around a center point:
```python
# 400px gap between dates (center ± 200)
birth_date_paired_offset_x = -200
death_date_paired_offset_x = 200

# 1050px gap between places (center ± 525)
birth_place_paired_offset_x = -525
death_place_paired_offset_x = 525
```

### Current Status

### ✅ Working
- 1gen: Gravity center with multiline
- 2gen: Loop-based with rotation, separate name parts (complex case)
- 3gen: Loop-based with rotation, full_name single-line
- 4gen: A1/A2 base positions + rotation for B/C/D subclades, paired offsets

### Key Learnings (Updated)

1. **Square canvas requires manual A1/A2 positioning** - rotation alone doesn't fill the space correctly
2. **Define base for father (A1) and mother (A2)** - then rotate to get other subclades
3. **Paired offsets need `effective_offset_x`** - must include both offset and paired_offset
4. **Use paired_offset for centering pairs** - birth on left, death on right, centered

---

## Generation Naming Convention

| Generation | Positions | Rotation Intervals | Notes |
|------------|-----------|-------------------|-------|
| 1gen | Position 0 | N/A | Gravity center |
| 2gen | Position 1, 2 | 0°, 180° | Complex: separate name parts |
| 3gen | A, B, C, D | 0°, 90°, 180°, 270° | Simple: full_name |
| 4gen | A1, A2, B1, B2, C1, C2, D1, D2 | 0°, 45°, 90°, ... | A1/A2 base + rotate |

---

## Session Date: 2026-02-19

### Major Accomplishments

### 1. Fixed Place Name Separation in 4gen

**Problem**: Birth and death places were printing on top of each other in A1 and A2 positions, unlike the dates above them which had proper separation.

**Root Cause**: The place handling code in `individual_printer.py` was missing the `effective_offset_x` calculation that the date handling code was using. Places were using individual base coordinates without the paired offset logic.

**Solution**: Applied the same centering technique to places as used for dates:

1. **Added `effective_offset_x` calculation for places**:
```python
# For birth places
effective_offset_x = birth_place_offset_x + birth_place_paired_offset_x

# For death places  
effective_offset_x = death_place_offset_x + death_place_paired_offset_x
```

2. **Added `paired_places_base_y` logic**:
```python
# For both birth and death places
if paired_places_base_y is not None:
    base_y = paired_places_base_y
else:
    base_y = birth_place_base_y if birth_place_base_y is not None else center_y
```

3. **Updated base positions to exact specifications**:
```python
# A1 position (bottom right to center)
POSITION_A1_BIRTH_PLACE_BASE_X = 518  # was 511
POSITION_A1_BIRTH_PLACE_BASE_Y = 1888  # was 1925

# A2 position (mirrored across x=975)
POSITION_A2_BIRTH_PLACE_BASE_X = 1432  # was 1439
POSITION_A2_BIRTH_PLACE_BASE_Y = 1888  # was 1925
```

4. **Matched date gap length for consistency**:
```python
birth_place_paired_offset_x=-200,  # was -1000, now matches dates
death_place_paired_offset_x=200,   # was 1000, now matches dates
```

### Final Configuration

- **A1 Position**: Centered at `518, 1888` (bottom right to center)
- **A2 Position**: Centered at `1432, 1888` (mirrored across x=975)
- **Gap Length**: 400px total (same as dates)
  - Birth place offset: `-200` (left)
  - Death place offset: `+200` (right)
- **Y Position**: `1888` (37px higher than original `1925`)

### How It Works

1. **Same Base Position**: Both birth and death places use the same Y coordinate (`1888`)
2. **Horizontal Separation**: Birth place is offset left by 200 pixels, death place is offset right by 200 pixels
3. **Centering**: Each place name is centered around its calculated position
4. **Consistent with Dates**: Uses the exact same pattern and gap length as the dates above the names

### Key Learnings

1. **Paired offsets require `effective_offset_x`**: Must combine base offset with paired offset for all rotation cases
2. **Use same base Y for pairs**: Both birth and death places should share the same vertical center
3. **Match date styling exactly**: Same gap length creates visual consistency
4. **Exact positioning matters**: Small pixel adjustments (37px in this case) can make significant visual differences

### Files Modified

1. **`apps/generator/utils/prototype/individual_printer.py`**:
   - Added `effective_offset_x` calculation for birth places
   - Added `effective_offset_x` calculation for death places
   - Added `paired_places_base_y` logic for both birth and death places

2. **`apps/generator/utils/prototype/prototype_image_4generator.py`**:
   - Updated A1 and A2 base positions to exact specifications
   - Changed place offsets from `-1000`/`1000` to `-200`/`200` to match dates

---

## Current Status

### ✅ Working
- 1gen: Gravity center with multiline
- 2gen: Loop-based with rotation, separate name parts (complex case)
- 3gen: Loop-based with rotation, full_name single-line
- 4gen: A1/A2 base positions + rotation for B/C/D subclades, paired offsets for dates AND places

### 📋 Next Steps
- Test with real GEDCOM data to verify all edge cases
- Add user-adjustable settings for fine-tuning positions
- Document the complete positioning system for future reference

---

## Session Date: 2026-02-19 (continued)

### 2. Visual Theme Update: Dark Mode

**Change**: Updated default color scheme to black background with white text for better visibility and modern aesthetic.

**Modified in `prototype_image_1generator.py`**:
```python
GENERATION_1_SETTINGS_SCHEMA = {
    "primary_background_color": (Color, "#000000"),  # Changed from #FFFFFF
    "primary_font_color": (Color, "white"),           # Changed from black
    "primary_stroke_color": (Color, "white"),          # Changed from black
    "primary_birth_color": (Color, "white"),          # Changed from black
    "primary_birth_place_color": (Color, "white"),     # Changed from black
    "primary_death_color": (Color, "white"),          # Changed from black
    "primary_death_place_color": (Color, "white"),     # Changed from black
}
```

---

## Session Date: 2026-02-19 (evening)

### Major Issue Discovered: Generation Position Overflow

**Problem Found**: When testing 5gen and 6gen generators, the position labels (e.g., "A11", "A12", "A21", "A22") were printing in the WRONG locations - specifically appearing in the previous generation's overlay positions (4gen positions) rather than the intended outer perimeter positions.

**Observation from Test Output**:
- In `prototype_5gen_labels.png`: 4 labels (A11, A12, A21, A22) appeared in the 4gen overlay area (inner circle)
- The outer perimeter positions where 5gen names should print were EMPTY

**Root Cause Analysis**:
The 5gen chart is generated by:
1. First generating 4gen as an overlay
2. Then printing 5gen names on top

However, the test showed that when 5gen ancestors were added with only partial subclade data, the names appeared in the 4gen area instead of the outer 5gen area. This suggests either:
1. The position coordinates for 5gen are too close to center (overlapping with 4gen)
2. The template being used doesn't have the proper outer zone for 5gen
3. The compositing order or position calculation has an issue

**Confirmed Working**:
- Position-to-ancestor mapping IS correct - each position is checked individually and skips if no ancestor exists (doesn't shift)
- Missing ancestors leave their designated positions empty rather than filling with wrong names

---

## Session Date: 2026-02-20

### Issues Under Investigation

### 1. Position Ordering Bug (Father/Mother Inversion)

**Problem**: In 5gen and 6gen, the position labels were found to be inverted from the standard convention.

**Expected Convention** (per documentation):
- **1 = Father**
- **2 = Mother**
- Left position (smaller X) = Father (1)
- Right position (larger X) = Mother (2)

**Current Behavior** (WRONG):
- A11 was mapped to `pgf_father_father` (father's father = should be position 2!)
- A12 was mapped to `pgf_father_mother` (father's mother = should be position 1!)

The code was doing the OPPOSITE of the documented standard.

**Fix Required**: Swap father/mother assignments:
- A11 should map to `pgf_father_mother` (father's mother = 2)
- A12 should map to `pgf_father_father` (father's father = 1)
- A21 should map to `pgf_mother_mother` (mother's mother = 2)
- A22 should map to `pgf_mother_father` (mother's father = 1)

This fix needs to be applied to both 5gen and 6gen generators.

### 2. Multiline Centering Fix for Rotation

**Problem**: When using `use_display_text=True` (multiline mode), names in B, C, D subclades (rotated 90°, 180°, 270°) were rendering at slightly different vertical positions than the A subclade.

**Root Cause**: The vertical centering offset (`y_offset`) was being applied AFTER the rotation transform, causing it to be interpreted differently for each rotation angle.

**Solution Applied in `individual_printer.py`**:
```python
# Apply centering offset AFTER rotation - translation is in rotated coordinate space
# In rotated space: for 90°, rotated x points in original -y, rotated y points in original x
if rotation == 180:
    # For 180°, offset goes in rotated y (original -y)
    final_x = final_base_x + offset_x
    final_y = final_base_y + offset_y - centering_offset
elif rotation == 90:
    # For 90°, rotated x points in original -y direction
    final_x = final_base_x + offset_x - centering_offset
    final_y = final_base_y + offset_y
elif rotation == 270:
    # For 270°, need to account for X/Y swap in offset handling
    final_x = final_base_x + offset_x + centering_offset
    final_y = final_base_y + offset_y
else:
    # No rotation - normal vertical centering
    final_x = final_base_x + offset_x
    final_y = final_base_y + offset_y + centering_offset
```

**Verified Working**: After fix, C and D subclades render correctly. B subclade (rotation=270) required additional adjustment due to X/Y axis swap in the rotation logic.

### 3. 6gen Generator Created

**New File**: `prototype_image_6generator.py`

**Structure**:
- 32 positions (8 per subclade × 4 subclades)
- A111-A222: Paternal grandfather's great-great-grandparents
- B111-B222: Paternal grandmother's great-great-grandparents  
- C111-C222: Maternal grandfather's great-great-grandparents
- D111-D222: Maternal grandmother's great-great-grandparents

**Configuration**:
- Font sizes reduced: 11pt names, 8pt dates, 6pt places
- Overlay scale: 81.79% (5gen as overlay)
- Uses 6GEN_PREVIEW.png template

---

## Current Status

### ✅ Working
- 1gen: Gravity center with multiline, BLACK background, WHITE text
- 2gen: Loop-based with rotation, separate name parts
- 3gen: Loop-based with rotation, full_name single-line
- 4gen: A1/A2 base positions + rotation for B/C/D subclades, paired offsets
- 5gen: Position-to-ancestor mapping verified correct (skips missing ancestors)
- 6gen: Basic implementation complete

### 🐛 Known Issues
1. **5gen/6gen Position Ordering**: Father/mother assignments inverted - needs fix
2. **5gen/6gen Outer Positions**: Names appearing in wrong area (inner overlay vs outer perimeter)
3. **Position Coordinates**: 6gen positions too clustered, need spreading

### 📋 Next Steps
1. Fix father/mother position mapping in 5gen and 6gen
2. Debug why 5gen/6gen names print in 4gen overlay area instead of outer perimeter
3. Spread out 6gen position coordinates
4. Test with real GEDCOM data
5. Apply dark theme to all generator levels (2gen-6gen)

## Session Date: 2026-02-19 (Font Centering Investigation)
### Issue Investigated
A and B subclades in 7gen appeared slightly off from mirrored positions. Suspected font centering issue.

### Investigation
1. Analyzed `get_text_width_px()` function in individual_printer.py
2. Found it multiplied by `PIXEL_RATIO` (300/72 = 4.167)
3. Tested with `get_font_metrics()` - raw value was 21.0, multiplied became ~87
4. Added vertical centering using baseline offset

### Decision
Reverted changes - original horizontal centering was working correctly. The visual offset was due to:
- Sunbeam rotation angles causing text to appear at different positions
- The B/C/D positions weren't being rendered in the test script

### Accomplishments
1. Created debug_7gen_positions_test.py with all 64 positions (A/B/C/D subclades)
2. Verified sunbeam rotation logic works correctly
3. Documented sunbeam rotation in PROTOTYPE_STANDARD.md

### Files Modified
- debug_7gen_positions_test.py - New test file with all subclades
- PROTOTYPE_STANDARD.md - Added "Rotation Styles" section documenting sunbeam rotation

## Current Status
### ✅ Working
- 3gen through 6gen generators with fixed rotation (subclade-based)
- 7gen debug visualization with sunbeam rotation
- Prototype generators integrated into simple_buffer_manager.py

### 📋 Next Steps
1. Carry sunbeam rotation logic into prototype_image_7generator.py for actual name/date/place rendering
2. Verify 7gen positions display correctly with real family data
3. Test full 7gen generation flow
