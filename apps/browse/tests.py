from unittest.mock import patch

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from apps.browse.views import individual_detail
from apps.generator.models import GedcomFile


class IndividualDetailViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.sample_individual_data = {
            "id": "I1",
            "full_name": "John Doe",
            "given_name": "John",
            "surname": "Doe",
            "father": "I2",
            "mother": "I3",
            "spouse": ["I4"],
            "children": ["I5", "I6"],
            "siblings": ["I7"],
            "birth_date": "1980-01-01",
            "birth_place": "New York",
        }

        self.sample_parsed_data = {
            "individuals": {
                "I1": self.sample_individual_data,
                "I2": {
                    "id": "I2",
                    "full_name": "Father Doe",
                    "given_name": "Father",
                    "surname": "Doe",
                    "birth_date": "1950-01-01",
                },
                "I3": {
                    "id": "I3",
                    "full_name": "Mother Doe",
                    "given_name": "Mother",
                    "surname": "Doe",
                    "birth_date": "1955-01-01",
                },
                "I4": {
                    "id": "I4",
                    "full_name": "Jane Doe",
                    "given_name": "Jane",
                    "surname": "Doe",
                    "birth_date": "1982-01-01",
                },
                "I5": {
                    "id": "I5",
                    "full_name": "Child One",
                    "given_name": "Child",
                    "surname": "One",
                    "birth_date": "2005-01-01",
                },
                "I6": {
                    "id": "I6",
                    "full_name": "Child Two",
                    "given_name": "Child",
                    "surname": "Two",
                    "birth_date": "2007-01-01",
                },
                "I7": {
                    "id": "I7",
                    "full_name": "Sibling Doe",
                    "given_name": "Sibling",
                    "surname": "Doe",
                    "birth_date": "1978-01-01",
                },
            }
        }

    @patch("apps.generator.models.GedcomFile.objects.get")
    def test_individual_detail_view_with_family_relationships(self, mock_get):
        # Create a mock GedcomFile object
        mock_gedcom_file = GedcomFile()
        mock_gedcom_file.id = 1
        mock_gedcom_file.parsed_data = self.sample_parsed_data
        mock_get.return_value = mock_gedcom_file

        # Create a request with session
        request = self.factory.get("/person/I1/")
        request.session = {"current_gedcom_file_id": 1}

        # Add session middleware to process the session
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Call the view
        response = individual_detail(request, "I1")

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the context contains the expected data
        context = response.context

        # Check individual
        self.assertIsNotNone(context["individual"])
        self.assertEqual(context["individual"].id, "I1")
        self.assertEqual(context["individual"].full_name, "John Doe")

        # Check father
        self.assertIsNotNone(context["father"])
        self.assertEqual(context["father"].id, "I2")
        self.assertEqual(context["father"].full_name, "Father Doe")

        # Check mother
        self.assertIsNotNone(context["mother"])
        self.assertEqual(context["mother"].id, "I3")
        self.assertEqual(context["mother"].full_name, "Mother Doe")

        # Check siblings
        self.assertIsNotNone(context["siblings"])
        self.assertEqual(len(context["siblings"]), 1)
        self.assertEqual(context["siblings"][0].id, "I7")
        self.assertEqual(context["siblings"][0].full_name, "Sibling Doe")

        # Check spouses
        self.assertIsNotNone(context["spouses"])
        self.assertEqual(len(context["spouses"]), 1)
        self.assertEqual(context["spouses"][0].id, "I4")
        self.assertEqual(context["spouses"][0].full_name, "Jane Doe")

        # Check children
        self.assertIsNotNone(context["children"])
        self.assertEqual(len(context["children"]), 2)
        self.assertEqual(context["children"][0].id, "I5")
        self.assertEqual(context["children"][1].id, "I6")

        # Check individuals_dict
        self.assertIsNotNone(context["individuals_dict"])
        self.assertEqual(len(context["individuals_dict"]), 7)
        self.assertIn("I1", context["individuals_dict"])
        self.assertIn("I2", context["individuals_dict"])

        # Check file_id
        self.assertEqual(context["file_id"], 1)
