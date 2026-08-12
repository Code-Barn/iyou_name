"""
Tests for the multi-generation family tree image generation system.

This test suite covers:
- Settings validation (apps.generator.utils.settings_validator)
- Template mapping and generator wiring (apps.generator.template_mapping)
- Template preview endpoint (apps.hud.views_simple_buffered.get_template_preview_simple)
- Frontend integration
- Settings persistence across templates
"""

import importlib
import json
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

from django.conf import settings
from django.test import Client, TestCase
from wand.color import Color

from apps.generator.models import GedcomFile
from apps.generator.template_mapping import get_template_mapping
from apps.generator.utils import settings_validator
from apps.parser.models import PersonData


def set_client_session(client, **data):
    """Persist session data into the test client's signed cookie."""
    session = client.session
    session.update(data)
    session.save()
    client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key


class TestSettingsValidation(TestCase):
    """Test the settings validation helpers."""

    def test_validate_setting_converts_values(self):
        self.assertEqual(
            settings_validator.validate_setting("84", int, 10, "name_font_size"), 84
        )
        self.assertEqual(
            settings_validator.validate_setting(42, int, 10, "name_font_size"), 42
        )

    def test_validate_setting_falls_back_on_invalid(self):
        self.assertEqual(
            settings_validator.validate_setting("bad", int, 10, "name_font_size"), 10
        )
        self.assertEqual(
            settings_validator.validate_setting(None, str, "Arial", "font_family"),
            "Arial",
        )

    def test_validate_font_size_enforces_bounds(self):
        self.assertEqual(settings_validator.validate_font_size_setting(2, 12), 6)
        self.assertEqual(settings_validator.validate_font_size_setting(900, 12), 500)
        self.assertEqual(settings_validator.validate_font_size_setting(24, 12), 24)

    def test_validate_coordinate_setting(self):
        self.assertEqual(settings_validator.validate_coordinate_setting("50", 0), 50)
        self.assertEqual(
            settings_validator.validate_coordinate_setting(
                -5, 0, allow_negative=False
            ),
            0,
        )

    def test_validate_color_setting(self):
        color = settings_validator.validate_color_setting("#FF0000", "#FFFFFF", "bg")
        self.assertIsInstance(color, Color)
        self.assertEqual(color, Color("#f00"))

    def test_validate_color_setting_falls_back_on_invalid(self):
        fallback = settings_validator.validate_color_setting(
            "not-a-color", "#FFFFFF", "bg"
        )
        self.assertEqual(fallback, Color("#FFFFFF"))

    def test_get_validated_settings_with_schema(self):
        import os

        schema = {
            "font_family": (str, "Arial"),
            "primary_name_font_size": (int, 84),
            "primary_font_color": (str, "black"),
        }
        validated = settings_validator.get_validated_settings(
            {
                "font_family": "Arial",
                "primary_name_font_size": "120",
                "primary_font_color": "red",
            },
            schema,
        )
        self.assertEqual(validated["primary_name_font_size"], 120)
        self.assertEqual(validated["primary_font_color"], Color("#f00"))
        # Font family must resolve to a real font file on disk
        self.assertTrue(os.path.isfile(validated["font_family"]))


class TestTemplateMapping(TestCase):
    """Test template mapping and generator wiring."""

    def test_mapping_has_seven_generations(self):
        mapping = get_template_mapping()
        self.assertEqual(set(mapping.keys()), {"1", "2", "3", "4", "5", "6", "7"})

    def test_mapping_points_to_prototype_generators(self):
        mapping = get_template_mapping()
        for gen, config in mapping.items():
            self.assertEqual(config["function"], f"generate_prototype_{gen}gen_preview")
            self.assertEqual(
                config["module"],
                f"apps.generator.utils.prototype.prototype_image_{gen}generator",
            )

    def test_mapping_modules_are_importable(self):
        mapping = get_template_mapping()
        for config in mapping.values():
            module = importlib.import_module(config["module"])
            self.assertTrue(callable(getattr(module, config["function"])))


class TestImageGeneration(TestCase):
    """Wiring-level tests for the prototype generators."""

    def setUp(self):
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

    def test_1gen_generator_importable(self):
        from apps.generator.utils.prototype.prototype_image_1generator import (
            generate_prototype_1gen_preview,
        )

        self.assertTrue(callable(generate_prototype_1gen_preview))

    def test_2gen_generator_importable(self):
        from apps.generator.utils.prototype.prototype_image_2generator import (
            generate_prototype_2gen_preview,
        )

        self.assertTrue(callable(generate_prototype_2gen_preview))

    def test_generator_signature_matches_standard_call(self):
        import inspect

        from apps.generator.utils.prototype.prototype_image_2generator import (
            generate_prototype_2gen_preview,
        )

        params = list(inspect.signature(generate_prototype_2gen_preview).parameters)
        self.assertEqual(
            params[:4],
            ["primary_individual", "family_data", "template", "user_settings"],
        )

    def test_2gen_missing_parents_does_not_crash(self):
        """The 2gen generator must tolerate missing parents."""
        from apps.generator.utils.prototype import prototype_image_2generator as gen2

        person = PersonData(
            id="I1", full_name="No Parents", given_name="No", surname="Parents"
        )
        family_data = {"individuals": {"I1": person}}

        mock_img = MagicMock()
        mock_img.width = 100
        mock_img.height = 100
        mock_img.format = "PNG"
        mock_img.__enter__.return_value = mock_img
        mock_img.save = Mock(side_effect=lambda file: file.write(b"png-data"))
        mock_draw = MagicMock()

        with patch.object(gen2, "Image", return_value=mock_img), patch.object(
            gen2, "Drawing", return_value=mock_draw
        ), patch.object(gen2, "get_chart_buffer", return_value=BytesIO(b"overlay")), patch.object(
            gen2, "print_individual"
        ) as mock_print:
            result = gen2.generate_prototype_2gen_preview(person, family_data)

        self.assertIsInstance(result, BytesIO)
        # No parents -> neither parent is rendered
        mock_print.assert_not_called()


class TestTemplatePreviewEndpoint(TestCase):
    """Test the generic template preview endpoint."""

    def setUp(self):
        self.client = Client()
        self.gedcom_file = GedcomFile.objects.create(
            file="test.gedcom",
            home_person_id="I1",
            parsed_data={
                "individuals": {
                    "I1": {
                        "id": "I1",
                        "full_name": "John Doe",
                        "given_name": "John",
                        "surname": "Doe",
                        "father": "I2",
                        "mother": "I3",
                    },
                    "I2": {
                        "id": "I2",
                        "full_name": "Robert Doe",
                        "given_name": "Robert",
                        "surname": "Doe",
                    },
                    "I3": {
                        "id": "I3",
                        "full_name": "Jane Smith",
                        "given_name": "Jane",
                        "surname": "Smith",
                    },
                },
                "families": {},
            },
        )
        set_client_session(
            self.client,
            current_gedcom_file_id=self.gedcom_file.id,
            selected_individual_id="I1",
        )

    @patch("apps.hud.views_simple_buffered.get_chart_buffer")
    def test_get_preview_success(self, mock_get_chart_buffer):
        mock_get_chart_buffer.return_value = BytesIO(b"fake_image_data")

        response = self.client.get(
            "/hud/get-template-preview/1/", {"individual_id": "I1"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        mock_get_chart_buffer.assert_called_once()
        self.assertEqual(mock_get_chart_buffer.call_args.args[3], 1)

    @patch("apps.hud.views_simple_buffered.get_chart_buffer")
    def test_post_preview_with_settings(self, mock_get_chart_buffer):
        mock_get_chart_buffer.return_value = BytesIO(b"fake_image_data")
        payload = {
            "individual_id": "I1",
            "user_settings": {
                "primary_name_font_size": 100,
                "primary_background_color": "#FF0000",
            },
        }

        response = self.client.post(
            "/hud/get-template-preview/2/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        _, _, user_settings, generation = mock_get_chart_buffer.call_args.args
        self.assertEqual(user_settings["primary_name_font_size"], 100)
        self.assertEqual(generation, 2)

    @patch("apps.hud.views_simple_buffered.get_chart_buffer")
    def test_invalid_template_returns_500(self, mock_get_chart_buffer):
        mock_get_chart_buffer.side_effect = ValueError("Unsupported generation: 999")

        response = self.client.get(
            "/hud/get-template-preview/999/", {"individual_id": "I1"}
        )

        self.assertEqual(response.status_code, 500)

    def test_non_numeric_template_returns_400(self):
        response = self.client.get(
            "/hud/get-template-preview/abc/", {"individual_id": "I1"}
        )
        self.assertEqual(response.status_code, 400)

    def test_preview_without_session_file_returns_400(self):
        client = Client()
        response = client.get(
            "/hud/get-template-preview/1/", {"individual_id": "I1"}
        )
        self.assertEqual(response.status_code, 400)


class TestSettingsPersistence(TestCase):
    """Test settings persistence across template switches."""

    def setUp(self):
        self.client = Client()
        self.gedcom_file = GedcomFile.objects.create(
            file="test.gedcom",
            home_person_id="I1",
            parsed_data={
                "individuals": {
                    "I1": {
                        "id": "I1",
                        "full_name": "John Doe",
                        "given_name": "John",
                        "surname": "Doe",
                    }
                },
                "families": {},
            },
        )

    def test_save_settings_requires_session(self):
        response = self.client.post(
            "/hud/save-settings/",
            data={
                "individual_id": "I1",
                "template": "1",
                "primary_name_font_size": "91",
            },
        )
        # No file/individual selected in session -> 400
        self.assertEqual(response.status_code, 400)

    @patch("apps.hud.views_simple_buffered.apply_settings_change")
    def test_save_settings_with_session(self, mock_apply):
        set_client_session(
            self.client,
            current_gedcom_file_id=self.gedcom_file.id,
            selected_individual_id="I1",
        )

        response = self.client.post(
            "/hud/save-settings/",
            data=json.dumps({"settings": {"primary_name_font_size": 91}}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        mock_apply.assert_called_once()

    @patch("apps.hud.views_simple_buffered.get_chart_buffer")
    def test_session_settings_are_passed_to_buffer_layer(self, mock_get_chart_buffer):
        set_client_session(
            self.client,
            current_gedcom_file_id=self.gedcom_file.id,
            selected_individual_id="I1",
            hud_settings={"primary_name_font_size": 91},
        )
        mock_get_chart_buffer.return_value = BytesIO(b"fake_image_data")

        response = self.client.get(
            "/hud/get-template-preview/1/", {"individual_id": "I1"}
        )

        # Session settings flow through to the buffer layer.
        _, _, user_settings, _ = mock_get_chart_buffer.call_args.args
        self.assertEqual(user_settings["primary_name_font_size"], 91)
        self.assertEqual(response.status_code, 200)
