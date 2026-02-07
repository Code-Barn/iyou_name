"""
Unified HUD Settings Management System

This replaces all competing settings implementations with a single,
consistent approach for managing settings across all generations.
"""


def get_unified_settings(session_settings, generation=None):
    """
    Get settings for a specific generation with proper inheritance.

    Args:
        session_settings: Settings from request.session['hud_settings']
        generation: 'primary', 'parent', 'grandparent', or None for all

    Returns:
        Dictionary with settings for the requested generation
    """
    if not session_settings:
        session_settings = {}

    # Base settings (inherited by all generations)
    base_settings = {
        k: v
        for k, v in session_settings.items()
        if not k in ["primary", "parent", "grandparent"]
    }

    if generation is None:
        # Return all settings organized by generation
        return {
            "base": base_settings,
            "primary": session_settings.get("primary", {}),
            "parent": session_settings.get("parent", {}),
            "grandparent": session_settings.get("grandparent", {}),
        }

    # Return settings for specific generation with inheritance
    generation_settings = session_settings.get(generation, {})

    # Merge base settings with generation-specific settings
    # Generation settings take precedence
    return {**base_settings, **generation_settings}


def categorize_setting(key, value):
    """
    Categorize a setting based on its key name.

    Args:
        key: Setting key name (e.g., 'primary_font_color')
        value: Setting value

    Returns:
        Tuple of (category, clean_key, value)
    """
    # Remove common prefixes and categorize
    if key.startswith("primary_"):
        return "primary", key.replace("primary_", ""), value
    elif key.startswith("parent_"):
        return "parent", key.replace("parent_", ""), value
    elif key.startswith("father_") or key.startswith("mother_"):
        # Parent-specific settings (father_font_color, mother_font_color)
        return "parent", key.replace("father_", "").replace("mother_", ""), value
    elif key.startswith("grandparent_"):
        return "grandparent", key.replace("grandparent_", ""), value
    elif key.startswith("paternal_") or key.startswith("maternal_"):
        # Grandparent-specific settings
        return (
            "grandparent",
            key.replace("paternal_", "").replace("maternal_", ""),
            value,
        )
    else:
        # Base settings (font_family, default_stroke_width, etc.)
        return "base", key, value


def flatten_settings(settings_dict):
    """
    Flatten nested settings dict to flat structure for forms.

    Args:
        settings_dict: Nested settings from get_unified_settings

    Returns:
        Flat dictionary with prefixed keys
    """
    flat_settings = {}

    # Add base settings (no prefix)
    for key, value in settings_dict.get("base", {}).items():
        flat_settings[key] = value

    # Add generation settings with prefixes
    for generation in ["primary", "parent", "grandparent"]:
        gen_settings = settings_dict.get(generation, {})
        for key, value in gen_settings.items():
            flat_settings[f"{generation}_{key}"] = value

    return flat_settings


def get_default_settings():
    """
    Get default settings for all generations.

    Returns:
        Dictionary with default settings organized by generation
    """
    return {
        "base": {
            "font_family": "Arial",
            "default_stroke_width": 0.5,
        },
        "primary": {
            "name_font_size": 84,
            "date_info_font_size": 60,
            "place_info_font_size": 28,
            "font_color": "#000000",
            "background_color": "#FFFFFF",
            "stroke_color": "#000000",
            "birth_color": "#000000",
            "birth_place_color": "#000000",
            "death_color": "#000000",
            "death_place_color": "#000000",
            "translate_x": 0,
            "translate_y": 0,
            "name_rotate": -45,
            "birth_translate_x": 0,
            "birth_translate_y": 0,
            "birth_rotate": -90,
            "birth_place_translate_x": 0,
            "birth_place_translate_y": 0,
            "birth_place_rotate": 0,
            "death_translate_x": 0,
            "death_translate_y": 0,
            "death_rotate": 0,
            "death_place_translate_x": 0,
            "death_place_translate_y": 0,
            "death_place_rotate": -90,
        },
        "parent": {
            "name_font_size": 72,
            "date_info_font_size": 48,
            "place_info_font_size": 24,
            "font_color": "#000000",
            "stroke_color": "#000000",
            "birth_color": "#000000",
            "birth_place_color": "#000000",
            "death_color": "#000000",
            "death_place_color": "#000000",
            "translate_x": 0,
            "translate_y": 0,
            "name_rotate": -45,
            "birth_translate_x": 0,
            "birth_translate_y": 0,
            "birth_rotate": -90,
            "birth_place_translate_x": 0,
            "birth_place_translate_y": 0,
            "birth_place_rotate": 0,
            "death_translate_x": 0,
            "death_translate_y": 0,
            "death_rotate": 0,
            "death_place_translate_x": 0,
            "death_place_translate_y": 0,
            "death_place_rotate": -90,
        },
        "grandparent": {
            "name_font_size": 60,
            "date_info_font_size": 36,
            "place_info_font_size": 18,
            "font_color": "#000000",
            "stroke_color": "#000000",
            "birth_color": "#000000",
            "birth_place_color": "#000000",
            "death_color": "#000000",
            "death_place_color": "#000000",
            "translate_x": 0,
            "translate_y": 0,
            "name_rotate": -45,
            "birth_translate_x": 0,
            "birth_translate_y": 0,
            "birth_rotate": -90,
            "birth_place_translate_x": 0,
            "birth_place_translate_y": 0,
            "birth_place_rotate": 0,
            "death_translate_x": 0,
            "death_translate_y": 0,
            "death_rotate": 0,
            "death_place_translate_x": 0,
            "death_place_translate_y": 0,
            "death_place_rotate": -90,
        },
    }
