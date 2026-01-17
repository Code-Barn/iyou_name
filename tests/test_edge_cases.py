"""
Comprehensive edge case tests for the restructured namechart application
"""

import os

import django
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory, TestCase

from apps.charts.views import generate_chart
from apps.generator.models import GedcomFile
from apps.hud.views import display_tree_hud
from apps.selector.views import confirm_selection, select_individual
from apps.users.views import profile

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


class EdgeCaseTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = SessionStore()
        self.session.save()

        # Create test user
        self.user = User.objects.create_user(
            username="edge_test_user", password="testpass123"
        )

        # Create test GEDCOM files
        self.normal_file = GedcomFile.objects.create(
            user=self.user,
            file="normal.ged",
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

        self.empty_file = GedcomFile.objects.create(
            user=self.user,
            file="empty.ged",
            parsed_data={
                "individuals": {},
                "families": {},
                "root_individuals": [],
            },
            home_person_id=None,
            is_processed=True,
        )

        self.unprocessed_file = GedcomFile.objects.create(
            user=self.user,
            file="unprocessed.ged",
            parsed_data=None,
            home_person_id=None,
            is_processed=False,
        )

        # Create another user for access control tests
        self.other_user = User.objects.create_user(
            username="other_user", password="testpass123"
        )

    def test_selector_with_empty_file(self):
        """Test selector view with empty GEDCOM file"""
        request = self.factory.get(f"/selector/select/{self.empty_file.id}/")
        request.user = self.user
        request.session = self.session
        request.session["current_gedcom_file_id"] = self.empty_file.id
        request.session.save()

        response = select_individual(request, self.empty_file.id)
        self.assertEqual(response.status_code, 200)
        # Should show empty table or appropriate message
        self.assertContains(response, "individuals")

    def test_selector_with_unprocessed_file(self):
        """Test selector view with unprocessed GEDCOM file"""
        request = self.factory.get(f"/selector/select/{self.unprocessed_file.id}/")
        request.user = self.user
        request.session = self.session
        request.session["current_gedcom_file_id"] = self.unprocessed_file.id
        request.session.save()

        response = select_individual(request, self.unprocessed_file.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "File not processed yet")

    def test_selector_access_control(self):
        """Test that users can only access their own files"""
        request = self.factory.get(f"/selector/select/{self.normal_file.id}/")
        request.user = self.other_user  # Different user
        request.session = self.session
        request.session.save()

        response = select_individual(request, self.normal_file.id)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_confirm_selection_invalid_individual(self):
        """Test selection confirmation with invalid individual ID"""
        request = self.factory.post(
            f"/selector/confirm/{self.normal_file.id}/",
            {"individual_id": "INVALID_ID", "action": "set_home"},
        )
        request.user = self.user
        request.session = self.session
        request.session.save()

        response = confirm_selection(request, self.normal_file.id)
        # Should handle gracefully, likely redirect or show error
        self.assertIn(response.status_code, [302, 200])

    def test_hud_without_selected_individual(self):
        """Test HUD view without selected individual in session"""
        request = self.factory.get("/hud/display-tree/")
        request.user = self.user
        request.session = self.session
        request.session["current_gedcom_file_id"] = self.normal_file.id
        # No selected_individual_id in session
        request.session.save()

        response = display_tree_hud(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No individual selected")

    def test_hud_with_invalid_file(self):
        """Test HUD view with invalid file ID"""
        request = self.factory.get("/hud/display-tree/")
        request.user = self.user
        request.session = self.session
        request.session["current_gedcom_file_id"] = 99999  # Invalid ID
        request.session["selected_individual_id"] = "I1"
        request.session.save()

        response = display_tree_hud(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GEDCOM file not found")

    def test_chart_generation_without_file_selection(self):
        """Test chart generation without proper file selection"""
        request = self.factory.get("/charts/generate/")
        request.user = self.user
        request.session = self.session
        # No file or individual selected
        request.session.save()

        # Pass dummy values for file_id and individual_id to match the function signature
        response = generate_chart(request, file_id=99999, individual_id="INVALID_ID")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GEDCOM file not found")

    def test_profile_with_no_files(self):
        """Test user profile with no uploaded files"""
        # Create user with no files
        empty_user = User.objects.create_user(
            username="empty_user", password="testpass123"
        )

        request = self.factory.get("/users/profile/")
        request.user = empty_user
        request.session = self.session
        request.session.save()

        response = profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No GEDCOM files uploaded yet")

    def test_selector_with_nonexistent_file(self):
        """Test selector with non-existent file ID"""
        request = self.factory.get("/selector/select/99999/")
        request.user = self.user
        request.session = self.session
        request.session.save()

        response = select_individual(request, 99999)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GEDCOM file not found")

    def test_confirm_selection_without_post_data(self):
        """Test selection confirmation without POST data"""
        request = self.factory.get(f"/selector/confirm/{self.normal_file.id}/")
        request.user = self.user
        request.session = self.session
        request.session.save()

        response = confirm_selection(request, self.normal_file.id)
        self.assertEqual(response.status_code, 302)  # Should redirect


if __name__ == "__main__":
    import unittest

    unittest.main()
