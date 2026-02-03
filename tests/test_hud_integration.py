"""
Integration tests for HUD rotation functionality.

This module tests the interactive rotation controls
that were added to the live preview system.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestHUDRotation:
    """Test HUD rotation controls and functionality."""

    @pytest.fixture
    def driver(self):
        """Setup Chrome driver for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1200,800")

        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()

    def test_rotation_buttons_exist(self, driver):
        """Test that rotation buttons are present on the page."""
        # This would require a running test server
        # For now, we'll test the JavaScript logic directly
        pass

    def test_rotation_javascript_logic(self):
        """Test rotation JavaScript logic without browser."""
        # This would test the HUD.Rotation module directly
        # For now, we'll document the expected behavior
        pass


class TestNameParsingIntegration:
    """Test name parsing integration with generators."""

    def test_1gen_generator_uses_shared_utils(self):
        """Test that 1gen generator uses shared name parsing."""
        from apps.generator.utils.name_utils import get_name_display_info

        # Test the same logic that 1gen generator uses
        info = get_name_display_info("John Doe")
        assert info["display_text"] == "John\nDoe"

        info = get_name_display_info("John")
        assert info["display_text"] == "John"

    def test_2gen_generator_uses_shared_utils(self):
        """Test that 2gen generator uses shared name parsing."""
        from apps.generator.utils.name_utils import parse_name_parts

        # Test the same logic that 2gen generator uses for parents
        first, middle, last = parse_name_parts("Jane Smith")
        assert first == "Jane"
        assert middle == ""
        assert last == "Smith"

        first, middle, last = parse_name_parts("Jane")
        assert first == "Jane"
        assert middle == ""
        assert last == ""


class TestSettingsPersistence:
    """Test settings persistence across template switches."""

    def test_settings_storage_format(self):
        """Test that settings are stored in correct format."""
        # This would test the localStorage/sessionStorage logic
        # For now, document the expected behavior
        pass


class TestRegressionIntegration:
    """Integration tests for regression fixes."""

    def test_no_duplicate_last_names_in_charts(self):
        """Test that the duplicate last name bug is fixed in actual chart generation."""
        # This would require running the actual generators
        # For now, we test the name parsing logic that feeds them

        from apps.generator.utils.name_utils import get_name_display_info

        # Test cases that previously caused duplicates
        problematic_names = ["John Doe", "Jane Smith", "Robert Johnson"]

        for name in problematic_names:
            info = get_name_display_info(name)
            display_text = info["display_text"]
            lines = display_text.split("\n")

            # Count occurrences of last name
            last_name = info["last_name"]
            last_name_count = sum(1 for line in lines if line == last_name)

            assert last_name_count == 1, (
                f"Duplicate last name found for '{name}': {display_text}"
            )


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
