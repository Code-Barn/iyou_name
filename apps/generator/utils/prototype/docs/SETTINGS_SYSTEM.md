# Settings Systems Documentation

## Overview

This document catalogs the current settings systems in the codebase, analyzes their inconsistencies, and provides a roadmap for consolidation.

---

## Current Settings Systems

### 1. HUD Templates (`apps/hud/templates/hud/settings/`)

**Purpose**: User-facing settings UI in the browser

| File | Settings Provided |
|------|------------------|
| `1gen_settings.html` | Color, Font, Font Size, Position (primary, birth date/place, death date/place) |
| `2gen_settings.html` | Adds parent generation colors and positions |
| `3gen_settings.html` | Adds grandparent generation colors and positions |
| `4gen_settings.html` | Adds great-grandparent generation |
| `5gen_settings.html` | Adds great-great-grandparent generation |
| `6gen_settings.html` | Adds 3x great-grandparent generation |
| `7gen_settings.html` | Adds 4x great-grandparent generation |

**Characteristics**:
- Per-generation specific settings (e.g., `primary_`, `parent_`, `grandparent_`, `greatgrandparent_`, etc.)
- Position settings: translate_x, translate_y, rotate for each element
- Color settings: background, stroke, font, birth/death dates/places
- Font settings: family, sizes per generation

---

### 2. Main Display Template (`display_tree.html`)

**Purpose**: Chart-wide settings that apply to all generations

**Current Sections**:
- Generation selector
- Place Name Formatting (checkboxes)
- Date Format (dropdown + checkboxes)
- Name Formatting (checkboxes)
- Dynamic settings panel (per-generation template)

**Settings**:
```python
# Place settings
place_use_country_abbrev: bool
place_use_state_abbrev: bool
place_show_county: bool
place_show_country: bool
place_hide_usa_with_state: bool
place_show_township: bool
place_show_flag: bool
place_flag_type: str ("birth" | "death")

# Date settings
date_format: str ("da_mon_year" | "american_month" | "international_month" | "american" | "international")
date_year_only: bool
date_retain_leading_zeros: bool

# Name settings
name_use_first_middle_only: bool
name_hide_hyphenated_surname: bool
```

---

### 3. Generator Schemas (`prototype_image_Xgenerator.py`)

**Purpose**: Validation and defaults for generator settings

Each generator has a `GENERATION_X_SETTINGS_SCHEMA` dict:

```python
GENERATION_1_SETTINGS_SCHEMA = {
    "font_family": (str, "Arial"),
    "primary_background_color": (Color, "#000000"),
    "primary_font_color": (Color, "white"),
    # ... many more settings per generation
    # Chart-wide settings
    "date_format": (str, "da_mon_year"),
    "date_year_only": (bool, False),  # 6gen+
    "place_use_country_abbrev": (bool, False),
    "place_use_state_abbrev": (bool, True),
    # ... more place settings
}
```

---

### 4. Individual Printer (`individual_printer.py`)

**Purpose**: Core function that renders each individual's info on the chart

**Parameters**:
- Position: `center_x`, `center_y`, `rotation`
- Font sizes: `name_font_size`, `date_font_size`, `place_font_size`
- Offsets: `*_offset_x`, `*_offset_y` for each element
- Base positions: `*_base_x`, `*_base_y` for dates/places
- Rotations: `*_rotation` for each element
- Flags: `birth_flag`, `death_flag`
- Display options: `use_display_text`, `use_gravity_center`, `multiline_*`
- **Chart settings**: `chart_settings` (NEW - carries date/name format options)

---

### 5. Utility Modules

#### `date_utils.py`
- `parse_date()` - Parse various date formats
- `format_date()` - Format with options
- `format_date_from_settings()` - Format using settings dict

**Settings handled**:
```python
date_format: str
date_year_only: bool  
date_retain_leading_zeros: bool
```

#### `name_utils.py`
- `parse_name_parts()` - Split name into first/middle/last
- `parse_name_parts_with_settings()` - With format options
- `get_name_display_info()` - Get display dict
- `get_name_display_info_with_settings()` - With format options

**Settings handled**:
```python
name_use_first_middle_only: bool
name_hide_hyphenated_surname: bool
```

#### `place_name_utils.py`
- `parse_place()` - Parse location components
- `format_place()` - Format with options
- `format_place_from_settings()` - Format using settings

**Settings handled**:
```python
place_use_country_abbrev: bool
place_use_state_abbrev: bool
place_show_county: bool
place_show_country: bool
place_hide_usa_with_state: bool
place_show_township: bool
place_show_flag: bool
place_flag_type: str
```

---

## Settings Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HUD TEMPLATES                                  │
│  ┌─────────────────┐    ┌──────────────────────┐                   │
│  │ display_tree   │    │ Xgen_settings.html   │                   │
│  │ (chart-wide)   │    │ (per-gen positions)  │                   │
│  └────────┬────────┘    └──────────┬───────────┘                   │
│           │                         │                                 │
│           ▼                         ▼                                 │
│    ┌────────────────────────────────────────────┐                   │
│    │           hud/views.py (save_hud_settings) │                   │
│    │   - Parses POST data                      │                   │
│    │   - Builds hud_settings dict               │                   │
│    │   - Saves to session                      │                   │
│    └────────────────────┬─────────────────────┘                    │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SESSION/STORAGE                                │
│    hud_settings = {                                                │
│        # Chart-wide (from display_tree)                           │
│        "date_format": "da_mon_year",                              │
│        "name_use_first_middle_only": False,                        │
│        "place_show_country": True,                                │
│        # Per-gen (from Xgen_settings)                             │
│        "primary_name_font_size": 84,                              │
│        "parent_font_size": 36,                                     │
│        ...                                                          │
│    }                                                               │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     GENERATOR VIEWS                                  │
│    ┌─────────────────────────────────────────────┐                  │
│    │ generator/views.py (generate_preview)       │                  │
│    │ - Collects settings from POST or session    │                  │
│    │ - Passes to generator function               │                  │
│    └────────────────────┬──────────────────────┘                  │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   GENERATOR FUNCTIONS                                │
│    ┌─────────────────────────────────────────────┐                  │
│    │ prototype_image_Xgenerator.py               │                  │
│    │ - get_validated_settings()                  │                  │
│    │ - Creates chart image                        │                  │
│    │ - For each individual:                      │                  │
│    │   1. Format place (pre-process)             │                  │
│    │   2. Call print_individual()                │                  │
│    └────────────────────┬──────────────────────┘                  │
└─────────────────────────┼───────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────┐    ┌─────────────────────────────────────┐
│   PLACE SETTINGS    │    │         PRINT_INDIVIDUAL()          │
│  (pre-processed)    │    │                                     │
│                     │    │  Parameters:                        │
│ Format in generator │    │  - Position (x, y, rotation)        │
│ before calling      │    │  - Font sizes                       │
│ print_individual()  │    │  - Offsets                          │
│                     │    │  - chart_settings  ◄────────┐       │
│ Uses:               │    │                               │       │
│ format_place_       │    │  Internally uses:               │       │
│ from_settings()     │    │  - get_name_display_info()    │       │
│                     │    │    with settings               │       │
└─────────────────────┘    │  - format_date_from_settings()  │       │
                          │                               │       │
                          │  chart_settings contains:      │       │
                          │  - date_format                 │       │
                          │  - date_year_only              │       │
                          │  - date_retain_leading_zeros   │       │
                          │  - name_use_first_middle_only │       │
                          │  - name_hide_hyphenated_surname│       │
                          └───────────────────────────────┘       │
                                                             ─────┘
```

---

## Current Inconsistencies

### 1. Place Settings Are Pre-processed

**Current**: Place formatting happens in the generator BEFORE `print_individual()` is called
**Problem**: Inconsistent with date/name which are passed as settings

```python
# Current approach in generator:
formatted_birth_place = format_place_from_settings(birth_place_raw, validated_settings)

formatted_individual = FormattedIndividual(
    primary_individual, formatted_birth_place, formatted_death_place
)

print_individual(..., individual=formatted_individual, ...)
```

**Better Approach**: Pass place settings through `chart_settings` like dates/names

### 2. Two Different Settings UIs

- `display_tree.html` - Chart-wide settings (date, name, place format)
- `Xgen_settings.html` - Per-generation positions and colors

**Problem**: User has to look in multiple places for settings

### 3. Schema Duplication

Each generator has its own `GENERATION_X_SETTINGS_SCHEMA` with many duplicated entries.

### 4. Outdated Settings Templates

The `Xgen_settings.html` templates are:
- Not using the new date/name/place format settings
- Missing the new options we just added
- Not following a consistent pattern

---

## Roadmap for Consolidation

### Phase 1: Unify Settings Flow (Recommended Next)

1. **Move place formatting into `print_individual()`**
   - Pass place settings through `chart_settings`
   - Remove pre-processing in generators
   - Simplifies generator code

2. **Create single settings schema system**
   - Base schema with chart-wide settings
   - Per-generation extends base
   - Use inheritance pattern

### Phase 2: Update HUD Templates

1. **Add new date/name settings to Xgen_settings.html**
   - Currently only in `display_tree.html`
   - Should be available at all generation levels

2. **Standardize template structure**
   - Follow consistent pattern across 1-7gen
   - Include all format options

3. **Consider merging into single UI**
   - All settings in one place?
   - Or clear separation: format vs. position?

### Phase 3: Documentation

1. Update `PROTOTYPE_STANDARD.md` with settings documentation
2. Add settings reference to each utility module
3. Create settings migration guide

---

## Recommended Settings Schema Structure

```python
# Base chart-wide settings (all generations)
CHART_SETTINGS_SCHEMA = {
    # Date formatting
    "date_format": (str, "da_mon_year"),
    "date_year_only": (bool, False),
    "date_retain_leading_zeros": (bool, False),
    
    # Name formatting  
    "name_use_first_middle_only": (bool, False),
    "name_hide_hyphenated_surname": (bool, False),
    
    # Place formatting
    "place_use_country_abbrev": (bool, False),
    "place_use_state_abbrev": (bool, True),
    "place_show_county": (bool, True),
    "place_show_country": (bool, True),
    "place_hide_usa_with_state": (bool, True),
    "place_show_township": (bool, True),
    "place_show_flag": (bool, False),
    "place_flag_type": (str, "birth"),
    
    # Fonts
    "font_family": (str, "Arial"),
}

# Per-generation settings (extends base)
GENERATION_1_SCHEMA = {
    **CHART_SETTINGS_SCHEMA,
    "primary_background_color": (Color, "#FFFFFF"),
    "primary_font_color": (Color, "black"),
    # ... position and size settings
}
```

---

## Summary

| Aspect | Current State | Recommended |
|--------|---------------|-------------|
| Place formatting | Pre-processed in generator | Pass via chart_settings |
| Date formatting | Via chart_settings | Good |
| Name formatting | Via chart_settings | Good |
| Settings UI | Split between 2 files | Unify |
| Schemas | Duplicated per-gen | Use inheritance |
| Documentation | Scattered | Centralize |
