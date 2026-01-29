#!/usr/bin/env python3

import json
import os
import sys

print("=== STARTING TEST ===")

# Add the project directory to the Python path
sys.path.insert(0, "/home/user/CODE_BASE/namechart")

# Set up Django environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.test import Client
from django.urls import reverse


def test_preview_endpoint():
    """Simple test of the preview endpoint"""

    client = Client()

    # Test URL - use the actual URL path instead of reverse
    url = "/hud/get-1gen-preview/"

    # Test data with non-default values
    test_data = {
        "individual_id": "I1",  # Use a real individual ID from your test data
        "user_settings": {
            "font_family": "Times New Roman",
            "primary_name_font_size": 120,  # Changed from default 88
            "primary_date_info_font_size": 100,  # Changed from default 88
            "default_stroke_width": 1.5,  # Changed from default 0.5
            "primary_stroke_color": "#FF0000",  # Changed from default #000000
            "primary_font_color": "#00FF00",  # Changed from default #000000
            "primary_birth_color": "#0000FF",  # Changed from default #000000
            "primary_place_color": "#FFFF00",  # Changed from default #000000
            "primary_death_color": "#FF00FF",  # Changed from default #000000
            "primary_name_x": 10,
            "primary_name_y": 20,
            "primary_name_rotate": -30,  # Changed from default -45
            "primary_birth_x": 5,
            "primary_birth_y": 150,  # Changed from default 135
            "primary_birth_rotate": 60,  # Changed from default 45
            "primary_place_x": 15,
            "primary_place_y": 100,  # Changed from default 90
            "primary_place_rotate": -30,  # Changed from default -45
            "subject_translate_x": 50,
            "subject_translate_y": 30,
        },
    }

    print("=== TESTING PREVIEW ENDPOINT ===")
    print(f"Sending POST request to: {url}")
    print(f"Request data: {json.dumps(test_data, indent=2)}")

    try:
        # First, set up a session with the required data
        session = client.session
        session["current_gedcom_file_id"] = (
            1  # Use a valid GEDCOM file ID from your test data
        )
        session["selected_individual_id"] = "I1"  # Use a valid individual ID
        session.save()

        # Make the POST request
        response = client.post(
            url, data=json.dumps(test_data), content_type="application/json"
        )

        print(f"Response status: {response.status_code}")
        print(f"Response content type: {response.get('Content-Type', 'unknown')}")

        if response.status_code == 200:
            print("SUCCESS: Preview generated successfully!")
            print(f"Response content length: {len(response.content)} bytes")

            # Save the response to a file for inspection
            with open("test_preview_output.png", "wb") as f:
                f.write(response.content)
            print("Preview saved to: test_preview_output.png")
        else:
            print(
                f"ERROR: Preview generation failed with status {response.status_code}"
            )
            print(
                f"Response content: {response.content.decode('utf-8', errors='replace')}"
            )

    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        import traceback

        traceback.print_exc()

        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_preview_endpoint()
