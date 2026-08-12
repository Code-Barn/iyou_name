import hashlib
import json
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.generator.models import GedcomFile, GedcomShare
from apps.parser.models import PersonData
from apps.chart_storage.models import IndividualPhoto

# Configure logger
logger = logging.getLogger(__name__)


def can_access_gedcom_file(user, gedcom_file):
    """Check if user can access the GEDCOM file (owner or shared with)."""
    if gedcom_file.user == user:
        return True
    return GedcomShare.objects.filter(
        gedcom_file=gedcom_file, shared_with=user
    ).exists()


def get_spouse_sort_key(spouse, individual, individuals_dict):
    """
    Get sorting key for a spouse: marriage date or oldest child's birth date.
    Returns a tuple (has_date, date_value) for sorting - earlier dates come first.
    """
    spouse_id = spouse.id

    # Check for marriage date in spouse's events
    if spouse.events:
        for event in spouse.events:
            if event.get("tag") == "MARR" and event.get("date"):
                return (True, event.get("date", ""))

    # Check for marriage date in individual's events (the marriage to this spouse)
    if individual.events:
        for event in individual.events:
            if event.get("tag") == "MARR" and event.get("date"):
                return (True, event.get("date", ""))

    # Check for oldest child's birth date from spouses_children
    # Handle both attribute access (PersonData) and dict access
    spouses_children = None
    if hasattr(individual, "spouses_children"):
        spouses_children = individual.spouses_children
    elif isinstance(individual, dict):
        spouses_children = individual.get("spouses_children")

    if spouses_children:
        children_ids = spouses_children.get(spouse_id, [])
        oldest_date = None
        for child_id in children_ids:
            if child_id in individuals_dict:
                child = individuals_dict[child_id]
                if child.birth_date:
                    if oldest_date is None or child.birth_date < oldest_date:
                        oldest_date = child.birth_date
        if oldest_date:
            return (True, oldest_date)

    # No date found - put at end
    return (False, "")


def browse_individuals(request):
    """
    View for browsing all individuals in the uploaded GEDCOM file
    """
    # Check if a file_id is provided in the request
    if request.method == "POST" and "file_id" in request.POST:
        gedcom_file_id = request.POST["file_id"]
        request.session["current_gedcom_file_id"] = gedcom_file_id

        # Check if we should redirect to individual detail
        if "redirect_to_individual" in request.POST:
            individual_id = request.POST["redirect_to_individual"]
            return redirect("browse:individual_detail", ind_id=individual_id)
    else:
        gedcom_file_id = request.session.get("current_gedcom_file_id")
        if not gedcom_file_id:
            # No file selected, redirect to upload
            return redirect("upload:home")
            # Logic moved above to handle both authenticated and anonymous users

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)

        # Check if the file belongs to the current user or is shared
        if request.user.is_authenticated:
            if not can_access_gedcom_file(request.user, gedcom_file):
                logger.error("User trying to access another user's file")
                return redirect("upload:home")
        else:
            if gedcom_file.user is not None:
                logger.error("Anonymous user trying to access owned file")
                return redirect("upload:home")

        logger.debug(f"Retrieved GEDCOM file: {gedcom_file_id}")
        logger.debug(f"parsed_data exists: {gedcom_file.parsed_data is not None}")
        if gedcom_file.parsed_data:
            logger.debug(f"parsed_data keys: {list(gedcom_file.parsed_data.keys())}")
            logger.debug(
                f"'individuals' key exists: {'individuals' in gedcom_file.parsed_data}"
            )

        if not gedcom_file.parsed_data:
            logger.error("parsed_data is None")
            return render(
                request, "browse/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})
        logger.debug(f"Number of individuals: {len(individuals)}")
        logger.debug(
            f"First individual: {list(individuals.items())[0] if individuals else 'None'}"
        )

        # Convert dictionaries to PersonData objects
        processed_individuals = []
        for ind_id, individual in individuals.items():
            logger.debug(f"Processing individual {ind_id}: {type(individual)}")
            if isinstance(individual, dict):
                person = PersonData(**individual)
                processed_individuals.append(person)
                logger.debug(f"Created PersonData for {ind_id}: {person.full_name}")
            else:
                # Ensure that non-dict individuals are PersonData objects
                if isinstance(individual, PersonData):
                    processed_individuals.append(individual)
                    logger.debug(
                        f"Using existing PersonData for {ind_id}: {individual.full_name}"
                    )
                else:
                    # Convert to PersonData if it's not already
                    person = PersonData(**individual.__dict__)
                    processed_individuals.append(person)
                    logger.debug(
                        f"Converted to PersonData for {ind_id}: {person.full_name}"
                    )

        # Get photos for individuals (if user is authenticated)
        photos = {}
        gedcom_hash = None
        if request.user.is_authenticated and gedcom_file.file:
            gedcom_hash = hashlib.sha256(gedcom_file.file.name.encode()).hexdigest()[
                :16
            ]
            individual_ids = [ind.id for ind in processed_individuals]
            photo_records = IndividualPhoto.objects.filter(
                user=request.user,
                gedcom_hash=gedcom_hash,
                individual_id__in=individual_ids,
            )
            for photo in photo_records:
                photos[photo.individual_id] = photo

        return render(
            request,
            "browse/browse_individuals.html",
            {
                "individuals": processed_individuals,
                "gedcom_file": gedcom_file,
                "photos": photos,
                "gedcom_hash": gedcom_hash,
            },
        )

    except GedcomFile.DoesNotExist:
        return render(request, "browse/error.html", {"error": "GEDCOM file not found"})


def select_individual(request):
    """
    View for selecting an individual from the GEDCOM file
    This now redirects to the unified selector
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        # No file selected, try to find available files for the user
        if request.user.is_authenticated:
            # Get user's uploaded files
            gedcom_files = GedcomFile.objects.filter(user=request.user).order_by(
                "-uploaded_at"
            )
            if gedcom_files.exists():
                # If user has files, redirect to selector for the most recent file
                most_recent_file = gedcom_files.first()
                return redirect(
                    "selector:select_individual", file_id=most_recent_file.id
                )
            else:
                # User has no files, redirect to upload
                return redirect("upload:home")
        else:
            # Anonymous user, check for anonymous files
            anonymous_files = GedcomFile.objects.filter(user=None).order_by(
                "-uploaded_at"
            )
            if anonymous_files.exists():
                # If there are anonymous files, use the most recent one
                most_recent_file = anonymous_files.first()
                return redirect(
                    "selector:select_individual", file_id=most_recent_file.id
                )
            else:
                # No files available, redirect to upload
                return redirect("upload:home")

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        return redirect("selector:select_individual", file_id=gedcom_file.id)
    except GedcomFile.DoesNotExist:
        return render(request, "browse/error.html", {"error": "GEDCOM file not found"})


def individual_detail(request, ind_id):
    """
    View for displaying detailed information about an individual
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return render(
            request, "browse/error.html", {"error": "No GEDCOM file selected"}
        )

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)

        # Check if the file belongs to the current user or is shared
        if request.user.is_authenticated:
            if not can_access_gedcom_file(request.user, gedcom_file):
                return render(
                    request,
                    "browse/error.html",
                    {"error": "Not authorized to access this file"},
                )
        else:
            if gedcom_file.user is not None:
                return render(
                    request,
                    "browse/error.html",
                    {"error": "Not authorized to access this file"},
                )

        logger.debug(f"Retrieved GEDCOM file: {gedcom_file_id}")
        logger.debug(f"parsed_data exists: {gedcom_file.parsed_data is not None}")
        if gedcom_file.parsed_data:
            logger.debug(f"parsed_data keys: {list(gedcom_file.parsed_data.keys())}")
            logger.debug(
                f"'individuals' key exists: {'individuals' in gedcom_file.parsed_data}"
            )

        if not gedcom_file.parsed_data:
            logger.error("parsed_data is None")
            return render(
                request, "browse/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})
        logger.debug(f"Looking for individual: {ind_id}")
        logger.debug(f"Available individuals: {list(individuals.keys())}")

        if ind_id not in individuals:
            logger.error(f"Individual {ind_id} not found in individuals")
            return render(
                request, "browse/error.html", {"error": "Individual not found"}
            )

        individual_data = individuals[ind_id]
        logger.debug(f"Individual data type: {type(individual_data)}")
        if isinstance(individual_data, dict):
            individual = PersonData(**individual_data)
            logger.debug(f"Created PersonData for {ind_id}: {individual.full_name}")
        else:
            individual = individual_data
            logger.debug(
                f"Using existing PersonData for {ind_id}: {individual.full_name}"
            )

        # Debug: Print individual's family relationships
        logger.debug(f"Individual {ind_id} family relationships:")
        logger.debug(f"  Father: {individual.father}")
        logger.debug(f"  Mother: {individual.mother}")
        logger.debug(f"  Spouse: {individual.spouse}")
        logger.debug(f"  Children: {individual.children}")
        logger.debug(f"  Siblings: {individual.siblings}")
        logger.debug(f"  Adoptive Parents: {individual.adoptive_parents}")
        logger.debug(f"  Foster Parents: {individual.foster_parents}")
        logger.debug(f"  Step Parents: {individual.step_parents}")
        logger.debug(f"  Step Siblings: {individual.step_siblings}")
        logger.debug(f"  Spouses Children: {individual.spouses_children}")

        # Debug: Print all available individuals to see if family members exist
        logger.debug(f"Available individuals in file: {list(individuals.keys())}")

        # Debug: Check if potential family members exist in the individuals dict
        if individual.father:
            logger.debug(
                f"Father {individual.father} exists: {individual.father in individuals}"
            )
        if individual.mother:
            logger.debug(
                f"Mother {individual.mother} exists: {individual.mother in individuals}"
            )
        if individual.spouse:
            for spouse_id in individual.spouse:
                logger.debug(f"Spouse {spouse_id} exists: {spouse_id in individuals}")
        if individual.children:
            for child_id in individual.children:
                logger.debug(f"Child {child_id} exists: {child_id in individuals}")
        if individual.siblings:
            for sibling_id in individual.siblings:
                logger.debug(
                    f"Sibling {sibling_id} exists: {sibling_id in individuals}"
                )

        # Prepare family relationship data
        individuals_dict = {}
        processed_individuals = []

        # Convert all individuals to PersonData objects and create a lookup dictionary
        for ind_id, ind_data in individuals.items():
            if isinstance(ind_data, dict):
                person = PersonData(**ind_data)
                individuals_dict[ind_id] = person
                processed_individuals.append(person)
            else:
                # Ensure that non-dict individuals are PersonData objects
                if isinstance(ind_data, PersonData):
                    individuals_dict[ind_id] = ind_data
                    processed_individuals.append(ind_data)
                else:
                    # Convert to PersonData if it's not already
                    person = PersonData(**ind_data.__dict__)
                    individuals_dict[ind_id] = person
                    processed_individuals.append(person)

        # Get father and mother objects
        father = None
        mother = None
        if individual.father and individual.father in individuals_dict:
            father = individuals_dict[individual.father]
        if individual.mother and individual.mother in individuals_dict:
            mother = individuals_dict[individual.mother]

        # Get siblings objects (full siblings)
        siblings = []
        if individual.siblings:
            for sibling_id in individual.siblings:
                if sibling_id in individuals_dict:
                    siblings.append(individuals_dict[sibling_id])

        # Get half-siblings objects
        half_siblings = []
        if hasattr(individual, "half_siblings") and individual.half_siblings:
            for sibling_id in individual.half_siblings:
                if sibling_id in individuals_dict:
                    half_siblings.append(individuals_dict[sibling_id])

        # Get step-siblings objects
        step_siblings = []
        if hasattr(individual, "step_siblings") and individual.step_siblings:
            for sibling_id in individual.step_siblings:
                if sibling_id in individuals_dict:
                    step_siblings.append(individuals_dict[sibling_id])

        # Get all siblings objects (combined list for counting)
        all_siblings = []
        if hasattr(individual, "all_siblings") and individual.all_siblings:
            for sibling_id in individual.all_siblings:
                if sibling_id in individuals_dict:
                    all_siblings.append(individuals_dict[sibling_id])

        # Sort all siblings by birth date (oldest first, then by name for ties)
        def get_birth_sort_key(person):
            date = person.birth_date if hasattr(person, "birth_date") else None
            if date:
                # Try to parse year
                import re

                year_match = re.search(r"\d{4}", str(date))
                if year_match:
                    return (int(year_match.group()), person.full_name.lower())
            return (
                9999,
                person.full_name.lower() if hasattr(person, "full_name") else "",
            )

        all_siblings.sort(key=get_birth_sort_key)
        siblings.sort(key=get_birth_sort_key)
        half_siblings.sort(key=get_birth_sort_key)
        step_siblings.sort(key=get_birth_sort_key)

        # Get spouses objects
        spouses = []
        if individual.spouse:
            for spouse_id in individual.spouse:
                if spouse_id in individuals_dict:
                    spouses.append(individuals_dict[spouse_id])

        # Sort spouses by marriage date or oldest child's birth date
        spouses.sort(key=lambda s: get_spouse_sort_key(s, individual, individuals_dict))

        # Get children objects
        children = []
        children_relationship = {}  # {child_id: 'biological', 'adopted', 'foster', 'step'}

        if individual.children:
            for child_id in individual.children:
                if child_id in individuals_dict:
                    child = individuals_dict[child_id]
                    children.append(child)

                    # Determine relationship type based on child's adoptive_parents/foster_parents/step_parents
                    # Also check if child has adopted flag
                    is_adopted = hasattr(child, "adopted") and child.adopted
                    rel_type = "biological"
                    if hasattr(child, "adoptive_parents") and child.adoptive_parents:
                        if individual.id in child.adoptive_parents:
                            rel_type = "adopted"
                    if (
                        rel_type == "biological"
                        and hasattr(child, "foster_parents")
                        and child.foster_parents
                    ):
                        if individual.id in child.foster_parents:
                            rel_type = "foster"
                    if (
                        rel_type == "biological"
                        and hasattr(child, "step_parents")
                        and child.step_parents
                    ):
                        if individual.id in child.step_parents:
                            # If child has adopted flag, treat as adopted even if in step_parents
                            if is_adopted:
                                rel_type = "adopted"
                            else:
                                rel_type = "step"
                    children_relationship[child_id] = rel_type

        # Build structured spouse groups: each group carries the spouse object plus
        # the children shared with that spouse (excluding the spouse's step/adoptive/
        # foster children, matching the previous template-side count logic).
        spouse_groups = []
        assigned_child_ids = set()
        for spouse in spouses:
            spouse_child_ids = (
                individual.spouses_children.get(spouse.id, [])
                if hasattr(individual, "spouses_children")
                and individual.spouses_children
                else []
            )
            group_children = []
            for child_id in spouse_child_ids:
                if child_id not in individuals_dict:
                    continue
                child = individuals_dict[child_id]
                step_parents = getattr(child, "step_parents", None) or []
                adoptive_parents = getattr(child, "adoptive_parents", None) or []
                foster_parents = getattr(child, "foster_parents", None) or []
                if (
                    spouse.id in step_parents
                    or spouse.id in adoptive_parents
                    or spouse.id in foster_parents
                ):
                    continue
                group_children.append(child)
                assigned_child_ids.add(child_id)
            spouse_groups.append(
                {
                    "spouse": spouse,
                    "children": group_children,
                    "count": len(group_children),
                }
            )

        # Children who belong to this individual but are not tied to any spouse group
        # (e.g. single parents, or children from relationships without a FAM record)
        unassigned_children = [
            child for child in children if child.id not in assigned_child_ids
        ]

        # Explicit sibling metadata for template count badges
        full_siblings_count = len(siblings)
        half_siblings_count = len(half_siblings)
        step_siblings_count = len(step_siblings)
        total_siblings_count = len(all_siblings)

        # Check if this individual is the home person for this file
        is_home_person = False
        if gedcom_file.home_person_id == individual.id:
            is_home_person = True

        # Get photo for this individual (if user is authenticated)
        individual_photo = None
        photos = {}
        gedcom_hash = None
        gedcom_hash_short = None
        if request.user.is_authenticated and gedcom_file.file:
            gedcom_hash = hashlib.sha256(gedcom_file.file.name.encode()).hexdigest()
            gedcom_hash_short = gedcom_hash[:16]
            try:
                individual_photo = IndividualPhoto.objects.get(
                    user=request.user,
                    gedcom_hash=gedcom_hash_short,
                    individual_id=individual.id,
                )
            except IndividualPhoto.DoesNotExist:
                individual_photo = None
            # Get all photos for family members
            family_ids = [ind_id for ind_id in individuals_dict.keys()]
            photo_records = IndividualPhoto.objects.filter(
                user=request.user,
                gedcom_hash=gedcom_hash_short,
                individual_id__in=family_ids,
            )
            for photo in photo_records:
                photos[photo.individual_id] = photo

        return render(
            request,
            "browse/individual_detail.html",
            {
                "individual": individual,
                "file_id": gedcom_file_id,
                "father": father,
                "mother": mother,
                "siblings": siblings,
                "half_siblings": half_siblings,
                "step_siblings": step_siblings,
                "all_siblings": all_siblings,
                "full_siblings_count": full_siblings_count,
                "half_siblings_count": half_siblings_count,
                "step_siblings_count": step_siblings_count,
                "total_siblings_count": total_siblings_count,
                "spouses": spouses,
                "spouse_groups": spouse_groups,
                "children": children,
                "children_relationship": children_relationship,
                "unassigned_children": unassigned_children,
                "individuals_dict": individuals_dict,
                "individuals_json": json.dumps(
                    [ind.to_dict() for ind in processed_individuals]
                ),
                "is_home_person": is_home_person,
                "file_name": gedcom_file.file.name
                if gedcom_file.file
                else "Unknown File",
                "individual_photo": individual_photo,
                "gedcom_hash": gedcom_hash_short,
                "photos": photos,
            },
        )

    except GedcomFile.DoesNotExist:
        return render(request, "browse/error.html", {"error": "GEDCOM file not found"})
