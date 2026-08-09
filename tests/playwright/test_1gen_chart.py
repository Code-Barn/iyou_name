"""
Playwright test to debug the 1-generation chart generation.
This test automates the process of logging in, navigating to the HUD view,
and clicking the "Generate Final Chart" button to verify that the PDF is generated without errors.
"""

import os
import sys
import time
from pathlib import Path

import django
from playwright.sync_api import sync_playwright

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import Django models


def test_1gen_chart_generation():
    """Test the generation of the 1-generation chart."""
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Log in to the application
        page.goto("http://localhost:8000/users/auth/login/")
        page.fill("input[name='username']", "baddod134")
        page.fill("input[name='password']", ",*36bC8Uay?c7g")
        page.click("button[type='submit']")

        # Wait for login to complete
        page.wait_for_url("**/*")

        # Directly navigate to the HUD view with session variables
        # Set session variables manually for testing
        page.goto(
            "http://localhost:8000/hud/display-tree/?file_id=1&individual_id=I282583958371"
        )

        # Wait for the page to load
        page.wait_for_selector("h2:has-text('Interactive Family Tree Preview')")

        # Select the 1-generation template
        page.select_option("select[name='template']", "1")

        # Wait for the template to be applied
        time.sleep(2)

        # Click the "Generate Final Chart" button
        with page.expect_response("**/generator/generate/") as response_info:
            page.click("button:has-text('Generate Final Chart')")

        # Wait for the response
        response = response_info.value
        assert response.status == 200, f"Expected status 200, got {response.status}"

        # Verify that the response is a PDF
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Expected PDF, got {content_type}"

        # Close the browser
        browser.close()


if __name__ == "__main__":
    test_1gen_chart_generation()
