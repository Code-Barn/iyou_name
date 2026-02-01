import sys
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.generator.utils.image_1generator import generate_1gen_preview
from apps.parser.models import PersonData

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

# Test the function call
try:
    result = generate_1gen_preview(
        mock_individual,
        mock_family_data,
        '1gen',
        {'font_family': 'Arial'}
    )
    print('SUCCESS: Function call works correctly')
    print('Function returned:', type(result))
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()