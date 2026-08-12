"""Tests for the individual detail relationship rendering pipeline."""

from django.conf import settings
from django.test import Client, TestCase

from apps.generator.models import GedcomFile


def _person(**kwargs):
    base = {
        "id": "I1",
        "full_name": "Test Person",
        "given_name": "Test",
        "surname": "Person",
    }
    base.update(kwargs)
    return base


def _family_info_html(response):
    """Extract just the family_info block (before the individuals JSON script)."""
    content = response.content.decode()
    before = content.split("Family Information</h5>", 1)[1]
    return before.split("<script>", 1)[0]


class IndividualDetailRelationshipTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _set_file(self, individuals):
        self.gedcom_file = GedcomFile.objects.create(
            file="test.gedcom",
            home_person_id=None,
            parsed_data={"individuals": individuals, "families": {}},
        )
        session = self.client.session
        session["current_gedcom_file_id"] = self.gedcom_file.id
        session.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

    def test_married_parent_children_render_under_spouse_no_duplicates(self):
        individuals = {
            "I1": _person(
                id="I1",
                full_name="Married Parent",
                spouse=["I8"],
                spouses_children={"I8": ["I2", "I3"]},
                children=["I2", "I3"],
            ),
            "I8": _person(id="I8", full_name="Spouse Person"),
            "I2": _person(id="I2", full_name="Shared Child Alpha", father="I1", mother="I8"),
            "I3": _person(id="I3", full_name="Shared Child Beta", father="I1", mother="I8"),
        }
        self._set_file(individuals)

        response = self.client.get("/browse/person/I1/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Spouses & Marriages", response.content.decode())
        self.assertNotIn("Unassigned Children", response.content.decode())

        body = _family_info_html(response)
        self.assertEqual(body.count("Shared Child Alpha"), 1)
        self.assertEqual(body.count("Shared Child Beta"), 1)

        spouse_groups = response.context["spouse_groups"]
        self.assertEqual(len(spouse_groups), 1)
        self.assertEqual(spouse_groups[0]["spouse"].id, "I8")
        self.assertEqual(spouse_groups[0]["count"], 2)
        self.assertEqual(len(response.context["unassigned_children"]), 0)

    def test_single_parent_children_render_unassigned(self):
        individuals = {
            "I1": _person(id="I1", full_name="Single Parent", children=["I2", "I3"]),
            "I2": _person(id="I2", full_name="Child Alpha", father="I1"),
            "I3": _person(id="I3", full_name="Child Beta", father="I1"),
        }
        self._set_file(individuals)

        response = self.client.get("/browse/person/I1/")

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Unassigned Children", content)

        body = _family_info_html(response)
        self.assertEqual(body.count("Child Alpha"), 1)
        self.assertEqual(body.count("Child Beta"), 1)

        self.assertEqual(len(response.context["spouse_groups"]), 0)
        self.assertEqual(len(response.context["unassigned_children"]), 2)

    def test_siblings_render_without_parents(self):
        individuals = {
            "I1": _person(
                id="I1",
                full_name="Parentless Person",
                siblings=["I2"],
                all_siblings=["I2"],
            ),
            "I2": _person(
                id="I2",
                full_name="Sibling Gamma",
                siblings=["I1"],
                all_siblings=["I1"],
            ),
        }
        self._set_file(individuals)

        response = self.client.get("/browse/person/I1/")

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Siblings (1)", content)
        self.assertIn("Sibling Gamma", content)

        # Grey category headers must be gone in favor of a unified sibling list.
        self.assertNotIn("Full Siblings (", content)

        self.assertEqual(response.context["full_siblings_count"], 1)
        self.assertEqual(response.context["total_siblings_count"], 1)

    def test_all_collapsible_sections_expanded_by_default(self):
        """Every relationship accordion must ship with `collapse show` so content is
        visible on page load without a JS click, and the scoped visibility override
        must be present to defeat Tailwind's `.collapse { visibility: collapse }`
        utility colliding with Bootstrap's collapse component class."""
        individuals = {
            "I1": _person(
                id="I1",
                full_name="Hub Person",
                father="I2",
                mother="I3",
                spouse=["I4"],
                spouses_children={"I4": ["I5"]},
                children=["I5", "I9"],
                siblings=["I6"],
                all_siblings=["I6"],
                half_siblings=["I7"],
                step_siblings=["I8"],
            ),
            "I2": _person(id="I2", full_name="Father Fred"),
            "I3": _person(id="I3", full_name="Mother Mary"),
            "I4": _person(id="I4", full_name="Spouse Sally"),
            "I5": _person(id="I5", full_name="Child Charlie", father="I1", mother="I4"),
            "I6": _person(id="I6", full_name="Brother Bob"),
            "I7": _person(id="I7", full_name="Half Hans"),
            "I8": _person(id="I8", full_name="Step Steve"),
            "I9": _person(id="I9", full_name="Unassigned Uma"),
        }
        self._set_file(individuals)

        response = self.client.get("/browse/person/I1/")

        self.assertEqual(response.status_code, 200)
        body = _family_info_html(response)
        for collapse_id in [
            "originFamilyCollapse",
            "siblingsCollapse",
            "spousesCollapse",
            "unassignedChildrenCollapse",
            "childrenCollapseI4",
        ]:
            self.assertIn(f'class="collapse show" id="{collapse_id}"', body)

        # Scoped CSS guard against the Tailwind `.collapse` visibility utility
        # (rendered in the component's `<style>` block above the heading).
        content = response.content.decode()
        self.assertIn(".family-info .collapse", content)
        self.assertIn("visibility: visible", content)

        # Multi-line template comments must never leak into the rendered HTML.
        self.assertNotIn("Scoped fix", content)
        self.assertNotIn("Tailwind", content)

    def test_profile_photo_hero_layout_with_placeholder(self):
        """The top hero card must use a flex layout (info left, photo right) and
        render a clean avatar frame with the Upload Photo action underneath."""
        individuals = {
            "I1": _person(id="I1", full_name="Hero Person", sex="M"),
        }
        self._set_file(individuals)

        response = self.client.get("/browse/person/I1/")

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('class="flex flex-col md:flex-row gap-6 justify-between items-start mt-4"', content)
        self.assertIn('class="flex-1 w-full"', content)
        self.assertIn('class="w-48 shrink-0 md:self-start"', content)
        # Gender + XREF badges render next to the name.
        self.assertIn('<span class="badge bg-info ms-2 align-middle">M</span>', content)
        self.assertIn('<span class="badge bg-secondary ms-2 align-middle">XREF I1</span>', content)
        # Fallback avatar frame renders when no photo exists.
        self.assertIn('class="rounded-xl shadow-sm border border-gray-200 bg-gray-50', content)
        self.assertIn('bi bi-person', content)

    def test_half_and_step_siblings_labeled(self):
        individuals = {
            "I1": _person(
                id="I1",
                full_name="Main Person",
                father="I9",
                half_siblings=["I2"],
                step_siblings=["I3"],
                all_siblings=["I2", "I3"],
            ),
            "I2": _person(id="I2", full_name="Half Sibling Delta", father="I9"),
            "I3": _person(id="I3", full_name="Step Sibling Epsilon"),
            "I9": _person(id="I9", full_name="Shared Father"),
        }
        self._set_file(individuals)

        response = self.client.get("/browse/person/I1/")

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Siblings (2)", content)
        self.assertIn("Half Sibling Delta", content)
        self.assertIn("Step Sibling Epsilon", content)
        self.assertIn("(Half - via father)", content)
        self.assertIn("(Step)", content)

        # Grey category headers must be gone in favor of a unified sibling list.
        self.assertNotIn("Full Siblings (", content)
        self.assertNotIn("Half Siblings (", content)
        self.assertNotIn("Step Siblings (", content)

        self.assertEqual(response.context["half_siblings_count"], 1)
        self.assertEqual(response.context["step_siblings_count"], 1)
        self.assertEqual(response.context["total_siblings_count"], 2)
