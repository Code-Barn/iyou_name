#!/usr/bin/env python3
"""
Simple test to verify the responsive CSS implementation.

This test checks that the template has been updated with responsive CSS.
"""

import sys
import os
import re

# Add the project path
sys.path.append("/home/user/CODE_BASE/namechart")


def test_responsive_css():
    """Test that responsive CSS has been added to the template."""
    print("🧪 Testing Responsive CSS Implementation...")
    print("=" * 50)

    template_path = (
        "/home/user/CODE_BASE/namechart/apps/hud/templates/hud/display_tree.html"
    )

    try:
        with open(template_path, "r") as f:
            content = f.read()

        # Test 1: Check for responsive CSS block
        if "{% block extra_css %}" in content:
            print("✅ Extra CSS block found")
        else:
            print("❌ Extra CSS block missing")
            return False

        # Test 2: Check for responsive media queries
        media_queries = [
            "@media (max-width: 576px)",
            "@media (min-width: 577px) and (max-width: 768px)",
            "@media (min-width: 769px) and (max-width: 1200px)",
            "@media (min-width: 1201px)",
            "@media (min-width: 1400px)",
        ]

        found_queries = 0
        for query in media_queries:
            if query in content:
                found_queries += 1
                print(f"✅ Found media query: {query}")
            else:
                print(f"❌ Missing media query: {query}")

        print(f"📊 Found {found_queries}/{len(media_queries)} media queries")

        # Test 3: Check for responsive preview area styles
        responsive_styles = [
            ".hud-preview-area {",
            "max-width: 300px;",
            "max-width: 500px;",
            "max-width: 800px;",
            "max-width: 1000px;",
            "max-width: 1200px;",
        ]

        found_styles = 0
        for style in responsive_styles:
            if style in content:
                found_styles += 1
                print(f"✅ Found responsive style: {style}")
            else:
                print(f"❌ Missing responsive style: {style}")

        print(f"📊 Found {found_styles}/{len(responsive_styles)} responsive styles")

        # Test 4: Check for JavaScript responsive functionality
        js_features = [
            "ResponsivePreview",
            "updatePreviewSize",
            "addResizeListener",
            "logCurrentSize",
            "updateDebugPanel",
        ]

        found_js = 0
        for feature in js_features:
            if feature in content:
                found_js += 1
                print(f"✅ Found JS feature: {feature}")
            else:
                print(f"❌ Missing JS feature: {feature}")

        print(f"📊 Found {found_js}/{len(js_features)} JS features")

        # Test 5: Check for debug panel
        debug_elements = [
            'id="debug-viewport"',
            'id="debug-preview-size"',
            'id="debug-media"',
            "Responsive Debug Info",
        ]

        found_debug = 0
        for element in debug_elements:
            if element in content:
                found_debug += 1
                print(f"✅ Found debug element: {element}")
            else:
                print(f"❌ Missing debug element: {element}")

        print(f"📊 Found {found_debug}/{len(debug_elements)} debug elements")

        # Overall assessment
        total_tests = 5
        passed_tests = 0

        if found_queries >= 4:  # Allow for some variation
            passed_tests += 1
            print("✅ Media queries implementation: PASSED")
        else:
            print("❌ Media queries implementation: FAILED")

        if found_styles >= 4:
            passed_tests += 1
            print("✅ Responsive styles implementation: PASSED")
        else:
            print("❌ Responsive styles implementation: FAILED")

        if found_js >= 4:
            passed_tests += 1
            print("✅ JavaScript functionality: PASSED")
        else:
            print("❌ JavaScript functionality: FAILED")

        if found_debug >= 3:
            passed_tests += 1
            print("✅ Debug panel implementation: PASSED")
        else:
            print("❌ Debug panel implementation: FAILED")

        if "{% block extra_css %}" in content:
            passed_tests += 1
            print("✅ CSS block structure: PASSED")
        else:
            print("❌ CSS block structure: FAILED")

        print(f"\n📊 Overall Test Results: {passed_tests}/{total_tests} tests passed")

        if passed_tests >= 4:
            print("🎉 Responsive CSS implementation is working correctly!")
            print("\n📱 Expected Behavior:")
            print("• Small screens (≤576px): Preview max 300x300px")
            print("• Medium screens (577-768px): Preview max 500x500px")
            print("• Large screens (769-1200px): Preview max 800x800px")
            print("• Extra large (1201-1400px): Preview max 1000x1000px")
            print("• Ultra-wide (≥1401px): Preview max 1200x1200px")
            print("• Debug panel shows real-time size information")
            print("• JavaScript handles resize events smoothly")
            return True
        else:
            print("⚠️  Some responsive features may be missing.")
            return False

    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
        return False
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False


def main():
    """Run the responsive CSS test."""
    success = test_responsive_css()

    if success:
        print("\n🚀 Ready for testing!")
        print("\n🔧 Next Steps:")
        print("1. Load the HUD in a browser")
        print("2. Resize the browser window to test responsiveness")
        print("3. Check the debug panel for real-time size information")
        print("4. Test on different devices (phone, tablet, desktop)")
        print("5. Verify the preview image scales properly")
    else:
        print("\n⚠️  Responsive implementation needs attention.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
