import sys
import os
import django

from apps.generator.utils. import generate_1gen_preview
from apps.parser.models import PersonData

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Create a mock individual with all required fields
mock_individual = PersonData(
    id='I1',
    given_name='John',
    surname='Doe',
    full_name='John Doe',
    birth_date='1 JAN 1900',
    birth_place='New York',
    death_date='1 JAN 1980',
    death_place='California',
    sex='M'
)

# Mock family data
mock_family_data = {
    'individuals': {},
    'families': {}
}

# Mock user settings
mock_user_settings = {
    'font_family': 'Arial',
    'primary_name_font_size': 84,
    'primary_background_color': '#FFFFFF',
    'primary_font_color': '#000000'
}

print("Testing preview mode...")
try:
    preview_result = generate_1gen_preview(
        mock_individual,
        mock_family_data,
        "preview",
        mock_user_settings
    )
    print('SUCCESS: Preview generation works')
    print('Preview result type:', type(preview_result))
except Exception as e:
    print(f'ERROR in preview mode: {e}')
    import traceback
    traceback.print_exc()

print("\nTesting final mode...")
try:
    final_result = generate_1gen_preview(
        mock_individual,
        mock_family_data,
        "final",
        mock_user_settings
    )
    print('SUCCESS: Final chart generation works')
    print('Final result type:', type(final_result))
except Exception as e:
    print(f'ERROR in final mode: {e}')
    import traceback
    traceback.print_exc()
