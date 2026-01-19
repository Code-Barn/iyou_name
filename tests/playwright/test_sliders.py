import pytest
from playwright.sync_api import expect


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


def test_slider_interactions(page):
    """Test that sliders update their display values and ChartSettings."""
    # Step 1: Log in
    page.goto("http://localhost:8000/users/auth/login/")
    page.fill("#id_username", "baddod134")
    page.fill("#id_password", ",*36bC8Uay?c7g")
    page.click("button[type='submit']")
    expect(page).not_to_have_url("http://localhost:8000/users/auth/login/")

    # Step 2: Navigate to HUD
    page.goto("http://localhost:8000/hud/display-tree/")
    expect(page).to_have_title("Namechart Generator")

    # Step 3: Verify Chart Settings section
    chart_settings = page.locator(".card-header", has_text="Chart Settings")
    expect(chart_settings).to_be_visible()

    # Step 4: Test primary_name_font_size slider
    font_size_slider = page.locator("input[name='primary_name_font_size']")
    expect(font_size_slider).to_be_visible()

    # Get initial display value
    initial_value = page.locator("#primary-name-font-size-slider-value").text_content()
    print(f"Initial slider value: {initial_value}")

    # Adjust slider and verify display value updates
    font_size_slider.fill("100")
    font_size_slider.evaluate(
        "node => node.dispatchEvent(new Event('input', { bubbles: true }))"
    )
    font_size_slider.evaluate(
        "node => node.dispatchEvent(new Event('change', { bubbles: true }))"
    )

    # Verify display value updated
    updated_value = page.locator("#primary-name-font-size-slider-value").text_content()
    print(f"Updated slider value: {updated_value}")
    expect(updated_value).not_to_be(initial_value)
    expect(updated_value).to_be("100")

    # Step 5: Verify chartSettings object was updated
    chart_settings_obj = page.evaluate("window.familyTreeHUD.chartSettings")
    expect(chart_settings_obj["primary_name_font_size"]).to_be(100)


def test_apply_settings_button(page):
    """Test that the Apply Settings button saves ChartSettings."""
    # Step 1: Log in
    page.goto("http://localhost:8000/users/auth/login/")
    page.fill("#id_username", "baddod134")
    page.fill("#id_password", ",*36bC8Uay?c7g")
    page.click("button[type='submit']")
    expect(page).not_to_have_url("http://localhost:8000/users/auth/login/")

    # Step 2: Navigate to HUD
    page.goto("http://localhost:8000/hud/display-tree/")
    expect(page).to_have_title("Namechart Generator")

    # Step 3: Verify Chart Settings section
    chart_settings = page.locator(".card-header", has_text="Chart Settings")
    expect(chart_settings).to_be_visible()

    # Step 4: Adjust a slider
    font_size_slider = page.locator("input[name='primary_name_font_size']")
    expect(font_size_slider).to_be_visible()
    font_size_slider.fill("100")
    font_size_slider.evaluate(
        "node => node.dispatchEvent(new Event('input', { bubbles: true }))"
    )
    font_size_slider.evaluate(
        "node => node.dispatchEvent(new Event('change', { bubbles: true }))"
    )

    # Step 5: Click Apply Settings button
    apply_button = page.locator("#apply-settings")
    expect(apply_button).to_be_visible()
    apply_button.click()

    # Step 6: Verify status message updated
    status_message = page.locator(".hud-status")
    expect(status_message).to_have_text("Settings saved", timeout=5000)

    # Step 7: Verify API call was made
    request = page.wait_for_request("**/hud/api/chart-settings/save/")
    expect(request).to_be_truthy()
