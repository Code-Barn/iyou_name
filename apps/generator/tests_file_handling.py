"""
Comprehensive test suite for the new file handling implementation
Tests all aspects of the file upload, processing, and management functionality
"""

import os
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from generator.models import GedcomFile, PersonData
from generator.utils.gedcom_parser import parse_gedcom_data


class FileHandlingComprehensiveTest(TestCase):
    """
    Comprehensive test suite for file handling functionality
    """

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

        # Create a simple GEDCOM file content for testing
        self.simple_gedcom = """0 HEAD
1 SOUR TEST
2 VERS 5.5
1 GEDC
2 VERS 5.5
1 CHAR ANSI
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1 JAN 1980
1 DEAT
2 DATE 15 DEC 2020
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
1 BIRT
2 DATE 15 MAR 1982
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
0 TRLR
"""

        self.complex_gedcom = """0 HEAD
1 SOUR TEST
2 VERS 5.5
1 GEDC
2 VERS 5.5
1 CHAR ANSI
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1 JAN 1980
2 PLAC New York, USA
1 DEAT
2 DATE 15 DEC 2020
2 PLAC Boston, USA
1 OCCU Software Engineer
1 TITL Dr.
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
1 BIRT
2 DATE 15 MAR 1982
2 PLAC Chicago, USA
1 OCCU Teacher
0 @I3@ INDI
1 NAME Jack /Doe/
1 SEX M
1 BIRT
2 DATE 10 APR 2005
2 PLAC Boston, USA
1 FAMC @F1@
0 @I4@ INDI
1 NAME Jill /Doe/
1 SEX F
1 BIRT
2 DATE 5 JUN 2008
2 PLAC Boston, USA
1 FAMC @F1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
1 CHIL @I4@
1 MARR
2 DATE 15 JUN 2000
2 PLAC Boston, USA
0 TRLR
"""

    def test_file_upload_basic(self):
        """Test basic file upload functionality"""
        print("\n=== Testing Basic File Upload ===")

        # Login the user
        self.client.login(username="testuser", password="testpass123")

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.simple_gedcom.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            # Upload the file
            with open(temp_file_path, "rb") as f:
                response = self.client.post("/", {"gedcom_file": f})

            # Check that upload was successful
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "generator/select_individual.html")

            # Check that GedcomFile was created
            gedcom_files = GedcomFile.objects.filter(user=self.user)
            self.assertEqual(gedcom_files.count(), 1)

            gedcom_file = gedcom_files.first()

            # Verify file properties
            self.assertTrue(gedcom_file.is_processed)
            self.assertIsNotNone(gedcom_file.parsed_data)
            self.assertIsNotNone(gedcom_file.home_person_id)
            self.assertIsNotNone(gedcom_file.processing_date)

            # Verify parsed data structure
            parsed_data = gedcom_file.parsed_data
            self.assertIn("individuals", parsed_data)
            self.assertIn("families", parsed_data)
            self.assertIn("root_individuals", parsed_data)

            # Verify individuals were parsed
            individuals = parsed_data["individuals"]
            self.assertEqual(len(individuals), 2)  # John and Jane

            # Verify John Doe
            john = individuals.get("I1")
            self.assertIsNotNone(john)
            self.assertEqual(john["full_name"], "John Doe")
            self.assertEqual(john["given_name"], "John")
            self.assertEqual(john["surname"], "Doe")

            print("✅ Basic file upload test passed")

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_complex_file_upload(self):
        """Test upload of complex GEDCOM file with relationships"""
        print("\n=== Testing Complex File Upload ===")

        self.client.login(username="testuser", password="testpass123")

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.complex_gedcom.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            # Upload the file
            with open(temp_file_path, "rb") as f:
                response = self.client.post("/", {"gedcom_file": f})

            self.assertEqual(response.status_code, 200)

            # Get the GedcomFile
            gedcom_file = GedcomFile.objects.filter(user=self.user).first()
            parsed_data = gedcom_file.parsed_data

            # Verify complex data was parsed correctly
            individuals = parsed_data["individuals"]
            self.assertEqual(len(individuals), 4)  # John, Jane, Jack, Jill

            # Verify John Doe has complete data
            john = individuals["I1"]
            self.assertEqual(john["full_name"], "John Doe")
            self.assertEqual(john["birth_date"], "1 JAN 1980")
            self.assertEqual(john["birth_place"], "New York, USA")
            self.assertEqual(john["death_date"], "15 DEC 2020")
            self.assertEqual(john["death_place"], "Boston, USA")
            self.assertEqual(john["occupation"], "Software Engineer")
            self.assertEqual(john["title"], "Dr.")

            # Verify family relationships
            self.assertEqual(john["spouse"], ["I2"])
            self.assertEqual(john["children"], ["I3", "I4"])

            # Verify Jane Smith
            jane = individuals["I2"]
            self.assertEqual(jane["full_name"], "Jane Smith")
            self.assertEqual(jane["spouse"], ["I1"])
            self.assertEqual(jane["children"], ["I3", "I4"])

            # Verify children
            jack = individuals["I3"]
            self.assertEqual(jack["full_name"], "Jack Doe")
            self.assertEqual(jack["father"], "I1")
            self.assertEqual(jack["mother"], "I2")

            print("✅ Complex file upload test passed")

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_file_selection(self):
        """Test file selection functionality"""
        print("\n=== Testing File Selection ===")

        self.client.login(username="testuser", password="testpass123")

        # Upload two files
        files = []
        for i, gedcom_content in enumerate([self.simple_gedcom, self.complex_gedcom]):
            with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
                temp_file.write(gedcom_content.encode("utf-8"))
                temp_file_path = temp_file.name

            try:
                with open(temp_file_path, "rb") as f:
                    self.client.post("/", {"gedcom_file": f})
                files.append(temp_file_path)
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        # Get the files
        gedcom_files = GedcomFile.objects.filter(user=self.user).order_by("id")
        self.assertEqual(gedcom_files.count(), 2)

        # Select the first file
        first_file = gedcom_files.first()
        response = self.client.get(f"/select-file/{first_file.id}/")
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Check that session was updated
        session = self.client.session
        self.assertEqual(session["current_gedcom_file_id"], str(first_file.id))

        print("✅ File selection test passed")

    def test_file_deletion(self):
        """Test file deletion functionality"""
        print("\n=== Testing File Deletion ===")

        self.client.login(username="testuser", password="testpass123")

        # Upload a file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.simple_gedcom.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                self.client.post("/", {"gedcom_file": f})

            # Get the file
            gedcom_file = GedcomFile.objects.filter(user=self.user).first()
            file_id = gedcom_file.id

            # Delete the file
            response = self.client.post(f"/delete-file/{file_id}/")
            self.assertEqual(response.status_code, 200)

            # Verify file was deleted
            self.assertEqual(GedcomFile.objects.filter(user=self.user).count(), 0)

            # Verify session was cleaned up
            session = self.client.session
            self.assertNotIn("current_gedcom_file_id", session)

            print("✅ File deletion test passed")

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_data_persistence(self):
        """Test that data persists across sessions"""
        print("\n=== Testing Data Persistence ===")

        self.client.login(username="testuser", password="testpass123")

        # Upload a file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.simple_gedcom.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                self.client.post("/", {"gedcom_file": f})

            # Get the file ID
            gedcom_file = GedcomFile.objects.filter(user=self.user).first()
            file_id = gedcom_file.id

            # Create a new client to simulate new session
            new_client = Client()
            new_client.login(username="testuser", password="testpass123")

            # Select the file in the new session
            response = new_client.get(f"/select-file/{file_id}/")
            self.assertEqual(response.status_code, 302)

            # Verify we can access the data
            response = new_client.get("/browse/")
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "generator/browse_individuals.html")

            print("✅ Data persistence test passed")

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_anonymous_user_upload(self):
        """Test file upload for anonymous (non-authenticated) users"""
        print("\n=== Testing Anonymous User Upload ===")

        # Don't login - test as anonymous user

        # Upload a file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.simple_gedcom.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                response = self.client.post("/", {"gedcom_file": f})

            self.assertEqual(response.status_code, 200)

            # Check that file was created without user association
            gedcom_files = GedcomFile.objects.filter(user__isnull=True)
            self.assertEqual(gedcom_files.count(), 1)

            gedcom_file = gedcom_files.first()
            self.assertTrue(gedcom_file.is_processed)
            self.assertIsNotNone(gedcom_file.parsed_data)

            # Verify session has the file ID
            session = self.client.session
            self.assertIn("current_gedcom_file_id", session)

            print("✅ Anonymous user upload test passed")

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_individual_detail_view(self):
        """Test individual detail view with new data access"""
        print("\n=== Testing Individual Detail View ===")

        self.client.login(username="testuser", password="testpass123")

        # Upload a file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.complex_gedcom.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                self.client.post("/", {"gedcom_file": f})

            # Get John Doe's ID
            gedcom_file = GedcomFile.objects.filter(user=self.user).first()
            john_id = "I1"  # John Doe's ID

            # Access individual detail page
            response = self.client.get(f"/person/{john_id}/")
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "generator/person_view.html")

            # Verify context contains expected data
            self.assertIn("individual", response.context)
            self.assertIn("father", response.context)
            self.assertIn("mother", response.context)
            self.assertIn("spouses", response.context)
            self.assertIn("children", response.context)

            # Verify individual data
            individual = response.context["individual"]
            self.assertEqual(individual.full_name, "John Doe")
            self.assertEqual(individual.birth_date, "1 JAN 1980")

            print("✅ Individual detail view test passed")

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_browse_individuals(self):
        """Test browse individuals functionality"""
        print("\n=== Testing Browse Individuals ===")

        self.client.login(username="testuser", password="testpass123")

        # Upload a file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.complex_gedcom.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                self.client.post("/", {"gedcom_file": f})

            # Access browse page
            response = self.client.get("/browse/")
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "generator/browse_individuals.html")

            # Verify individuals are in context
            self.assertIn("individuals", response.context)
            individuals = response.context["individuals"]
            self.assertEqual(len(individuals), 4)

            # Verify we can find specific individuals
            names = [ind.full_name for ind in individuals]
            self.assertIn("John Doe", names)
            self.assertIn("Jane Smith", names)
            self.assertIn("Jack Doe", names)
            self.assertIn("Jill Doe", names)

            print("✅ Browse individuals test passed")

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_select_individual(self):
        """Test select individual functionality"""
        print("\n=== Testing Select Individual ===")

        self.client.login(username="testuser", password="testpass123")

        # Upload a file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.complex_gedcom.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as f:
                self.client.post("/", {"gedcom_file": f})

            # Access select individual page
            response = self.client.get("/select/")
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "generator/select_individual.html")

            # Verify individuals are available for selection
            self.assertIn("individuals", response.context)
            individuals = response.context["individuals"]
            self.assertEqual(len(individuals), 4)

            # Test selecting John Doe and generating chart
            john_id = "I1"
            response = self.client.post(
                "/select/", {"individual_id": john_id, "template": "4"}
            )

            # Should return a PDF file
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "application/pdf")
            self.assertIn("attachment", response["Content-Disposition"])

            print("✅ Select individual test passed")

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


if __name__ == "__main__":
    import os

    import django
    from django.conf import settings

    # Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "namechart.settings")
    django.setup()

    # Run tests
    import unittest

    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    # Run only our test suite
    failures = test_runner.run_tests(["generator.tests_file_handling"])

    if not failures:
        print("\n🎉 All file handling tests passed!")
        print("✅ File upload and processing: Working")
        print("✅ Complex data parsing: Working")
        print("✅ File selection: Working")
        print("✅ File deletion: Working")
        print("✅ Data persistence: Working")
        print("✅ Anonymous users: Working")
        print("✅ Individual views: Working")
        print("✅ Browse functionality: Working")
        print("✅ Chart generation: Working")
    else:
        print(f"\n❌ {failures} test(s) failed.")
