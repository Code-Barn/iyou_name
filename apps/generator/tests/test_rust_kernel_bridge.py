"""Tests for the PyO3 Rust kernel bridge helpers in apps.generator.views."""

from django.test import SimpleTestCase

from apps.parser.models import PersonData

from apps.generator.views import (
    _ancestor_position_labels,
    _as_bool,
    _as_float,
    _build_ancestors_payload,
    _build_settings_payload,
    _person_to_kernel_payload,
)


def make_person(person_id, full_name="John Michael Smith", given="John", surname="Smith",
                father=None, mother=None, birth="1970-05-15", birth_place="New York, NY"):
    return PersonData(
        id=person_id,
        full_name=full_name,
        given_name=given,
        surname=surname,
        birth_date=birth,
        birth_place=birth_place,
        father=father,
        mother=mother,
    )


class PersonPayloadTests(SimpleTestCase):
    def test_payload_shape_matches_kernel_person_data(self):
        person = make_person("I1")
        payload = _person_to_kernel_payload(person)
        self.assertEqual(
            set(payload.keys()),
            {"id", "full_name", "given_name", "surname",
             "birth_date", "birth_place", "death_date", "death_place"},
        )
        self.assertEqual(payload["id"], "I1")
        self.assertEqual(payload["full_name"], "John Michael Smith")
        self.assertIsNone(payload["death_date"])

    def test_payload_coerces_none_fields(self):
        person = PersonData(id="I1", full_name=None, given_name=None, surname=None)
        payload = _person_to_kernel_payload(person)
        self.assertEqual(payload["full_name"], "")
        self.assertEqual(payload["given_name"], "")
        self.assertEqual(payload["surname"], "")


class AncestorLabelTests(SimpleTestCase):
    def test_gen2_labels(self):
        self.assertEqual(_ancestor_position_labels(2), ["1", "2"])

    def test_gen3_labels(self):
        self.assertEqual(_ancestor_position_labels(3), ["A", "B", "C", "D"])

    def test_gen4_labels(self):
        self.assertEqual(
            _ancestor_position_labels(4),
            ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"],
        )

    def test_gen5_labels(self):
        self.assertEqual(len(_ancestor_position_labels(5)), 16)

    def test_gen6_labels(self):
        self.assertEqual(len(_ancestor_position_labels(6)), 32)

    def test_gen7_labels(self):
        self.assertEqual(len(_ancestor_position_labels(7)), 64)

    def test_unsupported(self):
        self.assertEqual(_ancestor_position_labels(8), [])


class AncestorsPayloadTests(SimpleTestCase):
    def test_gen1_has_no_ancestors(self):
        self.assertEqual(_build_ancestors_payload({}, "I1", 1), {"individuals": {}})

    def test_gen2_maps_father_and_mother(self):
        people = {
            "I1": make_person("I1", father="F", mother="M"),
            "F": make_person("F", full_name="Father One", given="Father", surname="One"),
            "M": make_person("M", full_name="Mother One", given="Mother", surname="One"),
        }
        payload = _build_ancestors_payload(people, "I1", 2)
        self.assertEqual(set(payload["individuals"].keys()), {"1", "2"})
        self.assertEqual(payload["individuals"]["1"]["id"], "F")
        self.assertEqual(payload["individuals"]["2"]["id"], "M")

    def test_gen3_maps_grandparents_and_includes_parents(self):
        people = {
            "I1": make_person("I1", father="F", mother="M"),
            "F": make_person("F", full_name="Father", given="Father", surname="S",
                             father="GF", mother="GM"),
            "M": make_person("M", full_name="Mother", given="Mother", surname="S",
                             father="GMf", mother="GMm"),
            "GF": make_person("GF", full_name="PGF", given="PG", surname="F"),
            "GM": make_person("GM", full_name="PGM", given="PM", surname="F"),
            "GMf": make_person("GMf", full_name="MGF", given="MG", surname="F"),
            "GMm": make_person("GMm", full_name="MGM", given="MM", surname="F"),
        }
        payload = _build_ancestors_payload(people, "I1", 3)
        # Gen2 parents must be present for the nested overlay validation
        self.assertEqual(payload["individuals"]["1"]["id"], "F")
        self.assertEqual(payload["individuals"]["2"]["id"], "M")
        self.assertEqual(payload["individuals"]["A"]["id"], "GF")
        self.assertEqual(payload["individuals"]["B"]["id"], "GM")
        self.assertEqual(payload["individuals"]["C"]["id"], "GMf")
        self.assertEqual(payload["individuals"]["D"]["id"], "GMm")

    def test_missing_ancestor_is_skipped(self):
        people = {"I1": make_person("I1", father=None, mother=None)}
        payload = _build_ancestors_payload(people, "I1", 2)
        self.assertEqual(payload["individuals"], {})


class SettingsPayloadTests(SimpleTestCase):
    def test_default_settings(self):
        payload = _build_settings_payload({})
        self.assertEqual(payload["font_color"], "#000000")
        self.assertEqual(payload["background_color"], "#FFFFFF")
        self.assertEqual(payload["name_font_size"], 84.0)
        self.assertEqual(payload["stroke_width"], 0.5)
        self.assertFalse(payload["use_outside_stroke"])

    def test_settings_override(self):
        payload = _build_settings_payload(
            {
                "primary_font_color": "#FF0000",
                "primary_name_font_size": "120",
                "use_outside_stroke": "true",
                "default_stroke_width": 2.0,
            }
        )
        self.assertEqual(payload["font_color"], "#FF0000")
        self.assertEqual(payload["name_font_size"], 120.0)
        self.assertTrue(payload["use_outside_stroke"])
        self.assertEqual(payload["stroke_width"], 2.0)

    def test_font_family_resolves_to_existing_file(self):
        import os

        payload = _build_settings_payload({"font_family": "Arial"})
        self.assertTrue(os.path.isfile(payload["font_family"]))


class CoercionHelperTests(SimpleTestCase):
    def test_as_bool(self):
        self.assertTrue(_as_bool("true"))
        self.assertTrue(_as_bool("1"))
        self.assertTrue(_as_bool(True))
        self.assertFalse(_as_bool("false"))
        self.assertFalse(_as_bool("0"))
        self.assertFalse(_as_bool(None))

    def test_as_float(self):
        self.assertEqual(_as_float("84.5"), 84.5)
        self.assertEqual(_as_float(42), 42.0)
        self.assertEqual(_as_float("not-a-number", 7.0), 7.0)
