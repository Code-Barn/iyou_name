# Quick Reference: 1gen & 2gen Implementation

## Three Name Printing Modes

### Mode 1: Gravity Center (1gen only)
```
use_gravity_center=True
use_display_text=True
# Uses image center (975, 975), multiline with \n
```

### Mode 2: Multiline at Base Position (3gen)
```
use_display_text=True
use_gravity_center=False
first_name_base_x=975, first_name_base_y=1500
# Multiline display_text centered at base position
```

### Mode 3: Single-Line Full Name (Recommended 3gen+)
```
full_name=individual.full_name
use_display_text=False
use_gravity_center=False
first_name_base_x=975, first_name_base_y=1750
# Full name on ONE line at base position
```

---

## Centering Pattern (ALL text uses this)
```
translate(x, y) → rotate(degrees) → translate(-text_width//2, 0) → text(0, 0)
```

### Constants
```python
class Generation1Constants:
    CENTER_X = 975
    CENTER_Y = 975
    RESOLUTION = 300
    PIXEL_RATIO = 300 / 72  # ~4.167
    
    # Base positions for info
    BIRTH_DATE_X = 200       # Left edge
    BIRTH_PLACE_Y = 1875     # Bottom edge
    DEATH_DATE_Y = 200       # Top edge
    DEATH_PLACE_X = 1875     # Right edge
```

### Working Call (use_display_text=True, use_gravity_center=True)
```python
print_individual(
    draw=draw,
    content_img=content_img,
    individual=person,
    settings=validated_settings,
    center_x=975,
    center_y=975,
    rotation=0,
    name_font_size=84,
    date_font_size=60,
    place_font_size=28,
    first_name_rotation=-45,
    birth_date_base_x=200,
    birth_date_rotation=-90,
    birth_place_base_y=1875,
    death_date_base_y=200,
    death_place_base_x=1875,
    death_place_rotation=-90,
    use_display_text=True,
    use_gravity_center=True,
)
```

---

## 2gen: Two Individuals (Father/Mother)

### Position System
- **Position 1 (Father)**: rotation=0
  - First name: bottom edge (base_y=1875)
  - Last name: right edge (base_x=1875), vertical (-90°)
- **Position 2 (Mother)**: rotation=180
  - Same base positions, rotated 180° around image center
  - First name: top edge (after flip)
  - Last name: left edge (after flip), vertical

### Constants
```python
class Generation2Constants:
    IMAGE_CENTER_X = 975
    IMAGE_CENTER_Y = 975
    
    # Position 1 base (father)
    POSITION_1_FIRST_NAME_BASE_X = 975   # Center X
    POSITION_1_FIRST_NAME_BASE_Y = 1875  # Bottom edge
    
    POSITION_1_LAST_NAME_BASE_X = 1875   # Right edge
    POSITION_1_LAST_NAME_BASE_Y = 975    # Center Y
    
    PARENT_NAME_FONT_SIZE = 48
    PARENT_DATE_INFO_FONT_SIZE = 36
    PARENT_PLACE_INFO_FONT_SIZE = 20
```

### Father Call (rotation=0)
```python
print_individual(
    draw=draw,
    content_img=content_img,
    individual=father,
    settings=validated_settings,
    center_x=975,
    center_y=975,
    rotation=0,
    name_font_size=48,
    first_name_base_x=975,
    first_name_base_y=1875,
    first_name_rotation=0,
    last_name_base_x=1875,
    last_name_base_y=975,
    last_name_rotation=-90,  # Vertical text
    use_display_text=False,
    use_gravity_center=False,
)
```

### Mother Call (rotation=180) - SAME base positions!
```python
print_individual(
    draw=draw,
    content_img=content_img,
    individual=mother,
    settings=validated_settings,
    center_x=975,
    center_y=975,
    rotation=180,  # Rotated 180° - same code, different position!
    name_font_size=48,
    # SAME base positions as father
    first_name_base_x=975,
    first_name_base_y=1875,
    first_name_rotation=0,
    last_name_base_x=1875,
    last_name_base_y=975,
    last_name_rotation=-90,
    use_display_text=False,
    use_gravity_center=False,
)
```

### Rotation Math
```python
# 180° rotation around center
final_base_x = 2 * center_x - base_x  # 975→975, 1875→75
final_base_y = 2 * center_y - base_y  # 975→975, 1875→75
```

---

## Key Insight

**Define base positions ONCE, apply rotation to get all positions.**

For 2gen: 1 set of base positions → rotated 0° and 180°
For 3gen: 1 set → rotated 0°, 90°, 180°, 270°
For Ngen: 1 set → rotated N times around center
