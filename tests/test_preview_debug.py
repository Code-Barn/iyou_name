#!/usr/bin/env python3

import json
import logging

import requests

# Set up logging to see the debug output
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_preview_endpoint():
    """Test the preview endpoint with different settings to see what's received"""

    # Test URL (adjust as needed for your setup)
    url = "http://localhost:8000/hud/get-1gen-preview/"

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
        # Make the POST request
        response = requests.post(
            url,
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "X-CSRFToken": "test-token",  # You may need a real CSRF token
            },
        )

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content type: {response.headers.get('Content-Type')}")
        print(f"Response content length: {len(response.content)} bytes")

        if response.status_code == 200:
            print("SUCCESS: Preview generated successfully!")
            # Save the response to a file for inspection
            with open("test_preview_output.png", "wb") as f:
                f.write(response.content)
            print("Preview saved to: test_preview_output.png")
        else:
            print(
                f"ERROR: Preview generation failed with status {response.status_code}"
            )
            print(f"Response text: {response.text}")

    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        import traceback

        traceback.print_exc()

        traceback.print_exc()

if __name__ == "__main__":
    test_preview_endpoint()
