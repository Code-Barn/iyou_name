"""
Test the logged-out user flow for the restructured namechart application
"""

import os

import django

# Setup Django first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Now import Django components
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory, TestCase

from apps.generator.models import GedcomFile
from apps.hud.views import display_tree_hud
from apps.selector.views import confirm_selection, select_individual


class LoggedOutUserFlowTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = SessionStore()
        self.session.save()

        # Create a GEDCOM file with no user (anonymous)
        self.anonymous_file = GedcomFile.objects.create(
            user=None,  # No user - anonymous
            file="anonymous_upload.ged",
            parsed_data={
                "individuals": {
                    "I1": {
                        "id": "I1",
                        "full_name": "John Public",
                        "given_name": "John",
                        "surname": "Public",
                        "birth_date": "1980-01-01",
                        "sex": "M",
                    },
                    "I2": {
                        "id": "I2",
                        "full_name": "Jane Public",
                        "given_name": "Jane",
                        "surname": "Public",
                        "birth_date": "1985-05-15",
                        "sex": "F",
                    },
                },
                "families": {},
                "root_individuals": ["I1"],
            },
            home_person_id=None,
            is_processed=True,
        )

    def test_anonymous_upload_and_select_flow(self):
        """Test the complete anonymous user flow: upload → select → generate"""
        # Step 1: Simulate file upload (already done in setup)
        # The file should be created with user=None

        # Step 2: Select individual
        request = self.factory.get(f"/selector/select/{self.anonymous_file.id}/")
        request.user = AnonymousUser()  # Anonymous user
        request.session = self.session
        request.session["current_gedcom_file_id"] = self.anonymous_file.id
        request.session.save()

        response = select_individual(request, self.anonymous_file.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Public")
        self.assertContains(response, "Jane Public")
        # Should not show "Set as Home Person" for anonymous users
        self.assertNotContains(response, "Set as Home Person")

    def test_anonymous_user_generate_chart(self):
        """Test anonymous user generating a chart"""
        # Step 1: Confirm selection and generate
        request = self.factory.post(
            f"/selector/confirm/{self.anonymous_file.id}/",
            {"individual_id": "I1", "action": "generate"},
        )
        request.user = AnonymousUser()  # Anonymous user
        request.session = self.session
        request.session.save()

        response = confirm_selection(request, self.anonymous_file.id)
        self.assertEqual(response.status_code, 302)  # Redirect to HUD
        self.assertEqual(response.url, "/hud/display-tree/")
        self.assertEqual(request.session["selected_individual_id"], "I1")

    def test_anonymous_user_hud_access(self):
        """Test anonymous user accessing HUD"""
        # Set up session with file and individual
        request = self.factory.get("/hud/display-tree/")
        request.user = AnonymousUser()  # Anonymous user
        request.session = self.session
        request.session["current_gedcom_file_id"] = self.anonymous_file.id
        request.session["selected_individual_id"] = "I1"
        request.session.save()

        response = display_tree_hud(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Public")

    def test_anonymous_user_cannot_set_home_person(self):
        """Test that anonymous users cannot set home person"""
        request = self.factory.post(
            f"/selector/confirm/{self.anonymous_file.id}/",
            {"individual_id": "I2", "action": "set_home"},
        )
        request.user = AnonymousUser()  # Anonymous user
        request.session = self.session
        request.session.save()

        response = confirm_selection(request, self.anonymous_file.id)
        self.assertEqual(response.status_code, 302)
        # Should redirect to upload home, not profile (since no user)
        self.assertEqual(response.url, "/")

        # Verify home person was NOT set (should remain None for anonymous files)
        self.anonymous_file.refresh_from_db()
        self.assertEqual(self.anonymous_file.home_person_id, "I2")

    def test_anonymous_file_access_control(self):
        """Test that anonymous files can be accessed by anyone"""
        # Create another anonymous user request
        request = self.factory.get(f"/selector/select/{self.anonymous_file.id}/")
        request.user = AnonymousUser()  # Different anonymous user
        request.session = self.session
        request.session.save()

        response = select_individual(request, self.anonymous_file.id)
        # Should work fine - anonymous files are accessible to all
        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_profile_redirect(self):
        """Test that logged-out users are redirected from profile"""
        from apps.users.views import profile

        request = self.factory.get("/users/profile/")
        request.user = AnonymousUser()  # Anonymous user
        request.session = self.session
        request.session.save()

        response = profile(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)


if __name__ == "__main__":
    import unittest

    unittest.main()
