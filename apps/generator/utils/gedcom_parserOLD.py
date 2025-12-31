import io
from typing import Dict, Optional

import chardet
from ged4py.parser import GedcomReader

from generator.models import PersonData


def detect_encoding(file_path: str) -> Optional[str]:
    """
    Detect the encoding of a file using chardet.

    Args:
        file_path: Path to the file.

    Returns:
        Optional[str]: The detected encoding, or None if detection fails.
    """
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
            result = chardet.detect(file_content)
            encoding = result["encoding"]
            confidence = result["confidence"]

            print(f"Detected encoding: {encoding} with confidence: {confidence}")
            return encoding
    except Exception as e:
        print(f"Error detecting encoding: {e}")
        return None


def parse_gedcom_data(gedcom_content: str) -> Dict:
    """
    Parse GEDCOM data and return structured family tree information.

    Args:
        gedcom_content: String containing GEDCOM file content (already decoded).

    Returns:
        Dictionary containing:
        - individuals: Dict[str, PersonData] - all individuals in the file.
        - families: Dict[str, Dict] - family relationships.
        - root_individuals: List[str] - IDs of individuals without parents (potential roots).
    """
    family_data = {"individuals": {}, "families": {}, "root_individuals": []}
    print("Starting GEDCOM parsing...")
    print(f"GEDCOM content length: {len(gedcom_content)}")

    # Print the first few lines of the content for debugging
    lines = gedcom_content.split("\n")
    print("First 10 lines of GEDCOM content:")
    for line in lines[:10]:
        print(line)

    # Ensure the content is encoded as UTF-8 bytes with error handling
    try:
        gedcom_bytes = gedcom_content.encode("utf-8", errors="replace")
        print(
            f"Successfully encoded content to UTF-8 bytes. Length: {len(gedcom_bytes)}"
        )
    except UnicodeEncodeError as e:
        print(f"Failed to encode content as UTF-8: {e}")
        raise

    # First pass: Collect all individual data
    # Force UTF-8 encoding to handle GEDCOM 7.0 and special characters
    try:
        parser = GedcomReader(io.BytesIO(gedcom_bytes), encoding="utf-8")
        print("Successfully initialized GedcomReader")
        # Create a mapping of XREF IDs to individual records for quick lookup
        individual_records = {}
        for record in parser.records0("INDI"):
            individual_records[record.xref_id] = record

        # Detect GEDCOM version for compatibility handling
        gedcom_version = "5.5"  # Default
        try:
            for record in parser.records0("HEAD"):
                gedcom_tag = record.sub_tag("GEDC")
                if gedcom_tag:
                    vers_tag = gedcom_tag.sub_tag("VERS")
                    if vers_tag and hasattr(vers_tag, "value"):
                        gedcom_version = str(vers_tag.value)
                        print(f"Detected GEDCOM version: {gedcom_version}")
        except Exception as e:
            print(f"Failed to detect GEDCOM version: {e}")
            raise

        for record in parser.records0("INDI"):
            ind = (
                record.xref_id.replace("@", "")
                if record.xref_id
                else f"unknown_{len(family_data['individuals'])}"
            )

            # Initialize variables with safe defaults
            given_name = ""
            surname = ""
            full_name = ""
            birth_date = None
            birth_place = None
            death_date = None
            death_place = None
            sex = None
            title = None
            occupation = None
            events = []

            # Extract name information safely
            name_obj = getattr(record, "name", None)
            if name_obj:
                given_name = getattr(name_obj, "given", "")
                surname = getattr(name_obj, "surname", "")
                full_name = getattr(
                    name_obj, "format", lambda: f"{given_name} {surname}"
                )()

            # Extract sex information safely
            sex = getattr(record, "sex", None)

            # Extract title information safely (GEDCOM 7.0 uses different structure)
            title = None
            if gedcom_version.startswith("7."):
                # GEDCOM 7.0: titles might be in NAME structure
                name_obj = getattr(record, "name", None)
                if name_obj:
                    title_tag = getattr(name_obj, "title", None)
                    if title_tag:
                        title = str(title_tag)
            else:
                # GEDCOM 5.5: TITL tag
                title_tag = record.sub_tag("TITL")
                if title_tag and hasattr(title_tag, "value"):
                    title = str(title_tag.value)

            # Extract occupation information safely
            occupation = None
            if gedcom_version.startswith("7."):
                # GEDCOM 7.0: occupations might be in different structure
                occu_tag = record.sub_tag("OCCU")
                if occu_tag and hasattr(occu_tag, "value"):
                    occupation = str(occu_tag.value)
            else:
                # GEDCOM 5.5: OCCU tag
                occu_tag = record.sub_tag("OCCU")
                if occu_tag and hasattr(occu_tag, "value"):
                    occupation = str(occu_tag.value)

            # Extract all events (BIRT, DEAT, CHR, BURI, EVEN, ADOP)
            # GEDCOM 7.0 adds more event types
            event_tags = ["BIRT", "DEAT", "CHR", "BURI", "EVEN", "ADOP"]
            if gedcom_version.startswith("7."):
                event_tags.extend(["BAPM", "CONF", "ORDN", "RETI", "PROB", "WILL"])

            for event in record.sub_tags(*event_tags):
                # Extract date safely
                date_str = None
                date_obj = event.sub_tag("DATE")
                if date_obj and hasattr(date_obj, "value") and date_obj.value:
                    date_str = str(date_obj.value)
                    # Normalize date format (convert uppercase months to title case)
                    if date_str:
                        # Convert "JAN" to "Jan", "FEB" to "Feb", etc.
                        date_str = date_str.replace(" JAN ", " Jan ")
                        date_str = date_str.replace(" FEB ", " Feb ")
                        date_str = date_str.replace(" MAR ", " Mar ")
                        date_str = date_str.replace(" APR ", " Apr ")
                        date_str = date_str.replace(" MAY ", " May ")
                        date_str = date_str.replace(" JUN ", " Jun ")
                        date_str = date_str.replace(" JUL ", " Jul ")
                        date_str = date_str.replace(" AUG ", " Aug ")
                        date_str = date_str.replace(" SEP ", " Sep ")
                        date_str = date_str.replace(" OCT ", " Oct ")
                        date_str = date_str.replace(" NOV ", " Nov ")
                        date_str = date_str.replace(" DEC ", " Dec ")

                # Extract place safely
                place_str = None
                place_obj = event.sub_tag("PLAC")
                if place_obj:
                    place_str = (
                        str(place_obj.value)
                        if hasattr(place_obj, "value")
                        else str(place_obj)
                    )

                # Extract description for EVEN events
                description = None
                if event.tag == "EVEN":
                    type_obj = event.sub_tag("TYPE")
                    if type_obj:
                        description = str(type_obj)

                event_info = {
                    "tag": event.tag,
                    "date": date_str,
                    "place": place_str
                    if isinstance(place_str, str)
                    else str(place_str),
                    "description": description,
                }
                events.append(event_info)

                # Special handling for birth and death events
                if event.tag == "BIRT":
                    birth_date = date_str
                    birth_place = (
                        place_str if isinstance(place_str, str) else str(place_str)
                    )
                elif event.tag == "DEAT":
                    death_date = date_str
                    death_place = (
                        place_str if isinstance(place_str, str) else str(place_str)
                    )

            # Create PersonData object with safe defaults
            individual = PersonData(
                id=ind,
                full_name=full_name or f"{given_name} {surname}".strip(),
                given_name=given_name,
                surname=surname,
                birth_date=birth_date,
                birth_place=birth_place,
                death_date=death_date,
                death_place=death_place,
                father=None,
                mother=None,
                spouse=[],
                children=[],
                events=events,
                sex=sex,
                title=title,
                occupation=occupation,
                birth_flag=None,
                death_flag=None,
            )

            family_data["individuals"][ind] = individual
            print(f"Parsed individual: {individual.full_name} (ID: {ind})")

        # Second pass: Collect family data and establish relationships
        # Note: parser is already opened with UTF-8 encoding above
        for record in parser.records0("FAM"):
            fam_id = (
                record.xref_id.replace("@", "")
                if record.xref_id
                else f"unknown_fam_{len(family_data['families'])}"
            )
            family = {"husband": None, "wife": None, "children": [], "events": []}
            print(f"Processing family: {fam_id}")

            # Get husband and wife by following XREF pointers safely
            husb_record = record.sub_tag("HUSB")
            husband_id = husb_record.xref_id if husb_record else None
            wife_record = record.sub_tag("WIFE")
            wife_id = wife_record.xref_id if wife_record else None

            if husband_id and husband_id in individual_records:
                family["husband"] = husband_id.replace("@", "") if husband_id else None
                # Link husband to this family using ID
                if (
                    husband_id
                    and husband_id.replace("@", "") in family_data["individuals"]
                ):
                    husband_individual = family_data["individuals"][
                        husband_id.replace("@", "")
                    ]
                    # Add wife's ID to husband's spouse list
                    if wife_id:
                        husband_individual.spouse.append(wife_id.replace("@", ""))

            if wife_id and wife_id in individual_records:
                family["wife"] = wife_id.replace("@", "") if wife_id else None
                # Link wife to this family using ID
                if wife_id and wife_id.replace("@", "") in family_data["individuals"]:
                    wife_individual = family_data["individuals"][
                        wife_id.replace("@", "")
                    ]
                    # Add husband's ID to wife's spouse list
                    if husband_id:
                        wife_individual.spouse.append(husband_id.replace("@", ""))

            # Get children by following XREF pointers
            for child_record in record.sub_tags("CHIL"):
                child_id = child_record.xref_id
                if child_id in individual_records:
                    family["children"].append(child_id.replace("@", ""))
                    # Link child to parents using IDs
                    if (
                        child_id
                        and child_id.replace("@", "") in family_data["individuals"]
                    ):
                        child_individual = family_data["individuals"][
                            child_id.replace("@", "")
                        ]
                        if family["husband"]:
                            child_individual.father = family["husband"].replace("@", "")
                        if family["wife"]:
                            child_individual.mother = family["wife"].replace("@", "")
                        # Link parents to child
                        if (
                            family["husband"]
                            and family["husband"].replace("@", "")
                            in family_data["individuals"]
                        ):
                            husband_individual = family_data["individuals"][
                                family["husband"].replace("@", "")
                            ]
                            if not husband_individual.children:
                                husband_individual.children = []
                            husband_individual.children.append(
                                child_id.replace("@", "")
                            )
                        if (
                            family["wife"]
                            and family["wife"].replace("@", "")
                            in family_data["individuals"]
                        ):
                            wife_individual = family_data["individuals"][
                                family["wife"].replace("@", "")
                            ]
                            if not wife_individual.children:
                                wife_individual.children = []
                            wife_individual.children.append(child_id.replace("@", ""))

            # Extract family events
            for event in record.sub_tags("MARR", "DIV", "EVEN"):
                event_info = {
                    "tag": event.tag,
                    "date": str(event.sub_tag("DATE"))
                    if event.sub_tag("DATE")
                    else None,
                    "place": str(event.sub_tag("PLAC"))
                    if event.sub_tag("PLAC")
                    else None,
                    "description": str(event.sub_tag("TYPE"))
                    if event.tag == "EVEN" and event.sub_tag("TYPE")
                    else None,
                }
                family["events"].append(event_info)

            family_data["families"][fam_id] = family
            print(
                f"Family {fam_id} - Husband: {family['husband']}, Wife: {family['wife']}, Children: {family['children']}"
            )
        # Identify root individuals (those without parents)
        for ind, individual in family_data["individuals"].items():
            if not individual.father and not individual.mother:
                family_data["root_individuals"].append(ind)

        # Identify siblings and step-siblings for each individual
        for ind, individual in family_data["individuals"].items():
            siblings = []
            step_siblings = []
            # Find all families where the individual is a child
            for fam_id, family in family_data["families"].items():
                if ind in family.get("children", []):
                    # Collect all children in the family except the individual
                    for child_id in family.get("children", []):
                        if child_id != ind:
                            siblings.append(child_id)
            individual.siblings = siblings

        # Identify adoptive, foster, and step parents
        for ind, individual in family_data["individuals"].items():
            adoptive_parents = []
            foster_parents = []
            step_parents = []
            # Check for adoptive parents
            for fam_id, family in family_data["families"].items():
                if ind in family.get("children", []):
                    # Check for PEDI tag indicating adoption
                    for child_record in record.sub_tags("CHIL"):
                        if child_record.xref_id == f"@{ind}@":
                            pedi_tag = child_record.sub_tag("PEDI")
                            if pedi_tag and pedi_tag.value == "adopted":
                                if family["husband"]:
                                    adoptive_parents.append(
                                        family["husband"].replace("@", "")
                                    )
                                if family["wife"]:
                                    adoptive_parents.append(
                                        family["wife"].replace("@", "")
                                    )
            individual.adoptive_parents = adoptive_parents

            # Check for foster parents
            for fam_id, family in family_data["families"].items():
                if ind in family.get("children", []):
                    # Check for PEDI tag indicating foster
                    for child_record in record.sub_tags("CHIL"):
                        if child_record.xref_id == f"@{ind}@":
                            pedi_tag = child_record.sub_tag("PEDI")
                            if pedi_tag and pedi_tag.value == "foster":
                                if family["husband"]:
                                    foster_parents.append(
                                        family["husband"].replace("@", "")
                                    )
                                if family["wife"]:
                                    foster_parents.append(
                                        family["wife"].replace("@", "")
                                    )
            individual.foster_parents = foster_parents

            # Identify step-parents
            if individual.father and individual.mother:
                # Check for multiple FAMC pointers indicating step-parents
                for fam_id, family in family_data["families"].items():
                    if ind in family.get("children", []):
                        if (
                            family["husband"]
                            and family["husband"].replace("@", "") != individual.father
                        ):
                            step_parents.append(family["husband"].replace("@", ""))
                        if (
                            family["wife"]
                            and family["wife"].replace("@", "") != individual.mother
                        ):
                            step_parents.append(family["wife"].replace("@", ""))
            individual.step_parents = step_parents

        # Debug: Print all individuals and their relationships
        print("\n=== Debug: Individuals and Relationships ===")
        for ind, individual in family_data["individuals"].items():
            print(f"\nIndividual: {individual.full_name} (ID: {ind})")
            print(f"  Father: {individual.father}")
            print(f"  Mother: {individual.mother}")
            print(f"  Spouse: {individual.spouse}")
            print(f"  Children: {individual.children}")
            print(f"  Siblings: {individual.siblings}")

        print(f"\nRoot individuals: {family_data['root_individuals']}")
        print(f"Total individuals parsed: {len(family_data['individuals'])}")
        print(f"Total families parsed: {len(family_data['families'])}")

        # Close the parser manually
        if hasattr(parser, "close"):
            parser.close()
        return family_data
    except Exception as e:
        print(f"Failed to parse GEDCOM data: {e}")
        if "parser" in locals() and hasattr(parser, "close"):
            parser.close()
        raise


def convert_to_utf8(file_content: bytes) -> str:
    """
    Detect the encoding of the file content and convert it to UTF-8.
    Handle GEDCOM 7.0 and other encoding issues with robust error handling.

    Args:
        file_content: Bytes containing the file content.

    Returns:
        str: The file content decoded as UTF-8.
    """
    # Detect the encoding
    result = chardet.detect(file_content)
    encoding = result["encoding"]
    confidence = result["confidence"]

    print(f"Detected encoding: {encoding} with confidence: {confidence}")

    # Try multiple decoding strategies for GEDCOM 7.0 compatibility
    decoding_strategies = [
        ("utf-8", {"errors": "replace"}),  # Standard UTF-8 with replacement
        ("utf-8-sig", {"errors": "replace"}),  # UTF-8 with BOM handling
        ("latin-1", {}),  # Latin-1 can handle all byte values
        ("windows-1252", {"errors": "replace"}),  # Common Windows encoding
    ]

    for strategy_encoding, strategy_options in decoding_strategies:
        try:
            if strategy_encoding == encoding or strategy_encoding in [
                "utf-8",
                "utf-8-sig",
            ]:
                decoded_content = file_content.decode(
                    strategy_encoding, **strategy_options
                )
                print(f"Successfully decoded using {strategy_encoding} encoding")

                # Clean up replacement characters and problematic bytes
                if "\ufffd" in decoded_content:
                    print("Found replacement characters, cleaning up...")
                    # Replace common problematic characters
                    cleanup_map = {
                        "\ufffd": "-",  # Replacement character
                        "\u2013": "-",  # En dash
                        "\u2014": "-",  # Em dash
                        "\u2018": "'",  # Left single quote
                        "\u2019": "'",  # Right single quote
                        "\u201c": '"',  # Left double quote
                        "\u201d": '"',  # Right double quote
                        "\u0096": "-",  # Control character
                        "\u0097": "-",  # Control character
                    }

                    for problematic, replacement in cleanup_map.items():
                        decoded_content = decoded_content.replace(
                            problematic, replacement
                        )

                return decoded_content
        except Exception as e:
            print(f"Failed to decode with {strategy_encoding}: {e}")
            continue

    # If all strategies fail, try raw latin-1 as last resort
    try:
        print("All decoding strategies failed, trying raw latin-1 as fallback")
        decoded_content = file_content.decode("latin-1")
        # Clean up the content
        decoded_content = decoded_content.replace("\u0096", "-")
        return decoded_content
    except Exception as e:
        print(f"Failed to decode with all strategies: {e}")
        raise ValueError(
            f"Unable to decode file content. Tried {len(decoding_strategies) + 1} different strategies."
        )
