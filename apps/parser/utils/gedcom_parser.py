import io
import logging
from typing import Dict, Optional

import chardet
from ged4py.parser import GedcomReader

from apps.parser.models import PersonData

# Set up logging
logger = logging.getLogger(__name__)


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
        print("Attempting to initialize GedcomReader...")
        parser = GedcomReader(io.BytesIO(gedcom_bytes), encoding="utf-8")
        print("Successfully initialized GedcomReader")
        # Create a mapping of XREF IDs to individual records for quick lookup
        individual_records = {}
        for record in parser.records0("INDI"):
            individual_records[record.xref_id] = record

        # Detect GEDCOM version for compatibility handling
        gedcom_version = "5.5"  # Default
        try:
            print("Detecting GEDCOM version...")
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

        print("Starting to parse individuals...")
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
                    # Only update death info if we don't have it yet, or if this event has actual data
                    if not death_date and date_str and date_str != "":
                        death_date = date_str
                    if (
                        not death_place
                        and place_str
                        and place_str != "None"
                        and place_str != ""
                    ):
                        death_place = (
                            place_str if isinstance(place_str, str) else str(place_str)
                        )

            # Create PersonData object with safe defaults
            # Debug: Check for family tags in GEDCOM 7.0
            if gedcom_version.startswith("7."):
                logger.debug(f"Checking GEDCOM 7.0 family tags for individual {ind}")
                # Check for FAMC (Family Child) tags
                famc_tags = record.sub_tags("FAMC")
                logger.debug(f"FAMC tags found: {len(famc_tags)}")
                for famc_tag in famc_tags:
                    logger.debug(
                        f"FAMC: {famc_tag.xref_id if hasattr(famc_tag, 'xref_id') else famc_tag}"
                    )

                # Check for FAMS (Family Spouse) tags
                fams_tags = record.sub_tags("FAMS")
                logger.debug(f"FAMS tags found: {len(fams_tags)}")
                for fams_tag in fams_tags:
                    logger.debug(
                        f"FAMS: {fams_tag.xref_id if hasattr(fams_tag, 'xref_id') else fams_tag}"
                    )

                # Check for other family-related tags
                all_tags = [tag for tag in record.sub_tags()]
                family_related_tags = [tag for tag in all_tags if "FAM" in str(tag)]
                logger.debug(f"All family-related tags: {family_related_tags}")

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

        print(f"Finished parsing individuals. Total: {len(family_data['individuals'])}")

        # Second pass: Collect family data and establish relationships
        # Note: parser is already opened with UTF-8 encoding above
        print("Starting to parse families...")
        # Debug: Count how many family records exist
        all_family_records = list(parser.records0("FAM"))
        print(f"Found {len(all_family_records)} family records in GEDCOM file")
        for fam_rec in all_family_records:
            print(f"Family record ID: {fam_rec.xref_id}")

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

            # Check if the family record is incomplete
            if not husb_record or not wife_record:
                logger.warning(
                    f"Incomplete family record: {fam_id} (missing husband or wife)"
                )
                continue

            # Skip if husband or wife is missing
            if not husband_id or not wife_id:
                logger.warning(
                    f"Skipping family record {fam_id} due to missing husband or wife"
                )
                continue

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
                    family["children"].append(
                        child_id.replace("@", "") if child_id else ""
                    )
                    # Link child to parents using IDs
                    if (
                        child_id
                        and child_id.replace("@", "") in family_data["individuals"]
                    ):
                        child_individual = family_data["individuals"][
                            child_id.replace("@", "")
                        ]
                        # Only set father and mother if they are not already set
                        if family["husband"] and not child_individual.father:
                            child_individual.father = family["husband"].replace("@", "")
                        if family["wife"] and not child_individual.mother:
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
                            if (
                                child_id.replace("@", "")
                                not in husband_individual.children
                            ):
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
                            if (
                                child_id.replace("@", "")
                                not in wife_individual.children
                            ):
                                wife_individual.children.append(
                                    child_id.replace("@", "")
                                )

                        # Populate spouses_children dictionary
                        if (
                            family["husband"]
                            and family["husband"].replace("@", "")
                            in family_data["individuals"]
                        ):
                            husband_individual = family_data["individuals"][
                                family["husband"].replace("@", "")
                            ]
                            # Initialize spouses_children if not exists
                            if husband_individual.spouses_children is None:
                                husband_individual.spouses_children = {}
                            # Add child to this spouse's children list
                            if (
                                family["wife"].replace("@", "")
                                not in husband_individual.spouses_children
                            ):
                                husband_individual.spouses_children[
                                    family["wife"].replace("@", "")
                                ] = []
                            if (
                                child_id.replace("@", "")
                                not in husband_individual.spouses_children[
                                    family["wife"].replace("@", "")
                                ]
                            ):
                                husband_individual.spouses_children[
                                    family["wife"].replace("@", "")
                                ].append(child_id.replace("@", ""))

                        if (
                            family["wife"]
                            and family["wife"].replace("@", "")
                            in family_data["individuals"]
                        ):
                            wife_individual = family_data["individuals"][
                                family["wife"].replace("@", "")
                            ]
                            # Initialize spouses_children if not exists
                            if wife_individual.spouses_children is None:
                                wife_individual.spouses_children = {}
                            # Add child to this spouse's children list
                            if (
                                family["husband"].replace("@", "")
                                not in wife_individual.spouses_children
                            ):
                                wife_individual.spouses_children[
                                    family["husband"].replace("@", "")
                                ] = []
                            if (
                                child_id.replace("@", "")
                                not in wife_individual.spouses_children[
                                    family["husband"].replace("@", "")
                                ]
                            ):
                                wife_individual.spouses_children[
                                    family["husband"].replace("@", "")
                                ].append(child_id.replace("@", ""))

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

        print(f"Finished parsing families. Total: {len(family_data['families'])}")

        print(f"Finished parsing families. Total: {len(family_data['families'])}")
        # Identify root individuals (those without parents)
        print("Identifying root individuals...")
        for ind, individual in family_data["individuals"].items():
            if not individual.father and not individual.mother:
                family_data["root_individuals"].append(ind)

        # Identify siblings for each individual
        for ind, individual in family_data["individuals"].items():
            siblings = []
            # Find all families where the individual is a child
            for fam_id, family in family_data["families"].items():
                if ind in family.get("children", []):
                    # Collect all children in the family except the individual
                    for child_id in family.get("children", []):
                        if child_id != ind:
                            siblings.append(child_id)
            # Also check for siblings in other families with the same parents
            if individual.father and individual.mother:
                for fam_id, family in family_data["families"].items():
                    if (
                        family["husband"] == individual.father
                        and family["wife"] == individual.mother
                    ):
                        for child_id in family.get("children", []):
                            if child_id != ind and child_id not in siblings:
                                siblings.append(child_id)
            individual.siblings = siblings

        # Identify adoptive, foster, and step parents
        for ind, individual in family_data["individuals"].items():
            adoptive_parents = []
            foster_parents = []
            step_parents = []
            # Check for adoptive parents
            individual_record = individual_records.get(f"@{ind}@")
            if individual_record:
                for famc_record in individual_record.sub_tags("FAMC"):
                    # Manually parse the GEDCOM content to extract the PEDI tag
                    fam_id = famc_record.xref_id.replace("@", "")
                    if fam_id in family_data["families"]:
                        family = family_data["families"][fam_id]
                        # Check if the individual has a PEDI tag indicating adoption
                        # This requires manually parsing the GEDCOM content
                        for line in gedcom_content.split("\n"):
                            if f"0 @{ind}@ INDI" in line:
                                # Look for the FAMC tag and PEDI sub-tag
                                lines = gedcom_content.split("\n")
                                for i, line in enumerate(lines):
                                    if f"1 FAMC @{fam_id}@" in line:
                                        # Check the next line for the PEDI tag
                                        if (
                                            i + 1 < len(lines)
                                            and "2 PEDI adopted" in lines[i + 1]
                                        ):
                                            if family["husband"]:
                                                adoptive_parents.append(
                                                    family["husband"].replace("@", "")
                                                )
                                            if family["wife"]:
                                                adoptive_parents.append(
                                                    family["wife"].replace("@", "")
                                                )
                                            break
            individual.adoptive_parents = adoptive_parents

            # Check for foster parents
            individual_record = individual_records.get(f"@{ind}@")
            if individual_record:
                for famc_record in individual_record.sub_tags("FAMC"):
                    # Manually parse the GEDCOM content to extract the PEDI tag
                    fam_id = famc_record.xref_id.replace("@", "")
                    if fam_id in family_data["families"]:
                        family = family_data["families"][fam_id]
                        # Check if the individual has a PEDI tag indicating foster
                        # This requires manually parsing the GEDCOM content
                        for line in gedcom_content.split("\n"):
                            if f"0 @{ind}@ INDI" in line:
                                # Look for the FAMC tag and PEDI sub-tag
                                lines = gedcom_content.split("\n")
                                for i, line in enumerate(lines):
                                    if f"1 FAMC @{fam_id}@" in line:
                                        # Check the next line for the PEDI tag
                                        if (
                                            i + 1 < len(lines)
                                            and "2 PEDI foster" in lines[i + 1]
                                        ):
                                            if family["husband"]:
                                                foster_parents.append(
                                                    family["husband"].replace("@", "")
                                                )
                                            if family["wife"]:
                                                foster_parents.append(
                                                    family["wife"].replace("@", "")
                                                )
                                            break
            individual.foster_parents = foster_parents

            # Identify step-parents
            # Step-parents are identified when an individual has multiple families
            # with the same parent but different spouses
            if individual.father or individual.mother:
                for fam_id, family in family_data["families"].items():
                    if ind in family.get("children", []):
                        # Check if the husband is not the biological father
                        if (
                            family["husband"]
                            and family["husband"].replace("@", "") != individual.father
                        ):
                            step_parents.append(family["husband"].replace("@", ""))
                        # Check if the wife is not the biological mother
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

        print("Finished parsing GEDCOM data successfully!")
        return family_data
    except Exception as e:
        print(f"Failed to parse GEDCOM data: {e}")
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
