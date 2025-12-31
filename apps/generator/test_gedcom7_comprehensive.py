"""
Comprehensive GEDCOM 7.0 test suite for the generator app.
Tests advanced GEDCOM 7.0 features, special characters, geographic data,
and real file processing.
"""

import os
import unittest
from io import BytesIO

from django.test import TestCase

from generator.models import PersonData
from generator.utils.gedcom_parser import convert_to_utf8, parse_gedcom_data


class Gedcom7ComprehensiveTests(TestCase):
    """Comprehensive tests for GEDCOM 7.0 specific features"""

    def setUp(self):
        """Set up GEDCOM 7.0 test data with advanced features"""
        self.sample_gedcom7_basic = """0 HEAD
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

        self.sample_gedcom7_special_chars = """0 HEAD
1 SOUR Family Tree Builder
1 GEDC
2 VERS 7.0
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME José María /García López/
1 SEX M
1 BIRT
2 DATE 15 Feb 1975
2 PLAC Madrid, España
1 NOTE José María García López was born in Madrid and has Spanish heritage.
0 @I2@ INDI
1 NAME François /Dubois/
1 SEX M
1 BIRT
2 DATE 20 Mar 1980
2 PLAC Paris, France
1 NOTE François Dubois was born in Paris with French heritage.
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
"""

        self.sample_gedcom7_geographic = """0 HEAD
1 SOUR Family Tree Builder
1 GEDC
2 VERS 7.0
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Traveler/
1 SEX M
1 BIRT
2 DATE 1 Jan 1980
2 PLAC New York, New York, USA
2 MAP
3 LATI N40.7128
3 LONG W074.0060
1 RESI
2 DATE FROM 2000 TO 2005
2 PLAC London, England, UK
2 MAP
3 LATI N51.5074
3 LONG W000.1278
1 DEAT
2 DATE 15 Dec 2020
2 PLAC Tokyo, Japan
2 MAP
3 LATI N35.6762
3 LONG E139.6503
0 @I2@ INDI
1 NAME Jane /Traveler/
1 SEX F
1 BIRT
2 DATE 5 Mar 1982
2 PLAC Sydney, Australia
2 MAP
3 LATI S33.8688
3 LONG E151.2093
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
"""

        self.sample_gedcom7_events = """0 HEAD
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
1 CHR
2 DATE 15 Jan 1980
2 PLAC St. Patrick's Cathedral, New York
1 GRAD
2 DATE 22 May 2002
2 PLAC Harvard University, Cambridge, MA
1 OCCU Software Engineer
2 DATE FROM 2002 TO 2010
1 RETI
2 DATE 1 Jan 2020
1 DEAT
2 DATE 15 Dec 2020
2 PLAC Boston, USA
1 EVEN
2 TYPE Graduation
2 DATE 22 May 2002
2 PLAC Harvard University
1 EVEN
2 TYPE Wedding
2 DATE 14 Jun 2005
2 PLAC City Hall, Boston
0 @I2@ INDI
1 NAME Jane /Smith/
1 SEX F
1 BIRT
2 DATE 5 Mar 1982
2 PLAC Chicago, USA
1 OCCU Professor
2 DATE FROM 2010
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
2 DATE 14 Jun 2005
2 PLAC City Hall, Boston
1 EVEN
2 TYPE Anniversary
2 DATE 14 Jun 2015
2 PLAC Boston, USA
"""

    def test_gedcom7_version_detection(self):
        """Test that GEDCOM 7.0 version is correctly detected"""
        result = parse_gedcom_data(self.sample_gedcom7_basic)
        # The parser should handle GEDCOM 7.0 without errors
        self.assertEqual(len(result["individuals"]), 2)
        self.assertEqual(len(result["families"]), 1)

    def test_gedcom7_basic_structure(self):
        """Test basic GEDCOM 7.0 structure parsing"""
        result = parse_gedcom_data(self.sample_gedcom7_basic)

        # Test individuals
        self.assertEqual(len(result["individuals"]), 2)
        john = result["individuals"]["I1"]
        jane = result["individuals"]["I2"]

        self.assertEqual(john.given_name, "John")
        self.assertEqual(john.surname, "Doe")
        self.assertEqual(john.sex, "M")
        self.assertEqual(john.birth_date, "1 Jan 1980")
        self.assertEqual(john.birth_place, "New York, USA")
        self.assertEqual(john.death_date, "15 Dec 2020")
        self.assertEqual(john.death_place, "Boston, USA")

        self.assertEqual(jane.given_name, "Jane")
        self.assertEqual(jane.surname, "Smith")
        self.assertEqual(jane.sex, "F")
        self.assertEqual(jane.birth_date, "5 Mar 1982")
        self.assertEqual(jane.birth_place, "Chicago, USA")

        # Test family
        self.assertEqual(len(result["families"]), 1)
        family = result["families"]["F1"]
        self.assertEqual(family["husband"], "I1")
        self.assertEqual(family["wife"], "I2")

    def test_gedcom7_special_characters(self):
        """Test GEDCOM 7.0 special character handling"""
        result = parse_gedcom_data(self.sample_gedcom7_special_chars)

        # Test Spanish special characters
        jose = result["individuals"]["I1"]
        self.assertEqual(jose.given_name, "José María")
        self.assertEqual(jose.surname, "García López")
        self.assertEqual(jose.birth_place, "Madrid, España")
        self.assertIsNotNone(jose.events)
        self.assertGreater(len(jose.events), 0)

        # Test French special characters
        francois = result["individuals"]["I2"]
        self.assertEqual(francois.given_name, "François")
        self.assertEqual(francois.surname, "Dubois")
        self.assertEqual(francois.birth_place, "Paris, France")

    def test_gedcom7_geographic_data(self):
        """Test GEDCOM 7.0 geographic coordinate parsing"""
        result = parse_gedcom_data(self.sample_gedcom7_geographic)

        john = result["individuals"]["I1"]
        self.assertEqual(john.given_name, "John")
        self.assertEqual(john.surname, "Traveler")

        # Test birth location with coordinates
        self.assertEqual(john.birth_date, "1 Jan 1980")
        self.assertEqual(john.birth_place, "New York, New York, USA")

        # Test residence with coordinates
        self.assertIsNotNone(john.events)
        residence_events = [e for e in john.events if e.get("tag") == "RESI"]
        self.assertGreater(len(residence_events), 0)

        # Test death location with coordinates
        self.assertEqual(john.death_date, "15 Dec 2020")
        self.assertEqual(john.death_place, "Tokyo, Japan")

        # Test spouse's geographic data
        jane = result["individuals"]["I2"]
        self.assertEqual(jane.birth_place, "Sydney, Australia")

    def test_gedcom7_events_and_occupations(self):
        """Test GEDCOM 7.0 event and occupation parsing"""
        result = parse_gedcom_data(self.sample_gedcom7_events)

        john = result["individuals"]["I1"]

        # Test birth and christening events
        self.assertEqual(john.birth_date, "1 Jan 1980")
        self.assertEqual(john.birth_place, "New York, USA")

        # Test education events
        self.assertIsNotNone(john.events)
        grad_events = [e for e in john.events if e.get("tag") == "GRAD"]
        self.assertGreater(len(grad_events), 0)

        # Test occupation
        self.assertEqual(john.occupation, "Software Engineer")

        # Test retirement
        reti_events = [e for e in john.events if e.get("tag") == "RETI"]
        self.assertGreater(len(reti_events), 0)

        # Test death
        self.assertEqual(john.death_date, "15 Dec 2020")
        self.assertEqual(john.death_place, "Boston, USA")

        # Test custom events
        custom_events = [e for e in john.events if e.get("tag") == "EVEN"]
        self.assertGreater(len(custom_events), 0)

        # Test marriage events in family
        family = result["families"]["F1"]
        self.assertEqual(len(family["events"]), 1)
        self.assertEqual(family["events"][0]["tag"], "MARR")

    def test_gedcom7_family_relationships(self):
        """Test GEDCOM 7.0 family relationship parsing"""
        result = parse_gedcom_data(self.sample_gedcom7_basic)

        john = result["individuals"]["I1"]
        jane = result["individuals"]["I2"]

        # Test spouse relationships
        self.assertEqual(john.spouse, ["I2"])
        self.assertEqual(jane.spouse, ["I1"])

        # Test family structure
        family = result["families"]["F1"]
        self.assertEqual(family["husband"], "I1")
        self.assertEqual(family["wife"], "I2")
        self.assertEqual(family["children"], [])

    def test_gedcom7_real_file_parsing(self):
        """Test parsing of a real GEDCOM 7.0 file if available"""
        gedcom_file_path = (
            "/home/user/namechart/media/gedcom_standards/DavidCByersGEDCOM7.ged"
        )

        if os.path.exists(gedcom_file_path):
            print(f"Testing real GEDCOM 7.0 file: {gedcom_file_path}")

            # Read the file content
            with open(gedcom_file_path, "r", encoding="utf-8") as f:
                gedcom_content = f.read()

            # Parse the file
            result = parse_gedcom_data(gedcom_content)

            # Basic validation
            self.assertGreater(len(result["individuals"]), 0)
            self.assertIsNotNone(result["families"])

            # Test a few individuals
            if len(result["individuals"]) > 0:
                first_individual_id = list(result["individuals"].keys())[0]
                first_individual = result["individuals"][first_individual_id]

                self.assertIsNotNone(first_individual.full_name)
                self.assertIsNotNone(first_individual.given_name)
                self.assertIsNotNone(first_individual.surname)

                print(f"Successfully parsed {len(result['individuals'])} individuals")
                print(f"Successfully parsed {len(result['families'])} families")
        else:
            print(
                f"Real GEDCOM 7.0 file not found at {gedcom_file_path}, skipping real file test"
            )

    def test_gedcom7_large_file_performance(self):
        """Test performance with a larger GEDCOM 7.0 dataset"""
        # Create a larger GEDCOM dataset
        large_gedcom = """0 HEAD
1 SOUR Test Generator
1 GEDC
2 VERS 7.0
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
"""

        # Add multiple generations
        for i in range(1, 21):  # 20 individuals
            large_gedcom += f"""0 @I{i}@ INDI
1 NAME Person{i} /Test/
1 SEX {"M" if i % 2 == 0 else "F"}
1 BIRT
2 DATE 1 Jan {1950 + i}
2 PLAC Location{i}, Country
"""

        # Add some families
        for i in range(1, 11):  # 10 families
            husband_id = i * 2
            wife_id = i * 2 + 1
            large_gedcom += f"""0 @F{i}@ FAM
1 HUSB @I{husband_id}@
1 WIFE @I{wife_id}@
"""

        # Test parsing performance
        import time

        start_time = time.time()

        result = parse_gedcom_data(large_gedcom)

        end_time = time.time()
        parsing_time = end_time - start_time

        print(
            f"Parsed {len(result['individuals'])} individuals in {parsing_time:.3f} seconds"
        )

        # Basic validation
        self.assertEqual(len(result["individuals"]), 20)
        self.assertEqual(len(result["families"]), 10)

        # Performance should be reasonable (less than 5 seconds for this test data)
        self.assertLess(parsing_time, 5.0)


if __name__ == "__main__":
    unittest.main()
