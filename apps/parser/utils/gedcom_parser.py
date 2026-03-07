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

            # Extract name information safely, prioritizing birth names
            # GEDCOM supports multiple NAME records with TYPE to indicate name type
            name_obj = getattr(record, "name", None)
            given_name = ""
            surname = ""
            full_name = ""

            if name_obj:
                given_name = getattr(name_obj, "given", "") or ""
                surname = getattr(name_obj, "surname", "") or ""
                full_name = (
                    getattr(name_obj, "format", lambda: f"{given_name} {surname}")()
                    or f"{given_name} {surname}".strip()
                )

            # Check for TYPE BIRTH name among NAME records
            birth_given = ""
            birth_surname = ""
            birth_full = ""
            try:
                name_records = list(record.sub_tags("NAME"))
                print(f"[DEBUG] Found {len(name_records)} NAME records for {ind}")
                # Search ALL name records for TYPE=BIRTH (not just multiple)
                for i, name_record in enumerate(name_records):
                    print(
                        f"[DEBUG] NAME record {i}: {getattr(name_record, 'format', lambda: 'N/A')()}"
                    )
                    # Get all sub-tags and look for TYPE
                    type_value = ""
                    for sub in name_record.sub_tags():
                        print(
                            f"[DEBUG]   sub-tag: {getattr(sub, 'tag', '?')} = {getattr(sub, 'value', '?')}"
                        )
                        if hasattr(sub, "tag") and sub.tag == "TYPE":
                            if hasattr(sub, "value") and sub.value:
                                type_value = str(sub.value).upper()
                            print(f"[DEBUG]   Found TYPE: {type_value}")
                            break

                    if type_value == "BIRTH":
                        # Extract given and surname from sub-tags
                        birth_given = ""
                        birth_surname = ""
                        for sub in name_record.sub_tags():
                            if hasattr(sub, "tag"):
                                if sub.tag == "GIVN" and hasattr(sub, "value"):
                                    birth_given = str(sub.value)
                                elif sub.tag == "SURN" and hasattr(sub, "value"):
                                    birth_surname = str(sub.value)
                        birth_full = f"{birth_given} {birth_surname}".strip()
                        print(f"[DEBUG] Found BIRTH name: {birth_full}")
                        break

                # Use birth name if found and valid
                if birth_surname:
                    given_name = birth_given
                    surname = birth_surname
                    full_name = birth_full
            except Exception as e:
                # If anything goes wrong, keep the default name
                print(f"[DEBUG] Error finding birth name: {e}")
                pass

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
                # Only use the FIRST BIRT event (not alternates)
                if event.tag == "BIRT" and birth_date is None and birth_place is None:
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

            # Process family record even if only one spouse is present
            # (GEDCOM allows single-parent families)

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
                        print(
                            f"  Added spouse {wife_id.replace('@', '')} to {husband_individual.id}, now has {len(husband_individual.spouse)} spouses"
                        )
                        # Initialize spouses_children for this spouse even if no children
                        if husband_individual.spouses_children is None:
                            husband_individual.spouses_children = {}
                        if (
                            wife_id.replace("@", "")
                            not in husband_individual.spouses_children
                        ):
                            husband_individual.spouses_children[
                                wife_id.replace("@", "")
                            ] = []

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
                        # Initialize spouses_children for this spouse even if no children
                        if wife_individual.spouses_children is None:
                            wife_individual.spouses_children = {}
                        if (
                            husband_id.replace("@", "")
                            not in wife_individual.spouses_children
                        ):
                            wife_individual.spouses_children[
                                husband_id.replace("@", "")
                            ] = []

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
                                print(
                                    f"  Added child {child_id.replace('@', '')} to husband {husband_individual.id}, now has {len(husband_individual.children)} children"
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
                            # Add child to this spouse's children list (only if wife exists)
                            if family["wife"]:
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
                            # Add child to this spouse's children list (only if husband exists)
                            if family["husband"]:
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
            full_siblings = []  # Same both parents
            half_siblings = []  # Same one parent only

            # Get all families where this individual is a child
            individual_families = []
            for fam_id, family in family_data["families"].items():
                if ind in family.get("children", []):
                    individual_families.append((fam_id, family))

            # For each family this person belongs to
            for fam_id, fam in individual_families:
                father_id = fam.get("husband")
                mother_id = fam.get("wife")

                # First: add siblings from the SAME family (definitely full siblings)
                for child_id in fam.get("children", []):
                    if child_id == ind:
                        continue
                    if child_id not in full_siblings:
                        full_siblings.append(child_id)

                # Then: look at other families to find half-siblings
                for other_fam_id, other_fam in family_data["families"].items():
                    if other_fam_id == fam_id:
                        continue

                    other_father = other_fam.get("husband")
                    other_mother = other_fam.get("wife")

                    # Get children of the other family
                    other_children = other_fam.get("children", [])

                    for child_id in other_children:
                        if child_id == ind:
                            continue

                        # Check if this child is already identified as full sibling
                        if child_id in full_siblings:
                            continue

                        # Get the other child's parents
                        child_obj = family_data["individuals"].get(child_id)
                        if not child_obj:
                            continue

                        child_father = child_obj.father
                        child_mother = child_obj.mother

                        # Count shared parents
                        shared_parents = 0
                        if father_id and child_father and father_id == child_father:
                            shared_parents += 1
                        if mother_id and child_mother and mother_id == child_mother:
                            shared_parents += 1

                        if shared_parents == 1:
                            # Half siblings - same one parent
                            if child_id not in half_siblings:
                                half_siblings.append(child_id)

            individual.siblings = full_siblings
            individual.half_siblings = half_siblings
            # step_siblings requires step-parent data which is complex to determine
            # Leave as empty for now - can be enhanced later with PEDI tags
            individual.step_siblings = []

        # Identify adoptive, foster parents using PEDI tags
        # Use direct string parsing as ged4py doesn't expose PEDI reliably
        pedi_map = {}  # {individual_id: {family_id: pedi_type}}

        lines = gedcom_content.split("\n")
        current_indi = None
        current_famc = None

        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("0 ") and " INDI" in line:
                # New individual record
                parts = line.split()
                if len(parts) >= 2:
                    current_indi = parts[1].replace("@", "")
                    current_famc = None
            elif line.startswith("1 FAMC @"):
                # Family where individual is child
                fam_id = line.split("@")[1] if "@" in line else None
                if fam_id and current_indi:
                    if current_indi not in pedi_map:
                        pedi_map[current_indi] = {}
                    current_famc = fam_id
            elif line.startswith("2 PEDI ") and current_famc and current_indi:
                # PEDI tag for the current FAMC
                pedi_type = line.replace("2 PEDI ", "").strip().lower()
                if current_indi in pedi_map:
                    pedi_map[current_indi][current_famc] = pedi_type
                    print(
                        f"[PEDI DEBUG] Set {current_indi}.{current_famc} = {pedi_type}"
                    )

        print(f"[PEDI DEBUG] PEDI map: {pedi_map}")

        # Now apply PEDI info to individuals
        for ind, individual in family_data["individuals"].items():
            adoptive_parents = []
            foster_parents = []

            if ind in pedi_map:
                for fam_id, pedi_type in pedi_map[ind].items():
                    if fam_id in family_data["families"]:
                        family = family_data["families"][fam_id]
                        husband_id = (family.get("husband") or "").replace("@", "")
                        wife_id = (family.get("wife") or "").replace("@", "")

                        if pedi_type == "adopted":
                            if husband_id:
                                adoptive_parents.append(husband_id)
                            if wife_id:
                                adoptive_parents.append(wife_id)
                        elif pedi_type == "foster":
                            if husband_id:
                                foster_parents.append(husband_id)
                            if wife_id:
                                foster_parents.append(wife_id)

            individual.adoptive_parents = adoptive_parents
            individual.foster_parents = foster_parents
            individual.step_parents = []  # Phase 2

            # Debug output for adoptive/foster parents
            if adoptive_parents:
                print(
                    f"[PEDI] {individual.full_name} has adoptive parents: {adoptive_parents}"
                )
            if foster_parents:
                print(
                    f"[PEDI] {individual.full_name} has foster parents: {foster_parents}"
                )

        # Debug: Print all individuals and their relationships
        print("\n=== Debug: Individuals and Relationships ===")
        for ind, individual in family_data["individuals"].items():
            print(f"\nIndividual: {individual.full_name} (ID: {ind})")
            print(f"  Father: {individual.father}")
            print(f"  Mother: {individual.mother}")
            print(f"  Spouse: {individual.spouse}")
            print(f"  Children: {individual.children}")
            print(f"  Siblings: {individual.siblings}")
            if individual.adoptive_parents:
                print(f"  Adoptive Parents: {individual.adoptive_parents}")
            if individual.foster_parents:
                print(f"  Foster Parents: {individual.foster_parents}")

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
