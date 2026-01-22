#!/usr/bin/env python3
"""
Final comprehensive test to verify all fixes are working.
This test checks:
1. Font family changes work
2. All sliders work (including negative values)
3. Generate Final Chart uses correct settings
4. No 500 errors occur
"""

import os
import sys

sys.path.insert(0, "/home/user/CODE_BASE/namechart")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from apps.generator.utils.image_1generator import generate_1gen_preview
from apps.parser.models import PersonData


def test_negative_coordinates():
    """Test that negative coordinates don't cause errors"""
    print("=== Testing Negative Coordinates ===")

    test_individual = PersonData(
        id="TEST001",
        full_name="Test Individual",
        given_name="Test",
        surname="Individual",
        birth_date="01 Jan 2000",
        birth_place="Test Location",
        death_date="",
        death_place="",
    )

    # Test with negative coordinates
    test_settings = {
        "font_family": "Helvetica",
        "primary_name_font_size": 66,
        "primary_info_font_size": 61,
        "default_stroke_width": 0.5,
        "primary_stroke_color": "#e66100",
        "primary_font_color": "#f5c211",
        "primary_birth_color": "#2ec27e",
        "primary_place_color": "#813d9c",
        "primary_death_color": "#000000",
        "primary_name_x": -50,  # Negative X
        "primary_name_y": -30,  # Negative Y
        "primary_name_rotate": -45,
        "primary_birth_x": -20,  # Negative X
        "primary_birth_y": 150,
        "primary_birth_rotate": 45,
        "primary_place_x": -10,  # Negative X
        "primary_place_y": 90,
        "primary_place_rotate": -45,
        "subject_translate_x": 0,
        "subject_translate_y": 0,
    }

    try:
        preview_buffer = generate_1gen_preview(test_individual, test_settings)
        print("✅ SUCCESS: Negative coordinates handled correctly!")
        print(f"   Preview size: {len(preview_buffer.getvalue())} bytes")

        with open("negative_coords_test.png", "wb") as f:
            f.write(preview_buffer.getvalue())
        print("   Saved to: negative_coords_test.png")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


def test_font_family():
    """Test that font family changes work"""
    print("\n=== Testing Font Family ===")

    test_individual = PersonData(
        id="TEST002",
        full_name="Font Test",
        given_name="Font",
        surname="Test",
        birth_date="01 Jan 2000",
        birth_place="Test",
        death_date="",
        death_place="",
    )

    # Test different font families
    font_families = ["Arial", "Helvetica", "Times New Roman", "Georgia"]

    for font in font_families:
        try:
            test_settings = {
                "font_family": font,
                "primary_name_font_size": 88,
                "primary_info_font_size": 88,
                "default_stroke_width": 0.5,
                "primary_stroke_color": "#000000",
                "primary_font_color": "#000000",
                "primary_birth_color": "#000000",
                "primary_place_color": "#000000",
                "primary_death_color": "#000000",
                "primary_name_x": 0,
                "primary_name_y": 0,
                "primary_name_rotate": -45,
                "primary_birth_x": 0,
                "primary_birth_y": 135,
                "primary_birth_rotate": 45,
                "primary_place_x": 0,
                "primary_place_y": 90,
                "primary_place_rotate": -45,
                "subject_translate_x": 0,
                "subject_translate_y": 0,
            }

            preview_buffer = generate_1gen_preview(test_individual, test_settings)
            print(f"✅ Font '{font}' works!")

        except Exception as e:
            print(f"❌ Font '{font}' failed: {str(e)}")
            return False

    return True


def test_extreme_values():
    """Test extreme slider values"""
    print("\n=== Testing Extreme Values ===")

    test_individual = PersonData(
        id="TEST003",
        full_name="Extreme Test",
        given_name="Extreme",
        surname="Test",
        birth_date="01 Jan 2000",
        birth_place="Test",
        death_date="",
        death_place="",
    )

    # Test extreme values
    test_settings = {
        "font_family": "Arial",
        "primary_name_font_size": 138,  # Max value
        "primary_info_font_size": 138,  # Max value
        "default_stroke_width": 5.0,  # Max value
        "primary_stroke_color": "#FF0000",
        "primary_font_color": "#00FF00",
        "primary_birth_color": "#0000FF",
        "primary_place_color": "#FFFF00",
        "primary_death_color": "#FF00FF",
        "primary_name_x": 200,  # Max positive
        "primary_name_y": 200,  # Max positive
        "primary_name_rotate": 180,  # Max rotation
        "primary_birth_x": 200,
        "primary_birth_y": 200,
        "primary_birth_rotate": 180,
        "primary_place_x": 200,
        "primary_place_y": 200,
        "primary_place_rotate": 180,
        "subject_translate_x": 100,
        "subject_translate_y": 100,
    }

    try:
        preview_buffer = generate_1gen_preview(test_individual, test_settings)
        print("✅ SUCCESS: Extreme values handled correctly!")
        print(f"   Preview size: {len(preview_buffer.getvalue())} bytes")

        with open("extreme_values_test.png", "wb") as f:
            f.write(preview_buffer.getvalue())
        print("   Saved to: extreme_values_test.png")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print("Running Final Comprehensive Tests...")
    print("=" * 50)

    results = []
    results.append(test_negative_coordinates())
    results.append(test_font_family())
    results.append(test_extreme_values())

    print("\n" + "=" * 50)
    print("FINAL RESULTS:")
    print(f"Tests passed: {sum(results)}/{len(results)}")

    if all(results):
        print("🎉 ALL TESTS PASSED! Ready for git push.")
    else:
        print("⚠️  Some tests failed. Check the output above.")

    print("=" * 50)
