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

### US_STATE_ABBREVIATIONS

Maps full US state names to two-letter abbreviations:

```python
US_STATE_ABBREVIATIONS = {
    "alabama": "AL",
    "california": "CA",
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

Combined lookup table for both US states and Canadian provinces (includes reverse lookup for abbreviations like "IL" -> "IL").

## Functions

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
    'parts_count': int
}

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
#     'parts_count': 4
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
- `show_county` (bool): Include county in output (default: True)
- `show_township` (bool): Include township in output (default: True)
- `show_country` (bool): Include country in output (default: True)
- `hide_usa_with_state` (bool): Hide "USA" when US state is present (default: True)
- `country_first` (bool): Put country before other parts (default: False)

**Returns:**
- `str`: Formatted place string

**Examples:**
```python
# Full place
place = "Chicago, Cook County, Illinois, USA"

# Show everything
format_place(place, show_county=True, show_township=True)
# -> "Chicago, Cook County, Illinois, USA"

# Hide county, abbreviate state
format_place(place, show_county=False, use_state_abbrev=True)
# -> "Chicago, IL, USA"

# Hide USA when state shown
format_place(place, hide_usa_with_state=True)
# -> "Chicago, Cook County, Illinois"

# Country first (non-US places)
format_place("London, England, UK", country_first=True)
# -> "UK, London, England"
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
  - `place_show_county`: bool
  - `place_show_township`: bool
  - `place_show_country`: bool
  - `place_hide_usa_with_state`: bool
  - `place_country_first`: bool
- `flag` (str): Optional flag emoji to append

**Returns:**
- `str`: Formatted place string

**Note:** The `flag` parameter is deprecated - flags should be positioned separately using the `print_individual()` function parameters.

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

## Settings Integration

The HUD form provides checkboxes for place formatting:

| Setting | Default | Description |
|---------|---------|-------------|
| `place_show_county` | False | Show county names |
| `place_show_township` | True | Show township names |
| `place_show_country` | True | Show country names |
| `place_use_state_abbrev` | True | Abbreviate states (IL vs Illinois) |
| `place_use_country_abbrev` | True | Abbreviate countries (USA vs United States) |
| `place_hide_usa_with_state` | True | Hide "USA" when state is shown |
| `place_show_flag` | False | Show country flag emoji |
| `place_flag_type` | "birth" | Which place to get flag from (birth/death) |

## Known Issues Fixed

1. **Checkbox handling**: The HUD template was using `!= False` which always checked boxes. Fixed to use proper boolean evaluation.

2. **State abbreviation check**: The `hide_usa_with_state` logic was checking against full state names but the state had already been abbreviated. Fixed by checking against `STATE_ABBREVIATIONS` which includes both full names and abbreviations.

3. **Position-based county detection**: For US places with 3-4 parts ending in state/USA, the 2nd part is always the county. Updated parsing logic to detect unlabeled counties based on position.
