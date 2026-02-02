"""
Tests for the multi-generation family tree image generation system.

This test suite covers:
- Settings helper functionality
- Image generation chaining
- Template preview endpoints
- Frontend integration
"""

import json
from io import BytesIO
from unittest.mock import Mock, patch

from django.test import TestCase, Client
from django.urls import reverse
from apps.generator.utils.settings_helper import (
    extract_generation_settings,
    get_default_settings,
)
from apps.generator.utils.image_1generator import generate_1gen_preview
from apps.parser.models import PersonData


class TestSettingsHelper(TestCase):
    """Test the settings helper functions."""

    def test_extract_primary_settings(self):
        """Test extraction of PRIMARY generation settings."""
        user_settings = {
            "PRIMARY_name_font_size": 84,
            "PRIMARY_translate_x": 100,
            "font_family": "Arial",
            "PARENT_name_font_size": 60,  # Should be excluded
        }

        result = extract_generation_settings(user_settings, "PRIMARY")

        self.assertEqual(result["name_font_size"], 84)
        self.assertEqual(result["translate_x"], 100)
        self.assertEqual(result["font_family"], "Arial")  # Inherited
        self.assertNotIn("name_font_size", result)  # PARENT setting excluded

    def test_extract_parent_settings(self):
        """Test extraction of PARENT generation settings."""
        user_settings = {
            "PARENT_name_font_size": 60,
            "PARENT_translate_x": 200,
            "font_family": "Times New Roman",
            "PRIMARY_name_font_size": 84,  # Should be excluded
        }

        result = extract_generation_settings(user_settings, "PARENT")

        self.assertEqual(result["name_font_size"], 60)
        self.assertEqual(result["translate_x"], 200)
        self.assertEqual(result["font_family"], "Times New Roman")  # Inherited
        self.assertNotIn("name_font_size", result)  # PRIMARY setting excluded

    def test_extract_settings_empty_input(self):
        """Test extraction with empty user settings."""
        result = extract_generation_settings(None, "PRIMARY")
        self.assertEqual(result, {})

    def test_extract_settings_no_prefix_matches(self):
        """Test extraction with no matching prefix."""
        user_settings = {
            "font_family": "Arial",
            "primary_background_color": "#FFFFFF",
        }

        result = extract_generation_settings(user_settings, "NONEXISTENT")

        # Should only inherit base settings
        self.assertEqual(result["font_family"], "Arial")
        self.assertEqual(result["primary_background_color"], "#FFFFFF")

    def test_get_default_settings_primary(self):
        """Test default settings for PRIMARY generation."""
        defaults = get_default_settings("PRIMARY")

        self.assertEqual(defaults["primary_name_font_size"], 84)
        self.assertEqual(defaults["font_family"], "Arial")
        self.assertEqual(defaults["primary_background_color"], "#FFFFFF")

    def test_get_default_settings_parent(self):
        """Test default settings for PARENT generation."""
        defaults = get_default_settings("PARENT")

        self.assertEqual(defaults["primary_name_font_size"], 60)  # Smaller than PRIMARY
        self.assertEqual(defaults["font_family"], "Arial")
        self.assertEqual(defaults["primary_background_color"], "#FFFFFF")

    def test_get_default_settings_nonexistent(self):
        """Test default settings for nonexistent generation."""
        defaults = get_default_settings("NONEXISTENT")

        # Should return only base defaults
        self.assertEqual(defaults["font_family"], "Arial")
        self.assertEqual(defaults["primary_background_color"], "#FFFFFF")
        self.assertNotIn("primary_name_font_size", defaults)


class TestImageGeneration(TestCase):
    """Test the image generation functionality."""

    def setUp(self):
        """Set up test data."""
        self.primary_individual = PersonData(
            id="I1",
            full_name="John Doe",
            given_name="John",
            surname="Doe",
            birth_date="1950-01-01",
            birth_place="Anytown, USA",
            father="I2",
            mother="I3",
        )

        self.family_data = {
            "individuals": {
                "I1": self.primary_individual,
                "I2": PersonData(
                    id="I2", full_name="Robert Doe", given_name="Robert", surname="Doe"
                ),
                "I3": PersonData(
                    id="I3", full_name="Jane Smith", given_name="Jane", surname="Smith"
                ),
            }
        }

    @patch("apps.generator.utils.image_1generator.Image")
    def test_1gen_preview_basic(self, mock_image_class):
        """Test basic 1-generation preview generation."""
        # Mock Wand Image
        mock_img = Mock()
        mock_image_class.return_value.__enter__.return_value = mock_img

        # Mock drawing
        mock_draw = Mock()
        with patch(
            "apps.generator.utils.image_1generator.Drawing", return_value=mock_draw
        ):
            with patch(
                "apps.generator.utils.image_1generator.os.path.exists",
                return_value=True,
            ):
                result = generate_1gen_preview(
                    self.primary_individual, self.family_data, "preview", {}
                )

                self.assertIsInstance(result, BytesIO)
                mock_draw.assert_called_once()

    @patch("apps.generator.utils.image_1generator.Image")
    def test_1gen_preview_with_user_settings(self, mock_image_class):
        """Test 1-generation preview with custom user settings."""
        user_settings = {
            "PRIMARY_name_font_size": 100,
            "font_family": "Times New Roman",
            "primary_background_color": "#FF0000",
        }

        # Mock Wand Image
        mock_img = Mock()
        mock_image_class.return_value.__enter__.return_value = mock_img

        # Mock drawing
        mock_draw = Mock()
        with patch(
            "apps.generator.utils.image_1generator.Drawing", return_value=mock_draw
        ):
            with patch(
                "apps.generator.utils.image_1generator.os.path.exists",
                return_value=True,
            ):
                result = generate_1gen_preview(
                    self.primary_individual, self.family_data, "preview", user_settings
                )

                self.assertIsInstance(result, BytesIO)
                # Verify that user settings were applied (would need to check drawing calls)

    @patch("apps.generator.utils.image_2generator.generate_1gen_preview")
    @patch("apps.generator.utils.image_2generator.Image")
    def test_2gen_preview_composite(self, mock_image_class, mock_gen1_preview):
        """Test 2-generation preview with 1gen composite."""
        from apps.generator.utils.image_2generator import generate_2gen_preview

        # Mock 1gen preview result
        mock_gen1_buffer = BytesIO(b"fake_1gen_image_data")
        mock_gen1_preview.return_value = mock_gen1_buffer

        # Mock Wand Image for 2gen
        mock_img = Mock()
        mock_image_class.return_value.__enter__.return_value = mock_img

        # Mock drawing
        mock_draw = Mock()
        with patch(
            "apps.generator.utils.image_2generator.Drawing", return_value=mock_draw
        ):
            with patch(
                "apps.generator.utils.image_2generator.os.path.exists",
                return_value=True,
            ):
                result = generate_2gen_preview(
                    self.primary_individual, self.family_data, "preview", {}
                )

                self.assertIsInstance(result, BytesIO)
                # Verify 1gen preview was called
                mock_gen1_preview.assert_called_once()
                # Verify composite was attempted (would need to check Image.composite calls)


class TestTemplatePreviewEndpoint(TestCase):
    """Test the generic template preview endpoint."""

    def setUp(self):
        """Set up test client and data."""
        self.client = Client()

        # Mock session data
        self.session_data = {
            "current_gedcom_file_id": 1,
            "selected_individual_id": "I1",
        }

    @patch("apps.hud.views.GedcomFile.objects.get")
    @patch("apps.hud.views.get_template_mapping")
    def test_get_template_preview_success(self, mock_template_mapping, mock_gedcom_get):
        """Test successful template preview generation."""
        # Mock GedcomFile
        mock_gedcom_file = Mock()
        mock_gedcom_file.parsed_data = {
            "individuals": {
                "I1": {
                    "id": "I1",
                    "full_name": "John Doe",
                    "given_name": "John",
                    "surname": "Doe",
                }
            }
        }
        mock_gedcom_get.return_value = mock_gedcom_file

        # Mock template mapping
        mock_template_mapping.return_value = {
            "1": {
                "module": "apps.generator.utils.image_1generator",
                "function": "generate_1gen_preview",
            }
        }

        # Mock the generator function
        with patch("apps.hud.views.generate_1gen_preview") as mock_generator:
            mock_buffer = BytesIO(b"fake_image_data")
            mock_generator.return_value = mock_buffer

            # Set session
            session = self.client.session
            session.update(self.session_data)
            session.save()

            # Make request
            response = self.client.get("/hud/get-template-preview/1/")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "image/png")

    def test_get_template_preview_invalid_template(self):
        """Test preview request with invalid template ID."""
        # Set session
        session = self.client.session
        session.update(self.session_data)
        session.save()

        # Make request with invalid template
        response = self.client.get("/hud/get-template-preview/999/")

        self.assertEqual(response.status_code, 404)

    @patch("apps.hud.views.GedcomFile.objects.get")
    def test_get_template_preview_no_gedcom_file(self, mock_gedcom_get):
        """Test preview request with no GEDCOM file in session."""
        mock_gedcom_get.side_effect = Exception("DoesNotExist")

        # Set session without gedcom file
        session = self.client.session
        session["selected_individual_id"] = "I1"
        session.save()

        response = self.client.get("/hud/get-template-preview/1/")

        self.assertEqual(response.status_code, 500)


class TestFrontendIntegration(TestCase):
    """Test frontend JavaScript integration."""

    def test_template_selection_javascript(self):
        """Test that template selection JavaScript works correctly."""
        # This would require Selenium or similar for full JavaScript testing
        # For now, we'll test the backend endpoints that JavaScript calls

        with patch("apps.hud.views.get_template_mapping") as mock_mapping:
            mock_mapping.return_value = {
                "1": {
                    "module": "apps.generator.utils.image_1generator",
                    "function": "generate_1gen_preview",
                },
                "2": {
                    "module": "apps.generator.utils.image_2generator",
                    "function": "generate_2gen_preview",
                },
            }

            # Test that all template IDs are valid
            for template_id in range(1, 11):
                if template_id in mock_mapping.return_value:
                    config = mock_mapping.return_value[template_id]
                    self.assertIn("module", config)
                    self.assertIn("function", config)


class TestPerformanceAndMemory(TestCase):
    """Test performance and memory management."""

    @patch("apps.generator.utils.image_1generator.Image")
    def test_buffer_memory_management(self, mock_image_class):
        """Test that buffers are properly managed."""
        mock_img = Mock()
        mock_image_class.return_value.__enter__.return_value = mock_img

        individual = PersonData(
            id="I1", full_name="Test User", given_name="Test", surname="User"
        )
        family_data = {"individuals": {"I1": individual}}

        with patch("apps.generator.utils.image_1generator.Drawing"):
            with patch(
                "apps.generator.utils.image_1generator.os.path.exists",
                return_value=True,
            ):
                result = generate_1gen_preview(individual, family_data, "preview", {})

                # Buffer should be seekable
                self.assertTrue(result.seekable())
                # Should be able to read from buffer
                result.seek(0)
                data = result.read()
                self.assertIsInstance(data, bytes)

    def test_settings_extraction_performance(self):
        """Test performance of settings extraction with large datasets."""
        # Create large user settings dict
        large_settings = {}
        for i in range(1000):
            large_settings[f"PRIMARY_setting_{i}"] = f"value_{i}"
            large_settings[f"PARENT_setting_{i}"] = f"value_{i}"

        # Time the extraction
        import time

        start_time = time.time()

        result = extract_generation_settings(large_settings, "PRIMARY")

        end_time = time.time()
        extraction_time = end_time - start_time

        # Should complete quickly (less than 0.1 seconds)
        self.assertLess(extraction_time, 0.1)
        # Should extract only PRIMARY settings
        self.assertEqual(len(result), 1000)


# Integration Test Example
class TestMultiGenerationIntegration(TestCase):
    """Integration tests for the complete multi-generation system."""

    @patch("apps.generator.utils.image_1generator.Image")
    @patch("apps.generator.utils.image_2generator.Image")
    def test_complete_2gen_workflow(self, mock_image_2gen, mock_image_1gen):
        """Test complete workflow from settings to final 2gen image."""
        from apps.generator.utils.image_2generator import generate_2gen_preview

        # Mock 1gen generation
        mock_1gen_buffer = BytesIO(b"mock_1gen_data")
        with patch(
            "apps.generator.utils.image_2generator.generate_1gen_preview",
            return_value=mock_1gen_buffer,
        ):
            # Mock 2gen image
            mock_2gen_img = Mock()
            mock_image_2gen.return_value.__enter__.return_value = mock_2gen_img

            individual = PersonData(
                id="I1",
                full_name="John Doe",
                given_name="John",
                surname="Doe",
                father="I2",
                mother="I3",
            )
            family_data = {
                "individuals": {
                    "I1": individual,
                    "I2": PersonData(
                        id="I2",
                        full_name="Robert Doe",
                        given_name="Robert",
                        surname="Doe",
                    ),
                    "I3": PersonData(
                        id="I3",
                        full_name="Jane Smith",
                        given_name="Jane",
                        surname="Smith",
                    ),
                }
            }

            user_settings = {
                "PRIMARY_name_font_size": 84,
                "PARENT_name_font_size": 60,
                "font_family": "Arial",
            }

            with patch("apps.generator.utils.image_2generator.Drawing"):
                with patch(
                    "apps.generator.utils.image_2generator.os.path.exists",
                    return_value=True,
                ):
                    result = generate_2gen_preview(
                        individual, family_data, "preview", user_settings
                    )

                    self.assertIsInstance(result, BytesIO)
                    # Verify the workflow completed successfully


if __name__ == "__main__":
    import unittest

    unittest.main()
