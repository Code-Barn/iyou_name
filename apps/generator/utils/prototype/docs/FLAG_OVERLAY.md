# Flag Overlay System

## Overview

The flag overlay system provides country flag rendering for family tree charts. It supports PNG flag images with precise positioning and layering control.

## Key Design Decisions

1. **PNG over Emoji**: Emoji fonts don't render reliably on Linux (Noto Color Emoji fails, Symbola renders in B&W). PNG flags from flagcdn.com work consistently.

2. **Two Rendering Approaches**:
   - **Overlay approach** (`_render_flag_overlay`): Renders flags AFTER background, BEFORE text for layering control. Used in 1gen.
   - **print_individual approach**: Flags rendered within print_individual along with text. Used in 2gen, 3gen. Simpler but less layering control.

3. **Rotational Translation**: Flags use the same positioning system as text - define once at base position as OFFSET from center, then auto-translate to all quadrants for multi-gen charts.

4. **Small Positioning Drift**: There is a minor (~10px) positioning drift at 180° rotations. This is acceptable for now but may need refinement for production.

## Flag Image Storage

Location: `apps/charts/static/charts/images/flags/`

Format: `{country_code}.png` (e.g., `us.png`, `gb.png`, `gb-eng.png`)

Source: flagcdn.com (w640 resolution recommended)

## Current Implementation

### Generation 1 (1gen)
- Uses `_render_flag_overlay()` function
- Positioned via overlay approach with layer control
- Base offset: (609, 609) from center (975, 975)
- Rotation: -45° for flag tilt

### Generation 2 (2gen)
- Uses `print_individual()` approach
- Flag parameters passed to print_individual:
  - `flag_base_x=609`: X offset from center
  - `flag_base_y=609`: Y offset from center
  - `flag_rotation=-45`: Flag tilt
  - `flag_size=200`: Flag size in pixels
- Position rotation applied via print_individual's rotation parameter
- Results in flags at ~10px closer to center at 180° position (acceptable drift)

### Generation 3 (3gen)
- Uses `print_individual()` approach
- Flag parameters:
  - `flag_base_x=0`: X offset from center
  - `flag_base_y=645`: Y offset from center
  - `flag_size=200`: Flag size in pixels
- Similar minor drift at 180° position

## Constants

### COUNTRY_CODES

Maps country names to ISO 3166-1 alpha-2 codes:

```python
COUNTRY_CODES = {
    "usa": "us",
    "united states": "us",
    "uk": "gb",
    "united kingdom": "gb",
    "england": "gb-eng",
    "scotland": "gb-sct",
    "wales": "gb-wls",
    "canada": "ca",
    "germany": "de",
    # ... and more
}
```

## Functions

### get_flag_image_path(place: str) -> str

Returns the relative path to a PNG flag for a given place string.

```python
get_flag_image_path("Chicago, Illinois, USA")
# -> "charts/images/flags/us.png"

get_flag_image_path("London, England")
# -> "charts/images/flags/gb-eng.png"
```

### _render_flag_overlay(...)

Renders a flag as an overlay using the Wand library. Supports:

- **Rotational translation**: Apply same positioning as text for multi-gen charts
- **Layer control**: Place flag "top" (on text) or "bottom" (behind text on background)
- **Custom positioning**: Base X/Y offsets from center point

```python
_render_flag_overlay(
    content_img,
    primary_individual,
    validated_settings,
    flag_base_x=609,      # X offset from center
    flag_base_y=609,      # Y offset from center
    flag_rotation=-45,    # Rotation of flag itself
    flag_size=300,        # Size in pixels
    rotation=0,           # Quadrant rotation (0, 90, 180, 270)
)
```

### print_individual() Flag Parameters

When using print_individual approach:

```python
print_individual(
    draw=draw,
    content_img=content_img,
    individual=individual,
    settings=validated_settings,
    chart_settings=validated_settings,
    rotation=rotation,           # Position rotation (0, 90, 180, 270)
    flag_base_x=609,            # X OFFSET from center
    flag_base_y=609,            # Y OFFSET from center
    flag_rotation=-45,           # Flag's own rotation
    flag_size=200,              # Flag size in pixels
    # ... other parameters
)
```

**Important**: `flag_base_x` and `flag_base_y` are OFFSETS from center, not absolute positions!

## Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `place_show_flag` | bool | False | Enable flag rendering |
| `place_flag_type` | str | "birth" | Which place to use: "birth" or "death" |
| `place_flag_format` | str | "png" | Format: "png" or "emoji" |
| `place_flag_size` | int | 48 | Flag size in pixels |
| `place_flag_layer` | str | "bottom" | Layer: "top" (on text) or "bottom" (behind text) |
| `place_flag_in_overlay` | bool | True | Use overlay approach vs print_individual |

## Positioning Offsets by Generation

| Generation | flag_base_x | flag_base_y | Notes |
|------------|-------------|-------------|-------|
| 1gen | 609 | 609 | Via overlay |
| 2gen | 609 | 609 | Via print_individual |
| 3gen | 0 | 645 | Via print_individual |

## Multi-Generation Positioning

Flags use the same rotational translation system as text. The offset is rotated around center:

```python
# Base offset from center
dx = flag_base_x  # e.g., 609
dy = flag_base_y  # e.g., 609

# Rotate offset for each quadrant
for rotation in [0, 90, 180, 270]:
    angle_rad = math.radians(rotation)
    rotated_x = dx * cos(angle_rad) - dy * sin(angle_rad)
    rotated_y = dx * sin(angle_rad) + dy * cos(angle_rad)
    
    # Final position
    x = center_x + rotated_x
    y = center_y + rotated_y
```

## Layering Options (Overlay Approach)

### "bottom" (Default)
```
┌─────────────────────┐
│    Background       │
│  ┌───────────────┐  │
│  │    Flag       │  │  <- Behind text, on background
│  │  ┌─────────┐  │  │
│  │  │  Text   │  │  │
│  │  └─────────┘  │  │
│  └───────────────┘  │
└─────────────────────┘
```

### "top"
```
┌─────────────────────┐
│    Background       │
│  ┌───────────────┐  │
│  │  ┌─────────┐  │  │
│  │  │  Text   │  │  │
│  │  └─────────┘  │  │
│  │    Flag       │  │  <- On top of everything
│  └───────────────┘  │
└─────────────────────┘
```

## Rendering Order (print_individual Approach)

With print_individual, flags are drawn as part of the text drawing layer:

1. Background applied to content_img
2. draw() called to render all text + flags together
3. Result is flags appear at same layer as text (behind overlay if used)

## Known Issues

1. **Minor 180° Drift**: Flags at 180° positions render ~10px closer to center than expected. This is acceptable for now but may need refinement.

2. **Rotation Formula**: The rotation applies to position offset from center. Image rotation happens after position calculation, which can cause minor centering shifts.

## Future: Gen 4-7

For generations 4 and beyond, the overlay approach may be needed for better control:
- Flags will need to scale appropriately for tighter positions
- Consider using overlay approach from the start for consistency
- Same rotational translation pattern applies

## Troubleshooting

### Duplicate Flags

If seeing duplicate flags:
- Check `place_flag_in_overlay` setting
- Ensure only one rendering path is active

### Flag Not Showing

1. Check flag image exists: `apps/charts/static/charts/images/flags/{code}.png`
2. Verify country is in `COUNTRY_CODES` mapping
3. Check logs for "Flag image not found" warnings
4. Ensure flag_base_x/flag_base_y are offsets (not absolute positions)

### Flag Position Off

1. Verify flag_base_x/flag_base_y are offsets from center (not absolute)
2. Check rotation parameter matches position rotation
3. For 180° positions, minor drift is expected

## Files

| File | Purpose |
|------|---------|
| `place_name_utils.py` | Flag path resolution, country code mapping |
| `prototype_image_1generator.py` | 1gen flag overlay with `_render_flag_overlay` |
| `prototype_image_2generator.py` | 2gen flag via print_individual |
| `prototype_image_3generator.py` | 3gen flag via print_individual |
| `individual_printer.py` | Flag rendering within print_individual |
