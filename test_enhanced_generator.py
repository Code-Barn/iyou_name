#!/usr/bin/env python3
"""
Test script for enhanced 1-generation generator.

This script provides curl commands and test instructions for validating
the enhanced generator functionality.
"""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def print_test_instructions():
    """Print testing instructions and curl commands."""

    print("=" * 80)
    print("🧪 ENHANCED 1-GENERATION GENERATOR TEST INSTRUCTIONS")
    print("=" * 80)

    print("\n📋 TEST PREREQUISITES:")
    print("1. Make sure Django development server is running:")
    print("   python manage.py runserver")
    print("2. Have a GEDCOM file loaded and processed")
    print("3. Know the individual_id and file_id for testing")

    print("\n🔍 TEST ENDPOINTS CREATED:")
    print("1. Enhanced Generator Test:")
    print("   /hud/test-enhanced-1gen-preview/")
    print("2. Comparison Test (Enhanced vs Original):")
    print("   /hud/test-enhanced-1gen-comparison/")

    print("\n📝 CURL COMMANDS FOR TESTING:")

    print("\n1️⃣  TEST ENHANCED GENERATOR (GET):")
    print('curl -X GET "http://127.0.0.1:8000/hud/test-enhanced-1gen-preview/" \\')
    print('  -G -d "individual_id=I1" -d "file_id=1" \\')
    print("  --output enhanced_test.png")
    print("  # This will generate an image using the enhanced generator")

    print("\n2️⃣  TEST ENHANCED GENERATOR (POST):")
    print('curl -X POST "http://127.0.0.1:8000/hud/test-enhanced-1gen-preview/" \\')
    print('  -H "Content-Type: application/json" \\')
    print(
        '  -d \'{"individual_id": "I1", "file_id": 1, "user_settings": {"font_family": "Arial", "primary_name_font_size": 84}}\' \\'
    )
    print("  --output enhanced_test_post.png")

    print("\n3️⃣  COMPARISON TEST (Enhanced vs Original):")
    print('curl -X GET "http://127.0.0.1:8000/hud/test-enhanced-1gen-comparison/" \\')
    print('  -G -d "individual_id=I1" -d "file_id=1"')
    print("  # This returns JSON comparison data")

    print("\n4️⃣  TEST ORIGINAL GENERATOR (for comparison):")
    print('curl -X GET "http://127.0.0.1:8000/hud/get-1gen-preview/" \\')
    print('  -G -d "individual_id=I1" -d "t=0" \\')
    print("  --output original_test.png")

    print("\n🔧 THINGS TO TEST:")
    print("✅ Settings validation (try invalid values)")
    print("✅ Buffer management (check for memory leaks)")
    print("✅ Error handling (try missing individual/file)")
    print("✅ Logging output (check Django logs)")
    print("✅ Image quality (compare enhanced vs original)")

    print("\n🐛 COMMON ISSUES & SOLUTIONS:")
    print("❌ 'individual_id is required' -> Add individual_id and file_id parameters")
    print("❌ 'GEDCOM file not found' -> Check file_id and ensure file is processed")
    print("❌ 'Individual not found' -> Verify individual_id exists in the GEDCOM")
    print("❌ Import errors -> Make sure all utility files are created")

    print("\n📊 EXPECTED BEHAVIOR:")
    print("✅ Enhanced generator should produce identical image to original")
    print("✅ Settings validation should catch invalid values and use defaults")
    print("✅ Logging should show clean, structured messages (no debug prints)")
    print("✅ Buffer operations should be safe and validated")
    print("✅ Error handling should provide meaningful error messages")

    print("\n📝 LOG MONITORING:")
    print("Watch Django logs for enhanced generator output:")
    print("tail -f /path/to/django.log | grep '1gen'")

    print("\n🎯 SUCCESS CRITERIA:")
    print("1. ✅ Enhanced generator produces valid PNG image")
    print("2. ✅ No debug print statements in logs")
    print("3. ✅ Proper error handling for edge cases")
    print("4. ✅ Settings validation works correctly")
    print("5. ✅ Performance is comparable to original")

    print("\n" + "=" * 80)
    print("🚀 READY TO TEST! Run the curl commands above.")
    print("=" * 80)


def test_imports():
    """Test that all enhanced modules can be imported successfully."""

    print("🔍 Testing imports...")

    try:
        from apps.generator.utils.settings_validator import (
            validate_setting,
            get_validated_settings,
            GenerationError,
        )

        print("✅ Settings validator imported successfully")
    except ImportError as e:
        print(f"❌ Settings validator import failed: {e}")
        return False

    try:
        from apps.generator.utils.buffer_manager import (
            create_preview_buffer,
            validate_buffer,
            BufferError,
        )

        print("✅ Buffer manager imported successfully")
    except ImportError as e:
        print(f"❌ Buffer manager import failed: {e}")
        return False

    try:
        from apps.generator.utils.image_1generator_enhanced import (
            generate_1gen_preview_enhanced,
            Generation1Constants,
        )

        print("✅ Enhanced generator imported successfully")
    except ImportError as e:
        print(f"❌ Enhanced generator import failed: {e}")
        return False

    print("✅ All imports successful!")
    return True


def run_quick_validation_test():
    """Run a quick validation test to verify the framework works."""

    print("\n🧪 Running quick validation test...")

    try:
        from apps.generator.utils.settings_validator import validate_setting

        # Test string validation
        result = validate_setting("Arial", str, "Times", "font_family")
        assert result == "Arial", f"Expected 'Arial', got '{result}'"
        print("✅ String validation works")

        # Test integer validation with conversion
        result = validate_setting("84.5", int, 72, "font_size")
        assert result == 84, f"Expected 84, got '{result}'"
        print("✅ Integer validation with conversion works")

        # Test fallback to default
        result = validate_setting(None, str, "Default", "test_setting")
        assert result == "Default", f"Expected 'Default', got '{result}'"
        print("✅ Default fallback works")

        # Test invalid value handling
        result = validate_setting("invalid", int, 42, "test_int")
        assert result == 42, f"Expected 42, got '{result}'"
        print("✅ Invalid value handling works")

        print("✅ All validation tests passed!")
        return True

    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Enhanced Generator Test Suite")
    print("=" * 50)

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check file paths and dependencies.")
        sys.exit(1)

    # Test validation
    if not run_quick_validation_test():
        print("\n❌ Validation tests failed. Please check the settings validator.")
        sys.exit(1)

    # Print instructions
    print_test_instructions()

    print("\n🎉 Test setup complete! You can now run the curl commands above.")
