#!/usr/bin/env python
"""
Debug script to test the actual request flow and see what settings are being received
by the generate_final_chart view.
"""

import sys
import os
import django
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from apps.generator.views import generate_final_chart
from apps.generator.models import GedcomFile
from apps.parser.models import PersonData

print("=== DEBUGGING REQUEST FLOW ===")
print("Testing what happens when generate_final_chart receives a request...")
print()

# Create a test client
client = Client()

# First, we need to set up a session with a GEDCOM file
# Let's create a mock GEDCOM file in the database
try:
    # Create a test GEDCOM file
    test_file = GedcomFile.objects.create(
        file="test.ged",
        user=None,
        home_person_id="I1",
        is_processed=True,
        last_activity="2023-01-01T00:00:00Z"
    )
    
    # Set up parsed data
    test_file.parsed_data = {
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
    test_file.save()
    
    print(f"✓ Created test GEDCOM file with ID: {test_file.id}")
    
except Exception as e:
    print(f"✗ Failed to create test GEDCOM file: {e}")
    # Try to get an existing file instead
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
    'primary_name_font_size': 200,  # OBVIOUS setting
    'primary_date_info_font_size': 150,  # OBVIOUS setting
    'primary_place_info_font_size': 100,  # OBVIOUS setting
    'default_stroke_width': 5.0,  # OBVIOUS setting
    'primary_background_color': '#FF00FF',  # OBVIOUS setting
    'primary_stroke_color': '#00FF00',  # OBVIOUS setting
    'primary_font_color': '#FF0000',  # OBVIOUS setting
    'primary_birth_color': '#0000FF',  # OBVIOUS setting
    'primary_birth_place_color': '#FFFF00',  # OBVIOUS setting
    'primary_death_color': '#FF00FF',  # OBVIOUS setting
    'primary_death_place_color': '#00FFFF',  # OBVIOUS setting
    'primary_name_x': 500,  # OBVIOUS setting
    'primary_name_y': 500,  # OBVIOUS setting
    'primary_name_rotate': 0,  # OBVIOUS setting
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
    'subject_translate_y': 100,
    'template': '1'
}
session.save()

print("✓ Session set up with OBVIOUS settings")
print()

# Test 1: Request WITHOUT POST settings (should use session settings)
print("1. Testing request WITHOUT POST settings (should use session settings)...")
try:
    response = client.post('/generator/generate/', {
        'individual_id': 'I1',
        'template': '1'
    })
    
    print(f"✓ Request completed with status: {response.status_code}")
    
    if response.status_code == 200:
        # Save the result
        with open('debug_request_without_post.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Saved debug_request_without_post.pdf")
        print("✓ Check if this PDF shows the OBVIOUS settings from session")
    else:
        print(f"✗ Request failed with status: {response.status_code}")
        print(f"Response content: {response.content}")
        
except Exception as e:
    print(f"✗ Request failed with exception: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Request WITH POST settings (should use POST settings)
print("2. Testing request WITH POST settings (should use POST settings)...")
try:
    response = client.post('/generator/generate/', {
        'individual_id': 'I1',
        'template': '1',
        # OBVIOUS POST settings (different from session)
        'font_family': 'Arial',
        'primary_name_font_size': 300,  # DIFFERENT OBVIOUS setting
        'primary_date_info_font_size': 250,  # DIFFERENT OBVIOUS setting
        'primary_place_info_font_size': 200,  # DIFFERENT OBVIOUS setting
        'default_stroke_width': 10.0,  # DIFFERENT OBVIOUS setting
        'primary_background_color': '#FFFF00',  # DIFFERENT OBVIOUS setting
        'primary_stroke_color': '#FF0000',  # DIFFERENT OBVIOUS setting
        'primary_font_color': '#00FF00',  # DIFFERENT OBVIOUS setting
        'primary_birth_color': '#00FFFF',  # DIFFERENT OBVIOUS setting
        'primary_birth_place_color': '#FF00FF',  # DIFFERENT OBVIOUS setting
        'primary_death_color': '#FFFF00',  # DIFFERENT OBVIOUS setting
        'primary_death_place_color': '#0000FF',  # DIFFERENT OBVIOUS setting
        'primary_name_x': 1000,  # DIFFERENT OBVIOUS setting
        'primary_name_y': 1000,  # DIFFERENT OBVIOUS setting
        'primary_name_rotate': 45,  # DIFFERENT OBVIOUS setting
        'primary_birth_x': 1100,
        'primary_birth_y': 1100,
        'primary_birth_rotate': 90,
        'primary_birth_place_x': 1200,
        'primary_birth_place_y': 1200,
        'primary_birth_place_rotate': 180,
        'primary_death_x': 1300,
        'primary_death_y': 1300,
        'primary_death_rotate': 270,
        'primary_death_place_x': 1400,
        'primary_death_place_y': 1400,
        'primary_death_place_rotate': 360,
        'subject_translate_x': 200,
        'subject_translate_y': 200
    })
    
    print(f"✓ Request completed with status: {response.status_code}")
    
    if response.status_code == 200:
        # Save the result
        with open('debug_request_with_post.pdf', 'wb') as f:
            f.write(response.content)
        print("✓ Saved debug_request_with_post.pdf")
        print("✓ Check if this PDF shows the DIFFERENT OBVIOUS settings from POST")
    else:
        print(f"✗ Request failed with status: {response.status_code}")
        print(f"Response content: {response.content}")
        
except Exception as e:
    print(f"✗ Request failed with exception: {e}")
    import traceback
    traceback.print_exc()

print()
print("=== ANALYSIS GUIDE ===")
print("1. Open debug_request_without_post.pdf")
print("   - Should show OBVIOUS settings (font size 200, pink background, etc.)")
print("   - If it shows defaults instead, session settings are not being used")
print()
print("2. Open debug_request_with_post.pdf")
print("   - Should show DIFFERENT OBVIOUS settings (font size 300, yellow background, etc.)")
print("   - If it shows the same as #1, POST settings are not being used")
print("   - If it shows defaults, neither session nor POST settings are working")
print()
print("3. Compare both PDFs:")
print("   - They should look DIFFERENT (different obvious settings)")
print("   - If they look the same, the settings selection logic is broken")
print("   - If both show defaults, the settings are not being passed at all")