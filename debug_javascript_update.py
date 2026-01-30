#!/usr/bin/env python
"""
Debug script to test if the JavaScript form update is working correctly.
This simulates what should happen when the user clicks "Apply Settings".
"""

import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from apps.generator.models import GedcomFile

print("=== DEBUGGING JAVASCRIPT FORM UPDATE ===")
print("Testing if the JavaScript form update logic would work...")
print()

# Create a test client
client = Client()

# Set up session with a GEDCOM file
try:
    test_file = GedcomFile.objects.create(
        file="test.ged",
        user=None,
        home_person_id="I1",
        is_processed=True,
        last_activity="2023-01-01T00:00:00Z",
        parsed_data={
            "individuals": {
                "I1": {
                    "id": "I1",
                    "given_name": "John",
                    "surname": "Doe",
                    "full_name": "John Doe",
                    "birth_date": "01 JAN 1900",
                    "birth_place": "New York",
                    "death_date": "01 JAN 1980",
                    "death_place": "California",
                    "sex": "M"
                }
            },
            "families": {}
        }
    )
    
    print(f"✓ Created test GEDCOM file with ID: {test_file.id}")
    
except Exception as e:
    print(f"✗ Failed to create test GEDCOM file: {e}")
    test_file = GedcomFile.objects.first()
    if test_file:
        print(f"✓ Using existing GEDCOM file with ID: {test_file.id}")
    else:
        print("✗ No GEDCOM files available for testing")
        sys.exit(1)

# Set up session
session = client.session
session['current_gedcom_file_id'] = test_file.id
session['hud_settings'] = {
    'font_family': 'Arial',
    'primary_name_font_size': 84,  # Default values
    'primary_date_info_font_size': 60,
    'primary_place_info_font_size': 28,
    'default_stroke_width': 0.5,
    'primary_background_color': '#FFFFFF',
    'primary_stroke_color': '#000000',
    'primary_font_color': '#000000',
    'primary_birth_color': '#000000',
    'primary_birth_place_color': '#000000',
    'primary_death_color': '#000000',
    'primary_death_place_color': '#000000',
    'primary_name_x': 0,
    'primary_name_y': 0,
    'primary_name_rotate': -45,
    'primary_birth_x': 0,
    'primary_birth_y': 0,
    'primary_birth_rotate': -90,
    'primary_birth_place_x': 0,
    'primary_birth_place_y': 0,
    'primary_birth_place_rotate': 0,
    'primary_death_x': 0,
    'primary_death_y': 0,
    'primary_death_rotate': 0,
    'primary_death_place_x': 0,
    'primary_death_place_y': 0,
    'primary_death_place_rotate': -90,
    'subject_translate_x': 0,
    'subject_translate_y': 0,
    'template': '1'
}
session.save()

print("✓ Session set up with default settings")
print()

# Test 1: Request with default settings (simulates initial page load)
print("1. Testing with default settings (initial state)...")
try:
    response = client.post('/generator/generate/', {
        'individual_id': 'I1',
        'template': '1',
        'font_family': 'Arial',
        'primary_name_font_size': 84,
        'primary_date_info_font_size': 60,
        'primary_place_info_font_size': 28,
        'default_stroke_width': 0.5,
        'primary_background_color': '#FFFFFF',
        'primary_stroke_color': '#000000',
        'primary_font_color': '#000000',
        'primary_birth_color': '#000000',
        'primary_birth_place_color': '#000000',
        'primary_death_color': '#000000',
        'primary_death_place_color': '#000000',
        'primary_name_x': 0,
        'primary_name_y': 0,
        'primary_name_rotate': -45,
        'primary_birth_x': 0,
        'primary_birth_y': 0,
        'primary_birth_rotate': -90,
        'primary_birth_place_x': 0,
        'primary_birth_place_y': 0,
        'primary_birth_place_rotate': 0,
        'primary_death_x': 0,
        'primary_death_y': 0,
        'primary_death_rotate': 0,
        'primary_death_place_x': 0,
        'primary_death_place_y': 0,
        'primary_death_place_rotate': -90,
        'subject_translate_x': 0,
        'subject_translate_y': 0
    })
    
    if response.status_code == 200:
        with open('debug_default_settings.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Saved debug_default_settings.pdf (should show default settings)")
    else:
        print(f"✗ Request failed with status: {response.status_code}")
        print(f"Response: {response.content}")
        
except Exception as e:
    print(f"✗ Request failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Request with updated settings (simulates what should happen after JavaScript update)
print("2. Testing with updated settings (after JavaScript update)...")
try:
    response = client.post('/generator/generate/', {
        'individual_id': 'I1',
        'template': '1',
        # These are the OBVIOUS settings that should be applied by JavaScript
        'font_family': 'Arial',
        'primary_name_font_size': 200,  # OBVIOUS
        'primary_date_info_font_size': 150,  # OBVIOUS
        'primary_place_info_font_size': 100,  # OBVIOUS
        'default_stroke_width': 5.0,  # OBVIOUS
        'primary_background_color': '#FF00FF',  # OBVIOUS
        'primary_stroke_color': '#00FF00',  # OBVIOUS
        'primary_font_color': '#FF0000',  # OBVIOUS
        'primary_birth_color': '#0000FF',  # OBVIOUS
        'primary_birth_place_color': '#FFFF00',  # OBVIOUS
        'primary_death_color': '#FF00FF',  # OBVIOUS
        'primary_death_place_color': '#00FFFF',  # OBVIOUS
        'primary_name_x': 500,  # OBVIOUS
        'primary_name_y': 500,  # OBVIOUS
        'primary_name_rotate': 0,  # OBVIOUS
        'primary_birth_x': 600,
        'primary_birth_y': 600,
        'primary_birth_rotate': 0,
        'primary_birth_place_x': 700,
        'primary_birth_place_y': 700,
        'primary_birth_place_rotate': 0,
        'primary_death_x': 800,
        'primary_death_y': 800,
        'primary_death_rotate': 0,
        'primary_death_place_x': 900,
        'primary_death_place_y': 900,
        'primary_death_place_rotate': 0,
        'subject_translate_x': 100,
        'subject_translate_y': 100
    })
    
    if response.status_code == 200:
        with open('debug_updated_settings.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Saved debug_updated_settings.pdf (should show OBVIOUS settings)")
    else:
        print(f"✗ Request failed with status: {response.status_code}")
        print(f"Response: {response.content}")
        
except Exception as e:
    print(f"✗ Request failed: {e}")
    import traceback
    traceback.print_exc()

print()
print("=== ANALYSIS ===")
print("1. Open debug_default_settings.pdf")
print("   - Should show default settings (small text, white background, etc.)")
print()
print("2. Open debug_updated_settings.pdf")
print("   - Should show OBVIOUS settings (huge text, pink background, etc.)")
print()
print("3. If both look the same:")
print("   - The JavaScript form update is not working")
print("   - Check browser console for JavaScript errors")
print("   - Verify the JavaScript code is executing")
print()
print("4. If they look different:")
print("   - The JavaScript form update SHOULD work")
print("   - The issue might be elsewhere (JavaScript not executing, etc.)")
print()
print("5. To test JavaScript execution:")
print("   - Open browser console (F12)")
print("   - Go to /hud/display-tree/")
print("   - Change some settings and click 'Apply Settings'")
print("   - Check console for 'Updating final chart form with current settings...' message")
print("   - If you don't see this message, the JavaScript is not executing")