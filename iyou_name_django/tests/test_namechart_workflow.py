import pytest
from playwright.sync_api import Page, expect

# Test data
TEST_GEDCOM_FILE = "namechart/tests/test_data/sample.ged"
TEST_USER = {
    "username": "testuser",
    "password": "testpass123",
    "email": "testuser@example.com",
}


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown(page: Page):
    """Fixture to set up and tear down test data."""
    # Setup: Create a test user
    page.goto("http://localhost:8000/users/register/")
    expect(page).to_have_title("Register")
    page.fill("input[name='username']", TEST_USER["username"])
    page.fill("input[name='email']", TEST_USER["email"])
    page.fill("input[name='password1']", TEST_USER["password"])
    page.fill("input[name='password2']", TEST_USER["password"])
    page.click("button[type='submit']")
    expect(page).to_have_url("http://localhost:8000/")

    # Log in
    page.goto("http://localhost:8000/users/login/")
    page.fill("input[name='username']", TEST_USER["username"])
    page.fill("input[name='password']", TEST_USER["password"])
    page.click("button[type='submit']")

    yield page

    # Teardown: Delete test user and files (optional)
    # This can be implemented if needed


def test_upload_gedcom_file(page: Page):
    """Test uploading a GEDCOM file."""
    # Navigate to upload page
    page.goto("http://localhost:8000/upload-file/")
    expect(page).to_have_title("Upload GEDCOM File")

    # Upload a GEDCOM file
    page.set_input_files("input[name='gedcom_file']", TEST_GEDCOM_FILE)
    page.click("button[type='submit']")
    expect(page).to_have_url("http://localhost:8000/upload/select/")

    # Verify the file is uploaded and processed
    expect(page).to_have_url("http://localhost:8000/upload/select/")
    expect(page.locator("h2")).to_contain_text("Select Individual")


def test_select_gedcom_file_from_profile(page: Page):
    """Test selecting a GEDCOM file from the user's profile."""
    # Upload a GEDCOM file first
    test_upload_gedcom_file(page)

    # Navigate to user profile
    page.goto("http://localhost:8000/users/profile/")
    expect(page).to_have_title("User Profile")

    # Click the "Generate" button for the uploaded file
    page.click("a.btn-success:has-text('Generate')")
    expect(page).to_have_url("http://localhost:8000/upload/select/")

    # Verify the user is redirected to the select_individual page
    expect(page).to_have_url("http://localhost:8000/upload/select/")
    expect(page.locator("h2")).to_contain_text("Select Individual")


def test_generate_chart(page: Page):
    """Test generating a chart from a GEDCOM file."""
    # Upload and select a GEDCOM file
    test_select_gedcom_file_from_profile(page)

    # Select the first individual and generate a chart
    page.click("button[type='submit']")
    expect(page).to_have_url("http://localhost:8000/charts/generate/")

    # Verify the chart is generated successfully
    expect(page).to_have_url("http://localhost:8000/charts/generate/")
    expect(page.locator("h2")).to_contain_text("Chart Generated Successfully")
