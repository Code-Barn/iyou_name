#!/usr/bin/env python3
"""
Multi-Generation System Troubleshooting Script

Run this script to diagnose common issues with the multi-generation
family tree image generation system.

Usage: python troubleshoot_multigen.py
"""

import sys
import os
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "namechart.settings")

import django

django.setup()

from apps.generator.utils.settings_helper import (
    extract_generation_settings,
    get_default_settings,
)
from apps.generator.template_mapping import get_template_mapping
from apps.parser.models import PersonData


def test_settings_helper():
    """Test the settings helper functionality."""
    print("🔧 Testing Settings Helper...")

    try:
        # Test extraction
        user_settings = {
            "PRIMARY_name_font_size": 84,
            "PARENT_name_font_size": 60,
            "font_family": "Arial",
            "primary_background_color": "#FFFFFF",
        }

        primary_settings = extract_generation_settings(user_settings, "PRIMARY")
        parent_settings = extract_generation_settings(user_settings, "PARENT")

        print(f"✅ PRIMARY settings extracted: {len(primary_settings)} settings")
        print(f"✅ PARENT settings extracted: {len(parent_settings)} settings")

        # Test defaults
        primary_defaults = get_default_settings("PRIMARY")
        parent_defaults = get_default_settings("PARENT")

        print(f"✅ PRIMARY defaults loaded: {len(primary_defaults)} defaults")
        print(f"✅ PARENT defaults loaded: {len(parent_defaults)} defaults")

        return True

    except Exception as e:
        print(f"❌ Settings Helper Error: {e}")
        traceback.print_exc()
        return False


def test_template_mapping():
    """Test the template mapping configuration."""
    print("\n🗺️ Testing Template Mapping...")

    try:
        mapping = get_template_mapping()

        print(f"✅ Template mapping loaded: {len(mapping)} templates")

        for template_id, config in mapping.items():
            required_keys = ["module", "function", "name"]
            missing_keys = [key for key in required_keys if key not in config]

            if missing_keys:
                print(f"❌ Template {template_id} missing keys: {missing_keys}")
                return False
            else:
                print(f"✅ Template {template_id}: {config['name']}")

        return True

    except Exception as e:
        print(f"❌ Template Mapping Error: {e}")
        traceback.print_exc()
        return False


def test_person_data():
    """Test PersonData model functionality."""
    print("\n👤 Testing PersonData Model...")

    try:
        # Create test PersonData
        person = PersonData(
            id="I1",
            full_name="John Doe",
            given_name="John",
            surname="Doe",
            birth_date="1950-01-01",
            birth_place="Anytown, USA",
            father="I2",
            mother="I3",
        )

        print(f"✅ PersonData created: {person.full_name}")
        print(f"✅ Father ID: {person.father}")
        print(f"✅ Mother ID: {person.mother}")

        # Test to_dict conversion
        person_dict = person.to_dict()
        print(f"✅ PersonData to_dict: {len(person_dict)} fields")

        return True

    except Exception as e:
        print(f"❌ PersonData Error: {e}")
        traceback.print_exc()
        return False


def test_generator_imports():
    """Test that all generators can be imported."""
    print("\n📦 Testing Generator Imports...")

    try:
        from apps.generator.utils import image_1generator
        from apps.generator.utils import image_2generator

        print("✅ image_1generator imported")
        print("✅ image_2generator imported")

        # Test that required functions exist
        assert hasattr(image_1generator, "generate_1gen_preview")
        assert hasattr(image_2generator, "generate_2gen_preview")

        print("✅ Required generator functions found")

        return True

    except Exception as e:
        print(f"❌ Generator Import Error: {e}")
        traceback.print_exc()
        return False


def test_buffer_handling():
    """Test BytesIO buffer handling."""
    print("\n💾 Testing Buffer Handling...")

    try:
        from io import BytesIO

        # Create test buffer
        test_data = b"fake_image_data"
        buffer = BytesIO(test_data)

        # Test buffer operations
        buffer.seek(0)
        read_data = buffer.read()

        assert read_data == test_data
        print("✅ Buffer read/write works")

        # Test buffer seek
        buffer.seek(0)
        assert buffer.tell() == 0
        print("✅ Buffer seek works")

        return True

    except Exception as e:
        print(f"❌ Buffer Handling Error: {e}")
        traceback.print_exc()
        return False


def check_file_structure():
    """Check that required files exist."""
    print("\n📁 Checking File Structure...")

    required_files = [
        "apps/generator/utils/settings_helper.py",
        "apps/generator/utils/image_1generator.py",
        "apps/generator/utils/image_2generator.py",
        "apps/generator/template_mapping.py",
        "apps/hud/views.py",
        "apps/hud/templates/hud/display_tree.html",
    ]

    missing_files = []

    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)

    return len(missing_files) == 0


def run_diagnostics():
    """Run all diagnostic tests."""
    print("🔍 Multi-Generation System Diagnostics")
    print("=" * 50)

    tests = [
        ("File Structure", check_file_structure),
        ("Settings Helper", test_settings_helper),
        ("Template Mapping", test_template_mapping),
        ("PersonData Model", test_person_data),
        ("Generator Imports", test_generator_imports),
        ("Buffer Handling", test_buffer_handling),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)

    passed = 0
    failed = 0

    for test_name, result in results:
        if result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            failed += 1

    print(f"\n📈 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All diagnostics passed! System is ready.")
    else:
        print("⚠️  Some issues found. Check the errors above.")

    return failed == 0


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Multi-Generation System Troubleshooting Script")
        print("\nUsage:")
        print("  python troubleshoot_multigen.py          # Run all diagnostics")
        print("  python troubleshoot_multigen.py --help   # Show this help")
        return

    success = run_diagnostics()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
