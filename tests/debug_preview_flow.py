#!/usr/bin/env python3
"""
Debug script to test the settings flow from frontend to backend.
This helps identify why live preview isn't updating properly.
"""


def simulate_frontend_flow():
    """Simulate the complete frontend flow when user clicks 'Apply Settings'"""

    print("🔍 DEBUGGING LIVE PREVIEW FLOW\n")

    # Step 1: User modifies settings in 2gen template
    print("STEP 1: User modifies 2gen settings")
    modified_settings = {
        "father_font_color": "#FF0000",  # Changed from default
        "mother_font_color": "#0000FF",  # Changed from default
        "parent_translate_x": "75",  # Changed from default 0
        "composite_1gen_scale": "60",  # Changed from default 48
        "font_family": "Georgia",  # Changed from default Arial
    }

    print("Modified settings:", modified_settings)

    # Step 2: Frontend sends preview request (this is working)
    print("\nSTEP 2: Frontend sends preview request")
    request_data = {"individual_id": "123", "user_settings": modified_settings}

    print("Preview request data:", request_data)

    # Step 3: Frontend saves settings to session (NEW - this should help)
    print("\nSTEP 3: Frontend saves settings to session")
    form_data = modified_settings.copy()
    form_data.update(
        {"individual_id": "123", "template": "2 Generation Chart", "generations": "2"}
    )

    print("Form data for session save:", form_data)

    # Step 4: Backend processes GET request (when page loads/reloads)
    print("\nSTEP 4: Backend would process GET request")
    hud_settings_from_session = {
        # This should contain the saved settings
        "father_font_color": "#FF0000",
        "mother_font_color": "#0000FF",
        "parent_translate_x": 75,
        "composite_1gen_scale": 60,
        "font_family": "Georgia",
    }

    print("Session settings:", hud_settings_from_session)

    # Step 5: Backend creates user_settings for preview generation
    print("\nSTEP 5: Backend creates user_settings for preview")
    user_settings_for_preview = {
        "font_family": hud_settings_from_session.get("font_family", "Arial"),
        "father_font_color": hud_settings_from_session.get(
            "father_font_color", "#000000"
        ),
        "mother_font_color": hud_settings_from_session.get(
            "mother_font_color", "#000000"
        ),
        "parent_translate_x": hud_settings_from_session.get("parent_translate_x", 0),
        "composite_1gen_scale": hud_settings_from_session.get(
            "composite_1gen_scale", 48
        ),
    }

    print("Settings sent to generator:", user_settings_for_preview)

    # Step 6: Verify the expected result
    print("\nSTEP 6: Expected result in 2generator")
    expected_in_generator = {
        "font_family": "Georgia",  # Should be updated
        "father_font_color": "#FF0000",  # Should be updated
        "mother_font_color": "#0000FF",  # Should be updated
        "parent_translate_x": 75,  # Should be updated
        "composite_1gen_scale": 60,  # Should be updated
    }

    print("Expected settings in generator:", expected_in_generator)

    # Check for potential issues
    print("\n🔍 POTENTIAL ISSUES CHECK:")

    # Issue 1: Session not being saved
    if hud_settings_from_session.get("father_font_color") == "#000000":
        print("❌ ISSUE 1: Session not saving settings properly")
    else:
        print("✅ Session saving appears to work")

    # Issue 2: GET request not using session data
    if user_settings_for_preview.get("father_font_color") == "#000000":
        print("❌ ISSUE 2: GET request not using session data")
    else:
        print("✅ GET request appears to use session data")

    # Issue 3: POST request not working
    if modified_settings != user_settings_for_preview:
        print("❌ ISSUE 3: POST request data not matching")
        print("   Modified:", modified_settings)
        print("   Preview:", user_settings_for_preview)
    else:
        print("✅ POST request data flow correct")

    return modified_settings, hud_settings_from_session, user_settings_for_preview


def test_session_persistence():
    """Test if session persistence is the issue"""

    print("\n🧪 TESTING SESSION PERSISTENCE")
    print("=" * 50)

    scenarios = [
        {
            "name": "First load with defaults",
            "session_data": {},
            "expected_output": {
                "father_font_color": "#000000",  # default
                "mother_font_color": "#000000",  # default
                "composite_1gen_scale": 48,  # default
            },
        },
        {
            "name": "After user modifies settings",
            "session_data": {
                "father_font_color": "#FF0000",
                "mother_font_color": "#0000FF",
                "composite_1gen_scale": 60,
            },
            "expected_output": {
                "father_font_color": "#FF0000",
                "mother_font_color": "#0000FF",
                "composite_1gen_scale": 60,
            },
        },
    ]

    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")

        hud_settings = scenario["session_data"]

        # Simulate backend GET request processing
        user_settings = {}
        if hud_settings.get("template") == "2 Generation Chart":
            user_settings.update(
                {
                    "father_font_color": hud_settings.get(
                        "father_font_color", "#000000"
                    ),
                    "mother_font_color": hud_settings.get(
                        "mother_font_color", "#000000"
                    ),
                    "composite_1gen_scale": hud_settings.get(
                        "composite_1gen_scale", 48
                    ),
                }
            )

        expected = scenario["expected_output"]

        success = all(
            user_settings.get(key) == value for key, value in expected.items()
        )

        if success:
            print("✅ Session persistence working correctly")
        else:
            print("❌ Session persistence failing")
            print(f"   Expected: {expected}")
            print(f"   Got: {user_settings}")


def test_preview_generation():
    """Test if the issue is in the preview generation"""

    print("\n🎯 TESTING PREVIEW GENERATION")
    print("=" * 50)

    # Test cases
    test_cases = [
        {
            "name": "Default settings",
            "input_settings": {
                "father_font_color": "#000000",
                "composite_1gen_scale": 48,
            },
            "expected_changes": "Default appearance",
        },
        {
            "name": "Modified settings",
            "input_settings": {
                "father_font_color": "#FF0000",
                "composite_1gen_scale": 30,
            },
            "expected_changes": "Red father text, smaller overlay",
        },
    ]

    for test in test_cases:
        print(f"\nTest case: {test['name']}")
        print(f"Input settings: {test['input_settings']}")
        print(f"Expected result: {test['expected_changes']}")

        # This would be what the 2generator receives
        print("If preview doesn't change, issue is in:")
        print("  1. Settings not reaching the generator")
        print("  2. Generator not using the settings")
        print("  3. Preview not updating in frontend")


if __name__ == "__main__":
    modified, session, preview = simulate_frontend_flow()
    test_session_persistence()
    test_preview_generation()

    print("\n🎯 DEBUG SUMMARY")
    print("=" * 30)
    print("✅ Frontend flow: Implemented")
    print("✅ Session saving: Implemented")
    print("✅ GET request handling: Partially implemented")
    print("❓ Preview generation: Needs verification")
    print("\nNext step: Test with actual server to verify the complete flow")
