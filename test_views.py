from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.generator.models import GedcomFile


class ViewTests(TestCase):
    """Test view functionality across all apps"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

    def test_upload_file_view(self):
        """Test upload file view"""
        response = self.client.get(reverse("upload:upload_file"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "upload/upload_file.html")

    def test_browse_individuals_view(self):
        """Test browse individuals view"""
        # Create a test GEDCOM file in session
        session = self.client.session
        session["current_gedcom_file_id"] = 1
        session.save()

        response = self.client.get(reverse("browse:browse_individuals"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "browse/browse_individuals.html")

    def test_hud_display_view(self):
        """Test HUD display view"""
        session = self.client.session
        session["current_gedcom_file_id"] = 1
        session.save()

        response = self.client.get(reverse("hud:display_tree"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hud/display_tree.html")

    def test_charts_adjust_output_view(self):
        """Test charts adjust output view"""
        session = self.client.session
        session["current_gedcom_file_id"] = 1
        session.save()

        response = self.client.get(reverse("charts:adjust_output"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "charts/adjust_output.html")

    def test_users_profile_view(self):
        """Test users profile view"""
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
