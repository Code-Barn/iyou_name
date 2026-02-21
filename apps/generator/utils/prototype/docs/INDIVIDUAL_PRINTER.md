# Individual Printer Module Documentation

## Overview

`individual_printer.py` is the core rendering engine for family tree charts. It handles all text rendering for a single individual including their name, birth/death dates, birth/death places, and country flags.

**File**: `apps/generator/utils/prototype/individual_printer.py`  
**Lines**: ~860  
**Used by**: All prototype generators (1gen through 7gen)

---

## Architecture

### Core Functions

| Function | Lines | Purpose |
|----------|-------|---------|
| `get_text_width_px()` | 33-38 | Calculate text width in pixels for centering |
| `get_text_height_px()` | 41-46 | Calculate text height in pixels |
| `get_text_bounding_box()` | 49-67 | Get precise bounding box for centering |
| `print_individual()` | 70-815 | Main rendering function |
| `print_individual_simple()` | 818-861 | Simplified single-text renderer |

### Key Design Patterns

1. **Parameter Heaviness**: `print_individual()` accepts 80+ parameters for maximum flexibility
2. **Rotation Math**: Complex coordinate transformation for 0°, 90°, 180°, 270° rotations
3. **Settings Injection**: Uses `chart_settings` dict to control formatting (dates, names, places, flags)
4. **Dual Modes**: Supports both gravity-center (1gen) and offset-based positioning

---

## Function Reference

### `print_individual()`

The main workhorse. Renders name, dates, places, and flags for one person.

#### Parameters by Category

**Position (3)**
```python
center_x=0,      # Image center X for rotation calculations
center_y=0,      # Image center Y for rotation calculations  
rotation=0,      # Base rotation: 0, 90, 180, or 270 degrees
```

**Font Sizes (7)**
```python
name_font_size=72,
date_font_size=48,
place_font_size=24,
birth_date_font_size=None,   # Override for paired layouts
death_date_font_size=None,
birth_place_font_size=None,
death_place_font_size=None,
```

**Paired Layout Helpers (5)** - For displaying birth/death on same row
```python
paired_dates_base_y=None,
birth_date_paired_offset_x=0,
death_date_paired_offset_x=0,
paired_places_base_y=None,
birth_place_paired_offset_x=0,
death_place_paired_offset_x=0,
```

**Name Parameters (15)** - Each name part (first, middle, last) has base position, offset, and rotation
```python
full_name=None,              # Override: simple single-line mode
first_name_base_x=None, first_name_base_y=None,
first_name_offset_x=0, first_name_offset_y=0, first_name_rotation=0,
middle_name_base_x=None, middle_name_base_y=None,
middle_name_offset_x=0, middle_name_offset_y=0, middle_name_rotation=0,
last_name_base_x=None, last_name_base_y=None,
last_name_offset_x=0, last_name_offset_y=0, last_name_rotation=0,
```

**Birth Info Parameters (12)**
```python
birth_date_base_x=0, birth_date_base_y=None,
birth_date_offset_x=0, birth_date_offset_y=0, birth_date_rotation=0,
birth_place_base_x=None, birth_place_base_y=0,
birth_place_offset_x=0, birth_place_offset_y=0, birth_place_rotation=0,
```

**Death Info Parameters (12)** - Same structure as Birth
```python
death_date_base_x=None, death_date_base_y=0,
death_date_offset_x=0, death_date_offset_y=0, death_date_rotation=0,
death_place_base_x=0, death_place_base_y=None,
death_place_offset_x=0, death_place_offset_y=0, death_place_rotation=0,
```

**Flag Parameters (7)** - Country flag emoji
```python
birth_flag="", death_flag="",
flag_base_x=None, flag_base_y=None,
flag_offset_x=0, flag_offset_y=0,
flag_rotation=0, flag_font_size=None,
```

**Display Options (6)**
```python
use_display_text=True,     # Use multiline display_text vs individual parts
use_gravity_center=False, # Use center gravity for name positioning
multiline_line_spacing=1.2,
multiline_alignment="center",
chart_settings=None,       # Dict with date/name/place format settings
date_year_only=False,     # Compact: show only year
```

#### Internal Processing Flow

```
1. Extract chart_settings
2. Parse & format name (via name_utils)
3. Parse & format dates (via date_utils)  
4. Parse & format places (via place_name_utils)
5. Handle flags based on settings
6. Calculate positions with rotation transforms
7. Draw name (first/middle/last or display_text)
8. Draw birth date
9. Draw birth place
10. Draw death date
11. Draw death place
12. Draw flags (if enabled)
```

### Rotation Math

The function handles 4 rotation angles (0°, 90°, 180°, 270°) using coordinate transformation:

```python
# 180° example
if rotation == 180:
    final_base_x = 2 * center_x - base_x  # Flip horizontally
    final_base_y = 2 * center_y - base_y  # Flip vertically
    offset_x = -offset_x  # Invert offsets
    offset_y = -offset_y
    rot = rotation + element_rotation  # Combine rotations
```

---

## Settings Integration

### `chart_settings` Parameter

All formatting options are passed via the `chart_settings` dict:

```python
chart_settings = {
    # Date formatting
    "date_format": "da_mon_year",           # Format: american, international, etc.
    "date_year_only": False,                 # Compact: show only year
    "date_retain_leading_zeros": False,    # Keep leading zeros
    
    # Name formatting  
    "name_use_first_middle_only": False,    # Single middle name
    "name_hide_hyphenated_surname": False, # Hide hyphenated surnames
    
    # Place formatting
    "place_use_country_abbrev": False,     # USA, UK
    "place_use_state_abbrev": True,        # IL, CA
    "place_show_county": True,
    "place_show_country": True,
    "place_hide_usa_with_state": True,
    "place_show_township": True,
    "place_show_flag": False,              # Show flag emoji
    "place_flag_type": "birth",             # Which place to show flag from
}
```

---

## SWOT Analysis

### Strengths

| Area | Description |
|------|-------------|
| **Flexibility** | 80+ parameters allow precise control over every element |
| **Consistency** | Single function used across all generations (1-7) |
| **Centralization** | All text rendering logic in one place |
| **Settings Flow** | Clean integration with date_utils, name_utils, place_name_utils |
| **Rotation Support** | Comprehensive 4-angle rotation handling |
| **Paired Layouts** | Built-in support for birth/death on same row |

### Weaknesses

| Area | Description |
|------|-------------|
| **Parameter Explosion** | 80+ parameters makes function signature overwhelming |
| **Code Duplication** | Similar rotation math repeated for first/middle/last names, dates, places |
| **Documentation Burden** | Hard to understand all parameters without extensive docs |
| **No Type Hints** | Python typing not used, making IDE support limited |
| **Magic Numbers** | Hardcoded values like `PIXEL_RATIO = 300/72` scattered |
| **Monolithic** | Single 750-line function is hard to maintain |

### Opportunities

| Area | Description |
|------|-------------|
| **Refactoring** | Extract rotation math into helper functions |
| **Type Hints** | Add Python type annotations for better IDE support |
| **Dataclass/Struct** | Create a config dataclass instead of 80+ parameters |
| **Defaults** | Use **kwargs with defaults for less common parameters |
| **Testing** | Currently no unit tests - add coverage |
| **Validation** | Add runtime validation of rotation values |

### Threats

| Area | Description |
|------|-------------|
| **Complexity Barrier** | New developers may be intimidated |
| **Bug Risk** | Complex rotation math is easy to misalign |
| **Parameter Drift** | Generators may pass inconsistent parameter combos |
| **Breaking Changes** | Adding new formatting options requires all generators to pass them |

---

## Recommendations

### Short-term

1. **Add docstrings** to each parameter group explaining the rotation behavior
2. **Extract rotation math** into helper functions:
   ```python
   def transform_position(x, y, center_x, center_y, rotation, offset_x, offset_y):
       """Apply rotation transform around center."""
       ...
   ```
3. **Add type hints** to function signatures

### Medium-term

1. **Create configuration dataclass**:
   ```python
   @dataclass
   class PrintConfig:
       center_x: int = 0
       center_y: int = 0
       rotation: int = 0
       name_font_size: int = 72
       # ... with defaults
   ```
2. **Add unit tests** for rotation math and text centering
3. **Validate rotation values** at function entry

### Long-term

1. Consider splitting into smaller focused functions:
   - `render_name()`
   - `render_date()`
   - `render_place()`
   - `apply_rotation_transform()`

---

## Usage Examples

### 1gen (Gravity Center Mode)
```python
print_individual(
    draw=draw,
    content_img=content_img,
    individual=person,
    settings=validated_settings,
    chart_settings=validated_settings,
    center_x=975, center_y=975,
    rotation=0,
    use_gravity_center=True,
    use_display_text=True,
)
```

### 7gen (Sunbeam Rotation)
```python
print_individual(
    draw=draw,
    content_img=content_img,
    individual=person,
    settings=validated_settings,
    chart_settings=validated_settings,
    center_x=975, center_y=975,
    rotation=sunbeam_rotation,  # Dynamic based on position
    full_name=person.full_name,  # Single-line mode
    first_name_base_x=pos_x,
    first_name_base_y=pos_y,
    first_name_rotation=sunbeam_rotation,
    date_year_only=True,  # Compact for tight spaces
)
```

---

## Dependencies

```
┌─────────────────────────────────────────────────────────┐
│                 individual_printer.py                    │
├─────────────────────────────────────────────────────────┤
│  External:                                             │
│  - wand (ImageMagick bindings)                        │
│  - math (standard library)                             │
│                                                         │
│  Internal:                                             │
│  - name_utils.get_name_display_info()                 │
│  - name_utils.get_name_display_info_with_settings()     │
│  - date_utils.format_date_from_settings()             │
│  - place_name_utils.format_place_from_settings()      │
│  - place_name_utils.get_flag_from_place()             │
└─────────────────────────────────────────────────────────┘
```

---

## Maintenance Notes

- When adding new formatting options, add to `chart_settings` and handle in the relevant utility module
- When adding new positioning options, consider if it's rotation-related (add to math section) or base-position related
- Test with all 4 rotation angles (0, 90, 180, 270) when modifying rotation logic
- The function intentionally doesn't validate inputs - generators are responsible for passing valid data
