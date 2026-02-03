"""
Name parsing utilities for family tree generators.

This module provides functions for parsing and formatting names consistently
across all generation-specific image generators.
"""

import logging

logger = logging.getLogger(__name__)


def parse_name_parts(full_name):
    """
    Parse a full name into first, middle, and last name parts.
    Handles edge cases like missing middle names properly.

    Args:
        full_name: Full name string to parse

    Returns:
        tuple: (first_name, middle_name, last_name)

    Examples:
        parse_name_parts("John Doe") -> ("John", "", "Doe")
        parse_name_parts("John Michael Smith") -> ("John", "Michael", "Smith")
        parse_name_parts("John") -> ("John", "", "")
        parse_name_parts("") -> ("", "", "")
    """
    name_parts = full_name.split()

    if len(name_parts) == 0:
        # No name parts at all
        first_name = ""
        middle_name = ""
        last_name = ""
    elif len(name_parts) == 1:
        # Only first name: "John"
        first_name = name_parts[0]
        middle_name = ""
        last_name = ""
    elif len(name_parts) == 2:
        # First and last name: "John Doe"
        first_name = name_parts[0]
        middle_name = ""
        last_name = name_parts[1]
    else:
        # First, middle(s), and last name: "John Michael Smith"
        first_name = name_parts[0]
        middle_name = name_parts[1]  # Take only first middle name for now
        last_name = name_parts[-1]

    logger.debug(
        f"Parsed name '{full_name}' -> first:'{first_name}', middle:'{middle_name}', last:'{last_name}'"
    )
    return first_name, middle_name, last_name


def format_name_multiline(first_name, middle_name, last_name):
    """
    Format name parts as a multiline string, only including non-empty parts.

    Args:
        first_name: First name string
        middle_name: Middle name string
        last_name: Last name string

    Returns:
        str: Multiline string with non-empty name parts joined by newlines

    Examples:
        format_name_multiline("John", "", "Doe") -> "John\nDoe"
        format_name_multiline("John", "Michael", "Smith") -> "John\nMichael\nSmith"
        format_name_multiline("John", "", "") -> "John"
    """
    name_parts_to_display = [
        part for part in [first_name, middle_name, last_name] if part.strip()
    ]
    return "\n".join(name_parts_to_display)


def get_name_display_info(full_name):
    """
    Get complete name display information including parsed parts and formatted text.

    Args:
        full_name: Full name string to parse and format

    Returns:
        dict: {
            'first_name': str,
            'middle_name': str,
            'last_name': str,
            'display_text': str  # multiline formatted text
        }
    """
    first_name, middle_name, last_name = parse_name_parts(full_name)
    display_text = format_name_multiline(first_name, middle_name, last_name)

    return {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "display_text": display_text,
    }
