#!/usr/bin/env python3

"""
Generate a visual test image to confirm place name separation.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/home/user/CODE_BASE/namechart')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.parser.models import PersonData
from apps.generator.utils.prototype.prototype_image_4generator import test_prototype_4gen

def main():
    """Generate test image and save to file."""
    
    # Run the test to generate the image
    result = test_prototype_4gen()
    
    # Save to file
    output_path = '/home/user/CODE_BASE/namechart/prototype_4gen_output_test.png'
    with open(output_path, 'wb') as f:
        f.write(result.getvalue())
    
    print(f"Generated test image: {output_path}")
    print(f"File size: {result.getbuffer().nbytes} bytes")
    print("Check the image to verify that birth and death places are properly separated.")
    print("The gap between 'Boston, MA' and 'Philadelphia, PA' should be clearly visible.")

if __name__ == "__main__":
    main()