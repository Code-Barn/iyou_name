from django.template.loader import get_template
from django.test import TestCase


class TemplateTests(TestCase):
    """Test template existence and inheritance"""

    def test_core_templates(self):
        """Test core app templates"""
        template = get_template("core/base.html")
        self.assertIsNotNone(template)

    def test_upload_templates(self):
        """Test upload app templates"""
        templates = [
            "upload/upload_file.html",
            "upload/error.html",
        ]

        for template_name in templates:
            with self.subTest(template=template_name):
                template = get_template(template_name)
                self.assertIsNotNone(template)

    def test_browse_templates(self):
        """Test browse app templates"""
        templates = [
            "browse/browse_individuals.html",
            "browse/individual_detail.html",
            "browse/error.html",
        ]

        for template_name in templates:
            with self.subTest(template=template_name):
                template = get_template(template_name)
                self.assertIsNotNone(template)

    def test_hud_templates(self):
        """Test HUD app templates"""
        templates = [
            "hud/display_tree.html",
            "hud/error.html",
            "hud/components/hud.html",
        ]

        for template_name in templates:
            with self.subTest(template=template_name):
                template = get_template(template_name)
                self.assertIsNotNone(template)

    def test_charts_templates(self):
        """Test charts app templates"""
        templates = [
            "charts/generate_chart.html",
            "charts/generate_success.html",
            "charts/error.html",
        ]

        for template_name in templates:
            with self.subTest(template=template_name):
                template = get_template(template_name)
                self.assertIsNotNone(template)

    def test_users_templates(self):
        """Test users app templates"""
        templates = [
            "users/profile.html",
            "users/register.html",
            "users/error.html",
            "users/auth/login.html",
            "users/auth/password_change.html",
            "users/auth/password_change_done.html",
            "users/auth/password_reset.html",
            "users/auth/password_reset_done.html",
            "users/auth/password_reset_confirm.html",
            "users/auth/password_reset_complete.html",
        ]

        for template_name in templates:
            with self.subTest(template=template_name):
                template = get_template(template_name)
                self.assertIsNotNone(template)
