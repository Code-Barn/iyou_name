"""
Date utilities for formatting and abbreviating date data.

Provides functions to parse, format, and abbreviate dates
for better display in family tree charts.
"""

import re
from datetime import datetime
from typing import Optional


MONTH_ABBREVIATIONS = {
    "january": "Jan",
    "february": "Feb",
    "march": "Mar",
    "april": "Apr",
    "may": "May",
    "june": "Jun",
    "july": "Jul",
    "august": "Aug",
    "september": "Sep",
    "october": "Oct",
    "november": "Nov",
    "december": "Dec",
}

MONTH_NUMBERS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


class DateFormat:
    AMERICAN = "american"
    INTERNATIONAL = "international"
    DA_MON_YEAR = "da_mon_year"
    AMERICAN_MONTH = "american_month"
    INTERNATIONAL_MONTH = "international_month"


DATE_QUALIFIERS = (
    "circa",
    "c.",
    "ca.",
    "abt",
    "about",
    "approx",
    "approximately",
    "bet",
    "between",
    "est",
    "estimated",
    "calculated",
    "calc",
    "before",
    "bef",
    "after",
    "aft",
    "unknown",
    "unk",
)


def parse_date(date_str: str) -> dict:
    """
    Parse a date string into components (day, month, year).

    Supports various input formats:
    - YYYY-MM-DD (ISO)
    - DD Mon YYYY (e.g., 15 Jan 1985)
    - Mon DD, YYYY (e.g., Jan 15, 1985)
    - Mon YYYY (e.g., March 1973)
    - MM/DD/YYYY (American)
    - DD/MM/YYYY (International)
    - YYYY (year only)
    - (April 17, 1857) - with parentheses
    - circa 1900, abt 1985, etc. - with qualifiers

    Returns:
        Dictionary with keys: day, month, month_num, year, original
        Returns empty values if parsing fails or only month is present.
    """
    if not date_str:
        return {
            "day": "",
            "month": "",
            "month_num": 0,
            "year": "",
            "original": "",
        }

    original = date_str.strip()
    date_str = original.strip()

    # Check for placeholder/invalid dates early
    date_str_lower = date_str.lower().strip()
    if date_str_lower in ("unknown", "unk", "", "-", "?", "[]"):
        return {
            "day": "",
            "month": "",
            "month_num": 0,
            "year": "",
            "original": original,
        }

    result = {
        "day": "",
        "month": "",
        "month_num": 0,
        "year": "",
        "original": original,
    }

    # Strip parentheses and brackets
    date_str = date_str.strip("()[]{}")

    # Remove date qualifiers (circa, abt, etc.)
    for qualifier in DATE_QUALIFIERS:
        if date_str.lower().startswith(qualifier):
            date_str = date_str[len(qualifier) :].strip()
            break
        # Also check for "bet X and Y" pattern
        if date_str_lower.startswith("bet ") and " and " in date_str:
            # Extract just the first year
            match = re.search(r"\b(1[0-9]{3}|20[0-2][0-9])\b", date_str)
            if match:
                result["year"] = match.group(1)
            return result

    # Handle year-only format (e.g., "1900")
    if re.match(r"^(1[0-9]{3}|20[0-2][0-9])$", date_str):
        result["year"] = date_str
        return result

    # Handle "Mon YYYY" format (e.g., "March 1973")
    mon_y_match = re.match(
        r"^([A-Za-z]+)\s+(1[0-9]{3}|20[0-2][0-9])$", date_str, re.IGNORECASE
    )
    if mon_y_match:
        month_str = mon_y_match.group(1).lower()
        result["year"] = mon_y_match.group(2)
        if month_str in MONTH_NUMBERS:
            result["month_num"] = MONTH_NUMBERS[month_str]
            result["month"] = MONTH_ABBREVIATIONS.get(
                month_str, mon_y_match.group(1).title()
            )
        return result

    # Handle ISO format (YYYY-MM-DD)
    iso_match = re.match(r"^(1[0-9]{3}|20[0-2][0-9])-(\d{1,2})-(\d{1,2})$", date_str)
    if iso_match:
        result["year"] = iso_match.group(1)
        result["month_num"] = int(iso_match.group(2))
        result["day"] = str(int(iso_match.group(3))).zfill(2)
        month_num = result["month_num"]
        for month_name, month_num_val in MONTH_NUMBERS.items():
            if month_num_val == month_num and month_name in MONTH_ABBREVIATIONS:
                result["month"] = MONTH_ABBREVIATIONS[month_name]
                break
        return result

    # Handle "DD Mon YYYY" format
    dmY_match = re.match(
        r"^(\d{1,2})\s+([A-Za-z]+)\s+(1[0-9]{3}|20[0-2][0-9])$", date_str, re.IGNORECASE
    )
    if dmY_match:
        result["day"] = dmY_match.group(1)
        month_str = dmY_match.group(2).lower()
        result["year"] = dmY_match.group(3)
        if month_str in MONTH_NUMBERS:
            result["month_num"] = MONTH_NUMBERS[month_str]
            result["month"] = MONTH_ABBREVIATIONS.get(
                month_str, dmY_match.group(2).title()
            )
        return result

    # Handle "Mon DD, YYYY" format
    mdY_match = re.match(
        r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(1[0-9]{3}|20[0-2][0-9])$",
        date_str,
        re.IGNORECASE,
    )
    if mdY_match:
        month_str = mdY_match.group(1).lower()
        result["day"] = mdY_match.group(2)
        result["year"] = mdY_match.group(3)
        if month_str in MONTH_NUMBERS:
            result["month_num"] = MONTH_NUMBERS[month_str]
            result["month"] = MONTH_ABBREVIATIONS.get(
                month_str, mdY_match.group(1).title()
            )
        return result

    # Handle slash format (MM/DD/YYYY or DD/MM/YYYY)
    # Try US first, if first number > 12 assume it's day (international)
    slash_match = re.match(r"^(\d{1,2})/(\d{1,2})/(1[0-9]{3}|20[0-2][0-9])$", date_str)
    if slash_match:
        first_num = int(slash_match.group(1))
        second_num = int(slash_match.group(2))

        if first_num > 12:
            # Must be DD/MM/YYYY (international)
            result["day"] = str(first_num).zfill(2)
            result["month_num"] = second_num
            result["year"] = slash_match.group(3)
        elif second_num > 12:
            # Must be MM/DD/YYYY (US)
            result["month_num"] = first_num
            result["day"] = str(second_num)
            result["year"] = slash_match.group(3)
        else:
            # Ambiguous - assume US (common in GEDCOM)
            result["month_num"] = first_num
            result["day"] = str(second_num)
            result["year"] = slash_match.group(3)

        month_num = result["month_num"]
        for month_name, month_num_val in MONTH_NUMBERS.items():
            if month_num_val == month_num and month_name in MONTH_ABBREVIATIONS:
                result["month"] = MONTH_ABBREVIATIONS[month_name]
                break
        return result

    # Try to extract just the month from the string
    month_lower = date_str.lower()
    for month_name, month_num in MONTH_NUMBERS.items():
        if month_lower.startswith(month_name):
            result["month_num"] = month_num
            result["month"] = MONTH_ABBREVIATIONS.get(month_name, month_name.title())
            break

    # Extract year if not already found
    if not result["year"]:
        year_match = re.search(r"\b(1[0-9]{3}|20[0-2][0-9])\b", date_str)
        if year_match:
            result["year"] = year_match.group(1)

    return result


def format_date(
    date_str: str,
    format_type: str = DateFormat.DA_MON_YEAR,
    year_only: bool = False,
    retain_leading_zeros: bool = False,
) -> str:
    """
    Format a date string into the specified format.

    Args:
        date_str: Original date string
        format_type: Output format - american, international, da_mon_year,
                     american_month, or international_month
        year_only: If True, return only the year
        retain_leading_zeros: If True, keep leading zeros (e.g., 01 Aug 1985)

    Returns:
        Formatted date string
    """
    if not date_str:
        return date_str

    parsed = parse_date(date_str)

    if not parsed["year"]:
        return date_str

    if year_only:
        return parsed["year"]

    # Handle partial dates - if no day, return month year format
    if not parsed["day"] and parsed["month"]:
        return f"{parsed['month']} {parsed['year']}"

    if not parsed["day"] and not parsed["month"]:
        return parsed["year"]

    if format_type == DateFormat.AMERICAN:
        month = parsed["month_num"] if parsed["month_num"] else 1
        day = int(parsed["day"]) if parsed["day"] else 1
        if retain_leading_zeros:
            month = str(month).zfill(2)
            day = str(day).zfill(2)
        else:
            month = str(month)
            day = str(day)
        return f"{month}/{day}/{parsed['year']}"

    elif format_type == DateFormat.INTERNATIONAL:
        day = int(parsed["day"]) if parsed["day"] else 1
        month = parsed["month_num"] if parsed["month_num"] else 1
        if retain_leading_zeros:
            month = str(month).zfill(2)
            day = str(day).zfill(2)
        else:
            month = str(month)
            day = str(day)
        return f"{day}/{month}/{parsed['year']}"

    elif format_type == DateFormat.DA_MON_YEAR:
        day = parsed["day"] if parsed["day"] else "1"
        month = parsed["month"] if parsed["month"] else "Jan"
        if retain_leading_zeros and day:
            day = day.zfill(2)
        return f"{day} {month} {parsed['year']}"

    elif format_type == DateFormat.AMERICAN_MONTH:
        month = parsed["month"] if parsed["month"] else "Jan"
        day = parsed["day"] if parsed["day"] else "1"
        if retain_leading_zeros and day:
            day = day.zfill(2)
        return f"{month} {day} {parsed['year']}"

    elif format_type == DateFormat.INTERNATIONAL_MONTH:
        day = parsed["day"] if parsed["day"] else "1"
        month = parsed["month"] if parsed["month"] else "Jan"
        if retain_leading_zeros and day:
            day = day.zfill(2)
        return f"{day} {month} {parsed['year']}"

    return date_str


def format_date_from_settings(
    date_str: str,
    settings: dict,
    year_only: bool = False,
) -> str:
    """
    Format a date string using settings from the generator.

    Args:
        date_str: Original date string
        settings: Dictionary with settings like:
            - date_format: "american", "international", or "da_mon_year"
            - date_retain_leading_zeros: bool
        year_only: If True, return only the year (overrides format)

    Returns:
        Formatted date string
    """
    if not date_str:
        return date_str

    format_type = settings.get("date_format", DateFormat.DA_MON_YEAR)
    retain_leading_zeros = settings.get("date_retain_leading_zeros", False)

    return format_date(date_str, format_type, year_only, retain_leading_zeros)


def get_year(date_str: str) -> str:
    """
    Extract just the year from a date string.

    Args:
        date_str: Original date string

    Returns:
        Year as string, or original string if no year found
    """
    if not date_str:
        return date_str

    parsed = parse_date(date_str)
    if parsed["year"]:
        return parsed["year"]

    return date_str
