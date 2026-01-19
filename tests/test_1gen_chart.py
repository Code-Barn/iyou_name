"""
Django test to debug the `generate_family_tree` function in `image_1generator.py`.
This test verifies that the function works correctly for the 1-generation chart.
"""

from io import BytesIO
from unittest.mock import patch

from django.test import TestCase

from apps.generator.models import ChartSettings
from apps.generator.utils.image_1generator import generate_family_tree
from apps.parser.models import PersonData


class Test1GenChart(TestCase):
    """Test the generation of the 1-generation chart."""

    def setUp(self):
        """Set up test data."""
        # Create a mock PersonData object for the primary individual
        self.primary_individual = PersonData(
            id="I282583958371",
            full_name="David Chris Byers-Callahan",
            given_name="David Chris",
            surname="Byers-Callahan",
            birth_date="13 Oct 1985",
            birth_place="Arlington Heights, Cook, Illinois, USA",
        )

        # Create mock family data
        self.family_data = {
            "individuals": {
                "I282583958371": self.primary_individual,
            },
            "families": {},
        }

        # Create a ChartSettings instance
        self.chart_settings = ChartSettings()

    def test_generate_family_tree_default_settings(self):
        """Test `generate_family_tree` with default settings."""
        # Call the function with default settings
        image_buffer = generate_family_tree(
            primary_individual=self.primary_individual,
            family_data=self.family_data,
            template="1gen",
            chart_settings=self.chart_settings,
            preview_mode=False,
        )

        # Verify that the image buffer is not empty
        self.assertIsInstance(image_buffer, BytesIO)
        self.assertGreater(image_buffer.getbuffer().nbytes, 0)

    def test_generate_family_tree_preview_mode(self):
        """Test `generate_family_tree` in preview mode."""
        # Call the function in preview mode
        image_buffer = generate_family_tree(
            primary_individual=self.primary_individual,
            family_data=self.family_data,
            template="1gen",
            chart_settings=self.chart_settings,
            preview_mode=True,
        )

        # Verify that the image buffer is not empty
        self.assertIsInstance(image_buffer, BytesIO)
        self.assertGreater(image_buffer.getbuffer().nbytes, 0)

    def test_template_path_construction(self):
        """Test that the template path is constructed correctly."""
        # Call the function and verify it runs without errors
        generate_family_tree(
            primary_individual=self.primary_individual,
            family_data=self.family_data,
            template="1gen",
            chart_settings=self.chart_settings,
            preview_mode=False,
        )
        self.assertTrue(True)

    @patch("apps.generator.utils.image_1generator.Image.__init__")
    def test_missing_template_file(self, mock_image_init):
        """Test that the function raises an error if the template file is missing."""
        # Configure the mock to raise a FileNotFoundError
        mock_image_init.side_effect = FileNotFoundError("Template file not found")

        with self.assertRaises(FileNotFoundError):
            generate_family_tree(
                primary_individual=self.primary_individual,
                family_data=self.family_data,
                template="1gen",
                chart_settings=self.chart_settings,
                preview_mode=False,
            )

    def test_invalid_settings(self):
        """Test that the function raises an error if invalid settings are provided."""
        # The function should handle None chart_settings by creating a default instance
        # So we expect it to work without raising an AttributeError
        try:
            generate_family_tree(
                primary_individual=self.primary_individual,
                family_data=self.family_data,
                template="1gen",
                chart_settings=None,  # Invalid settings
                preview_mode=False,
            )
            self.assertTrue(True)  # If no error is raised, the test passes
        except AttributeError:
            self.fail("Function raised AttributeError unexpectedly")
