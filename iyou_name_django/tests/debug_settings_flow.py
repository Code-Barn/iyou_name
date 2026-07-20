import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.generator.utils. import generate_1gen_preview
from apps.parser.models import PersonData

# Create test individual
mock_individual = PersonData(
    id='I1',
    given_name='Test',
    surname='User',
    full_name='Test User',
    birth_date='01 JAN 2000',
    birth_place='Test City',
    death_date='01 JAN 2050',
    death_place='Test City',
    sex='M'
)

mock_family_data = {'individuals': {}, 'families': {}}

# Test with VERY DISTINCT settings that will be obvious if they're applied
obvious_settings = {
    'font_family': 'Arial',
    'primary_name_font_size': 200,  # Very large font
    'primary_date_info_font_size': 150,  # Very large font
    'primary_place_info_font_size': 100,  # Very large font
    'default_stroke_width': 5.0,  # Very thick stroke
    'primary_background_color': '#FF00FF',  # Bright pink background
    'primary_stroke_color': '#00FF00',  # Bright green stroke
    'primary_font_color': '#FF0000',  # Bright red text
    'primary_birth_color': '#0000FF',  # Bright blue birth date
    'primary_birth_place_color': '#FFFF00',  # Bright yellow birth place
    'primary_death_color': '#FF00FF',  # Bright pink death date
    'primary_death_place_color': '#00FFFF',  # Bright cyan death place
    'primary_name_x': 500,  # Moved position
    'primary_name_y': 500,  # Moved position
    'primary_name_rotate': 0,  # No rotation
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
}

print("=== DEBUGGING SETTINGS FLOW ===")
print("Testing with VERY OBVIOUS settings that should be clearly visible...")
print()

# Test 1: Preview generation
print("1. Testing PREVIEW generation with obvious settings...")
try:
    preview_result = generate_1gen_preview(
        mock_individual,
        mock_family_data,
        "preview",
        obvious_settings
    )
    print("✓ Preview generation successful")

    # Save for visual inspection
    with open('debug_preview.png', 'wb') as f:
        f.write(preview_result.getvalue())
    print("✓ Saved debug_preview.png - check if settings are applied")
    print()

except Exception as e:
    print(f"✗ Preview generation failed: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test 2: Final chart generation
print("2. Testing FINAL CHART generation with same obvious settings...")
try:
    final_result = generate_1gen_preview(
        mock_individual,
        mock_family_data,
        "final",
        obvious_settings
    )
    print("✓ Final chart generation successful")

    # Save for visual inspection
    with open('debug_final.pdf', 'wb') as f:
        f.write(final_result.getvalue())
    print("✓ Saved debug_final.pdf - check if settings are applied")
    print()

except Exception as e:
    print(f"✗ Final chart generation failed: {e}")
    import traceback
    traceback.print_exc()
    print()

print("=== VISUAL INSPECTION GUIDE ===")
print("In both debug_preview.png and debug_final.pdf, you should see:")
print("- HUGE text (font sizes 200, 150, 100)")
print("- Bright pink background")
print("- Bright green stroke")
print("- Bright red name text")
print("- Bright blue birth date")
print("- Bright yellow birth place")
print("- Bright pink death date")
print("- Bright cyan death place")
print("- All text moved to different positions")
print("- No rotation (all rotate values = 0)")
print()
print("If you DON'T see these obvious changes, the settings are not being applied!")
print()
print("=== NEXT STEPS ===")
print("1. Open debug_preview.png - does it show the obvious settings?")
print("2. Open debug_final.pdf - does it show the same obvious settings?")
print("3. If preview shows settings but final doesn't, the issue is in the composite logic")
print("4. If neither shows settings, the issue is in the image generation logic")
print("5. If both show settings, then the issue is elsewhere (form submission, etc.)")
