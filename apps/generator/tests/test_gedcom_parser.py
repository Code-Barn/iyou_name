"""
Comprehensive test suite for the generator app.
Organized by functionality with clear separation of concerns.
"""

import os
import tempfile
import unittest
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from apps.generator.models import GedcomFile
from apps.generator.views import (
    get_spouse_and_children,
    preprocess_family_data,
)
from apps.parser.models import PersonData
from apps.parser.utils.gedcom_parser import convert_to_utf8, parse_gedcom_data


class GedcomParserTests(TestCase):
    """Test GEDCOM file parsing functionality"""

    def setUp(self):
        """Set up test data with a sample GEDCOM file"""
        self.sample_gedcom = """0 HEAD
1 SOUR Family Tree Builder
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 TITL Dr.
1 OCCU Software Engineer
1 BIRT
2 DATE 1 Jan 1980
2 PLAC New York
1 DEAT
2 DATE 15 Dec 2020
2 PLAC Boston
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
1 TITL Prof.
1 OCCU Professor
1 BIRT
2 DATE 5 Mar 1982
2 PLAC Chicago
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I1@
"""

        self.sample_gedcom7 = """0 HEAD
1 SOUR Family Tree Builder
1 GEDC
2 VERS 7.0
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 BIRT
2 DATE 1 Jan 1980
2 PLAC New York, USA
1 DEAT
2 DATE 15 Dec 2020
2 PLAC Boston, USA
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
1 BIRT
2 DATE 5 Mar 1982
2 PLAC Chicago, USA
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
"""

    def test_parse_individuals(self):
        """Test that parser creates correct number of PersonData objects"""
        result = parse_gedcom_data(self.sample_gedcom)
        self.assertEqual(len(result["individuals"]), 2)
        self.assertIn("I1", result["individuals"])
        self.assertIn("I2", result["individuals"])

    def test_parse_individual_attributes(self):
        """Test that individual attributes are parsed correctly"""
        result = parse_gedcom_data(self.sample_gedcom)
        individual = result["individuals"]["I1"]

        self.assertEqual(individual.given_name, "John")
        self.assertEqual(individual.surname, "Doe")
        self.assertEqual(individual.sex, "M")
        self.assertEqual(individual.title, "Dr.")
        self.assertEqual(individual.occupation, "Software Engineer")
        self.assertEqual(individual.birth_date, "1 Jan 1980")
        self.assertEqual(individual.birth_place, "New York")
        self.assertEqual(individual.death_date, "15 Dec 2020")
        self.assertEqual(individual.death_place, "Boston")

    def test_adoptive_parents(self):
        """Test that adoptive parents are correctly identified"""
        gedcom_with_adoption = """0 HEAD
1 SOUR Test
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Child /Doe/
1 SEX M
1 FAMC @F1@
2 PEDI adopted
0 @I2@ INDI
1 NAME John /Doe/
1 SEX M
0 @I3@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @F1@ FAM
1 HUSB @I2@
1 WIFE @I3@
1 CHIL @I1@
"""
        result = parse_gedcom_data(gedcom_with_adoption)
        individual = result["individuals"]["I1"]
        self.assertIn("I2", individual.adoptive_parents)
        self.assertIn("I3", individual.adoptive_parents)

    def test_foster_parents(self):
        """Test that foster parents are correctly identified"""
        gedcom_with_foster = """0 HEAD
1 SOUR Test
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Child /Doe/
1 SEX M
1 FAMC @F1@
2 PEDI foster
0 @I2@ INDI
1 NAME John /Doe/
1 SEX M
0 @I3@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @F1@ FAM
1 HUSB @I2@
1 WIFE @I3@
1 CHIL @I1@
"""
        result = parse_gedcom_data(gedcom_with_foster)
        individual = result["individuals"]["I1"]
        self.assertIn("I2", individual.foster_parents)
        self.assertIn("I3", individual.foster_parents)

    def test_step_parents(self):
        """Test that step-parents are correctly identified"""
        gedcom_with_step_parents = """0 HEAD
1 SOUR Test
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Child /Doe/
1 SEX M
1 FAMC @F1@
1 FAMC @F2@
0 @I2@ INDI
1 NAME John /Doe/
1 SEX M
0 @I3@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @I4@ INDI
1 NAME Bob /Johnson/
1 SEX M
0 @F1@ FAM
1 HUSB @I2@
1 WIFE @I3@
1 CHIL @I1@
0 @F2@ FAM
1 HUSB @I4@
1 WIFE @I3@
1 CHIL @I1@
"""
        result = parse_gedcom_data(gedcom_with_step_parents)
        individual = result["individuals"]["I1"]
        self.assertIn("I4", individual.step_parents)

    def test_parse_families(self):
        """Test that family relationships are parsed correctly"""
        result = parse_gedcom_data(self.sample_gedcom)
        self.assertEqual(len(result["families"]), 1)
        self.assertIn("F1", result["families"])

        family = result["families"]["F1"]
        self.assertEqual(family["husband"], "I1")
        self.assertEqual(family["wife"], "I2")
        self.assertEqual(family["children"], ["I1"])

    def test_parse_events(self):
        """Test that events are parsed correctly"""
        result = parse_gedcom_data(self.sample_gedcom)
        individual = result["individuals"]["I1"]
        self.assertIsNotNone(individual.events)
        self.assertGreater(len(individual.events), 0)

    def test_family_relationships(self):
        """Test that family relationships are correctly established"""
        result = parse_gedcom_data(self.sample_gedcom)
        individual = result["individuals"]["I1"]
        self.assertEqual(individual.spouse, ["I2"])
        self.assertEqual(individual.children, ["I1"])

    def test_root_individuals(self):
        """Test that root individuals (without parents) are identified"""
        result = parse_gedcom_data(self.sample_gedcom)
        # I2 is the only root individual since I1 has parents (I1 and I2)
        self.assertEqual(len(result["root_individuals"]), 1)
        self.assertIn("I2", result["root_individuals"])

    def test_to_dict_method(self):
        """Test the to_dict method of PersonData"""
        person = PersonData(
            id="I1",
            full_name="John Doe",
            given_name="John",
            surname="Doe",
            birth_date="1 Jan 1980",
            birth_place="New York",
        )
        person_dict = person.to_dict()
        self.assertEqual(person_dict["id"], "I1")
        self.assertEqual(person_dict["full_name"], "John Doe")

    def test_gedcom7_version_detection(self):
        """Test GEDCOM 7.0 version detection"""
        result = parse_gedcom_data(self.sample_gedcom7)
        # Check that GEDCOM 7.0 specific features are handled
        self.assertEqual(len(result["individuals"]), 2)


class ModelTests(TestCase):
    """Test Django models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_person_data_creation(self):
        """Test PersonData dataclass creation"""
        person = PersonData(
            id="I1",
            full_name="John Doe",
            given_name="John",
            surname="Doe",
            birth_date="1 Jan 1980",
            birth_place="New York",
            death_date="15 Dec 2020",
            death_place="Boston",
            father="F1",
            mother="M1",
            spouse=["S1"],
            children=["C1", "C2"],
            siblings=["B1"],
            sex="M",
            title="Dr.",
            occupation="Software Engineer",
        )

        self.assertEqual(person.id, "I1")
        self.assertEqual(person.full_name, "John Doe")
        self.assertEqual(person.get_full_name(), "John Doe")
        self.assertEqual(person.get_birth_info(), "b. 1 Jan 1980 in New York")
        self.assertEqual(person.get_death_info(), "d. 15 Dec 2020 in Boston")

    def test_gedcom_file_model(self):
        """Test GedcomFile model"""
        test_file = SimpleUploadedFile(
            "test.ged", b"0 HEAD\n1 SOUR Test", content_type="text/plain"
        )

        gedcom_file = GedcomFile.objects.create(user=self.user, file=test_file)

        self.assertEqual(gedcom_file.user, self.user)
        self.assertTrue(gedcom_file.file.name.endswith(".ged"))


class HelperFunctionTests(TestCase):
    """Test helper functions"""

    def setUp(self):
        self.sample_data = {
            "individuals": {
                "I1": {
                    "id": "I1",
                    "full_name": "John Doe",
                    "given_name": "John",
                    "surname": "Doe",
                    "sex": "M",
                },
                "I2": {
                    "id": "I2",
                    "full_name": "Jane Smith",
                    "given_name": "Jane",
                    "surname": "Smith",
                    "sex": "F",
                },
                "I3": {
                    "id": "I3",
                    "full_name": "Child Doe",
                    "given_name": "Child",
                    "surname": "Doe",
                    "sex": "M",
                },
            },
            "families": {"F1": {"husband": "I1", "wife": "I2", "children": ["I3"]}},
        }

    def test_get_spouse_and_children_with_valid_husband(self):
        """Test get_spouse_and_children with valid husband"""
        spouse, children = get_spouse_and_children(
            "I2",
            "I1",
            self.sample_data["individuals"],
            self.sample_data["families"]["F1"],
        )
        self.assertIsNotNone(spouse)
        self.assertEqual(spouse.id, "I2")
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].id, "I3")

    def test_get_spouse_and_children_with_valid_wife(self):
        """Test get_spouse_and_children with valid wife"""
        spouse, children = get_spouse_and_children(
            "I1",
            "I2",
            self.sample_data["individuals"],
            self.sample_data["families"]["F1"],
        )
        self.assertIsNotNone(spouse)
        self.assertEqual(spouse.id, "I1")
        self.assertEqual(len(children), 1)

    def test_get_spouse_and_children_with_invalid_spouse(self):
        """Test get_spouse_and_children with invalid spouse"""
        spouse, children = get_spouse_and_children(
            "INVALID",
            "I1",
            self.sample_data["individuals"],
            self.sample_data["families"]["F1"],
        )
        self.assertIsNone(spouse)
        self.assertEqual(len(children), 0)

    def test_get_spouse_and_children_with_no_children(self):
        """Test get_spouse_and_children with no children"""
        family_no_children = {"husband": "I1", "wife": "I2", "children": []}
        spouse, children = get_spouse_and_children(
            "I2", "I1", self.sample_data["individuals"], family_no_children
        )
        self.assertIsNotNone(spouse)
        self.assertEqual(len(children), 0)

    def test_preprocess_family_data(self):
        """Test preprocess_family_data function"""
        individuals_dict, families_dict, family_children_map = preprocess_family_data(
            self.sample_data
        )
        self.assertEqual(len(individuals_dict), 3)
        self.assertEqual(len(families_dict), 1)
        self.assertEqual(len(family_children_map), 1)
        self.assertIn("F1", family_children_map)


class EdgeCaseTests(TestCase):
    """Test edge cases and error handling"""

    def test_empty_gedcom(self):
        """Test parsing of empty GEDCOM content"""
        with self.assertRaises(Exception):
            parse_gedcom_data("")

    def test_malformed_gedcom(self):
        """Test parsing of malformed GEDCOM content"""
        malformed_gedcom = """0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
"""
        result = parse_gedcom_data(malformed_gedcom)
        # Should handle gracefully and return parsed data
        self.assertIsNotNone(result)
        self.assertGreater(len(result["individuals"]), 0)

    def test_individual_with_missing_fields(self):
        """Test handling of individuals with missing fields"""
        gedcom_missing_fields = """0 HEAD
1 SOUR Test
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
"""
        result = parse_gedcom_data(gedcom_missing_fields)
        self.assertEqual(len(result["individuals"]), 1)
        individual = result["individuals"]["I1"]
        self.assertEqual(individual.given_name, "John")
        self.assertIsNone(individual.birth_date)
        self.assertIsNone(individual.death_date)

    def test_step_siblings(self):
        """Test that step-siblings are correctly identified"""
        gedcom_with_step_siblings = """0 HEAD
1 SOUR Test
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME Child1 /Doe/
1 SEX M
1 FAMC @F1@
0 @I2@ INDI
1 NAME Child2 /Smith/
1 SEX F
1 FAMC @F2@
0 @I3@ INDI
1 NAME John /Doe/
1 SEX M
0 @I4@ INDI
1 NAME Jane /Smith/
1 SEX F
0 @F1@ FAM
1 HUSB @I3@
1 WIFE @I4@
1 CHIL @I1@
0 @F2@ FAM
1 HUSB @I3@
1 WIFE @I4@
1 CHIL @I2@
"""
        result = parse_gedcom_data(gedcom_with_step_siblings)
        individual1 = result["individuals"]["I1"]
        individual2 = result["individuals"]["I2"]
        self.assertEqual(len(individual1.siblings), 1)
        self.assertEqual(len(individual2.siblings), 1)


class ViewTests(TestCase):
    """Test view functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        self.sample_gedcom = """0 HEAD
1 SOUR Family Tree Builder
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Doe/
1 SEX M
1 TITL Dr.
1 OCCU Software Engineer
1 BIRT
2 DATE 1 Jan 1980
2 PLAC New York
1 DEAT
2 DATE 15 Dec 2020
2 PLAC Boston
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
1 TITL Prof.
1 OCCU Professor
1 BIRT
2 DATE 5 Mar 1982
2 PLAC Chicago
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I1@
"""

    def test_upload_view(self):
        """Test the upload view"""
        response = self.client.get(reverse("generator:upload_file"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "generator/upload_file.html")

    def test_register_view(self):
        """Test user registration"""
        response = self.client.post(
            reverse("generator:register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "newpass123",
                "password2": "newpass123",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful registration

    def test_profile_view(self):
        """Test user profile view"""
        response = self.client.get(reverse("generator:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "generator/profile.html")

    def test_upload_and_process_view(self):
        """Test the upload_and_process view with a sample GEDCOM file"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".ged", delete=False) as temp_file:
            temp_file.write(self.sample_gedcom.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            # Upload the file
            with open(temp_file_path, "rb") as f:
                response = self.client.post(
                    reverse("generator:home"), {"gedcom_file": f}
                )

            # Check that upload was successful or error is displayed
            self.assertIn(
                response.status_code, [200, 302]
            )  # 200 for error, 302 for redirect

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

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main()
