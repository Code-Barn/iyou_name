"""
Place name utilities for formatting and abbreviating location data.

Provides functions to parse, abbreviate, and format place names
for better display in family tree charts.
"""

import re
from typing import Optional


# Mapping of full country names to abbreviations
COUNTRY_ABBREVIATIONS = {
    "united states of america": "USA",
    "united states": "USA",
    "us": "USA",
    "u.s.": "USA",
    "u.s.a.": "USA",
    "united kingdom": "UK",
    "great britain": "GB",
}

# Country name to flag emoji mapping
COUNTRY_FLAGS = {
    "usa": "🇺🇸",
    "us": "🇺🇸",
    "united states": "🇺🇸",
    "united states of america": "🇺🇸",
    "u.s.": "🇺🇸",
    "u.s.a.": "🇺🇸",
    "uk": "🇬🇧",
    "united kingdom": "🇬🇧",
    "great britain": "🇬🇧",
    "gb": "🇬🇧",
    "england": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    "canada": "🇨🇦",
    "australia": "🇦🇺",
    "germany": "🇩🇪",
    "france": "🇫🇷",
    "italy": "🇮🇹",
    "spain": "🇪🇸",
    "mexico": "🇲🇽",
    "ireland": "🇮🇪",
    "netherlands": "🇳🇱",
    "belgium": "🇧🇪",
    "switzerland": "🇨🇭",
    "austria": "🇦🇹",
    "poland": "🇵🇱",
    "sweden": "🇸🇪",
    "norway": "🇳🇴",
    "denmark": "🇩🇰",
    "finland": "🇫🇮",
    "portugal": "🇵🇹",
    "brazil": "🇧🇷",
    "argentina": "🇦🇷",
    "japan": "🇯🇵",
    "china": "🇨🇳",
    "india": "🇮🇳",
    "russia": "🇷🇺",
    "south africa": "🇿🇦",
    "new zealand": "🇳🇿",
}

# Country name to ISO 3166-1 alpha-2 country code mapping
COUNTRY_CODES = {
    "usa": "us",
    "us": "us",
    "united states": "us",
    "united states of america": "us",
    "u.s.": "us",
    "u.s.a.": "us",
    "uk": "gb",
    "united kingdom": "gb",
    "great britain": "gb",
    "gb": "gb",
    "england": "gb-eng",
    "scotland": "gb-sct",
    "wales": "gb-wls",
    "northern ireland": "gb-nir",
    "canada": "ca",
    "australia": "au",
    "germany": "de",
    "france": "fr",
    "italy": "it",
    "spain": "es",
    "mexico": "mx",
    "ireland": "ie",
    "netherlands": "nl",
    "belgium": "be",
    "switzerland": "ch",
    "austria": "at",
    "poland": "pl",
    "sweden": "se",
    "norway": "no",
    "denmark": "dk",
    "finland": "fi",
    "portugal": "pt",
    "brazil": "br",
    "argentina": "ar",
    "japan": "jp",
    "china": "cn",
    "india": "in",
    "russia": "ru",
    "south africa": "za",
    "new zealand": "nz",
}

# Mapping of full US state names to abbreviations
US_STATE_ABBREVIATIONS = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
    "district of columbia": "DC",
}

# Canadian province abbreviations
CANADA_PROVINCE_ABBREVIATIONS = {
    "alberta": "AB",
    "british columbia": "BC",
    "manitoba": "MB",
    "new brunswick": "NB",
    "newfoundland": "NL",
    "nova scotia": "NS",
    "ontario": "ON",
    "prince edward island": "PE",
    "quebec": "QC",
    "saskatchewan": "SK",
}

# Combine all state/province abbreviations (full name -> abbreviation)
STATE_ABBREVIATIONS = {
    **US_STATE_ABBREVIATIONS,
    **CANADA_PROVINCE_ABBREVIATIONS,
}

# Create reverse lookup: abbreviation -> abbreviation (for parsing already-abbreviated places)
# e.g., "il" -> "IL", "ca" -> "CA"
STATE_ABBREVIATIONS_REVERSE = {v.lower(): v for v in STATE_ABBREVIATIONS.values()}
# Merge into main dict for lookup
STATE_ABBREVIATIONS = {**STATE_ABBREVIATIONS, **STATE_ABBREVIATIONS_REVERSE}


def parse_place(place: str) -> dict:
    """
    Parse a comma-separated place name into components.

    For American places: town, county, state, country (4 parts) or town, county, state (3 parts)
    The parts before the state are treated as town + county.

    Returns:
        Dictionary with keys: city, county, township, state, country, parts_count
    """
    if not place:
        return {
            "city": "",
            "county": "",
            "township": "",
            "state": "",
            "country": "",
            "other": "",
            "parts_count": 0,
        }

    parts = [p.strip() for p in place.split(",")]
    parts_count = len(parts)

    result = {
        "city": "",
        "county": "",
        "township": "",
        "state": "",
        "country": "",
        "other": "",
        "parts_count": parts_count,
    }

    if parts_count == 0:
        return result

    def is_explicit_county(part: str) -> bool:
        part_lower = part.lower()
        # Check for various county markers
        return (
            "county" in part_lower
            or "co." in part_lower
            or part_lower.endswith(", co")
            or part_lower.endswith(" co")
        )

    def is_explicit_township(part: str) -> bool:
        part_lower = part.lower()
        # Check for various township markers - be lenient since GEDCOM varies
        # Includes: township, twp, twp., ward (treated similarly)
        return (
            "township" in part_lower
            or part_lower.endswith(" twp")
            or part_lower.endswith(" twp.")
            or ", twp" in part_lower
            or "ward" in part_lower
        )

    known_countries = set(COUNTRY_ABBREVIATIONS.keys()) | {
        "usa",
        "us",
        "u.s.",
        "u.s.a.",
        "uk",
        "gb",
        "great britain",
        "united states",
        "united states of america",
        "canada",
        "australia",
        "germany",
        "france",
        "italy",
        "spain",
        "mexico",
        "ireland",
        "scotland",
        "wales",
        "england",
    }

    # Find country
    last_lower = parts[-1].lower().strip()
    has_country = last_lower in known_countries

    if has_country:
        result["country"] = parts[-1]
        parts = parts[:-1]
        parts_count = len(parts)

    # Find state
    if parts_count >= 1:
        last_lower = parts[-1].lower().strip()
        if last_lower in STATE_ABBREVIATIONS:
            result["state"] = parts[-1]
            parts = parts[:-1]
            parts_count = len(parts)

    # Now we have remaining parts - these are town/county
    # For American style: first part is town, second is county (if 2 parts after removing state/country)
    if parts_count >= 2:
        # Check for explicit township first
        if is_explicit_township(parts[-1]):
            result["township"] = parts[-1]
            parts = parts[:-1]
            parts_count = len(parts)

        # Check for explicit county marker
        if is_explicit_county(parts[-1]):
            result["county"] = parts[-1]
            parts = parts[:-1]
        elif parts_count >= 2:
            # US pattern with 2 parts remaining: town, county
            # The SECOND part (parts[-1]) is the county, FIRST is town
            # This applies to: town, county, state (3 parts) or town, county, state, country (4 parts)
            result["county"] = parts[-1]
            parts = parts[:-1]

        # What remains is city/town
        if len(parts) >= 1:
            result["city"] = ", ".join(parts) if len(parts) > 1 else parts[0]
    elif parts_count == 1:
        # Single part remaining - could be city or county
        if is_explicit_county(parts[0]):
            result["county"] = parts[0]
        elif is_explicit_township(parts[0]):
            result["township"] = parts[0]
        else:
            result["city"] = parts[0]

    return result


def abbreviate_country(country: str) -> str:
    """
    Abbreviate country name if known.

    Args:
        country: Full country name

    Returns:
        Abbreviated country name or original if not recognized
    """
    if not country:
        return country

    country_lower = country.lower().strip()
    return COUNTRY_ABBREVIATIONS.get(country_lower, country)


def abbreviate_state(state: str) -> str:
    """
    Abbreviate state/province name if known.

    Args:
        state: Full state or province name

    Returns:
        Abbreviated state name or original if not recognized
    """
    if not state:
        return state

    state_lower = state.lower().strip()
    return STATE_ABBREVIATIONS.get(state_lower, state)


def format_place(
    place: str,
    use_country_abbrev: bool = False,
    use_state_abbrev: bool = False,
    show_county: bool = True,
    show_township: bool = True,
    show_country: bool = True,
    hide_usa_with_state: bool = True,
    country_first: bool = False,
) -> str:
    """
    Format a place name based on settings.

    Args:
        place: Original place string (comma-separated)
        use_country_abbrev: Abbreviate country name (USA, UK, etc.)
        use_state_abbrev: Abbreviate state/province to 2-letter code
        show_county: Include county in output (only if detected as county)
        show_township: Include township in output (only if detected as township)
        show_country: Include country in output
        hide_usa_with_state: Hide "USA" when a US state is present
        country_first: Put country before other parts

    Returns:
        Formatted place string
    """
    if not place:
        return place

    parsed = parse_place(place)

    # Check hide_usa_with_state BEFORE abbreviating (need original state name)
    should_show_country = show_country
    if hide_usa_with_state and show_country:
        country_lower = parsed["country"].lower() if parsed["country"] else ""
        if country_lower in [
            "usa",
            "us",
            "u.s.",
            "u.s.a.",
            "united states",
            "united states of america",
        ]:
            if parsed["state"]:
                state_lower = parsed["state"].lower().strip()
                if state_lower in STATE_ABBREVIATIONS:
                    should_show_country = False

    # Apply abbreviations
    if use_country_abbrev and parsed["country"]:
        parsed["country"] = abbreviate_country(parsed["country"])

    if use_state_abbrev and parsed["state"]:
        parsed["state"] = abbreviate_state(parsed["state"])

    # Filter out county/township parts based on settings (handles unusual GEDCOM formats)
    # This catches cases where county/township aren't properly parsed into their fields
    original_parts = [p.strip() for p in place.split(",")]
    filtered_parts = []

    for part in original_parts:
        part_lower = part.lower()
        is_county = (
            "county" in part_lower
            or part_lower.endswith(", co")
            or part_lower.endswith(" co")
            or part_lower.endswith(" co.")
        )
        is_township = (
            "township" in part_lower or "twp" in part_lower or "ward" in part_lower
        )

        # Include part unless it's a county/township we're hiding
        if is_county and not show_county:
            continue
        if is_township and not show_township:
            continue
        filtered_parts.append(part)

    # Rebuild parsed from filtered parts (for "other" field)
    # Then rebuild output parts based on settings
    parts = []

    # Clean up county suffix for display (only if showing)
    display_county = ""
    if show_county and parsed["county"]:
        county = parsed["county"]
        county_lower = county.lower()
        if county_lower.endswith(" county"):
            display_county = county[:-7].strip()
        elif county_lower.endswith(", county"):
            display_county = county[:-9].strip()
        else:
            display_county = county

    # Clean up township suffix for display (only if showing)
    display_township = ""
    if show_township and parsed["township"]:
        township = parsed["township"]
        township_lower = township.lower()
        if township_lower.endswith(" township"):
            display_township = township[:-9].strip()
        elif township_lower.endswith(", township"):
            display_township = township[:-11].strip()
        elif township_lower.endswith(" twp"):
            display_township = township[:-4].strip()
        elif township_lower.endswith(" twp."):
            display_township = township[:-5].strip()
        else:
            display_township = township

    # Always order: town, county, state, country (for US places) or town, state, country (for non-US)
    # County goes after state so it can be hidden
    if show_county:
        # Order: town, township, county, state, country
        if country_first and should_show_country and parsed["country"]:
            parts.append(parsed["country"])

        if parsed["city"]:
            parts.append(parsed["city"])

        if show_township and display_township:
            parts.append(display_township)

        # County goes after state (for US: town, county, state, USA)
        if display_county:
            parts.append(display_county)

        if parsed["state"]:
            parts.append(parsed["state"])

        if not country_first and should_show_country and parsed["country"]:
            parts.append(parsed["country"])
    else:
        # Order when county hidden: town, township, state, country
        if country_first and should_show_country and parsed["country"]:
            parts.append(parsed["country"])

        if parsed["city"]:
            parts.append(parsed["city"])

        if show_township and display_township:
            parts.append(display_township)

        if parsed["state"]:
            parts.append(parsed["state"])

        if not country_first and should_show_country and parsed["country"]:
            parts.append(parsed["country"])

    if parsed["other"]:
        parts.append(parsed["other"])

    # Remove duplicate parts (case-insensitive) - handles GEDCOM data issues
    seen = set()
    unique_parts = []
    for part in parts:
        part_normalized = part.lower().strip()
        if part_normalized not in seen:
            seen.add(part_normalized)
            unique_parts.append(part)
    parts = unique_parts

    return ", ".join(parts)


def get_place_short(
    place: str,
    max_parts: int = 2,
) -> str:
    """
    Get a shortened version of place name.

    Args:
        place: Original place string
        max_parts: Maximum number of parts to include (from the end)

    Returns:
        Shortened place string (e.g., "Illinois, USA")
    """
    if not place:
        return place

    parts = [p.strip() for p in place.split(",")]
    if len(parts) <= max_parts:
        return place

    # Take the last max_parts
    return ", ".join(parts[-max_parts:])


def format_place_from_settings(place: str, settings: dict, flag: str = "") -> str:
    """
    Format a place name using settings from the generator.

    Args:
        place: Original place string
        settings: Dictionary with settings like:
            - place_use_country_abbrev: bool
            - place_use_state_abbrev: bool
            - place_show_county: bool
            - place_show_township: bool
            - place_show_country: bool
            - place_hide_usa_with_state: bool
            - place_country_first: bool
        flag: Optional flag emoji to append to place

    Returns:
        Formatted place string
    """
    if not place:
        return place

    formatted = format_place(
        place,
        use_country_abbrev=settings.get("place_use_country_abbrev", False),
        use_state_abbrev=settings.get("place_use_state_abbrev", False),
        show_county=settings.get("place_show_county", True),
        show_township=settings.get("place_show_township", True),
        show_country=settings.get("place_show_country", True),
        hide_usa_with_state=settings.get("place_hide_usa_with_state", True),
        country_first=settings.get("place_country_first", False),
    )

    if flag:
        formatted = f"{formatted} {flag}"

    return formatted


def get_flag_from_place(place: str) -> str:
    """
    Extract country flag emoji from a place string.

    Args:
        place: Place string (e.g., "Chicago, Illinois, USA")

    Returns:
        Flag emoji if country detected, empty string otherwise
    """
    if not place:
        return ""

    parsed = parse_place(place)
    country = parsed.get("country", "")

    if not country:
        return ""

    country_lower = country.lower().strip()
    return COUNTRY_FLAGS.get(country_lower, "")


def get_flag_image_path(place: str) -> str:
    """
    Get the flag image path for a place string.

    Args:
        place: Place string (e.g., "Chicago, Illinois, USA")

    Returns:
        Relative path to flag image (e.g., "charts/images/flags/us.png") if country detected, empty string otherwise
    """
    if not place:
        return ""

    parsed = parse_place(place)
    country = parsed.get("country", "")

    if not country:
        return ""

    country_lower = country.lower().strip()
    country_code = COUNTRY_CODES.get(country_lower)

    if not country_code:
        return ""

    return f"charts/images/flags/{country_code}.png"
