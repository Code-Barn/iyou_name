# Name Parsing Utilities

## Overview

The `name_utils.py` module provides functions for parsing and formatting names consistently across all generation-specific image generators.

## Location

`apps/generator/utils/name_utils.py`

## Functions

### parse_name_parts(full_name)

Parses a full name into first, middle, and last name parts. Handles edge cases like missing middle names.

**Parameters:**
- `full_name` (str): Full name string to parse

**Returns:**
- `tuple`: (first_name, middle_name, last_name)

**Examples:**
```python
parse_name_parts("John Doe") -> ("John", "", "Doe")
parse_name_parts("John Michael Smith") -> ("John", "Michael", "Smith")
parse_name_parts("John") -> ("John", "", "")
parse_name_parts("") -> ("", "", "")
```

### format_name_multiline(first_name, middle_name, last_name)

Formats name parts as a multiline string, only including non-empty parts.

**Parameters:**
- `first_name` (str): First name string
- `middle_name` (str): Middle name string
- `last_name` (str): Last name string

**Returns:**
- `str`: Multiline string with non-empty name parts joined by newlines

**Examples:**
```python
format_name_multiline("John", "", "Doe") -> "John\nDoe"
format_name_multiline("John", "Michael", "Smith") -> "John\nMichael\nSmith"
format_name_multiline("John", "", "") -> "John"
```

### get_name_display_info(full_name)

Gets complete name display information including parsed parts and formatted text.

**Parameters:**
- `full_name` (str): Full name string to parse and format

**Returns:**
- `dict`: {
    'first_name': str,
    'middle_name': str,
    'last_name': str,
    'display_text': str  # multiline formatted text
}

**Examples:**
```python
get_name_display_info("John Michael Smith")
# Returns:
# {
#     'first_name': 'John',
#     'middle_name': 'Michael',
#     'last_name': 'Smith',
#     'display_text': 'John\nMichael\nSmith'
# }
```

## Usage in Generators

The name parsing utilities are used throughout the generator modules:

```python
from apps.generator.utils.name_utils import (
    parse_name_parts,
    format_name_multiline,
    get_name_display_info,
)

# In a generator function:
name_info = get_name_display_info(individual.full_name)
first_name = name_info["first_name"]
middle_name = name_info["middle_name"]
last_name = name_info["last_name"]
display_text = name_info["display_text"]
```

## Notes

- `parse_name_parts()` takes only the first middle name if multiple middle names exist
- Empty parts are filtered out in `format_name_multiline()`
- Logging is provided for debugging name parsing issues
