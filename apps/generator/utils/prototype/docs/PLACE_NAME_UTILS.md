# Place Name Utilities

## Overview

The `place_name_utils.py` module provides functions for parsing, abbreviating, and formatting place names for better display in family tree charts.

## Location

`apps/generator/utils/prototype/place_name_utils.py`

## Constants

### COUNTRY_ABBREVIATIONS

Maps full country names to standard abbreviations:

```python
COUNTRY_ABBREVIATIONS = {
    "united states of america": "USA",
    "united states": "USA",
    "us": "USA",
    "u.s.": "USA",
    "u.s.a.": "USA",
    "united kingdom": "UK",
    "great britain": "GB",
}
```

### COUNTRY_FLAGS

Maps country names to flag emoji:

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

### COUNTRY_CODES

Maps country names to ISO 3166-1 alpha-2 codes for flag images:

```python
COUNTRY_CODES = {
    "usa": "us",
    "uk": "gb",
    "england": "gb-eng",
    "scotland": "gb-sct",
    # ... and more
}
```

### US_STATE_ABBREVIATIONS

Maps full US state names to two-letter abbreviations:

```python
US_STATE_ABBREVIATIONS = {
    "alifornia": "CA",
    "illinois": "IL",
    # ... all 50 states + DC
}
```

### CANADA_PROVINCE_ABBREVIATIONS

Maps Canadian province names to abbreviations:

```python
CANADA_PROVINCE_ABBREVIATIONS = {
    "alberta": "AB",
    "ontario": "ON",
    "quebec": "QC",
    # ... and more
}
```

### STATE_ABBREVIATIONS

Combined lookup table for both US states and Canadian provinces (includes reverse lookup for abbreviations like "il" -> "IL").

### UK_COUNTY_ABBREVIATIONS

Extensive mapping for UK and Irish county abbreviations (e.g., "Yorkshire" -> "Yorks.", "London" -> "Lon.").

### KNOWN_COUNTRIES

Set of known country identifiers for place parsing.

### UK_COUNTRIES

Set of UK constituent countries (England, Scotland, Wales, N. Ireland).

## Functions

### detect_country(place: str) -> dict

Detects the country of a place name with support for UK constituent countries.

**Parameters:**
- `place` (str): Place string (e.g., "Chicago, Illinois, USA" or "London, England, UK")

**Returns:**
- `dict`: {
    'country': str,        # Detected country name (or UK constituent)
    'is_us': bool,        # True if place is in the US
    'is_uk': bool,        # True if place is in the UK
    'raw_country': str    # Raw last part if it's a country identifier
}

**Examples:**
```python
detect_country("Chicago, Illinois, USA")
# Returns: {'country': 'USA', 'is_us': True, 'is_uk': False, 'raw_country': 'USA'}

detect_country("Edinburgh, Scotland, UK")
# Returns: {'country': 'Scotland', 'is_us': False, 'is_uk': True, 'raw_country': 'UK'}
```

### parse_place(place: str) -> dict

Parses a comma-separated place name into components.

**Parameters:**
- `place` (str): Place string (e.g., "Chicago, Cook County, Illinois, USA")

**Returns:**
- `dict`: {
    'city': str,
    'county': str,
    'township': str,
    'state': str,
    'country': str,
    'other': str,
    'parts_count': int,
    'is_us': bool,
    'is_uk': bool
}

**Helper Functions (internal):**
- `is_explicit_county(part)` - Checks for "County", "Co." markers
- `is_explicit_township(part)` - Checks for "Township", "Twp", "Ward" markers

**Examples:**
```python
parse_place("Chicago, Cook County, Illinois, USA")
# Returns:
# {
#     'city': 'Chicago',
#     'county': 'Cook County',
#     'township': '',
#     'state': 'Illinois',
#     'country': 'USA',
#     'other': '',
#     'parts_count': 4,
#     'is_us': True,
#     'is_uk': False
# }
```

### abbreviate_country(country: str) -> str

Abbreviates a country name if recognized.

**Parameters:**
- `country` (str): Full country name

**Returns:**
- `str`: Abbreviated name or original

### abbreviate_state(state: str) -> str

Abbreviates a state/province name if recognized.

**Parameters:**
- `state` (str): Full state or province name

**Returns:**
- `str`: Two-letter abbreviation or original

### format_place(place: str, **kwargs) -> str

Formats a place name based on various settings.

**Parameters:**
- `place` (str): Original place string
- `use_country_abbrev` (bool): Abbreviate country (default: False)
- `use_state_abbrev` (bool): Abbreviate state to 2-letter code (default: False)
- `hide_us_counties` (bool): Hide US county names (default: True)
- `show_township` (bool): Include township in output (default: True)
- `show_country` (bool): Include country in output (default: True)
- `hide_usa_with_state` (bool): Hide "USA" when US state is present (default: True)
- `country_first` (bool): Put country before other parts (default: False)
- `auto_shorten` (bool): Reduce 3+ parts to 2 parts (default: False)
- `abbreviate_uk_counties` (bool): Abbreviate UK/Ireland counties (default: False)

**Returns:**
- `str`: Formatted place string

**County Display Logic:**
- US counties: "Marion County" → "Marion Co."
- Irish counties: "County Cork" → "Co. Cork"
- UK counties: displayed as-is

**Examples:**
```python
# Full place
place = "Chicago, Cook County, Illinois, USA"

# Show everything
format_place(place, hide_us_counties=False, show_township=True)
# -> "Chicago, Cook County, Illinois, USA"

# Hide county, abbreviate state
format_place(place, hide_us_counties=True, use_state_abbrev=True)
# -> "Chicago, IL, USA"

# Hide USA when state shown
format_place(place, hide_usa_with_state=True)
# -> "Chicago, Cook County, Illinois"

# Auto-shorten 3+ parts to 2
format_place(place, auto_shorten=True)
# -> "Illinois, USA"

# Abbreviate UK counties
format_place("Yorkshire, England, UK", abbreviate_uk_counties=True)
# -> "Yorks., England, UK"
```

### get_place_short(place: str, max_parts: int = 2) -> str

Gets a shortened version of a place name.

**Parameters:**
- `place` (str): Original place string
- `max_parts` (int): Maximum number of parts to include (from the end)

**Returns:**
- `str`: Shortened place string

**Examples:**
```python
get_place_short("Chicago, Cook County, Illinois, USA", max_parts=2)
# -> "Illinois, USA"
```

### format_place_from_settings(place: str, settings: dict, flag: str = "") -> str

Formats a place name using settings from the generator.

**Parameters:**
- `place` (str): Original place string
- `settings` (dict): Settings dictionary with keys:
  - `place_use_country_abbrev`: bool
  - `place_use_state_abbrev`: bool
  - `place_hide_us_counties`: bool
  - `place_show_township`: bool
  - `place_show_country`: bool
  - `place_hide_usa_with_state`: bool
  - `place_country_first`: bool
  - `place_auto_shorten`: bool
  - `place_abbreviate_uk_counties`: bool
- `flag` (str): Optional flag emoji to append (deprecated)

**Returns:**
- `str`: Formatted place string

### get_flag_from_place(place: str) -> str

Extracts country flag emoji from a place string.

**Parameters:**
- `place` (str): Place string (e.g., "Chicago, Illinois, USA")

**Returns:**
- `str`: Flag emoji if country detected, empty string otherwise

**Examples:**
```python
get_flag_from_place("Chicago, Illinois, USA")
# -> "🇺🇸"

get_flag_from_place("London, England")
# -> "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
```

### get_flag_image_path(place: str) -> str

Gets the relative path to a flag image file.

**Parameters:**
- `place` (str): Place string

**Returns:**
- `str`: Relative path (e.g., "charts/images/flags/us.png") or empty string

### get_flag_from_place_with_settings(place: str, birth_date: str, death_date: str, show_uk_flag: bool, show_ireland_flag: bool) -> str

Gets flag emoji with date-aware logic for UK and Ireland.

**Parameters:**
- `place` (str): Place string
- `birth_date` (str): Birth date in YYYY-MM-DD format (optional)
- `death_date` (str): Death date in YYYY-MM-DD format (optional)
- `show_uk_flag` (bool): Show UK flag instead of constituent country flag
- `show_ireland_flag` (bool): Apply date restrictions for Ireland flag

**Date Logic:**
- UK places: If `show_uk_flag=True`, only show UK flag if date is after 1801-01-01 (UK formation)
- Ireland places: If `show_ireland_flag=True`, only show Ireland flag if date is between 1801-01-01 and 1922-12-06 (when Ireland was part of the UK)

**Returns:**
- `str`: Flag emoji or empty string

**Internal Helpers:**
- `parse_date(date_str)` - Parse YYYY-MM-DD string to datetime
- `is_date_after(target_date_str, check_date)` - Check if date is after target
- `is_date_between(start_date_str, end_date_str, check_date)` - Check if date is in range

## Usage in Generators

Import and use in generator modules:

```python
from apps.generator.utils.prototype.place_name_utils import (
    format_place_from_settings,
    get_flag_from_place,
    parse_place,
)

# In a generator function:
birth_place_raw = getattr(individual, "birth_place", "") or ""

# Format place with settings
formatted_birth = format_place_from_settings(
    birth_place_raw,
    validated_settings,
)

# Get flag separately (do NOT append to place string)
if show_flag and flag_type == "birth":
    birth_flag = get_flag_from_place(birth_place_raw)
else:
    birth_flag = ""

# Pass flag to print_individual as separate parameter
print_individual(
    # ... other params
    birth_flag=birth_flag,
    flag_base_x=center_x,
    flag_base_y=center_y,
    flag_rotation=-45,
)
```

## Settings Integration (HUD)

The HUD form (`display_tree.html`) provides checkboxes for place formatting:

| Setting | Default | Description |
|---------|---------|-------------|
| `place_use_country_abbrev` | True | Abbreviate countries (USA, UK) |
| `place_use_state_abbrev` | True | Abbreviate states (IL vs Illinois) |
| `place_hide_us_counties` | True | Hide US county names |
| `place_show_township` | False | Show township names |
| `place_show_country` | True | Show country names |
| `place_hide_usa_with_state` | True | Hide "USA" when state is shown |
| `place_auto_shorten` | False | Reduce 3+ parts to 2 |
| `place_abbreviate_uk_counties` | False | Abbreviate UK/Ireland counties |
| `place_show_flag` | True | Show country flag |
| `place_show_uk_flag` | False | Show UK flag (after 1801) instead of constituent |
| `place_flag_type` | "birth" | Which place to get flag from (birth/death) |
| `place_flag_format` | "png" | Flag format (png/emoji) |
| `flag_font` | varies | Font for emoji flags (platform-specific) |

## Known Issues Fixed

1. **Checkbox handling**: The HUD template was using `!= False` which always checked boxes. Fixed to use proper boolean evaluation.

2. **State abbreviation check**: The `hide_usa_with_state` logic was checking against full state names but the state had already been abbreviated. Fixed by checking against `STATE_ABBREVIATIONS` which includes both full names and abbreviations.

3. **Position-based county detection**: For US places with 3-4 parts ending in state/USA, the 2nd part is always the county. Updated parsing logic to detect unlabeled counties based on position.

4. **UK flag date logic**: Added `get_flag_from_place_with_settings()` to handle date-aware UK and Ireland flag display based on historical events.
