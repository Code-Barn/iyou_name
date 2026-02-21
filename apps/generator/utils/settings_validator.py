"""
Settings validation utilities for family tree generators.

This module provides a standardized framework for validating and converting
user settings across all generation-specific image generators, with proper
error handling, logging, and fallback defaults.
"""

import logging
from typing import Any, Type, Union, Optional
from wand.color import Color

logger = logging.getLogger(__name__)


class GenerationError(Exception):
    """Custom exception for generation-related errors."""

    pass


def validate_setting(
    value: Any, expected_type: Type, default: Any, setting_name: str = "unknown"
) -> Any:
    """
    Validate and convert user setting with proper fallback and logging.

    Args:
        value: The raw value from user settings
        expected_type: The expected type (str, int, float, Color, etc.)
        default: Fallback value if validation fails
        setting_name: Name of the setting for logging purposes

    Returns:
        Validated and converted setting value

    Examples:
        >>> validate_setting("12.5", float, 10.0, "stroke_width")
        12.5
        >>> validate_setting("invalid", float, 10.0, "stroke_width")
        10.0  # with warning logged
        >>> validate_setting(None, str, "Arial", "font_family")
        "Arial"
    """
    # Handle None values
    if value is None:
        logger.debug(f"Setting '{setting_name}' is None, using default: {default}")
        return default

    # Handle values already of correct type
    if isinstance(value, expected_type):
        logger.debug(f"Setting '{setting_name}' already correct type: {value}")
        return value

    # Try to convert to expected type
    try:
        if expected_type == str:
            converted_value = str(value)
        elif expected_type == int:
            converted_value = int(float(value))  # Handle "12.5" -> 12
        elif expected_type == float:
            converted_value = float(value)
        elif expected_type == Color:
            if isinstance(value, Color):
                converted_value = value
            else:
                converted_value = Color(str(value))
        elif expected_type == bool:
            if isinstance(value, str):
                converted_value = value.lower() in ("true", "1", "yes", "on")
            else:
                converted_value = bool(value)
        else:
            converted_value = expected_type(value)

        logger.debug(
            f"Setting '{setting_name}' converted: {value} -> {converted_value}"
        )
        return converted_value

    except (ValueError, TypeError, Exception) as e:
        logger.warning(
            f"Failed to convert setting '{setting_name}' "
            f"from {type(value).__name__}('{value}') to {expected_type.__name__}: {e}. "
            f"Using default: {default}"
        )
        return default


def validate_color_setting(
    value: Any, default: Union[str, Color], setting_name: str = "color"
) -> Color:
    """
    Specialized validator for color settings with enhanced error handling.

    Args:
        value: Raw color value (string, Color object, etc.)
        default: Default color value
        setting_name: Name of the color setting

    Returns:
        Validated Color object
    """
    if value is None:
        return Color(default) if isinstance(default, str) else default

    try:
        if isinstance(value, Color):
            return value
        else:
            return Color(str(value))
    except Exception as e:
        logger.warning(
            f"Invalid color value for '{setting_name}': {value}. Using default: {default}"
        )
        return Color(default) if isinstance(default, str) else default


def validate_coordinate_setting(
    value: Any,
    default: int,
    setting_name: str = "coordinate",
    allow_negative: bool = True,
) -> int:
    """
    Specialized validator for coordinate settings with bounds checking.

    Args:
        value: Raw coordinate value
        default: Default coordinate value
        setting_name: Name of the coordinate setting
        allow_negative: Whether negative coordinates are allowed

    Returns:
        Validated integer coordinate
    """
    validated = validate_setting(value, int, default, setting_name)

    # Additional coordinate validation
    if not allow_negative and validated < 0:
        logger.warning(
            f"Negative coordinate not allowed for '{setting_name}': {validated}. Using 0."
        )
        validated = 0

    # Reasonable bounds checking (canvas size limits)
    if abs(validated) > 10000:
        logger.warning(
            f"Coordinate '{setting_name}' seems too large: {validated}. Using default: {default}"
        )
        validated = default

    return validated


def validate_font_size_setting(
    value: Any, default: int, setting_name: str = "font_size"
) -> int:
    """
    Specialized validator for font size settings with practical bounds.

    Args:
        value: Raw font size value
        default: Default font size
        setting_name: Name of the font size setting

    Returns:
        Validated font size integer
    """
    validated = validate_setting(value, int, default, setting_name)

    # Practical font size bounds
    if validated < 6:
        logger.warning(
            f"Font size '{setting_name}' too small: {validated}. Using minimum: 6"
        )
        validated = 6
    elif validated > 500:
        logger.warning(
            f"Font size '{setting_name}' too large: {validated}. Using maximum: 500"
        )
        validated = 500

    return validated


def validate_rotation_setting(
    value: Any, default: int, setting_name: str = "rotation"
) -> int:
    """
    Specialized validator for rotation settings with angle normalization.

    Args:
        value: Raw rotation value
        default: Default rotation angle
        setting_name: Name of the rotation setting

    Returns:
        Validated rotation angle (0-360 or -180 to 180)
    """
    validated = validate_setting(value, int, default, setting_name)

    # Normalize rotation to reasonable range
    # Allow -360 to 360 for flexibility
    if validated < -360:
        logger.warning(
            f"Rotation '{setting_name}' too negative: {validated}. Normalizing."
        )
        validated = validated % 360
    elif validated > 360:
        logger.warning(
            f"Rotation '{setting_name}' too large: {validated}. Normalizing."
        )
        validated = validated % 360

    return validated


VALID_DATE_FORMATS = (
    "american",
    "international",
    "da_mon_year",
    "american_month",
    "international_month",
)


def validate_date_format_setting(
    value: Any, default: str = "da_mon_year", setting_name: str = "date_format"
) -> str:
    """
    Specialized validator for date format settings.

    Args:
        value: Raw date format value
        default: Default date format
        setting_name: Name of the date format setting

    Returns:
        Validated date format string
    """
    validated = validate_setting(value, str, default, setting_name)

    if validated not in VALID_DATE_FORMATS:
        logger.warning(
            f"Invalid date format '{validated}' for '{setting_name}'. "
            f"Valid options: {VALID_DATE_FORMATS}. Using default: {default}"
        )
        return default

    return validated


def get_validated_settings(
    user_settings: dict, settings_schema: dict, generator_name: str = "unknown"
) -> dict:
    """
    Validate a complete settings dictionary against a schema.

    Args:
        user_settings: Raw user settings dictionary
        settings_schema: Schema defining expected settings and their validators
        generator_name: Name of the generator for logging

    Returns:
        Dictionary of validated settings

    Example:
        >>> schema = {
        ...     "font_family": (str, "Arial"),
        ...     "primary_stroke_width": (float, 0.5),
        ...     "primary_font_color": (Color, "black"),
        ... }
        >>> validated = get_validated_settings(user_settings, schema, "1gen")
    """
    if not user_settings:
        user_settings = {}

    validated_settings = {}

    for setting_key, (expected_type, default_value) in settings_schema.items():
        # Choose appropriate validator based on setting name patterns
        if "color" in setting_key.lower():
            validated_value = validate_color_setting(
                user_settings.get(setting_key), default_value, setting_key
            )
        elif "coordinate" in setting_key.lower() or setting_key.endswith(("_x", "_y")):
            validated_value = validate_coordinate_setting(
                user_settings.get(setting_key), default_value, setting_key
            )
        elif "font_size" in setting_key.lower():
            validated_value = validate_font_size_setting(
                user_settings.get(setting_key), default_value, setting_key
            )
        elif "rotate" in setting_key.lower() or setting_key.endswith("_rotate"):
            validated_value = validate_rotation_setting(
                user_settings.get(setting_key), default_value, setting_key
            )
        elif setting_key == "date_format":
            validated_value = validate_date_format_setting(
                user_settings.get(setting_key), default_value, setting_key
            )
        else:
            validated_value = validate_setting(
                user_settings.get(setting_key),
                expected_type,
                default_value,
                setting_key,
            )

        validated_settings[setting_key] = validated_value

    logger.info(
        f"Validated {len(validated_settings)} settings for {generator_name} generator"
    )
    return validated_settings


def log_settings_summary(settings: dict, generator_name: str = "unknown") -> None:
    """
    Log a summary of validated settings for debugging.

    Args:
        settings: Validated settings dictionary
        generator_name: Name of the generator
    """
    logger.debug(f"Settings summary for {generator_name}:")
    for key, value in sorted(settings.items()):
        if isinstance(value, Color):
            logger.debug(f"  {key}: {value} (Color)")
        else:
            logger.debug(f"  {key}: {value} ({type(value).__name__})")
