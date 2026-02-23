# Settings Systems Documentation

## Overview

This document catalogs the current settings systems in the codebase, analyzes their inconsistencies, and provides a roadmap for consolidation. It also documents the buffer caching system and cumulative settings approach for efficient navigation between generations.

> **Note**: For detailed design of persistent settings and buffer storage, see [PERSISTENT_SETTINGS_BUFFER_DESIGN.md](./PERSISTENT_SETTINGS_BUFFER_DESIGN.md)

---

## Buffer Caching System

### Purpose

The buffer caching system stores generated chart images to avoid regenerating them when navigating between generations, as long as settings haven't changed.

### How It Works

1. **Buffer Storage**: Generated chart images are stored in memory using `SimpleBufferManager`
2. **Settings Hash**: Each buffer is associated with a hash of the settings used to generate it
3. **Cache Validation**: When requesting a preview, the system checks if:
   - The individual is the same
   - The settings hash matches the cached version
4. **Cache Hit**: If valid, returns the cached buffer
5. **Cache Miss**: If invalid, generates new buffer and stores it

### Buffer Key Components

```python
# From simple_buffer_manager.py
buffer_key = str(generation)  # "1", "2", "3", etc.
settings_hash = hash(json.dumps(settings, sort_keys=True))
```

### Cache Invalidation

The buffer is invalidated when:
- Individual changes
- Settings change (detected via hash comparison)

---

## Cumulative Settings Approach

### Problem

When navigating between generations (e.g., 1gen → 2gen → 3gen), each generation has its own form with generation-specific settings. Without a unified approach, this caused:
- Different settings sent to backend for each generation
- Buffer cache misses even when user made no changes
- Inefficient regeneration of charts

### Solution

The cumulative settings approach ensures consistent settings across generations:

1. **Settings Storage**: Each generation's settings are stored in localStorage:
   - `hud_1gen_settings` - 1gen specific settings
   - `hud_2gen_settings` - 2gen specific settings
   - `hud_3gen_settings` - 3gen specific settings
   - etc.

2. **Cumulative Retrieval**: When viewing generation N:
   ```javascript
   // Get settings from all generations 1 through N
   function getCumulativeSettings(currentGeneration) {
       const cumulativeSettings = {};
       for (let gen = 1; gen <= currentGeneration; gen++) {
           const genSettings = getStoredGenerationSettings(gen);
           if (genSettings) {
               Object.assign(cumulativeSettings, genSettings);
           }
       }
       return cumulativeSettings;
   }
   ```

3. **Preview Generation**: Always uses cumulative settings when available:
   ```javascript
   // In updatePreviewImage()
   const cumulativeSettings = HUD.Storage.getCumulativeSettings(currentGen);
   if (cumulativeSettings && Object.keys(cumulativeSettings).length > 0) {
       userSettings = cumulativeSettings;  // Use cached cumulative settings
   } else {
       userSettings = collectUserSettings(formData);  // Fallback for first visit
   }
   ```

### Benefits

- **Consistent Cache Keys**: Same settings hash for same visual output
- **Efficient Navigation**: Sequential navigation (Prev/Next arrows) uses cached buffers
- **Settings Inheritance**: Lower generation settings apply to higher generations (for overlay compositing)

### JavaScript Module Structure

```javascript
HUD.Storage = {
    getStored1GenSettings()      // Get 1gen settings for 2gen overlay
    store1GenSettings(settings)  // Store when Apply clicked at 1gen
    storeGenerationSettings(gen, settings)  // Store for any generation
    getStoredGenerationSettings(gen)  // Get specific generation's settings
    getCumulativeSettings(gen)    // Get all settings from gen 1 to N
}
```

---

## Current Settings Systems

### 1. HUD Templates (`apps/hud/templates/hud/settings/`)

**Purpose**: User-facing settings UI in the browser

| File | Settings Provided |
|------|------------------|
| `1gen_settings.html` | Color, Font, Font Size, Position (primary, birth date/place, death date/place), Flag Size |
| `2gen_settings.html` | Adds parent generation colors and positions, Flag Size |
| `3gen_settings.html` | Adds grandparent generation colors and positions, Flag Size |
| `4gen_settings.html` | Adds great-grandparent generation |
| `5gen_settings.html` | Adds great-great-grandparent generation |
| `6gen_settings.html` | Adds 3x great-grandparent generation |
| `7gen_settings.html` | Adds 4x great-grandparent generation |

**Per-Generation Flag Size** (defaults):
- 1gen: 300px
- 2gen: 200px  
- 3gen: 200px

**Characteristics**:
- Per-generation specific settings (e.g., `primary_`, `parent_`, `grandparent_`, `greatgrandparent_`, etc.)
- Position settings: translate_x, translate_y, rotate for each element
- Color settings: background, stroke, font, birth/death dates/places
- Font settings: family, sizes per generation
- Flag settings: place_flag_size (controls PNG flag overlay size)

---

### 2. Main Display Template (`display_tree.html`)

**Purpose**: Chart-wide settings that apply to all generations

**Current Sections**:
- **Navigation**: Prev/Next arrow buttons for sequential generation navigation (replaced dropdown)
- Generation display ("1 Generation", "2 Generation Chart", etc.)
- Place Name Formatting (checkboxes)
- Date Format (dropdown + checkboxes)
- Name Formatting (checkboxes)
- Dynamic settings panel (per-generation template)

**Navigation Flow**:
```
[←] 1 Generation [→]  →  [←] 2 Generation Chart [→]  →  [←] 3 Generation Chart [→]
```

Each navigation triggers:
1. Load new settings panel for target generation
2. Apply cumulative settings from localStorage
3. Generate preview using cached buffer (if settings unchanged)

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

### Phase 1: Unify Settings Flow (COMPLETED)

1. **Cumulative Settings System** ✅
   - Settings stored per-generation in localStorage
   - `getCumulativeSettings(N)` retrieves all settings from gen 1 to N
   - Preview generation uses cumulative settings for consistent cache keys

2. **Buffer Caching** ✅
   - `SimpleBufferManager` stores generated buffers
   - Settings hash validates cache freshness
   - Sequential navigation (Prev/Next) uses cached buffers when settings unchanged

3. **Navigation UI** ✅
   - Replaced dropdown with Prev/Next arrow buttons
   - Smooth sequential generation navigation
   - Settings panel loads dynamically per generation

### Phase 2: Persistent Storage (COMPLETED)

1. **Database Models** ✅
   - `UserStorageQuota` - Per-user storage tracking (500MB default)
   - `UserSettingsPreset` - Named saved presets
   - `IndividualSettings` - Per gedcom+individual settings
   - `ChartBuffer` - Long-term buffer storage (model only, not yet active)

2. **API Endpoints** ✅
   - CRUD for presets
   - CRUD for individual settings
   - Home person management
   - Storage usage/clear

3. **JavaScript Integration** ✅
   - `HUD.PresetManager` module
   - Save/Load preset buttons
   - Set Home Person button with badge
   - Storage usage display

4. **Home Person Integration** ✅
   - Setting home person syncs GedcomFile AND IndividualSettings
   - Auto-loads saved settings when viewing home person
   - Badge next to name on browse and HUD pages

### Phase 3: Buffer Persistence (PENDING)

See [PERSISTENT_SETTINGS_BUFFER_DESIGN.md](./PERSISTENT_SETTINGS_BUFFER_DESIGN.md) for detailed design.

1. **PersistentBufferManager** - Uses database + disk storage
2. **Version Checking** - Invalidate buffers when code changes
3. **Quota Enforcement** - Check quota before storing
4. **PDF Downloads** - Use cached buffers for final chart generation

### Phase 4: Documentation ✅

1. ✅ Updated `PROTOTYPE_STANDARD.md` with buffer/flag documentation
2. ✅ Created `PERSISTENT_SETTINGS_BUFFER_DESIGN.md`
3. ✅ This document (SETTINGS_SYSTEM.md) updated

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
| Buffer Caching | Implemented with SimpleBufferManager | ✅ Complete |
| Cumulative Settings | Implemented via localStorage | ✅ Complete |
| Navigation UI | Prev/Next arrows | ✅ Complete |
| Place formatting | Pre-processed in generator | Pass via chart_settings |
| Date formatting | Via chart_settings | ✅ Good |
| Name formatting | Via chart_settings | ✅ Good |
| Settings UI | Split between 2 files | Unify |
| Schemas | Duplicated per-gen | Use inheritance |
| Documentation | Updated | ✅ Complete |
