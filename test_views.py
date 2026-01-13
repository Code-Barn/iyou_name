import os

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

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
        # Create a test GEDCOM file
        gedcom_file = GedcomFile.objects.create(
            user=self.user,
            file="test.ged",
            parsed_data={
                "individuals": {
                    "I1": {
                        "id": "I1",
                        "full_name": "John Doe",
                        "given_name": "John",
                        "surname": "Doe",
                        "birth_date": "1980-01-01",
                        "birth_place": "New York",
                    }
                },
                "families": {},
                "root_individuals": ["I1"],
            },
        )

        # Set the current GEDCOM file in session
        session = self.client.session
        session["current_gedcom_file_id"] = gedcom_file.id
        session.save()

        response = self.client.get(reverse("browse:browse_individuals"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "browse/browse_individuals.html")

    def test_hud_display_view(self):
        """Test HUD display view"""
        # Create a test GEDCOM file
        gedcom_file = GedcomFile.objects.create(
            user=self.user,
            file="test.ged",
            parsed_data={
                "individuals": {
                    "I1": {
                        "id": "I1",
                        "full_name": "John Doe",
                        "given_name": "John",
                        "surname": "Doe",
                        "birth_date": "1980-01-01",
                        "sex": "M",
                    },
                },
                "families": {},
                "root_individuals": ["I1"],
            },
            home_person_id="I1",
            is_processed=True,
        )

        session = self.client.session
        session["current_gedcom_file_id"] = gedcom_file.id
        session["selected_individual_id"] = "I1"
        session.save()

        response = self.client.get(reverse("hud:display_tree"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hud/display_tree.html")

    def test_charts_adjust_output_view(self):
        """Test charts adjust output view"""
        # Create a test GEDCOM file
        gedcom_file = GedcomFile.objects.create(
            user=self.user,
            file="test.ged",
            parsed_data={
                "individuals": {
                    "I1": {
                        "id": "I1",
                        "full_name": "John Doe",
                        "given_name": "John",
                        "surname": "Doe",
                        "birth_date": "1980-01-01",
                        "sex": "M",
                    },
                },
                "families": {},
                "root_individuals": ["I1"],
            },
            home_person_id="I1",
            is_processed=True,
        )

        session = self.client.session
        session["current_gedcom_file_id"] = gedcom_file.id
        session["selected_individual_id"] = "I1"
        session.save()

        response = self.client.get(reverse("hud:display_tree"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hud/display_tree.html")

    def test_users_profile_view(self):
        """Test users profile view"""
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
