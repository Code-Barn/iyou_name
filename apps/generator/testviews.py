from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory, TestCase

from .models import PersonData
from .views import get_spouse_and_children, individual_detail


class GetSpouseAndChildrenTestCase(TestCase):
    def setUp(self):
        # Sample data for testing
        self.individuals_dict = {
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
            "I3": {
                "id": "I3",
                "full_name": "Jim Doe",
                "given_name": "Jim",
                "surname": "Doe",
                "birth_date": "2005-10-20",
                "birth_place": "Chicago",
                "sex": "M",
            },
            "I4": {
                "id": "I4",
                "full_name": "Jill Doe",
                "given_name": "Jill",
                "surname": "Doe",
                "birth_date": "2010-03-10",
                "birth_place": "Chicago",
                "sex": "F",
            },
        }

        self.family = {
            "husband": "I1",
            "wife": "I2",
            "children": ["I3", "I4"],
        }

    def test_get_spouse_and_children_with_valid_husband(self):
        spouse, children = get_spouse_and_children(
            "I1", "I2", self.individuals_dict, self.family
        )
        self.assertIsNotNone(spouse)
        self.assertEqual(spouse.id, "I1")
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].id, "I3")
        self.assertEqual(children[1].id, "I4")

    def test_get_spouse_and_children_with_valid_wife(self):
        spouse, children = get_spouse_and_children(
            "I2", "I1", self.individuals_dict, self.family
        )
        self.assertIsNotNone(spouse)
        self.assertEqual(spouse.id, "I2")
        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].id, "I3")
        self.assertEqual(children[1].id, "I4")

    def test_get_spouse_and_children_with_invalid_spouse(self):
        spouse, children = get_spouse_and_children(
            "I99", "I1", self.individuals_dict, self.family
        )
        self.assertIsNone(spouse)
        self.assertEqual(len(children), 0)

    def test_get_spouse_and_children_with_no_children(self):
        family_without_children = {
            "husband": "I1",
            "wife": "I2",
        }
        spouse, children = get_spouse_and_children(
            "I1", "I2", self.individuals_dict, family_without_children
        )
        self.assertIsNotNone(spouse)
        self.assertEqual(spouse.id, "I1")
        self.assertEqual(len(children), 0)


class IndividualDetailViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = SessionStore()
        self.session.save()

        # Sample family data for testing
        self.family_data = {
            "individuals": {
                "I1": {
                    "id": "I1",
                    "full_name": "John Doe",
                    "given_name": "John",
                    "surname": "Doe",
                    "birth_date": "1980-01-01",
                    "birth_place": "New York",
                    "father": "I5",
                    "mother": "I6",
                    "spouse": ["F1"],
                    "children": ["I3", "I4"],
                    "siblings": ["I7"],
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
                "I3": {
                    "id": "I3",
                    "full_name": "Jim Doe",
                    "given_name": "Jim",
                    "surname": "Doe",
                    "birth_date": "2005-10-20",
                    "birth_place": "Chicago",
                    "sex": "M",
                },
                "I4": {
                    "id": "I4",
                    "full_name": "Jill Doe",
                    "given_name": "Jill",
                    "surname": "Doe",
                    "birth_date": "2010-03-10",
                    "birth_place": "Chicago",
                    "sex": "F",
                },
                "I5": {
                    "id": "I5",
                    "full_name": "Jack Doe",
                    "given_name": "Jack",
                    "surname": "Doe",
                    "birth_date": "1950-01-01",
                    "birth_place": "Boston",
                    "sex": "M",
                },
                "I6": {
                    "id": "I6",
                    "full_name": "Jill Doe",
                    "given_name": "Jill",
                    "surname": "Doe",
                    "birth_date": "1955-05-15",
                    "birth_place": "Boston",
                    "sex": "F",
                },
                "I7": {
                    "id": "I7",
                    "full_name": "Jake Doe",
                    "given_name": "Jake",
                    "surname": "Doe",
                    "birth_date": "1982-03-10",
                    "birth_place": "New York",
                    "sex": "M",
                },
            },
            "families": {
                "F1": {
                    "husband": "I1",
                    "wife": "I2",
                    "children": ["I3", "I4"],
                }
            },
            "root_individuals": ["I1"],
        }

    def test_individual_detail_with_valid_individual(self):
        request = self.factory.get(f"/person/I1/")
        request.session = self.session
        request.session["family_data"] = self.family_data
        request.session.save()

        response = individual_detail(request, "I1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")

    def test_individual_detail_with_invalid_individual(self):
        request = self.factory.get(f"/person/I99/")
        request.session = self.session
        request.session["family_data"] = self.family_data
        request.session.save()

        response = individual_detail(request, "I99")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Individual not found")

    def test_individual_detail_with_no_family_data(self):
        request = self.factory.get(f"/person/I1/")
        request.session = self.session
        request.session["family_data"] = {}
        request.session.save()

        response = individual_detail(request, "I1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No family data found")
