import pytest
from playwright.sync_api import expect, sync_playwright


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


def test_hud_with_login(page):
    """Test HUD functionality after logging in."""
    # Step 1: Log in
    page.goto("http://localhost:8000/users/auth/login/")

    # Check for form errors before submission
    print("Current URL before login:", page.url)
    print("Page content before login:", page.content()[:1000])

    page.fill("#id_username", "baddod134")
    page.fill("#id_password", ",*36bC8Uay?c7g")

    # Wait for navigation after login
    with page.expect_navigation():
        page.click("button[type='submit']")

    # Check if login succeeded (could be redirected to any page)
    expect(page).not_to_have_url("http://localhost:8000/users/auth/login/")

    # Step 2: Navigate to HUD
    page.goto("http://localhost:8000/hud/display-tree/")
    print("HUD page content:", page.content()[:1000])
    expect(page).to_have_title("Namechart Generator")

    # Step 3: Verify Chart Settings section
    chart_settings = page.locator(".card-header", has_text="Chart Settings")
    expect(chart_settings).to_be_visible(timeout=10000)

    # Debug: Print all input elements
    inputs = page.locator("#hud-settings-form input").all()
    for input_element in inputs:
        name = input_element.get_attribute("name")
        print(f"Found input: {name}")

    # Step 4: Test sliders
    font_size_slider = page.locator("input[name='primary_name_font_size']")
    expect(font_size_slider).to_be_visible(timeout=5000)
    font_size_slider.fill("16")
    font_size_slider.evaluate(
        "node => node.dispatchEvent(new Event('input', { bubbles: true }))"
    )
    font_size_slider.evaluate(
        "node => node.dispatchEvent(new Event('change', { bubbles: true }))"
    )

    # Verify slider value updated
    value_display = page.locator("#primary-name-font-size-slider-value")
    expect(value_display).to_have_text("16", timeout=5000)

    # Step 5: Test Apply Settings button
    apply_button = page.locator("#apply-settings")
    expect(apply_button).to_be_visible()
    apply_button.click()

    # Verify settings were saved
    status = page.locator(".hud-status")
    expect(status).to_have_text("Settings saved", timeout=5000)
