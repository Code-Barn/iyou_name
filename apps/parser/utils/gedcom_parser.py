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
            burial_place = None
            sex = None
            title = None
            occupation = None
            events = []
            has_adop_event = False

            # Extract name information safely, prioritizing birth names
            # GEDCOM supports multiple NAME records with TYPE to indicate name type
            name_obj = getattr(record, "name", None)
            given_name = ""
            surname = ""
            full_name = ""
            honorific = ""
            suffix = ""

            if name_obj:
                given_name = getattr(name_obj, "given", "") or ""
                surname = getattr(name_obj, "surname", "") or ""
                honorific = getattr(name_obj, "prefix", "") or ""
                suffix = getattr(name_obj, "suffix", "") or ""
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
                        birth_honorific = ""
                        birth_suffix = ""
                        for sub in name_record.sub_tags():
                            if hasattr(sub, "tag"):
                                if sub.tag == "GIVN" and hasattr(sub, "value"):
                                    birth_given = str(sub.value)
                                elif sub.tag == "SURN" and hasattr(sub, "value"):
                                    birth_surname = str(sub.value)
                                elif sub.tag == "NPFX" and hasattr(sub, "value"):
                                    birth_honorific = str(sub.value)
                                elif sub.tag == "NSFX" and hasattr(sub, "value"):
                                    birth_suffix = str(sub.value)
                        birth_full = f"{birth_given} {birth_surname}".strip()
                        if birth_honorific:
                            honorific = birth_honorific
                        if birth_suffix:
                            suffix = birth_suffix
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
                elif event.tag == "BURI":
                    # Parse burial place
                    if (
                        not burial_place
                        and place_str
                        and place_str != "None"
                        and place_str != ""
                    ):
                        burial_place = (
                            place_str if isinstance(place_str, str) else str(place_str)
                        )
                elif event.tag == "ADOP":
                    # Mark that this individual has an adoption event
                    has_adop_event = True

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
                burial_place=burial_place,
                father=None,
                mother=None,
                spouse=[],
                children=[],
                events=events,
                sex=sex,
                title=title,
                honorific=honorific,
                suffix=suffix,
                occupation=occupation,
                birth_flag=None,
                death_flag=None,
                adopted=has_adop_event,
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
                    # Note: Father/mother will be corrected in the PEDI pass below
                    # to properly handle step/adopted relationships
                    if (
                        child_id
                        and child_id.replace("@", "") in family_data["individuals"]
                    ):
                        child_individual = family_data["individuals"][
                            child_id.replace("@", "")
                        ]
                        # Only set father and mother if they are not already set
                        # We'll correct these later based on PEDI tags
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

        # Identify siblings for each individual - will be done AFTER PEDI correction below

        # Identify adoptive, foster, step parents using PEDI tags
        # Use direct string parsing as ged4py doesn't expose PEDI reliably
        pedi_map = {}  # {individual_id: {family_id: pedi_type}}

        lines = gedcom_content.split("\n")

        # First pass: parse from INDI records (PEDI tags)
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
            elif line.startswith("2 _FREL ") and current_famc and current_indi:
                # Ancestry.com custom tag for father relationship type
                # _FREL = Father Relationship
                rel_type = line.replace("2 _FREL ", "").strip().lower()
                if current_indi in pedi_map:
                    # _FREL step = step father, _FREL adopted = adopted, etc.
                    existing = pedi_map[current_indi].get(current_famc)
                    if existing is None:
                        # Only set if not already set by PEDI
                        if rel_type == "step":
                            pedi_map[current_indi][current_famc] = "step"
                        elif rel_type == "adopted":
                            pedi_map[current_indi][current_famc] = "adopted"
                        elif rel_type == "foster":
                            pedi_map[current_indi][current_famc] = "foster"
                        elif rel_type in ("birth", "natural"):
                            pedi_map[current_indi][current_famc] = "birth"
                    print(
                        f"[_FREL DEBUG] Set {current_indi}.{current_famc} = {rel_type}"
                    )
            elif line.startswith("2 _MREL ") and current_famc and current_indi:
                # Ancestry.com custom tag for mother relationship type
                # _MREL = Mother Relationship
                rel_type = line.replace("2 _MREL ", "").strip().lower()
                if current_indi in pedi_map:
                    existing = pedi_map[current_indi].get(current_famc)
                    if existing is None:
                        if rel_type == "step":
                            pedi_map[current_indi][current_famc] = "step"
                        elif rel_type == "adopted":
                            pedi_map[current_indi][current_famc] = "adopted"
                        elif rel_type == "foster":
                            pedi_map[current_indi][current_famc] = "foster"
                        elif rel_type in ("birth", "natural"):
                            pedi_map[current_indi][current_famc] = "birth"
                    print(
                        f"[_MREL DEBUG] Set {current_indi}.{current_famc} = {rel_type}"
                    )

        # Second pass: parse _FREL and _MREL from FAM records
        # These are Ancestry.com custom tags on the CHIL line
        current_fam = None
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("0 ") and " FAM" in line:
                # New family record
                parts = line.split()
                if len(parts) >= 2:
                    current_fam = parts[1].replace("@", "")
            elif current_fam and line.startswith("1 CHIL @"):
                # Child in family - check for _FREL or _MREL on following lines
                child_id = line.split("@")[1] if "@" in line else None
                if child_id:
                    # Look ahead for _FREL or _MREL
                    for j in range(i + 1, min(len(lines), i + 5)):
                        next_line = lines[j].strip()
                        if next_line.startswith("2 _FREL "):
                            rel_type = next_line.replace("2 _FREL ", "").strip().lower()
                            if child_id not in pedi_map:
                                pedi_map[child_id] = {}
                            # Only set if not already set
                            if current_fam not in pedi_map.get(child_id, {}):
                                if rel_type == "step":
                                    pedi_map[child_id][current_fam] = "step"
                                elif rel_type == "adopted":
                                    pedi_map[child_id][current_fam] = "adopted"
                                elif rel_type == "foster":
                                    pedi_map[child_id][current_fam] = "foster"
                                elif rel_type in ("birth", "natural"):
                                    pedi_map[child_id][current_fam] = "birth"
                            print(
                                f"[_FREL FAM DEBUG] Set {child_id}.{current_fam} = {rel_type}"
                            )
                            break
                        elif next_line.startswith("2 _MREL "):
                            rel_type = next_line.replace("2 _MREL ", "").strip().lower()
                            if child_id not in pedi_map:
                                pedi_map[child_id] = {}
                            if current_fam not in pedi_map.get(child_id, {}):
                                if rel_type == "step":
                                    pedi_map[child_id][current_fam] = "step"
                                elif rel_type == "adopted":
                                    pedi_map[child_id][current_fam] = "adopted"
                                elif rel_type == "foster":
                                    pedi_map[child_id][current_fam] = "foster"
                                elif rel_type in ("birth", "natural"):
                                    pedi_map[child_id][current_fam] = "birth"
                            print(
                                f"[_MREL FAM DEBUG] Set {child_id}.{current_fam} = {rel_type}"
                            )
                            break
                        elif next_line.startswith("1 ") or next_line.startswith("0 "):
                            # Moved to next tag, stop looking
                            break

        print(f"[PEDI DEBUG] PEDI map: {pedi_map}")

        # Now apply PEDI info to individuals
        for ind, individual in family_data["individuals"].items():
            adoptive_parents = []
            foster_parents = []
            step_parents = []

            # Find biological families for this specific individual
            # Families NOT in pedi_map are implicitly biological (no PEDI tag = birth)
            bio_families = []
            for fam_id in family_data["families"]:
                pedi_for_fam = pedi_map.get(ind, {}).get(fam_id)
                if pedi_for_fam is None or pedi_for_fam in ("birth", "", "natural"):
                    bio_families.append(fam_id)

            # Collect all biological parents from all biological families
            biological_parent_ids = set()
            for fam_id in bio_families:
                family = family_data["families"][fam_id]
                husband_id = (family.get("husband") or "").replace("@", "")
                wife_id = (family.get("wife") or "").replace("@", "")
                if husband_id:
                    biological_parent_ids.add(husband_id)
                if wife_id:
                    biological_parent_ids.add(wife_id)

            if ind in pedi_map:
                for fam_id, pedi_type in pedi_map[ind].items():
                    if fam_id in family_data["families"]:
                        family = family_data["families"][fam_id]
                        husband_id = (family.get("husband") or "").replace("@", "")
                        wife_id = (family.get("wife") or "").replace("@", "")

                        if pedi_type == "adopted":
                            if husband_id and husband_id not in biological_parent_ids:
                                adoptive_parents.append(husband_id)
                            if wife_id and wife_id not in biological_parent_ids:
                                adoptive_parents.append(wife_id)
                        elif pedi_type == "foster":
                            if husband_id and husband_id not in biological_parent_ids:
                                foster_parents.append(husband_id)
                            if wife_id and wife_id not in biological_parent_ids:
                                foster_parents.append(wife_id)
                        elif pedi_type == "step":
                            if husband_id and husband_id not in biological_parent_ids:
                                step_parents.append(husband_id)
                            if wife_id and wife_id not in biological_parent_ids:
                                step_parents.append(wife_id)
            else:
                # No PEDI tags found - check if individual has ADOP event
                # If so, treat non-biological parents as adoptive (not step)
                if hasattr(individual, "adopted") and individual.adopted:
                    # Individual has adoption event - find non-biological parents
                    for fam_id, family in family_data["families"].items():
                        if ind not in family.get("children", []):
                            continue
                        pedi_for_fam = pedi_map.get(ind, {}).get(fam_id)
                        if pedi_for_fam and pedi_for_fam in ("birth", "", "natural"):
                            continue  # Skip biological families
                        husband_id = (family.get("husband") or "").replace("@", "")
                        wife_id = (family.get("wife") or "").replace("@", "")
                        if husband_id and husband_id not in biological_parent_ids:
                            if husband_id not in adoptive_parents:
                                adoptive_parents.append(husband_id)
                        if wife_id and wife_id not in biological_parent_ids:
                            if wife_id not in adoptive_parents:
                                adoptive_parents.append(wife_id)

            # Fix father/mother assignments: only keep biological parents
            # Find biological families for this specific individual
            # Only look at families where this individual is a child
            child_in_families = []
            for fam_id, family in family_data["families"].items():
                if ind in family.get("children", []):
                    child_in_families.append(fam_id)

            bio_families = []
            for fam_id in child_in_families:
                pedi_for_fam = pedi_map.get(ind, {}).get(fam_id)
                if pedi_for_fam is None or pedi_for_fam in ("birth", "", "natural"):
                    bio_families.append(fam_id)

            if individual.father:
                father_in_bio_family = False
                for fam_id in bio_families:
                    family = family_data["families"][fam_id]
                    husband_id = (family.get("husband") or "").replace("@", "")
                    if husband_id == individual.father:
                        father_in_bio_family = True
                        break

                if not father_in_bio_family:
                    # Father is step/adopted - find biological father
                    new_father = None
                    for fam_id in bio_families:
                        family = family_data["families"][fam_id]
                        husband_id = (family.get("husband") or "").replace("@", "")
                        if husband_id:
                            new_father = husband_id
                            break

                    if new_father:
                        print(
                            f"[PEDI] Replacing step/adopted father {individual.father} with {new_father} for {individual.full_name}"
                        )
                        # Add the old father to adoptive_parents if adopted, else step_parents
                        if individual.father:
                            if hasattr(individual, "adopted") and individual.adopted:
                                if individual.father not in adoptive_parents:
                                    adoptive_parents.append(individual.father)
                            else:
                                if individual.father not in step_parents:
                                    step_parents.append(individual.father)
                        individual.father = new_father
                    else:
                        print(
                            f"[PEDI] Removing step/adopted father {individual.father} from {individual.full_name}"
                        )
                        if individual.father:
                            if hasattr(individual, "adopted") and individual.adopted:
                                if individual.father not in adoptive_parents:
                                    adoptive_parents.append(individual.father)
                            else:
                                if individual.father not in step_parents:
                                    step_parents.append(individual.father)
                        individual.father = None

            # Same for mother - check if current mother is in a biological family
            if individual.mother:
                mother_in_bio_family = False
                for fam_id in bio_families:
                    family = family_data["families"][fam_id]
                    wife_id = (family.get("wife") or "").replace("@", "")
                    if wife_id == individual.mother:
                        mother_in_bio_family = True
                        break

                if not mother_in_bio_family:
                    # Mother is step/adopted - find biological mother
                    new_mother = None
                    for fam_id in bio_families:
                        family = family_data["families"][fam_id]
                        wife_id = (family.get("wife") or "").replace("@", "")
                        if wife_id:
                            new_mother = wife_id
                            break

                    if new_mother:
                        print(
                            f"[PEDI] Replacing step/adopted mother {individual.mother} with {new_mother} for {individual.full_name}"
                        )
                        # Add the old mother to adoptive_parents if adopted, else step_parents
                        if individual.mother:
                            if hasattr(individual, "adopted") and individual.adopted:
                                if individual.mother not in adoptive_parents:
                                    adoptive_parents.append(individual.mother)
                            else:
                                if individual.mother not in step_parents:
                                    step_parents.append(individual.mother)
                        individual.mother = new_mother
                    else:
                        print(
                            f"[PEDI] Removing step/adopted mother {individual.mother} from {individual.full_name}"
                        )
                        if individual.mother:
                            if hasattr(individual, "adopted") and individual.adopted:
                                if individual.mother not in adoptive_parents:
                                    adoptive_parents.append(individual.mother)
                            else:
                                if individual.mother not in step_parents:
                                    step_parents.append(individual.mother)
                        individual.mother = None

            individual.adoptive_parents = adoptive_parents
            individual.foster_parents = foster_parents
            individual.step_parents = step_parents

            # Debug output for adoptive/foster parents
            if adoptive_parents:
                print(
                    f"[PEDI] {individual.full_name} has adoptive parents: {adoptive_parents}"
                )
            if foster_parents:
                print(
                    f"[PEDI] {individual.full_name} has foster parents: {foster_parents}"
                )

        # Identify siblings for each individual
        # Siblings = people who appear as children in the same family record
        # Then categorize relationship type (full, half, adopted, step, foster)

        # First, build a map of family -> children
        family_children = {}  # {family_id: [child_id, child_id, ...]}
        for fam_id, family in family_data["families"].items():
            children = family.get("children", [])
            if children:
                family_children[fam_id] = children

        # For each individual, find siblings from same families
        for ind, individual in family_data["individuals"].items():
            all_siblings = []  # All siblings from any family where both are children

            # Find families where this individual is a child
            for fam_id, children in family_children.items():
                if ind in children:
                    # This individual is in this family - find other children
                    for other_child_id in children:
                        if other_child_id != ind and other_child_id not in all_siblings:
                            all_siblings.append(other_child_id)

            individual.siblings = all_siblings
            individual.half_siblings = []
            individual.step_siblings = []

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
