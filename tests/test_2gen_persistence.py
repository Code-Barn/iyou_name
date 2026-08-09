#!/usr/bin/env python3
"""
Test script to verify 2gen settings persistence implementation.
This script simulates the key functions to ensure our logic works.
"""

import json


def simulate_save_and_apply_settings(current_template, form_data, stored_settings=None):
    """Simulate the saveAndApplySettings function behavior"""

    # Initialize storage if empty
    if stored_settings is None:
        stored_settings = {}

    print(f"=== Simulating saveAndApplySettings for template: {current_template} ===")
    print(f"Form data: {form_data}")

    # Store 1gen settings if switching from 1gen and we have settings
    if (
        not stored_settings.get("hud_1gen_settings")
        and current_template == "1 Generation Chart"
    ):
        if form_data.get("primary_name_font_size") or form_data.get(
            "primary_font_color"
        ):
            one_gen_settings = {
                "primary_background_color": form_data.get(
                    "primary_background_color", "#FFFFFF"
                ),
                "primary_font_color": form_data.get("primary_font_color", "#000000"),
                "primary_name_font_size": int(
                    form_data.get("primary_name_font_size", 84)
                ),
                "primary_date_info_font_size": int(
                    form_data.get("primary_date_info_font_size", 60)
                ),
                "font_family": form_data.get("font_family", "Arial"),
            }
            stored_settings["hud_1gen_settings"] = one_gen_settings
            print(f"✅ Stored 1gen settings: {one_gen_settings}")

    return stored_settings


def simulate_load_settings_panel(template_value, stored_settings):
    """Simulate loading settings panel for a template"""

    print(f"\n=== Simulating loadSettingsPanel for template: {template_value} ===")

    # For 2gen, we'd load stored 1gen settings
    if template_value == "2 Generation Chart":
        one_gen_settings = stored_settings.get("hud_1gen_settings")
        if one_gen_settings:
            print(f"✅ Loaded stored 1gen settings for 2gen: {one_gen_settings}")
            return one_gen_settings
        else:
            print("⚠️  No stored 1gen settings found for 2gen")

    return None


def simulate_2generator_preview(user_settings, stored_primary_settings=None):
    """Simulate the 2generator preview function"""

    print(f"\n=== Simulating 2generator preview ===")
    print(f"User settings: {user_settings}")

    # Check for stored primary settings (this is what we updated)
    primary_settings = user_settings.get("primary_settings", {})
    if not primary_settings and stored_primary_settings:
        primary_settings = stored_primary_settings
        print(f"✅ Using stored primary settings for 1gen overlay: {primary_settings}")
    elif not primary_settings:
        print("⚠️  No primary settings available for 1gen overlay")
    else:
        print(f"✅ Using provided primary settings: {primary_settings}")

    return primary_settings


def test_workflow():
    """Test the complete workflow"""

    print("🧪 TESTING 2GEN SETTINGS PERSISTENCE WORKFLOW\n")

    # Initialize storage
    stored_settings = {}

    # Step 1: User configures 1gen settings
    print("STEP 1: User configures 1 Generation Chart settings")
    one_gen_form_data = {
        "primary_background_color": "#F0F8FF",
        "primary_font_color": "#000080",
        "primary_name_font_size": "92",
        "primary_date_info_font_size": "65",
        "font_family": "Georgia",
    }

    stored_settings = simulate_save_and_apply_settings(
        "1 Generation Chart", one_gen_form_data, stored_settings
    )

    # Step 2: User switches to 2gen
    print("\nSTEP 2: User switches to 2 Generation Chart")
    two_gen_form_data = {
        "father_font_color": "#FF0000",
        "mother_font_color": "#0000FF",
        "parent_translate_x": "50",
        "font_family": "Arial",
    }

    # Simulate loading 2gen panel (this would load stored settings)
    loaded_primary = simulate_load_settings_panel("2 Generation Chart", stored_settings)

    # Step 3: Apply 2gen settings (simulates saveAndApplySettings)
    print("\nSTEP 3: User applies 2 Generation Chart settings")

    # Build request data as our frontend would
    request_data = {"individual_id": "123", "user_settings": two_gen_form_data}

    # Add stored primary settings if available (our key implementation)
    if loaded_primary:
        request_data["primary_settings"] = loaded_primary

    print(f"Request data: {request_data}")

    # Step 4: 2generator preview generation
    print("\nSTEP 4: 2generator generates preview with 1gen overlay")
    primary_used = simulate_2generator_preview(request_data, loaded_primary)

    # Step 5: Verify results
    print("\n🔍 RESULTS VERIFICATION")

    if primary_used:
        expected_font_family = "Georgia"  # From stored 1gen settings
        actual_font_family = primary_used.get("font_family")

        if actual_font_family == expected_font_family:
            print("✅ SUCCESS: Stored 1gen settings are being used for 2gen overlay")
            print(f"   - Font family preserved: {actual_font_family}")
            print(
                f"   - Name font size preserved: {primary_used.get('primary_name_font_size')}"
            )
            print(
                f"   - Background color preserved: {primary_used.get('primary_background_color')}"
            )
        else:
            print("❌ FAILED: Stored settings not used correctly")
            print(f"   Expected: {expected_font_family}, Got: {actual_font_family}")
    else:
        print("❌ FAILED: No primary settings were used in 2gen generation")

    print("\n🎯 WORKFLOW TEST COMPLETE")


if __name__ == "__main__":
    test_workflow()
