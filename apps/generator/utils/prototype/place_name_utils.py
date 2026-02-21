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

    Args:
        place: Place string (e.g., "Chicago,Cook County,Illinois,USA")

    Returns:
        Dictionary with keys: city, county, state, country
        Parts not matching known patterns go into 'other'

    County detection: Only treats a part as county if it explicitly
    contains "County" or "Co." - otherwise treated as city/town.

    Special American patterns:
    - 4 parts with state+USA at end: town, county, state, country
    - 3 parts with state at end: town, county, state
    """
    if not place:
        return {"city": "", "county": "", "state": "", "country": "", "other": ""}

    # Split by comma and clean up whitespace
    parts = [p.strip() for p in place.split(",")]

    result = {
        "city": "",
        "county": "",
        "state": "",
        "country": "",
        "other": "",
    }

    if len(parts) == 0:
        return result

    # Helper to check if a part explicitly indicates a county
    def is_explicit_county(part: str) -> bool:
        part_lower = part.lower()
        return "county" in part_lower or "co." in part_lower

    # Known countries (for quick lookup)
    known_countries = set(COUNTRY_ABBREVIATIONS.keys()) | {
        "usa",
        "us",
        "u.s.",
        "u.s.a.",
        "uk",
        "gb",
        "great britain",
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
        # Add US states that might appear as country
        "united states",
        "united states of america",
    }

    # Work from the end backwards to identify components

    # Step 1: Check last part - could be country or state
    last_lower = parts[-1].lower().strip()

    if last_lower in known_countries:
        # Last part is country
        result["country"] = parts[-1]
        remaining = parts[:-1]
    else:
        # No country - last part might be state or city
        remaining = parts[:]

    # Step 2: Check what's now last (remaining[-1]) - could be state
    if len(remaining) >= 1:
        last_remaining_lower = remaining[-1].lower().strip()
        if last_remaining_lower in STATE_ABBREVIATIONS:
            result["state"] = remaining[-1]
            remaining = remaining[:-1]

    # Step 3: Check for explicit county (only if it has "County" or "Co.")
    if len(remaining) >= 1:
        if is_explicit_county(remaining[-1]):
            result["county"] = remaining[-1]
            remaining = remaining[:-1]

    # Step 4: Whatever's left is city (or other)
    if len(remaining) >= 1:
        # Last remaining is city
        result["city"] = remaining[-1]
        if len(remaining) > 1:
            # Anything before city goes to other
            result["other"] = ", ".join(remaining[:-1])

    return result

    # Helper to check if a part explicitly indicates a county
    def is_explicit_county(part: str) -> bool:
        part_lower = part.lower()
        return "county" in part_lower or "co." in part_lower

    # Work from the end backwards to identify components

    # Step 1: Check last part - could be country or state
    last_lower = parts[-1].lower().strip()

    # Known countries
    known_countries = set(COUNTRY_ABBREVIATIONS.keys()) | {
        "usa",
        "us",
        "u.s.",
        "u.s.a.",
        "uk",
        "gb",
        "great britain",
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

    if last_lower in known_countries:
        # Last part is country
        result["country"] = parts[-1]
        remaining = parts[:-1]
    else:
        # No country - last part might be state or city
        remaining = parts

    # Step 2: Check what's now last - could be state or city
    if len(remaining) >= 1:
        second_last_lower = remaining[-1].lower().strip()
        if second_last_lower in STATE_ABBREVIATIONS:
            result["state"] = remaining[-1]
            remaining = remaining[:-1]

    # Step 3: Check for explicit county (only if it has "County" or "Co.")
    if len(remaining) >= 1:
        if is_explicit_county(remaining[-1]):
            result["county"] = remaining[-1]
            remaining = remaining[:-1]

    # Step 4: Whatever's left is city (or other)
    if len(remaining) >= 1:
        # Last remaining is city
        result["city"] = remaining[-1]
        if len(remaining) > 1:
            # Anything before city goes to other
            result["other"] = ", ".join(remaining[:-1])

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
        show_country: Include country in output
        hide_usa_with_state: Hide "USA" when a US state is present
        country_first: Put country before other parts

    Returns:
        Formatted place string
    """
    if not place:
        return place

    parsed = parse_place(place)

    # Apply abbreviations
    if use_country_abbrev and parsed["country"]:
        parsed["country"] = abbreviate_country(parsed["country"])

    if use_state_abbrev and parsed["state"]:
        parsed["state"] = abbreviate_state(parsed["state"])

    # Determine if we should show country
    should_show_country = show_country

    # If hide_usa_with_state is enabled, check if we have a US state
    if hide_usa_with_state and show_country:
        country_lower = parsed["country"].lower() if parsed["country"] else ""
        # Check if country is USA and we have a US state
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
                # Check if it's a US state (not Canadian province)
                if state_lower in US_STATE_ABBREVIATIONS:
                    should_show_country = False

    # Build output parts based on settings
    parts = []

    if country_first and should_show_country and parsed["country"]:
        parts.append(parsed["country"])

    if parsed["city"]:
        parts.append(parsed["city"])

    if show_county and parsed["county"]:
        # Clean up county suffix for display
        county = parsed["county"]
        county_lower = county.lower()
        if county_lower.endswith(" county"):
            county = county[:-7].strip()
        elif county_lower.endswith(", county"):
            county = county[:-9].strip()
        parts.append(county)

    if parsed["state"]:
        parts.append(parsed["state"])

    if not country_first and should_show_country and parsed["country"]:
        parts.append(parsed["country"])

    if parsed["other"]:
        parts.append(parsed["other"])

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


def format_place_from_settings(place: str, settings: dict) -> str:
    """
    Format a place name using settings from the generator.

    Args:
        place: Original place string
        settings: Dictionary with settings like:
            - place_use_country_abbrev: bool
            - place_use_state_abbrev: bool
            - place_show_county: bool
            - place_show_country: bool
            - place_hide_usa_with_state: bool
            - place_country_first: bool

    Returns:
        Formatted place string
    """
    if not place:
        return place

    return format_place(
        place,
        use_country_abbrev=settings.get("place_use_country_abbrev", False),
        use_state_abbrev=settings.get("place_use_state_abbrev", False),
        show_county=settings.get("place_show_county", True),
        show_country=settings.get("place_show_country", True),
        hide_usa_with_state=settings.get("place_hide_usa_with_state", True),
        country_first=settings.get("place_country_first", False),
    )
