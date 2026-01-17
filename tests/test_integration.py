import os
import tempfile

import django
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.generator.models import GedcomFile

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


django.setup()


class IntegrationTests(TestCase):
    """Test the integration between different apps"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        # Create a test GEDCOM file
        self.test_gedcom_content = """0 HEAD
1 SOUR MYFAMILY
2 VERS 1.0
1 DATE 1 JAN 2023
2 TIME 12:00:00
1 SUBM @SUBM1@
0 @SUBM1@ SUBM
1 NAME Test User
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1 JAN 1950
1 DEAT
2 DATE 1 JAN 2020
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
0 TRLR"""

    def test_upload_to_browse_flow(self):
        """Test the flow from upload to browse functionality"""

        # Step 1: Access upload page
        response = self.client.get(reverse("upload:upload_file"))
        self.assertEqual(response.status_code, 200)

        # Step 2: Upload a GEDCOM file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.test_gedcom_content.encode())
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                response = self.client.post(
                    reverse("upload:upload_file"),
                    {"gedcom_file": f},
                    format="multipart",
                )

            # Should redirect to select individual or show success
            self.assertIn(response.status_code, [200, 302])

            # Step 3: Access browse functionality
            response = self.client.get(reverse("browse:browse_individuals"))
            self.assertEqual(response.status_code, 200)

        finally:
            os.unlink(temp_file_path)

    def test_browse_to_charts_flow(self):
        """Test the flow from browse to charts functionality"""

        # Create a GEDCOM file in the database
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
                        "birth_date": "1 JAN 1950",
                        "death_date": "1 JAN 2020",
                    }
                },
                "families": {},
                "root_individuals": ["I1"],
            },
            home_person_id="I1",
            is_processed=True,
        )

        # Set the file in session
        session = self.client.session
        session["current_gedcom_file_id"] = gedcom_file.id
        session.save()

        # Step 1: Access individual detail
        response = self.client.get(reverse("browse:individual_detail", args=["I1"]))
        self.assertEqual(response.status_code, 200)

        # Step 2: Access chart adjustment
        response = self.client.get(reverse("hud:display_tree"))
        self.assertEqual(response.status_code, 200)

        # Step 3: Access chart generation
        response = self.client.get(
            reverse("charts:generate_chart", args=[gedcom_file.id, "I1"])
        )
        self.assertEqual(response.status_code, 200)

    def test_user_profile_with_files(self):
        """Test user profile shows uploaded files"""

        # Create a GEDCOM file for the user
        GedcomFile.objects.create(user=self.user, file="test.ged", is_processed=True)

        # Access user profile
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test.ged")
