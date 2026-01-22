#!/usr/bin/env python3

import json

from django.test import Client, TestCase
from django.urls import reverse


class PreviewEndpointTest(TestCase):
    """Test the preview endpoint to verify it receives updated settings"""

    def setUp(self):
        self.client = Client()
        # You may need to set up test data here (GEDCOM file, individual, etc.)

    def test_preview_endpoint_receives_updated_settings(self):
        """Test that the preview endpoint receives non-default settings"""

        # URL for the preview endpoint
        url = reverse("hud:get_1gen_preview")

        # Test data with non-default values
        test_data = {
            "individual_id": "I1",  # Use a real individual ID from your test data
            "user_settings": {
                "font_family": "Times New Roman",
                "primary_name_font_size": 120,  # Changed from default 88
                "primary_info_font_size": 100,  # Changed from default 88
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

        # Make the POST request
        response = self.client.post(
            url, data=json.dumps(test_data), content_type="application/json"
        )

        print(f"Response status: {response.status_code}")
        print(f"Response content type: {response.get('Content-Type', 'unknown')}")

        if response.status_code == 200:
            print("SUCCESS: Preview generated successfully!")
            print(f"Response content length: {len(response.content)} bytes")
        else:
            print(
                f"ERROR: Preview generation failed with status {response.status_code}"
            )
            print(
                f"Response content: {response.content.decode('utf-8', errors='replace')}"
            )


if __name__ == "__main__":
    import django
    from django.conf import settings

    # Configure Django settings
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "apps.hud",
            "apps.generator",
        ],
        ROOT_URLCONF="config.urls",
        SECRET_KEY="test-secret-key",
    )

    django.setup()

    # Run the test
    test_case = PreviewEndpointTest()
    test_case.setUp()
    test_case.test_preview_endpoint_receives_updated_settings()
