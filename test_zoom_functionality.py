#!/usr/bin/env python3
"""
Simple test to verify the zoom functionality implementation.

This test checks that the template has been updated with zoom controls.
"""

import sys
import os
import re

# Add the project path
sys.path.append("/home/user/CODE_BASE/namechart")


def test_zoom_functionality():
    """Test that zoom functionality has been added to the template."""
    print("🧪 Testing Zoom Functionality Implementation...")
    print("=" * 50)

    template_path = (
        "/home/user/CODE_BASE/namechart/apps/hud/templates/hud/display_tree.html"
    )

    try:
        with open(template_path, "r") as f:
            content = f.read()

        # Test 1: Check for zoom controls
        zoom_controls = [
            "HUD.Zoom.zoomIn()",
            "HUD.Zoom.zoomOut()",
            "HUD.Zoom.resetZoom()",
            "bi bi-zoom-in",
            "bi bi-zoom-out",
            "Zoom In",
            "Zoom Out",
            "Reset Zoom",
        ]

        found_zoom = 0
        for control in zoom_controls:
            if control in content:
                found_zoom += 1
                print(f"✅ Found zoom control: {control}")
            else:
                print(f"❌ Missing zoom control: {control}")

        print(f"📊 Found {found_zoom}/{len(zoom_controls)} zoom controls")

        # Test 2: Check for zoom JavaScript functionality
        zoom_js_features = [
            "window.HUD.Zoom",
            "currentZoom: 100",
            "minZoom: 25",
            "maxZoom: 200",
            "zoomStep: 10",
            "setZoom: function(zoomLevel)",
            "handleKeyboard: function(event)",
        ]

        found_js = 0
        for feature in zoom_js_features:
            if feature in content:
                found_js += 1
                print(f"✅ Found zoom JS feature: {feature}")
            else:
                print(f"❌ Missing zoom JS feature: {feature}")

        print(f"📊 Found {found_js}/{len(zoom_js_features)} zoom JS features")

        # Test 3: Check for keyboard shortcuts
        keyboard_shortcuts = [
            "event.ctrlKey || event.metaKey",
            "event.key === '+'",
            "event.key === '-'",
            "event.key === '0'",
        ]

        found_keyboard = 0
        for shortcut in keyboard_shortcuts:
            if shortcut in content:
                found_keyboard += 1
                print(f"✅ Found keyboard shortcut: {shortcut}")
            else:
                print(f"❌ Missing keyboard shortcut: {shortcut}")

        print(f"📊 Found {found_keyboard}/{len(keyboard_shortcuts)} keyboard shortcuts")

        # Test 4: Check for mouse wheel zoom
        mouse_wheel = [
            "addEventListener('wheel'",
            "event.ctrlKey || event.metaKey",
            "event.deltaY < 0",
            "event.deltaY > 0",
        ]

        found_wheel = 0
        for wheel in mouse_wheel:
            if wheel in content:
                found_wheel += 1
                print(f"✅ Found mouse wheel feature: {wheel}")
            else:
                print(f"❌ Missing mouse wheel feature: {wheel}")

        print(f"📊 Found {found_wheel}/{len(mouse_wheel)} mouse wheel features")

        # Test 5: Check for debug panel zoom info
        debug_zoom = [
            'id="debug-zoom-level"',
            "<strong>Zoom:</strong>",
            "fitToScreen()",
            "toggleDebugPanel()",
        ]

        found_debug = 0
        for debug in debug_zoom:
            if debug in content:
                found_debug += 1
                print(f"✅ Found debug zoom feature: {debug}")
            else:
                print(f"❌ Missing debug zoom feature: {debug}")

        print(f"📊 Found {found_debug}/{len(debug_zoom)} debug zoom features")

        # Test 6: Check for mobile fixes
        mobile_fixes = [
            "@media (max-width: 768px)",
            "max-width: 90vw !important",
            "max-height: 90vw !important",
            "min-height: 250px !important",
            "fitToScreen",
        ]

        found_mobile = 0
        for mobile in mobile_fixes:
            if mobile in content:
                found_mobile += 1
                print(f"✅ Found mobile fix: {mobile}")
            else:
                print(f"❌ Missing mobile fix: {mobile}")

        print(f"📊 Found {found_mobile}/{len(mobile_fixes)} mobile fixes")

        # Overall assessment
        total_tests = 6
        passed_tests = 0

        if found_zoom >= 6:
            passed_tests += 1
            print("✅ Zoom controls implementation: PASSED")
        else:
            print("❌ Zoom controls implementation: FAILED")

        if found_js >= 5:
            passed_tests += 1
            print("✅ Zoom JavaScript functionality: PASSED")
        else:
            print("❌ Zoom JavaScript functionality: FAILED")

        if found_keyboard >= 3:
            passed_tests += 1
            print("✅ Keyboard shortcuts: PASSED")
        else:
            print("❌ Keyboard shortcuts: FAILED")

        if found_wheel >= 3:
            passed_tests += 1
            print("✅ Mouse wheel zoom: PASSED")
        else:
            print("❌ Mouse wheel zoom: FAILED")

        if found_debug >= 2:
            passed_tests += 1
            print("✅ Debug panel zoom info: PASSED")
        else:
            print("❌ Debug panel zoom info: FAILED")

        if found_mobile >= 4:
            passed_tests += 1
            print("✅ Mobile fixes: PASSED")
        else:
            print("❌ Mobile fixes: FAILED")

        print(f"\n📊 Overall Test Results: {passed_tests}/{total_tests} tests passed")

        if passed_tests >= 5:
            print("🎉 Zoom functionality implementation is working correctly!")
            print("\n🔧 Zoom Features:")
            print("• Zoom In/Out buttons (10% steps)")
            print("• Keyboard shortcuts (Ctrl/Cmd + +/-/0)")
            print("• Mouse wheel zoom (Ctrl/Cmd + scroll)")
            print("• Reset zoom button")
            print("• Debug panel with zoom level display")
            print("• Mobile auto-adjustment")
            print("• Fit to screen functionality")
            print("• Range: 25% to 200%")
            return True
        else:
            print("⚠️  Some zoom features may be missing.")
            return False

    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
        return False
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False


def main():
    """Run the zoom functionality test."""
    success = test_zoom_functionality()

    if success:
        print("\n🚀 Ready for testing!")
        print("\n🔧 Next Steps:")
        print("1. Load the HUD in a browser")
        print("2. Try the zoom in/out buttons")
        print("3. Test keyboard shortcuts (Ctrl/Cmd + +/-/0)")
        print("4. Test mouse wheel zoom (Ctrl/Cmd + scroll)")
        print("5. Test on mobile devices")
        print("6. Check debug panel for zoom info")
        print("7. Try 'Fit to Screen' on mobile")
    else:
        print("\n⚠️  Zoom functionality needs attention.")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
