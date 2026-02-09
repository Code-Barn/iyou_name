"""
Helper functions for managing user settings across different family tree generations.

This module provides utilities for extracting generation-specific settings
from the full user settings dictionary, with proper inheritance and defaults.
"""


def extract_generation_settings(user_settings, generation_prefix):
    """
    Extract generation-specific settings from full user_settings.

    Args:
        user_settings: Full user settings dictionary
        generation_prefix: Prefix for this generation ('PRIMARY', 'PARENT', 'GRANDPARENT', etc.)

    Returns:
        Dictionary with settings for this specific generation
    """
    if not user_settings:
        return {}

    gen_settings = {}
    prefix = f"{generation_prefix}_"

    # Extract generation-specific settings (e.g., PARENT_name_font_size -> name_font_size)
    for key, value in user_settings.items():
        if key.startswith(prefix):
            # Remove prefix and add to gen_settings
            clean_key = key[len(prefix) :]
            gen_settings[clean_key] = value

    # Add inherited base settings without prefixes
    base_inheritance_keys = [
        "font_family",
        "primary_background_color",
        "primary_stroke_color",
        "primary_font_color",
        "primary_birth_color",
        "primary_birth_place_color",
        "primary_death_color",
        "primary_death_place_color",
    ]

    for key in base_inheritance_keys:
        if key in user_settings and key not in gen_settings:
            gen_settings[key] = user_settings[key]

    return gen_settings


def get_default_settings(generation_prefix):
    """
    Get default settings for a specific generation if no user settings are provided.

    Args:
        generation_prefix: Prefix for this generation ('PRIMARY', 'PARENT', 'GRANDPARENT', etc.)

    Returns:
        Dictionary with default settings for this generation
    """
    # Base defaults that apply to all generations
    base_defaults = {
        "font_family": "Arial",
        "primary_background_color": "#FFFFFF",
        "primary_stroke_color": "#000000",
        "primary_font_color": "#000000",
        "primary_birth_color": "#000000",
        "primary_birth_place_color": "#000000",
        "primary_death_color": "#000000",
        "primary_death_place_color": "#000000",
        "default_stroke_width": 0.5,
    }

    # Generation-specific defaults
    generation_defaults = {
        "PRIMARY": {
            "primary_name_font_size": 84,
            "primary_date_info_font_size": 60,
            "primary_place_info_font_size": 28,
            "primary_translate_x": 0,
            "primary_translate_y": 0,
            "primary_name_rotate": -45,
            "primary_birth_translate_x": 0,
            "primary_birth_translate_y": 0,
            "primary_birth_rotate": -90,
            "primary_birth_place_translate_x": 0,
            "primary_birth_place_translate_y": 0,
            "primary_birth_place_rotate": 0,
            "primary_death_translate_x": 0,
            "primary_death_translate_y": 0,
            "primary_death_rotate": 0,
            "primary_death_place_translate_x": 0,
            "primary_death_place_translate_y": 0,
            "primary_death_place_rotate": -90,
        },
        "PARENT": {
            "primary_name_font_size": 60,  # Smaller for parent generation
            "primary_date_info_font_size": 48,
            "primary_place_info_font_size": 24,
            "primary_translate_x": 0,
            "primary_translate_y": 0,
            "primary_name_rotate": -45,
            "primary_birth_translate_x": 0,
            "primary_birth_translate_y": 0,
            "primary_birth_rotate": -90,
            "primary_birth_place_translate_x": 0,
            "primary_birth_place_translate_y": 0,
            "primary_birth_place_rotate": 0,
            "primary_death_translate_x": 0,
            "primary_death_translate_y": 0,
            "primary_death_rotate": 0,
            "primary_death_place_translate_x": 0,
            "primary_death_place_translate_y": 0,
            "primary_death_place_rotate": -90,
        },
        "GRANDPARENT": {
            "primary_name_font_size": 48,  # Even smaller for grandparent generation
            "primary_date_info_font_size": 36,
            "primary_place_info_font_size": 18,
            "primary_translate_x": 0,
            "primary_translate_y": 0,
            "primary_name_rotate": -45,
            "primary_birth_translate_x": 0,
            "primary_birth_translate_y": 0,
            "primary_birth_rotate": -90,
            "primary_birth_place_translate_x": 0,
            "primary_birth_place_translate_y": 0,
            "primary_birth_place_rotate": 0,
            "primary_death_translate_x": 0,
            "primary_death_translate_y": 0,
            "primary_death_rotate": 0,
            "primary_death_place_translate_x": 0,
            "primary_death_place_translate_y": 0,
            "primary_death_place_rotate": -90,
        },
    }

    # Combine base defaults with generation-specific defaults
    defaults = base_defaults.copy()
    if generation_prefix in generation_defaults:
        defaults.update(generation_defaults[generation_prefix])

    return defaults
