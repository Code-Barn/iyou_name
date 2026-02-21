"""
Name parsing utilities for family tree generators.

This module provides functions for parsing and formatting names consistently
across all generation-specific image generators.
"""

import logging
import re

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


def parse_name_parts_with_settings(full_name, settings=None):
    """
    Parse a full name into first, middle, and last name parts with settings.

    Args:
        full_name: Full name string to parse
        settings: Dictionary with settings:
            - name_use_first_middle_only: bool - use only first middle name
            - name_hide_hyphenated_surname: bool - hide hyphenated surnames

    Returns:
        tuple: (first_name, middle_name, last_name)

    Examples:
        parse_name_parts_with_settings("John Michael Smith", {}) -> ("John", "Michael", "Smith")
        parse_name_parts_with_settings("John Michael Robert Smith", {"name_use_first_middle_only": True}) -> ("John", "Michael", "Smith")
        parse_name_parts_with_settings("John Smith-Jones", {"name_hide_hyphenated_surname": True}) -> ("John", "", "")
    """
    settings = settings or {}
    use_first_middle_only = settings.get("name_use_first_middle_only", False)
    hide_hyphenated = settings.get("name_hide_hyphenated_surname", False)

    name_parts = full_name.split()

    if len(name_parts) == 0:
        first_name = ""
        middle_name = ""
        last_name = ""
    elif len(name_parts) == 1:
        first_name = name_parts[0]
        middle_name = ""
        last_name = ""
    elif len(name_parts) == 2:
        first_name = name_parts[0]
        middle_name = ""
        last_name = name_parts[1]
    else:
        first_name = name_parts[0]
        if use_first_middle_only:
            middle_name = name_parts[1]
        else:
            middle_name = " ".join(name_parts[1:-1])
        last_name = name_parts[-1]

    # Handle hyphenated surname
    if hide_hyphenated and last_name and "-" in last_name:
        last_name = ""

    logger.debug(
        f"Parsed name '{full_name}' with settings -> first:'{first_name}', middle:'{middle_name}', last:'{last_name}'"
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


def get_name_display_info_with_settings(full_name, settings=None):
    """
    Get complete name display information with settings applied.

    Args:
        full_name: Full name string to parse and format
        settings: Dictionary with settings:
            - name_use_first_middle_only: bool
            - name_hide_hyphenated_surname: bool

    Returns:
        dict: {
            'first_name': str,
            'middle_name': str,
            'last_name': str,
            'display_text': str  # multiline formatted text
        }
    """
    first_name, middle_name, last_name = parse_name_parts_with_settings(
        full_name, settings
    )
    display_text = format_name_multiline(first_name, middle_name, last_name)

    return {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "display_text": display_text,
    }
