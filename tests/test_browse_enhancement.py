"""
Test for the browse enhancement: logged-out users with files should see browse page
"""

import os

import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory, TestCase

from apps.generator.models import GedcomFile
from apps.upload.views import upload_and_generate

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

User = get_user_model()


class BrowseEnhancementTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = SessionStore()
        self.session.save()

        # Create anonymous GEDCOM file
        self.anonymous_file = GedcomFile.objects.create(
            user=None,  # Anonymous user
            file="anonymous_test.ged",
            parsed_data={
                "individuals": {
                    "I1": {
                        "id": "I1",
                        "full_name": "Test Person",
                        "given_name": "Test",
                        "surname": "Person",
                        "birth_date": "1980-01-01",
                        "sex": "M",
                    },
                },
                "families": {},
                "root_individuals": ["I1"],
            },
            home_person_id=None,
            is_processed=True,
        )

    def test_anonymous_user_with_file_redirects_to_browse(self):
        """Test that anonymous users with files are redirected to browse"""
        # Set up session with file ID
        self.session["current_gedcom_file_id"] = self.anonymous_file.id
        self.session.save()

        # Create request to home page
        request = self.factory.get("/")
        request.user = AnonymousUser()  # Anonymous user
        request.session = self.session

        # Call the upload_and_generate view (handles home page)
        response = upload_and_generate(request)

        # Should redirect to browse view
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/browse/")

    def test_anonymous_user_without_file_sees_upload(self):
        """Test that anonymous users without files see upload page"""
        # Create request to home page without file in session
        request = self.factory.get("/")
        request.user = AnonymousUser()  # Anonymous user
        request.session = self.session  # Empty session

        # Call the upload_and_generate view
        # Mock the TEMPLATE_MAPPING since we removed it from upload views
        from apps.hud.views import get_template_mapping

        request.TEMPLATE_MAPPING = get_template_mapping()

        response = upload_and_generate(request)

        # Should render upload page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload Your GEDCOM File")

    def test_authenticated_user_redirects_to_profile(self):
        """Test that authenticated users still redirect to profile"""
        # Create authenticated user with unique username
        import uuid

        username = f"testuser_{uuid.uuid4().hex[:8]}"
        user = User.objects.create_user(username=username, password="test123")

        # Set up session with file ID
        self.session["current_gedcom_file_id"] = self.anonymous_file.id
        self.session.save()

        # Create request to home page
        request = self.factory.get("/")
        request.user = user  # Authenticated user
        request.session = self.session

        # Call the upload_and_generate view
        response = upload_and_generate(request)

        # Should redirect to profile
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/users/profile/")


if __name__ == "__main__":
    import unittest

    unittest.main()
