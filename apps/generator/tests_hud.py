"""
Test suite for the HUD (Heads-Up Display) system
"""

import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.generator.models import GedcomFile, PersonData
from apps.generator.utils.gedcom_parser import parse_gedcom_data


class HUDTests(TestCase):
    """Test HUD functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Sample GEDCOM data
        self.sample_gedcom = """0 HEAD
1 SOUR Family Tree Builder
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1 Jan 1980
2 PLAC New York
1 DEAT
2 DATE 15 Dec 2020
2 PLAC Boston
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
1 BIRT
2 DATE 5 Mar 1982
2 PLAC Chicago
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I1@
"""

        # Parse the GEDCOM data
        self.family_data = parse_gedcom_data(self.sample_gedcom)

        # Create a GedcomFile instance and store parsed data
        self.gedcom_file = GedcomFile.objects.create(
            user=self.user,
            file="test.ged",
            parsed_data={
                "individuals": {
                    ind_id: person.to_dict()
                    for ind_id, person in self.family_data["individuals"].items()
                },
                "families": self.family_data["families"],
                "root_individuals": self.family_data["root_individuals"],
            },
            home_person_id="I1",
            is_processed=True,
        )

        # Set up session
        self.session = self.client.session
        self.session["current_gedcom_file_id"] = self.gedcom_file.id
        self.session["selected_individual_id"] = "I1"
        self.session["selected_template"] = "4"
        self.session.save()

    def test_hud_family_data_api(self):
        """Test HUD family data API endpoint"""
        # Log in the user
        self.client.login(username="testuser", password="testpass123")

        # Make request to HUD family data endpoint
        response = self.client.get(reverse("generator:hud_family_data"))

        # Check response status
        self.assertEqual(response.status_code, 200)

        # Parse JSON response
        data = response.json()

        # Verify response structure
        self.assertIn("individuals", data)
        self.assertIn("families", data)
        self.assertIn("root_individuals", data)
        self.assertIn("current_individual", data)
        self.assertIn("current_template", data)

        # Verify individuals data
        self.assertEqual(len(data["individuals"]), 2)

        # Check first individual
        individual1 = data["individuals"][0]
        self.assertEqual(individual1["full_name"], "John Doe")
        self.assertEqual(individual1["birth_date"], "1 Jan 1980")
        self.assertEqual(individual1["birth_place"], "New York")

        # Check second individual
        individual2 = data["individuals"][1]
        self.assertEqual(individual2["full_name"], "Jane Smith")
        self.assertEqual(individual2["birth_date"], "5 Mar 1982")
        self.assertEqual(individual2["birth_place"], "Chicago")

    def test_hud_preview_api(self):
        """Test HUD preview API endpoint"""
        # Log in the user
        self.client.login(username="testuser", password="testpass123")

        # Make request to HUD preview endpoint
        response = self.client.get(
            reverse("generator:hud_preview"),
            {"individual_id": "I1", "template": "4", "generations": "4"},
        )

        # Check response status
        self.assertEqual(response.status_code, 200)

        # Parse JSON response
        data = response.json()

        # Verify response structure
        self.assertIn("primary", data)
        self.assertIn("template_id", data)
        self.assertIn("template_name", data)
        self.assertIn("generations", data)
        self.assertIn("family_count", data)
        self.assertIn("relationships", data)

        # Verify primary individual data
        self.assertEqual(data["primary"]["name"], "John Doe")
        self.assertEqual(data["primary"]["birth_date"], "1 Jan 1980")
        self.assertEqual(data["primary"]["birth_place"], "New York")

        # Verify other data
        self.assertEqual(data["template_id"], "4")
        self.assertEqual(data["generations"], 4)
        self.assertEqual(data["family_count"], 2)

    def test_hud_preview_api_missing_individual(self):
        """Test HUD preview API with missing individual_id parameter"""
        # Log in the user
        self.client.login(username="testuser", password="testpass123")

        # Make request without individual_id
        response = self.client.get(
            reverse("generator:hud_preview"), {"template": "4", "generations": "4"}
        )

        # Check response status
        self.assertEqual(response.status_code, 400)

        # Parse JSON response
        data = response.json()

        # Verify error response
        self.assertIn("error", data)
        self.assertEqual(data["error"], "individual_id parameter is required")

    def test_hud_preview_api_invalid_individual(self):
        """Test HUD preview API with invalid individual_id"""
        # Log in the user
        self.client.login(username="testuser", password="testpass123")

        # Make request with invalid individual_id
        response = self.client.get(
            reverse("generator:hud_preview"),
            {"individual_id": "INVALID", "template": "4", "generations": "4"},
        )

        # Check response status
        self.assertEqual(response.status_code, 404)

        # Parse JSON response
        data = response.json()

        # Verify error response
        self.assertIn("error", data)
        self.assertIn("INVALID", data["error"])

    def test_hud_settings_api_get(self):
        """Test HUD settings API GET endpoint"""
        # Log in the user
        self.client.login(username="testuser", password="testpass123")

        # Make GET request to settings endpoint
        response = self.client.get(reverse("generator:hud_settings"))

        # Check response status
        self.assertEqual(response.status_code, 200)

        # Parse JSON response
        data = response.json()

        # Verify response structure
        self.assertIn("individual_id", data)
        self.assertIn("template", data)
        self.assertIn("generations", data)
        self.assertIn("chart_parameters", data)

        # Verify session data
        self.assertEqual(data["individual_id"], "I1")
        self.assertEqual(data["template"], "4")

    def test_hud_settings_api_post(self):
        """Test HUD settings API POST endpoint"""
        # Log in the user
        self.client.login(username="testuser", password="testpass123")

        # New settings data
        new_settings = {
            "individual_id": "I2",
            "template": "1",
            "generations": "1",
            "chart_parameters": {"color_scheme": "black_and_white"},
        }

        # Make POST request to settings endpoint
        response = self.client.post(
            reverse("generator:hud_settings"),
            data=json.dumps(new_settings),
            content_type="application/json",
        )

        # Check response status
        self.assertEqual(response.status_code, 200)

        # Parse JSON response
        data = response.json()

        # Verify success response
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["message"], "Settings saved")

    def test_hud_no_family_data(self):
        """Test HUD endpoints when no family data is available"""
        # Create a new client without session data
        client = Client()

        # Test family data endpoint
        response = client.get(reverse("generator:hud_family_data"))
        self.assertEqual(response.status_code, 404)

        data = response.json()
        self.assertIn("error", data)
        self.assertIn("No family data found", data["error"])


if __name__ == "__main__":
    import unittest

    unittest.main()
