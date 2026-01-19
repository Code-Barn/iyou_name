from io import BytesIO

from django.test import TestCase

from apps.generator.models import ChartSettings
from apps.generator.utils.image_1generator import generate_family_tree
from apps.parser.models import PersonData

class Image1GeneratorTestCase(TestCase):
    """Test cases for image_1generator.py."""

    def setUp(self):
        """Set up test data."""
        self.primary_individual = PersonData(
            id="I1",
            given_name="John",
            surname="Doe",
            full_name="John Doe",
            birth_date="1950",
            birth_place="New York",
            death_date="2020",
        )
        self.family_data = {"individuals": {}}
        self.family_data["individuals"]["I1"] = self.primary_individual

        # Create a ChartSettings object
        self.chart_settings = ChartSettings.objects.create(
            initial_translate_x=0,
            initial_translate_y=0,
            subject_translate_x=0,
            subject_translate_y=0,
            font_family="Arial",
            primary_name_font_size=13,
            primary_info_font_size=13,
            default_stroke_width=0.5,
            stroke_antialias=True,
            primary_font_color="white",
            primary_birth_color="white",
            primary_place_color="white",
            primary_death_color="white",
            primary_stroke_color="white",
            primary_name_x=0,
            primary_name_y=0,
            primary_name_rotate=-45,
            primary_birth_x=0,
            primary_birth_y=135,
            primary_birth_rotate=45,
            primary_place_x=0,
            primary_place_y=90,
            primary_place_rotate=-45,
        )

    def test_generate_family_tree_with_settings(self):
        """Test that generate_family_tree works with ChartSettings."""
        try:
            # Call the generator with ChartSettings
            image_buffer = generate_family_tree(
                self.primary_individual,
                self.family_data,
                template="1gen",
                chart_settings=self.chart_settings,
            )
            self.assertIsInstance(image_buffer, BytesIO)
            self.assertGreater(image_buffer.getbuffer().nbytes, 0)
        except Exception as e:
            self.fail(f"generate_family_tree raised an exception: {e}")

    def test_generate_family_tree_without_settings(self):
        """Test that generate_family_tree works without ChartSettings."""
        try:
            # Call the generator without ChartSettings
            image_buffer = generate_family_tree(
                self.primary_individual,
                self.family_data,
                template="1gen",
            )
            self.assertIsInstance(image_buffer, BytesIO)
            self.assertGreater(image_buffer.getbuffer().nbytes, 0)
        except Exception as e:
            self.fail(f"generate_family_tree raised an exception: {e}")

    def test_generate_family_tree_preview(self):
        """Test that generate_family_tree works for live preview."""
        try:
            # Call the generator for live preview
            image_buffer = generate_family_tree(
                self.primary_individual,
                self.family_data,
                template="preview",
                chart_settings=self.chart_settings,
            )
            self.assertIsInstance(image_buffer, BytesIO)
            self.assertGreater(image_buffer.getbuffer().nbytes, 0)
        except Exception as e:
            self.fail(f"generate_family_tree raised an exception: {e}")
