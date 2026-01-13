from django.contrib.staticfiles.finders import find
from django.test import TestCase


class StaticFilesTests(TestCase):
    """Test static files are properly configured"""

    def test_core_static_files(self):
        """Test core app static files"""
        files = [
            "core/favicon.ico",
            "core/images/tinynamelogo.png",
            "core/css/style.css",
        ]

        for file_path in files:
            with self.subTest(file=file_path):
                found = find(file_path)
                self.assertIsNotNone(found, f"Static file {file_path} not found")

    def test_hud_static_files(self):
        """Test HUD app static files"""
        files = ["hud/css/hud.css", "hud/js/hud.js"]

        for file_path in files:
            with self.subTest(file=file_path):
                found = find(file_path)
                self.assertIsNotNone(found, f"Static file {file_path} not found")

    def test_charts_static_files(self):
        """Test charts app static files"""
        files = [
            "charts/images/base_image_templates/US_LETTER_4GEN_BW.pdf",
            "charts/images/base_image_templates/US_LETTER_5GEN_BW.pdf",
        ]

        for file_path in files:
            with self.subTest(file=file_path):
                found = find(file_path)
                self.assertIsNotNone(found, f"Static file {file_path} not found")
