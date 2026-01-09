"""
Playwright test to reproduce the 'individuals' error in chart generation.

This test:
1. Logs in as a test user
2. Uploads a GEDCOM file
3. Attempts to generate a chart
4. Captures the error and logs
"""

import logging
import os

import pytest
from playwright.sync_api import Page, expect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
TEST_GEDCOM_FILE = "namechart/tests/test_data/sample.ged"
TEST_USER = {
    "username": "testuser_chart",
    "password": "testpass123",
    "email": "testuser_chart@example.com",
}


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown(page: Page):
    """Fixture to set up and tear down test data."""
    # Setup: Create a test user if not exists
    try:
        page.goto("http://localhost:8000/users/register/")
        page.fill("input[name='username']", TEST_USER["username"])
        page.fill("input[name='email']", TEST_USER["email"])
        page.fill("input[name='password1']", TEST_USER["password"])
        page.fill("input[name='password2']", TEST_USER["password"])
        page.click("button[type='submit']")
        logger.info("Test user created successfully")
    except Exception as e:
        logger.info(f"Test user may already exist: {e}")

    # Log in
    page.goto("http://localhost:8000/users/login/")
    page.fill("input[name='username']", TEST_USER["username"])
    page.fill("input[name='password']", TEST_USER["password"])
    page.click("button[type='submit']")
    expect(page).to_have_url("http://localhost:8000/")
    logger.info("Logged in successfully")

    yield page

    # Teardown: Delete test user and files (optional)
    # This can be implemented if needed


def test_chart_generation_workflow(page: Page):
    """Test the complete chart generation workflow."""
    logger.info("Starting chart generation test")

    # Step 1: Upload a GEDCOM file
    logger.info("Step 1: Uploading GEDCOM file")
    page.goto("http://localhost:8000/upload-file/")
    expect(page).to_have_title("Upload GEDCOM File")

    # Upload the file
    page.set_input_files("input[name='gedcom_file']", TEST_GEDCOM_FILE)
    page.click("button[type='submit']")
    expect(page).to_have_url("http://localhost:8000/upload/select/")
    logger.info("GEDCOM file uploaded successfully")

    # Step 2: Verify individuals are displayed correctly
    logger.info("Step 2: Verifying individuals")
    individuals = page.locator(".individual-select")
    expect(individuals).to_have_count(3)  # Sample.ged has 3 individuals
    logger.info(f"Found {individuals.count()} individuals")

    # Check for duplicate names
    individual_names = page.locator(
        ".individual-select .individual-name"
    ).all_text_contents()
    logger.info(f"Individual names: {individual_names}")
    if len(set(individual_names)) != len(individual_names):
        logger.error("Duplicate individual names detected!")
        pytest.fail("Duplicate individual names detected")

    # Step 3: Select an individual and generate chart
    logger.info("Step 3: Selecting individual and generating chart")
    page.click("button[type='submit']")
    expect(page).to_have_url("http://localhost:8000/charts/generate/")

    # Step 4: Verify chart generation
    logger.info("Step 4: Verifying chart generation")
    try:
        expect(page.locator("h2")).to_contain_text("Chart Generated Successfully")
        logger.info("Chart generated successfully")
    except Exception as e:
        error_message = page.locator(".error-message").text_content()
        logger.error(f"Chart generation failed: {error_message}")
        pytest.fail(f"Chart generation failed: {error_message}")


def test_parsed_data_structure(page: Page):
    """Test that parsed_data contains the 'individuals' key."""
    logger.info("Testing parsed_data structure")

    # Upload a GEDCOM file
    page.goto("http://localhost:8000/upload-file/")
    page.set_input_files("input[name='gedcom_file']", TEST_GEDCOM_FILE)
    page.click("button[type='submit']")
    expect(page).to_have_url("http://localhost:8000/upload/select/")

    # Intercept the API call to check parsed_data
    with page.expect_response("**/charts/generate/") as response_info:
        page.click("button[type='submit']")
    response = response_info.value

    # Check if the response contains the error
    if response.status == 200:
        content = response.text()
        if "'individuals'" in content:
            logger.error("'individuals' key missing from parsed_data")
            pytest.fail("'individuals' key missing from parsed_data")
    else:
        logger.error(f"Request failed with status {response.status}")
        pytest.fail(f"Request failed with status {response.status}")
