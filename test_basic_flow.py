"""
Basic flow test to verify the new URL structure and view functionality
"""

import os

import django
from django.test import RequestFactory, TestCase

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore

from apps.generator.models import GedcomFile
from apps.selector.views import confirm_selection, select_individual
from apps.users.views import profile


class BasicFlowTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = SessionStore()
        self.session.save()

        # Create a test user with unique username
        import uuid

        self.username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.user = User.objects.create_user(
            username=self.username,
            password="testpass123",
            email=f"{self.username}@example.com",
        )

        # Create a test GEDCOM file
        self.gedcom_file = GedcomFile.objects.create(
            user=self.user,
            file=f"test_{self.username}.ged",
            parsed_data={
                "individuals": {
                    "I1": {
                        "id": "I1",
                        "full_name": "John Doe",
                        "given_name": "John",
                        "surname": "Doe",
                        "birth_date": "1980-01-01",
                        "birth_place": "New York",
                        "sex": "M",
                    },
                    "I2": {
                        "id": "I2",
                        "full_name": "Jane Doe",
                        "given_name": "Jane",
                        "surname": "Doe",
                        "birth_date": "1985-05-15",
                        "birth_place": "Los Angeles",
                        "sex": "F",
                    },
                },
                "families": {},
                "root_individuals": ["I1"],
            },
            home_person_id="I1",
            is_processed=True,
        )

    def test_selector_view(self):
        """Test the selector view"""
        request = self.factory.get(f"/selector/select/{self.gedcom_file.id}/")
        request.user = self.user
        request.session = self.session
        request.session["current_gedcom_file_id"] = self.gedcom_file.id
        request.session.save()

        response = select_individual(request, self.gedcom_file.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Jane Doe")

    def test_confirm_selection_set_home(self):
        """Test setting home person"""
        request = self.factory.post(
            f"/selector/confirm/{self.gedcom_file.id}/",
            {"individual_id": "I2", "action": "set_home"},
        )
        request.user = self.user
        request.session = self.session
        request.session.save()

        response = confirm_selection(request, self.gedcom_file.id)
        self.assertEqual(response.status_code, 302)  # Redirect

        # Check that home person was updated
        self.gedcom_file.refresh_from_db()
        self.assertEqual(self.gedcom_file.home_person_id, "I2")

    def test_confirm_selection_generate(self):
        """Test generating chart flow"""
        request = self.factory.post(
            f"/selector/confirm/{self.gedcom_file.id}/",
            {"individual_id": "I1", "action": "generate"},
        )
        request.user = self.user
        request.session = self.session
        request.session.save()

        response = confirm_selection(request, self.gedcom_file.id)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(request.session["selected_individual_id"], "I1")

    def tearDown(self):
        """No manual cleanup needed - Django test framework handles it"""
        pass

    def test_user_profile_view(self):
        """Test user profile view"""
        request = self.factory.get("/users/profile/")
        request.user = self.user
        request.session = self.session
        request.session.save()

        response = profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.username)
        self.assertContains(response, f"test_{self.username}.ged")


if __name__ == "__main__":
    import unittest

    unittest.main()
