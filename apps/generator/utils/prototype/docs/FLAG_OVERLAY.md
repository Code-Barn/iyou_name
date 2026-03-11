# Flag Overlay System

## Overview

The flag overlay system provides country flag rendering for family tree charts. It supports both **PNG flag images** and **emoji flags** with precise positioning and layering control.

## Two Flag Systems

There are two separate flag rendering approaches in the codebase:

### 1. PNG Image-Based System (Recommended)
- **Function**: `get_flag_image_path(place)` → returns path like `"charts/images/flags/us.png"`
- **Rendering**: Composites PNG image onto canvas using Wand
- **Pros**: Works consistently across platforms, scalable, reliable
- **Cons**: Requires flag image files to be present

### 2. Emoji-Based System (Legacy)
- **Function**: `get_flag_from_place(place)` → returns emoji like `"🇺🇸"`
- **Function**: `get_flag_from_place_with_settings()` → enhanced version with UK/Ireland date logic
- **Rendering**: Uses `draw.text()` with a special font (Symbola)
- **Pros**: No image files needed, smaller file size
- **Cons**: Fonts don't render reliably on Linux (Noto Color Emoji fails, Symbola renders in B&W)

## Key Design Decisions

1. **PNG is Default**: Emoji fonts don't render reliably on Linux. PNG flags from flagcdn.com work consistently.

2. **Two Rendering Approaches**:
   - **Overlay approach** (`_render_flag_overlay`): Renders flags AFTER background, BEFORE text for layering control. Used in 1gen. **PNG only**.
   - **print_individual approach**: Flags rendered within print_individual along with text. Used in 2gen-7gen. **Supports both PNG and emoji**.

3. **Rotational Translation**: Flags use the same positioning system as text - define once at base position as OFFSET from center, then auto-translate to all quadrants for multi-gen charts.

4. **Small Positioning Drift**: There is a minor (~10px) positioning drift at 180° rotations. This is acceptable for now but may need refinement for production.

## Important: Generation 1 Limitation

The `_render_flag_overlay()` function in 1gen **only supports PNG format**:

```python
# prototype_image_1generator.py:307-308
if flag_format != "png":
    return
```

This means:
- **1gen**: Can only show PNG flags (emoji option in HUD won't work)
- **2gen-7gen**: Can show both PNG and emoji via `flag_format` setting

## Flag Image Storage

Location: `apps/charts/static/charts/images/flags/`

Format: `{country_code}.png` (e.g., `us.png`, `gb.png`, `gb-eng.png`)

Source: flagcdn.com (w640 resolution recommended)

## Current Implementation

### Generation 1 (1gen)
- Uses `_render_flag_overlay()` function
- Positioned via overlay approach with layer control
- **Format**: PNG only (emoji not supported)
- Base offset: (609, 609) from center (975, 975)
- Rotation: -45° for flag tilt

### Generation 2 (2gen)
- Uses `print_individual()` approach
- **Formats**: Both PNG and emoji supported
- Flag parameters passed to print_individual:
  - `flag_base_x=609`: X offset from center
  - `flag_base_y=609`: Y offset from center
  - `flag_rotation=-45`: Flag tilt
  - `flag_size=200`: Flag size in pixels
- Position rotation applied via print_individual's rotation parameter
- Results in flags at ~10px closer to center at 180° position (acceptable drift)

### Generation 3-7 (3gen-7gen)
- Uses `print_individual()` approach
- **Formats**: Both PNG and emoji supported
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

### COUNTRY_FLAGS

Maps country names to emoji (used by emoji-based system):

```python
COUNTRY_FLAGS = {
    "usa": "🇺🇸",
    "uk": "🇬🇧",
    "england": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "canada": "🇨🇦",
    # ... and more
}
```

## Functions

### get_flag_image_path(place: str) -> str (PNG System)

Returns the relative path to a PNG flag for a given place string.

```python
get_flag_image_path("Chicago, Illinois, USA")
# -> "charts/images/flags/us.png"

get_flag_image_path("London, England")
# -> "charts/images/flags/gb-eng.png"
```

### get_flag_from_place(place: str) -> str (Emoji System)

Returns emoji flag for a given place string.

```python
get_flag_from_place("Chicago, Illinois, USA")
# -> "🇺🇸"

get_flag_from_place("London, England")
# -> "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
```

### get_flag_from_place_with_settings(place: str, ...) -> str (Emoji System)

Returns emoji flag with date-aware logic for UK and Ireland:

- UK places: If `show_uk_flag=True`, only shows UK flag if date is after 1801-01-01 (UK formation)
- Ireland places: If `show_ireland_flag=True`, only shows Ireland flag if date is between 1801-01-01 and 1922-12-06 (when Ireland was part of the UK)

### _render_flag_overlay(...)

Renders a flag as an overlay using the Wand library. **PNG only** - see limitation above.

Supports:

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

When using print_individual approach (2gen-7gen), supports both formats:

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

## Control Flow

```
place_flag_format setting ("png" or "emoji")
         │
         ├─► "png"  ──► individual_printer: uses get_flag_image_path() → composites PNG
         │              (1gen: _render_flag_overlay - PNG ONLY)
         │
         └─► "emoji" ──► individual_printer: uses get_flag_from_place() → draw.text() with Symbola font
                          (Note: 1gen does NOT support emoji)
```

## Date-Specific UK/Ireland Flag Logic (Not Currently Active)

There is **implemented but unused** date-aware flag logic designed to show historical flags based on an individual's birth/death dates:

### Implementation Location

- **Function**: `get_flag_from_place_with_settings()` in `place_name_utils.py` (lines 1039-1144)
- **Logic**: Uses birth/death dates to determine appropriate flag for UK and Ireland

### Historical Dates

```python
UK_FOUNDING_DATE = "1801-01-01"  # United Kingdom of Great Britain and Ireland formed
IRELAND_INDEPENDENCE_DATE = "1922-12-06"  # Irish Free State established
```

### How It Works

**For UK places (England, Scotland, Wales):**
- Default: Show constituent country flag (🏴󠁧󠁢󠁥󠁮󠁧󠁿, 🏴󠁧󠁢󠁳󠁣󠁴󠁿, 🏴󠁧󠁢󠁷󠁬󠁳󠁿)
- If `show_uk_flag=True`: Show UK Union Jack (🇬🇧), but only if birth/death is **after 1801-01-01**
- If date is before 1801: Returns empty string (no flag shown)

**For Ireland places:**
- Default: Always show Ireland flag (🇮🇪)
- If `show_ireland_flag=True`: Only show Ireland flag if date is **between 1801-01-01 and 1922-12-06** (when Ireland was part of the UK)
- Outside this range: Returns empty string

### HUD Settings

The following settings exist but are **not currently connected** to the rendering pipeline:

| Setting | Default | Description |
|---------|---------|-------------|
| `place_show_uk_flag` | False | Show UK flag instead of constituent (after 1801) |

### The Problem

The function `get_flag_from_place_with_settings()` exists and is fully implemented, BUT it is **never called** by the rendering code.

**Current code** (`individual_printer.py` lines 249-253):
```python
# Uses simple version WITHOUT date logic
birth_flag = get_flag_from_place(individual.birth_place or "")
birth_flag_path = get_flag_image_path(individual.birth_place or "")
```

**Should be using**:
```python
# With date-aware UK/Ireland logic
birth_flag = get_flag_from_place_with_settings(
    individual.birth_place or "",
    birth_date=individual.birth_date,
    death_date=individual.death_date,
    show_uk_flag=chart_settings.get("place_show_uk_flag", False),
    show_ireland_flag=chart_settings.get("place_show_ireland_flag", False),
)
```

### Future Implementation

To activate this feature:

1. Modify `individual_printer.py` to call `get_flag_from_place_with_settings()` instead of `get_flag_from_place()`
2. Pass `birth_date` and `death_date` from the individual to the function
3. Optionally add `place_show_ireland_flag` to HUD for Ireland-specific control

This would allow:
- Historical accuracy: Show England/Scotland/Wales flags for individuals born before 1801
- Show UK flag for those born after UK formation
- Show Ireland flag for those who died before Irish independence (1922)

---

## Future: Historical Date-Based Flag System

### Overview

Extend the date-based flag logic to support historical flags for any country. This allows displaying era-appropriate flags based on whether an individual was born or died during a particular historical period.

### What's Needed

#### 1. Data Structure: Historical Flag Mappings

```python
# Example structure
HISTORICAL_FLAGS = {
    "germany": [
        {"code": "de", "name": "German Empire", "start": "1871-01-18", "end": "1918-11-11"},
        {"code": "de", "name": "Weimar Republic", "start": "1919-02-11", "end": "1933-03-14"},
        {"code": "de", "name": "Nazi Germany", "start": "1933-03-14", "end": "1945-05-23"},
        {"code": "de", "name": "West Germany", "start": "1949-05-23", "end": "1990-10-02"},
        {"code": "de", "name": "East Germany", "start": "1949-10-07", "end": "1990-10-02"},
        # fallback to current flag
    ],
    "poland": [
        # Multiple partitions, interwar, WWII, communist era
    ],
    "russia": [
        {"code": "ru", "name": "Russian Empire", "start": None, "end": "1917-03-15"},
        {"code": "ru", "name": "Soviet Union", "start": "1922-12-30", "end": "1991-12-26"},
    ],
    # etc.
}
```

#### 2. PNG Image Files Needed

| Country | Historical Flags Needed |
|---------|------------------------|
| Germany | Empire (black/gold), Weimar (black/red/gold), East Germany |
| Poland | Partitions era, interwar, communist |
| Russia | Imperial (double-headed eagle), Soviet |
| Italy | Kingdom of Italy (shield) |
| Austria-Hungary | Austro-Hungarian empire |
| Czechoslovakia | Czech/Slovak split |
| Yugoslavia | Various iterations |
| Ireland | Before/after 1922 |
| UK | Before/after 1801 |

#### 3. Code Changes Required

**In `place_name_utils.py`:**
- Create `HISTORICAL_FLAGS` data structure
- Create `get_historical_flag_code(country, date)` function
- Update `get_flag_from_place_with_settings()` to accept date and return appropriate flag code

**In `individual_printer.py`:**
- Pass `birth_date` and `death_date` to flag rendering
- Call the date-aware function instead of simple version

**In generators (2gen-7gen):**
- Ensure dates are passed through to `print_individual`

#### 4. New Settings (Future)

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `place_historical_flags` | bool | False | Enable historical flag logic |
| `place_flag_date_type` | str | "birth" | Which date to use: "birth", "death", or "either" |

### Future Feature: Multiple Flags

#### Show Both Birth and Death Flags

**Setting**: `place_flag_type` = "both"

Display both birth and death flags when an individual was born in one country and died in another:

```
┌─────────────────────────────┐
│  John Smith                 │
│  Born: New York, USA  🇺🇸   │
│  Died: London, UK    🇬🇧   │
└─────────────────────────────┘
```

**Implementation notes:**
- Requires rendering two flags with offset positions
- May need additional positioning settings
- Consider limiting to cases where birth_country != death_country

#### Burial Place Option

**Setting**: `place_death_location_type` = "death" | "burial"

For genealogical accuracy, some users may want the death flag to reflect burial location rather than death location:

- **"death"** (default): Use death place for flag
- **"burial"**: Use burial place for flag

**GEDCOM Integration:**
- GEDCOM stores both `DEAT` (death) and `BURI` (burial) tags
- May need to extend `PersonData` model to include burial_place
- Parser may need updating to extract burial location

**Setting table:**

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `place_death_location_type` | str | "death" | Use death or burial place for death flag |

### Priority Countries for Genealogy

Most impactful for family history (in order):

1. **Germany** - Most common immigrant origin, multiple regime changes (1871+)
2. **Ireland** - Already partially implemented (1922 independence)
3. **Poland** - Complex partition history (1793-1918, interwar, communist)
4. **UK** - Already partially implemented (1801 formation)
5. **Russia/USSR** - Common immigrant origin (Imperial → Soviet → Russia)
6. **Italy** - Unified 1861, various states before
7. **Czechoslovakia/Yugoslavia** - Dissolved countries

### Implementation Roadmap

**Phase 1: Infrastructure**
- [ ] Connect existing `get_flag_from_place_with_settings()` to rendering
- [ ] Add date parameters to print_individual calls
- [ ] Test UK/Ireland historical logic end-to-end

**Phase 2: Core Countries**
- [ ] Germany (high priority - most common genealogical case)
- [ ] Complete Ireland/UK logic
- [ ] Add Poland historical flags

**Phase 3: Extended Coverage**
- [ ] Russia, Italy, Austria-Hungary
- [ ] Other European countries

**Phase 4: Polish UI**
- [ ] Add settings to enable/disable historical flags
- [ ] Add "both" flag type option
- [ ] Add burial place option for death flag
- [ ] Show "historical flag" indicator in UI

### Challenges & Solutions

1. **Date ambiguity**: What if someone was born in 1910 in Berlin?
   - Solution: Use German Empire flag (pre-WWI)

2. **Migration (birth/death in different countries)**: Person born in Austria-Hungary, died in USA
   - Solution: "both" flag option lets user see both

3. **Image availability**: Historical flags may not be readily available
   - Solution: Start with countries that have easy-to-find flag images
   - Consider using Wikipedia/public domain sources

4. **Multiple flags per country**: Some countries had 3-4 different flags in 100 years
   - Solution: Define date ranges precisely; fall back to current flag if no match

### Code Architecture

```python
# place_name_utils.py additions

def get_historical_flag(
    place: str,
    date: str,  # YYYY-MM-DD format
    historical_flags_enabled: bool = False,
) -> str:
    """
    Get flag emoji based on historical period.
    
    Args:
        place: Place string
        date: Date to check (birth or death)
        historical_flags_enabled: If False, returns current flag
    
    Returns:
        Historical flag emoji if enabled and matches
    """
    if not historical_flags_enabled:
        return get_flag_from_place(place)
    
    # Parse place to get country
    parsed = parse_place(place)
    country = parsed.get("country", "").lower()
    
    # Look up historical flags for country
    if country not in HISTORICAL_FLAGS:
        return get_flag_from_place(place)
    
    # Find matching historical period
    for period in HISTORICAL_FLAGS[country]:
        if is_date_in_range(date, period["start"], period["end"]):
            return COUNTRY_FLAGS.get(period["code"], "")
    
    # Fall back to current flag
    return get_flag_from_place(place)
```

---

## Current Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `place_show_flag` | bool | True | Enable flag rendering |
| `place_flag_type` | str | "birth" | Which place to use: "birth", "death", or "both" (future) |
| `place_flag_format` | str | "png" | Format: "png" or "emoji" |
| `place_flag_size` | int | 48 | Flag size in pixels |
| `place_flag_layer` | str | "bottom" | Layer: "top" (on text) or "bottom" (behind text) |
| `place_flag_in_overlay` | bool | True | Use overlay approach vs print_individual |
| `flag_font` | str | varies | Font for emoji flags |
| `place_show_uk_flag` | bool | False | Show UK flag for post-1801 dates (future) |
| `place_historical_flags` | bool | False | Enable historical flag logic (future) |
| `place_death_location_type` | str | "death" | Use death or burial place (future) |

## Positioning Offsets by Generation

| Generation | flag_base_x | flag_base_y | Format Support |
|------------|-------------|-------------|----------------|
| 1gen | 609 | 609 | PNG only |
| 2gen | 609 | 609 | PNG + emoji |
| 3gen | 0 | 645 | PNG + emoji |
| 4gen-7gen | varies | varies | PNG + emoji |

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

## Layering Options (Overlay Approach - 1gen Only)

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

## Known Issues

1. **1gen Emoji Not Supported**: The `_render_flag_overlay()` function skips emoji entirely. Users selecting "emoji" format in 1gen will see no flag.

2. **Minor 180° Drift**: Flags at 180° positions render ~10px closer to center than expected. This is acceptable for now but may need refinement.

3. **Rotation Formula**: The rotation applies to position offset from center. Image rotation happens after position calculation, which can cause minor centering shifts.

4. **Emoji Font Rendering**: On Linux, Symbola font renders flags in B&W, Noto Color Emoji may fail entirely. PNG is recommended.

## Future Improvements

1. Add emoji support to 1gen's `_render_flag_overlay()` function
2. Consider unifying both systems to always use print_individual approach for consistency
3. Add date-aware UK/Ireland flag logic to PNG system (currently only in emoji system)

## Troubleshooting

### Duplicate Flags

If seeing duplicate flags:
- Check `place_flag_in_overlay` setting
- Ensure only one rendering path is active

### Flag Not Showing (1gen)

1. Check if using emoji format (not supported in 1gen)
2. Check flag image exists: `apps/charts/static/charts/images/flags/{code}.png`
3. Verify country is in `COUNTRY_CODES` mapping
4. Check logs for "Flag image not found" warnings

### Flag Not Showing (2gen-7gen)

1. Verify format setting matches your expectation (png/emoji)
2. For emoji: ensure flag_font is set and font file exists
3. For PNG: check flag image exists
4. Check logs for warnings

### Flag Position Off

1. Verify flag_base_x/flag_base_y are offsets from center (not absolute)
2. Check rotation parameter matches position rotation
3. For 180° positions, minor drift is expected

### Emoji Shows as Square/Box

- Font not installed or not loading correctly
- Try different `flag_font` setting for your platform
- Consider switching to PNG format

## Files

| File | Purpose |
|------|---------|
| `place_name_utils.py` | Flag path resolution (PNG), emoji lookup (emoji), country code mapping |
| `prototype_image_1generator.py` | 1gen flag overlay with `_render_flag_overlay` (PNG only) |
| `prototype_image_2generator.py` | 2gen flag via print_individual |
| `prototype_image_3generator.py` | 3gen flag via print_individual |
| `prototype_image_4generator.py` | 4gen flag via print_individual |
| `prototype_image_5generator.py` | 5gen flag via print_individual |
| `prototype_image_6generator.py` | 6gen flag via print_individual |
| `prototype_image_7generator.py` | 7gen flag via print_individual |
| `individual_printer.py` | Flag rendering within print_individual (supports both PNG and emoji) |
