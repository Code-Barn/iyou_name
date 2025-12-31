import importlib
import json
import logging

from django.conf import settings
from django.contrib.auth import login
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

# Set up logging
logger = logging.getLogger(__name__)

from .forms import RegisterForm
from .models import GedcomFile, PersonData
from .utils.gedcom_parser import convert_to_utf8, parse_gedcom_data

logger.debug("STATICFILES_DIRS: %s", settings.STATICFILES_DIRS)
logger.debug("STATIC_ROOT: %s", settings.STATIC_ROOT)
logger.debug("STATIC_URL: %s", settings.STATIC_URL)

# Template mapping
TEMPLATE_MAPPING = {
    "1": {
        "module": "apps.generator.utils.image_1generator",
        "function": "generate_family_tree",
        "filename": "US_LETTER_1GEN_BW.pdf",
        "name": "1 Generation (Individual Only)",
    },
    "4": {
        "module": "apps.generator.utils.image_4generator",
        "function": "generate_family_tree",
        "filename": "US_LETTER_4GEN_BW.pdf",
        "name": "4 Generation Chart",
    },
    # Add more templates as you create them
    # '2': {...}, '3': {...}, etc.
}


def get_spouse_and_children(spouse_id, individual_id, individuals_dict, family):
    """
    Helper function to retrieve a spouse and their shared children.

    Args:
        spouse_id (str): The ID of the spouse.
        individual_id (str): The ID of the individual.
        individuals_dict (dict): Dictionary of all individuals.
        family (dict): The family data.

    Returns:
        tuple: (spouse, spouse_children) where spouse is a PersonData object and
               spouse_children is a list of PersonData objects.
    """
    spouse = None
    spouse_children = []

    if spouse_id and spouse_id != individual_id and spouse_id in individuals_dict:
        try:
            spouse_data = individuals_dict[spouse_id]
            spouse = PersonData(**spouse_data)

            # Filter children for this spouse
            if family.get("children"):
                for child_id in family["children"]:
                    if child_id in individuals_dict:
                        try:
                            child_data = individuals_dict[child_id]
                            spouse_children.append(PersonData(**child_data))
                        except Exception as e:
                            logger.error(
                                f"Error parsing child data for {child_id}: {str(e)}"
                            )
        except Exception as e:
            logger.error(f"Error parsing spouse data for {spouse_id}: {str(e)}")

    return spouse, spouse_children


def preprocess_family_data(family_data):
    """
    Pre-process family data to create quick lookup dictionaries.

    Args:
        family_data (dict): The raw family data from the session.

    Returns:
        tuple: (individuals_dict, families_dict, family_children_map) where:
               - individuals_dict: Dictionary of all individuals.
               - families_dict: Dictionary of all families.
               - family_children_map: Mapping of family IDs to their children.
    """
    individuals_dict = family_data.get("individuals", {})
    families_dict = family_data.get("families", {})
    family_children_map = {}

    # Pre-process family children for quick lookup
    for fam_id, family in families_dict.items():
        if family.get("children"):
            family_children_map[fam_id] = family["children"]

    return individuals_dict, families_dict, family_children_map


def upload_file(request):
    """
    View for displaying the upload file form.
    """
    return render(
        request,
        "generator/upload_file.html",
        {"TEMPLATE_MAPPING": TEMPLATE_MAPPING},
    )


def upload_and_generate(request):
    """
    View for handling the main upload and generate workflow
    """
    if request.method == "POST" and "gedcom_file" in request.FILES:
        gedcom_file = request.FILES["gedcom_file"]

        try:
            # Read the file content directly for parsing
            gedcom_content_bytes = gedcom_file.read()
            print(
                f"DEBUG: Read file content. Length: {len(gedcom_content_bytes)} bytes"
            )

            # Save the file
            gedcom_model = GedcomFile.objects.create(
                file=ContentFile(gedcom_content_bytes, name=gedcom_file.name),
                user=request.user if request.user.is_authenticated else None,
            )

            # Parse the GEDCOM data
            try:
                gedcom_content = convert_to_utf8(gedcom_content_bytes)
            except Exception as e:
                print(f"DEBUG: Error converting to UTF-8: {e}")
                raise

            try:
                family_data = parse_gedcom_data(gedcom_content)
            except Exception as e:
                print(f"DEBUG: Error parsing GEDCOM data: {e}")
                raise

            # Store parsed data directly in the GedcomFile model
            gedcom_model.parsed_data = {
                "individuals": {
                    ind_id: person.to_dict()
                    for ind_id, person in family_data["individuals"].items()
                },
                "families": family_data["families"],
                "root_individuals": family_data["root_individuals"],
            }
            gedcom_model.home_person_id = (
                family_data["root_individuals"][0]
                if family_data["root_individuals"]
                else None
            )
            gedcom_model.is_processed = True
            gedcom_model.processing_date = timezone.now()
            gedcom_model.save()

            # Store reference to the processed file in session
            request.session["current_gedcom_file_id"] = gedcom_model.id
            request.session["selected_template"] = "4"  # Default template

            individuals = list(family_data["individuals"].values())
            return render(
                request,
                "generator/select_individual.html",
                {
                    "individuals": individuals,
                    "template": "4",
                    "TEMPLATE_MAPPING": TEMPLATE_MAPPING,
                },
            )

        except Exception as e:
            logger.error(f"Error processing GEDCOM file: {e}")
            return render(request, "generator/error.html", {"error": str(e)})

    if request.user.is_authenticated:
        return redirect("generator:profile")
    return render(
        request, "generator/upload_file.html", {"TEMPLATE_MAPPING": TEMPLATE_MAPPING}
    )


def upload_and_process(request):
    if request.method == "POST" and "gedcom_file" in request.FILES:
        gedcom_file = request.FILES["gedcom_file"]

        # Read the file content directly for parsing
        gedcom_content_bytes = gedcom_file.read()

        # Save the file
        gedcom_model = GedcomFile.objects.create(
            file=ContentFile(gedcom_content_bytes, name=gedcom_file.name),
            user=request.user if request.user.is_authenticated else None,
        )

        # Parse only if not already processed
        if not gedcom_model.is_processed:
            try:
                # Convert the file content to UTF-8 and parse
                gedcom_content = convert_to_utf8(gedcom_content_bytes)
                family_data = parse_gedcom_data(gedcom_content)

                # Store parsed data directly in the GedcomFile model
                gedcom_model.parsed_data = {
                    "individuals": {
                        ind_id: person.to_dict()
                        for ind_id, person in family_data["individuals"].items()
                    },
                    "families": family_data["families"],
                    "root_individuals": family_data["root_individuals"],
                }
                gedcom_model.home_person_id = (
                    family_data["root_individuals"][0]
                    if family_data["root_individuals"]
                    else None
                )
                gedcom_model.is_processed = True
                gedcom_model.processing_date = timezone.now()
                gedcom_model.save()

            except Exception as e:
                # Handle parsing errors
                gedcom_model.delete()
                return render(request, "generator/error.html", {"error": str(e)})

        # Store reference to the processed file in session
        request.session["current_gedcom_file_id"] = gedcom_model.id
        request.session["selected_template"] = "4"  # Default template

        return redirect("generator:select_individual")


def get_family_data(request):
    """Centralized function to retrieve family data"""
    gedcom_file_id = request.session.get("current_gedcom_file_id")

    if gedcom_file_id:
        try:
            gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
            return gedcom_file.parsed_data
        except GedcomFile.DoesNotExist:
            pass

    # Fallback: Try to get the latest file for authenticated users
    if request.user.is_authenticated:
        latest_file = (
            GedcomFile.objects.filter(user=request.user)
            .order_by("-uploaded_at")
            .first()
        )
        if latest_file:
            request.session["current_gedcom_file_id"] = latest_file.id
            return latest_file.parsed_data

    return None


def delete_gedcom_file(request, file_id):
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)

        # Only allow deletion by the owner or admin
        if request.user != gedcom_file.user and not request.user.is_staff:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        file_name = gedcom_file.file.name
        gedcom_file.delete()

        # Clear session data if this was the current file
        if str(gedcom_file.id) == request.session.get("current_gedcom_file_id"):
            del request.session["current_gedcom_file_id"]
            if "family_data" in request.session:
                del request.session["family_data"]

        return JsonResponse(
            {
                "success": True,
                "message": f"File {file_name} and all associated data deleted successfully",
            }
        )

    except GedcomFile.DoesNotExist:
        return JsonResponse({"error": "File not found"}, status=404)


def get_cached_family_data(gedcom_file_id):
    """
    Get family data with caching support.

    Args:
        gedcom_file_id: ID of the GedcomFile to retrieve

    Returns:
        dict: Family data or None if not found
    """
    # Generate cache key
    cache_key = f"family_data_{gedcom_file_id}"

    # Try to get from cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.debug(f"Cache hit for file {gedcom_file_id}")
        return cached_data

    try:
        # Get from database
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        if gedcom_file and gedcom_file.parsed_data:
            # Cache for 1 hour (3600 seconds)
            cache.set(cache_key, gedcom_file.parsed_data, 3600)
            logger.debug(f"Cached data for file {gedcom_file_id}")
            return gedcom_file.parsed_data

    except GedcomFile.DoesNotExist:
        logger.warning(f"GedcomFile {gedcom_file_id} not found")
    except Exception as e:
        logger.error(f"Error retrieving cached data for {gedcom_file_id}: {e}")

    return None


def profile(request):
    """
    View for displaying the user's profile and uploaded GEDCOM files.
    """
    # Redirect to login if user is not authenticated
    if not request.user.is_authenticated:
        return redirect("generator:login")

    # Retrieve all GEDCOM files uploaded by the user
    gedcom_files = GedcomFile.objects.filter(user=request.user)

    # Handle manual entry of home person name
    if request.method == "POST" and "home_person_name" in request.POST:
        file_id = request.POST.get("file_id")
        home_person_name = request.POST.get("home_person_name")
        try:
            file = GedcomFile.objects.get(id=file_id, user=request.user)
            if file.parsed_data and "individuals" in file.parsed_data:
                # Search for the individual with the matching name
                for ind_id, individual_data in file.parsed_data["individuals"].items():
                    if home_person_name.lower() in individual_data["full_name"].lower():
                        file.home_person_id = ind_id
                        file.save()
                        break
        except GedcomFile.DoesNotExist:
            pass

    # Handle selection of home person from search results
    if request.method == "POST" and "home_person_id" in request.POST:
        file_id = request.POST.get("file_id")
        home_person_id = request.POST.get("home_person_id")
        try:
            file = GedcomFile.objects.get(id=file_id, user=request.user)
            file.home_person_id = home_person_id
            file.save()
        except GedcomFile.DoesNotExist:
            pass

    # The parsed data is now stored directly in the GedcomFile model
    # No need to retrieve from ParsedGedcomData
    for file in gedcom_files:
        if (
            file.parsed_data
            and file.home_person_id
            and "individuals" in file.parsed_data
        ):
            file.home_person = PersonData(
                **file.parsed_data["individuals"][file.home_person_id]
            )

    return render(
        request,
        "generator/profile.html",
        {"gedcom_files": gedcom_files},
    )


def browse_individuals(request):
    """View for browsing all individuals in the family data"""
    family_data = get_family_data(request)

    if not family_data:
        return render(
            request,
            "generator/error.html",
            {"error": "No family data found. Please upload a GEDCOM file first."},
        )

    # Convert back to PersonData objects for display
    individuals = []
    for ind_id, data in family_data["individuals"].items():
        individual = PersonData(**data)
        individuals.append(individual)

    return render(
        request,
        "generator/browse_individuals.html",
        {"individuals": individuals},
    )


def select_individual(request):
    """Handle selection of primary individual and generate chart"""
    logger.debug("select_individual called")
    try:
        if request.method == "GET":
            # Get family data using the centralized function
            family_data = get_family_data(request)
            if not family_data:
                logger.debug("No family data found, redirecting")
                return redirect("generator:home")

            # Convert back to PersonData objects for display
            individuals = []
            for ind_id, data in family_data["individuals"].items():
                individual = PersonData(**data)
                individuals.append(individual)

            # Get the selected template from session
            selected_template = request.session.get("selected_template", "4")

            template_name = TEMPLATE_MAPPING.get(selected_template, {}).get(
                "name", "Unknown"
            )

            return render(
                request,
                "generator/select_individual.html",
                {
                    "individuals": individuals,
                    "template": template_name,
                    "TEMPLATE_MAPPING": TEMPLATE_MAPPING,
                },
            )

        if request.method == "POST":
            logger.debug("POST request received")

            selected_id = request.POST.get("individual_id")
            logger.debug(f"Selected ID: {selected_id}")

            if not selected_id:
                logger.debug("No individual selected, redirecting")
                return redirect("generator:home")

            # Get family data using the centralized function
            family_data = get_family_data(request)
            if not family_data:
                logger.debug("No family data found, redirecting")
                return redirect("generator:home")

            # Convert back to PersonData objects for processing
            individuals = {}
            for ind_id, data in family_data["individuals"].items():
                individuals[ind_id] = PersonData(**data)

            # Reconstruct family_data with PersonData objects
            reconstructed_family_data = {
                "individuals": individuals,
                "families": family_data["families"],
                "root_individuals": family_data["root_individuals"],
            }

            # Update the home person in the current GEDCOM file
            if selected_id:
                gedcom_file_id = request.session.get("current_gedcom_file_id")
                if gedcom_file_id:
                    try:
                        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
                        gedcom_file.home_person_id = selected_id
                        gedcom_file.save()
                    except GedcomFile.DoesNotExist:
                        pass

            # Get the selected individual
            selected_individual = reconstructed_family_data["individuals"].get(
                selected_id
            )
            logger.debug(f"Selected individual: {selected_individual}")

            if not selected_individual:
                logger.debug("Selected individual not found, redirecting")  # Add this
                return redirect("generator:display")

            # Generate the family tree image using the selected template
            try:
                # Get the selected template from session
                selected_template = request.session.get("selected_template", "4")
                print(f"DEBUG: selected_template in POST = {selected_template}")
                print(
                    f"DEBUG: selected_template type in POST = {type(selected_template)}"
                )
                print(f"DEBUG: TEMPLATE_MAPPING keys = {list(TEMPLATE_MAPPING.keys())}")
                template_config = TEMPLATE_MAPPING.get(
                    selected_template, TEMPLATE_MAPPING["4"]
                )

                # Dynamically import the appropriate generator module
                module = importlib.import_module(template_config["module"])
                generator_func = getattr(module, template_config["function"])

                # Call the appropriate generator function
                if selected_template == "1":
                    # 1-gen template only needs the primary individual
                    image_buffer = generator_func(selected_individual)
                else:
                    # Other templates need full family data
                    image_buffer = generator_func(
                        selected_individual, reconstructed_family_data
                    )

                # Store settings in session for HUD
                request.session["selected_individual_id"] = selected_id
                request.session["selected_template"] = selected_template
                request.session["chart_parameters"] = {}

                # Redirect to HUD display instead of generating chart directly
                return redirect("generator:display_tree")

            except Exception as e:
                import traceback

                traceback.print_exc()
                return render(request, "generator/error.html", {"error": str(e)})

    except Exception as e:
        import traceback

        traceback.print_exc()
        return redirect("generator:display")


def individual_detail(request, ind_id):
    try:
        # Get the family data using centralized function
        family_data = get_family_data(request)

        if not family_data:
            return render(
                request,
                "generator/error.html",
                {"error": "No family data found. Please upload a GEDCOM file first."},
            )

        # Pre-process family data for quick lookups
        individuals_dict, families_dict, family_children_map = preprocess_family_data(
            family_data
        )

        # Fetch the individual's data using the ind_id
        individual_data = individuals_dict.get(ind_id)

        if not individual_data:
            return render(
                request,
                "generator/error.html",
                {"error": "Individual not found."},
            )

        # Convert the data back to a PersonData object
        try:
            individual = PersonData(**individual_data)
        except Exception as e:
            logger.error(f"Failed to parse individual data: {str(e)}")
            return render(
                request,
                "generator/error.html",
                {"error": f"Failed to parse individual data: {str(e)}"},
            )

        # Resolve family relationships
        father = None
        mother = None
        spouses = []
        children = []
        siblings = []
        spouses_children = {}  # Dictionary to store children for each spouse

        # Handle father data
        if individual.father and individual.father in individuals_dict:
            try:
                father_data = individuals_dict[individual.father]
                father = PersonData(**father_data)
            except Exception as e:
                logger.error(f"Error parsing father data: {str(e)}")

        # Handle mother data
        if individual.mother and individual.mother in individuals_dict:
            try:
                mother_data = individuals_dict[individual.mother]
                mother = PersonData(**mother_data)
            except Exception as e:
                logger.error(f"Error parsing mother data: {str(e)}")

        # Handle children data
        if individual.children:
            for child_id in individual.children:
                if child_id in individuals_dict:
                    try:
                        child_data = individuals_dict[child_id]
                        children.append(PersonData(**child_data))
                    except Exception as e:
                        logger.error(
                            f"Error parsing child data for {child_id}: {str(e)}"
                        )

        # Identify spouses and their shared children using PersonData information
        if individual.spouse:
            for spouse_id in individual.spouse:
                if spouse_id in individuals_dict:
                    try:
                        spouse_data = individuals_dict[spouse_id]
                        spouse = PersonData(**spouse_data)
                        spouses.append(spouse)
                        # Get children for this spouse
                        spouse_children = []
                        if individual.children:
                            for child_id in individual.children:
                                if child_id in individuals_dict:
                                    try:
                                        child_data = individuals_dict[child_id]
                                        child = PersonData(**child_data)
                                        # Check if the child is shared with the spouse
                                        if (
                                            child.father == individual.id
                                            and child.mother == spouse.id
                                        ):
                                            spouse_children.append(child)
                                            logger.debug(
                                                f"Child {child.full_name} added to spouse {spouse.full_name} (father: {individual.id}, mother: {spouse.id})"
                                            )
                                        elif (
                                            child.father == spouse.id
                                            and child.mother == individual.id
                                        ):
                                            spouse_children.append(child)
                                            logger.debug(
                                                f"Child {child.full_name} added to spouse {spouse.full_name} (father: {spouse.id}, mother: {individual.id})"
                                            )
                                    except Exception as e:
                                        logger.error(
                                            f"Error parsing child data for {child_id}: {str(e)}"
                                        )
                        if individual.spouses_children is None:
                            individual.spouses_children = {}
                        individual.spouses_children[spouse.id] = spouse_children
                        logger.debug(
                            f"Spouse: {spouse.full_name}, Children: {[child.full_name for child in spouse_children]}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error parsing spouse data for {spouse_id}: {str(e)}"
                        )

        # Identify siblings
        if individual.siblings:
            for sibling_id in individual.siblings:
                if sibling_id in individuals_dict:
                    try:
                        sibling_data = individuals_dict[sibling_id]
                        siblings.append(PersonData(**sibling_data))
                    except Exception as e:
                        logger.error(
                            f"Error parsing sibling data for {sibling_id}: {str(e)}"
                        )

        spouses_ids = [spouse.id for spouse in spouses]

        # Debug: Print spouses, spouses_children, and siblings
        logger.debug(f"Spouses: {[spouse.id for spouse in spouses]}")
        logger.debug(f"Spouses Children: {spouses_children}")
        logger.debug(f"Siblings: {[sibling.id for sibling in siblings]}")
        logger.debug(f"Spouses Children Keys: {spouses_children.keys()}")
        for spouse_id, children in spouses_children.items():
            logger.debug(
                f"Spouse ID: {spouse_id}, Children: {[child.id for child in children]}"
            )

        # Prepare individuals data for the search functionality
        individuals_list = []
        for ind_id, ind_data in individuals_dict.items():
            try:
                ind = PersonData(**ind_data)
                individuals_list.append(
                    {
                        "id": ind.id,
                        "full_name": ind.full_name,
                        "given_name": ind.given_name,
                        "surname": ind.surname,
                        "birth_date": ind.birth_date,
                        "birth_place": ind.birth_place,
                        "death_date": ind.death_date,
                        "death_place": ind.death_place,
                    }
                )
            except Exception as e:
                print(f"Error preparing individual data for {ind_id}: {str(e)}")

        # Debug: Print spouses_children before passing to template
        logger.debug(f"Spouses Children Before Render: {individual.spouses_children}")

        return render(
            request,
            "generator/person_view.html",
            {
                "individual": individual,
                "father": father,
                "mother": mother,
                "spouses": spouses,
                "spouses_ids": spouses_ids,
                "children": children,
                "siblings": siblings,
                "spouses_children": individual.spouses_children,  # Pass the children for each spouse
                "individuals_json": json.dumps(
                    individuals_list
                ),  # Pass individuals data for search
                "file_id": request.session.get("current_gedcom_file_id"),
                "individual_id": individual.id,
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in individual_detail: {str(e)}")
        return render(
            request,
            "generator/error.html",
            {"error": f"An unexpected error occurred: {str(e)}"},
        )


def individual_detail(request, ind_id):
    try:
        # Handle setting home person
        if request.method == "POST" and "set_home_person" in request.POST:
            file_id = request.POST.get("file_id")
            home_person_id = request.POST.get("home_person_id")
            try:
                file = GedcomFile.objects.get(id=file_id, user=request.user)
                file.home_person_id = home_person_id
                file.save()
            except GedcomFile.DoesNotExist:
                pass

        # Ensure file_id is set in session
        if "current_gedcom_file_id" not in request.session:
            gedcom_files = GedcomFile.objects.filter(user=request.user)
            if gedcom_files.exists():
                request.session["current_gedcom_file_id"] = gedcom_files.first().id

        # Get the family data using centralized function
        family_data = get_family_data(request)

        if not family_data:
            return render(
                request,
                "generator/error.html",
                {"error": "No family data found. Please upload a GEDCOM file first."},
            )

        # Pre-process family data for quick lookups
        individuals_dict, families_dict, family_children_map = preprocess_family_data(
            family_data
        )
        logger.debug(f"Individuals dict: {individuals_dict}")
        logger.debug(f"Families dict: {families_dict}")
        logger.debug(f"Family children map: {family_children_map}")

        # Fetch the individual's data using the ind_id
        individual_data = individuals_dict.get(ind_id)
        logger.debug(f"Individual data: {individual_data}")

        if not individual_data:
            return render(
                request,
                "generator/error.html",
                {"error": "Individual not found."},
            )

        # Convert the data back to a PersonData object
        try:
            individual = PersonData(**individual_data)
        except Exception as e:
            return render(
                request,
                "generator/error.html",
                {"error": f"Failed to parse individual data: {str(e)}"},
            )
        logger.debug(f"Individual: {individual}")

        # Resolve family relationships
        father = None
        mother = None
        spouses = []
        children = []
        siblings = []
        spouses_children = {}  # Dictionary to store children for each spouse
        logger.debug(f"Individual spouse: {individual.spouse}")
        logger.debug(f"Individual children: {individual.children}")
        logger.debug(f"Individual siblings: {individual.siblings}")

        # Handle father data
        if individual.father and individual.father in individuals_dict:
            try:
                father_data = individuals_dict[individual.father]
                father = PersonData(**father_data)
            except Exception as e:
                logger.error(f"Error parsing father data: {str(e)}")

        # Handle mother data
        if individual.mother and individual.mother in individuals_dict:
            try:
                mother_data = individuals_dict[individual.mother]
                mother = PersonData(**mother_data)
            except Exception as e:
                logger.error(f"Error parsing mother data: {str(e)}")

        # Handle children data
        if individual.children:
            for child_id in individual.children:
                if child_id in individuals_dict:
                    try:
                        child_data = individuals_dict[child_id]
                        children.append(PersonData(**child_data))
                    except Exception as e:
                        logger.error(
                            f"Error parsing child data for {child_id}: {str(e)}"
                        )

        # Identify spouses and their shared children using PersonData information
        if individual.spouse:
            for spouse_id in individual.spouse:
                if spouse_id in individuals_dict:
                    try:
                        spouse_data = individuals_dict[spouse_id]
                        spouse = PersonData(**spouse_data)
                        spouses.append(spouse)
                        # Get children for this spouse
                        spouse_children = []
                        if individual.children:
                            for child_id in individual.children:
                                if child_id in individuals_dict:
                                    try:
                                        child_data = individuals_dict[child_id]
                                        child = PersonData(**child_data)
                                        # Check if the child is shared with the spouse
                                        if (
                                            child.father == individual.id
                                            and child.mother == spouse.id
                                        ):
                                            spouse_children.append(child)
                                        elif (
                                            child.father == spouse.id
                                            and child.mother == individual.id
                                        ):
                                            spouse_children.append(child)
                                    except Exception as e:
                                        logger.error(
                                            f"Error parsing child data for {child_id}: {str(e)}"
                                        )
                        spouses_children[spouse.id] = spouse_children
                    except Exception as e:
                        logger.error(
                            f"Error parsing spouse data for {spouse_id}: {str(e)}"
                        )

        # Identify siblings
        if individual.siblings:
            for sibling_id in individual.siblings:
                if sibling_id in individuals_dict:
                    try:
                        sibling_data = individuals_dict[sibling_id]
                        siblings.append(PersonData(**sibling_data))
                    except Exception as e:
                        logger.error(
                            f"Error parsing sibling data for {sibling_id}: {str(e)}"
                        )
        logger.debug(f"Siblings: {[sibling.id for sibling in siblings]}")

        spouses_ids = [spouse.id for spouse in spouses]

        # Debug: Print spouses, spouses_children, and siblings
        logger.debug(f"Spouses: {[spouse.id for spouse in spouses]}")
        logger.debug(f"Spouses Children: {spouses_children}")
        logger.debug(f"Siblings: {[sibling.id for sibling in siblings]}")
        logger.debug(f"Spouses Children Keys: {spouses_children.keys()}")
        for spouse_id, children in spouses_children.items():
            logger.debug(
                f"Spouse ID: {spouse_id}, Children: {[child.id for child in children]}"
            )
        logger.debug(f"Individual spouses_children: {individual.spouses_children}")

        # Prepare individuals data for the search functionality
        individuals_list = []
        for ind_id, ind_data in individuals_dict.items():
            try:
                ind = PersonData(**ind_data)
                individuals_list.append(
                    {
                        "id": ind.id,
                        "full_name": ind.full_name,
                        "given_name": ind.given_name,
                        "surname": ind.surname,
                        "birth_date": ind.birth_date,
                        "birth_place": ind.birth_place,
                        "death_date": ind.death_date,
                        "death_place": ind.death_place,
                    }
                )
            except Exception as e:
                print(f"Error preparing individual data for {ind_id}: {str(e)}")

        return render(
            request,
            "generator/person_view.html",
            {
                "individual": individual,
                "father": father,
                "mother": mother,
                "spouses": spouses,
                "spouses_ids": spouses_ids,
                "children": children,
                "siblings": siblings,
                "spouses_children": spouses_children,  # Pass the children for each spouse
                "individuals_json": json.dumps(
                    individuals_list
                ),  # Pass individuals data for search
            },
        )

    except Exception as e:
        print(f"Unexpected error in individual_detail: {str(e)}")
        return render(
            request,
            "generator/error.html",
            {"error": f"An unexpected error occurred: {str(e)}"},
        )


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("generator:home")
    else:
        form = RegisterForm()
    return render(request, "generator/register.html", {"form": form})


def select_gedcom_file(request, file_id):
    """Select a GEDCOM file to work with"""
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id, user=request.user)
        request.session["current_gedcom_file_id"] = gedcom_file.id
        return redirect("generator:browse_individuals")
    except GedcomFile.DoesNotExist:
        return render(
            request,
            "generator/error.html",
            {"error": "File not found or you don't have permission to access it."},
        )


def adjust_output(request):
    """Adjust chart output parameters before generation"""
    if request.method == "POST":
        # Get adjustment parameters from form
        x_offset = request.POST.get("x_offset", 0)
        y_offset = request.POST.get("y_offset", 0)
        scale = request.POST.get("scale", 1.0)
        font_size = request.POST.get("font_size", 12)
        font_color = request.POST.get("font_color", "#000000")
        font_family = request.POST.get("font_family", "Arial")

        # Store parameters in session for use during generation
        request.session["chart_parameters"] = {
            "x_offset": float(x_offset),
            "y_offset": float(y_offset),
            "scale": float(scale),
            "font_size": int(font_size),
            "font_color": font_color,
            "font_family": font_family,
        }

        # Get the current individual and template from session
        individual_id = request.session.get("selected_individual_id")
        template = request.session.get("selected_template", "4")

        if not individual_id:
            return render(
                request,
                "generator/error.html",
                {"error": "No individual selected. Please select an individual first."},
            )

        # Redirect to chart generation
        return redirect("generator:generate_chart")

    # GET request - show adjustment form
    return render(request, "generator/adjust_output.html")


def generate_chart(request):
    """Generate the final chart with applied adjustments"""
    try:
        # Get family data
        family_data = get_family_data(request)
        if not family_data:
            return render(
                request,
                "generator/error.html",
                {"error": "No family data found. Please upload a GEDCOM file first."},
            )

        # Get selected individual
        individual_id = request.session.get("selected_individual_id")
        if not individual_id:
            return render(
                request,
                "generator/error.html",
                {"error": "No individual selected. Please select an individual first."},
            )

        # Get chart parameters from session
        chart_parameters = request.session.get("chart_parameters", {})

        # Convert back to PersonData objects for processing
        individuals = {}
        for ind_id, data in family_data["individuals"].items():
            individuals[ind_id] = PersonData(**data)

        # Get the selected individual
        selected_individual = individuals.get(individual_id)
        if not selected_individual:
            return render(
                request,
                "generator/error.html",
                {"error": "Selected individual not found."},
            )

        # Reconstruct family_data with PersonData objects
        reconstructed_family_data = {
            "individuals": individuals,
            "families": family_data["families"],
            "root_individuals": family_data["root_individuals"],
        }

        # Generate the family tree image using the selected template
        template = request.session.get("selected_template", "4")
        template_config = TEMPLATE_MAPPING.get(template, TEMPLATE_MAPPING["4"])

        # Dynamically import the appropriate generator module
        module = importlib.import_module(template_config["module"])
        generator_func = getattr(module, template_config["function"])

        # Call the appropriate generator function with parameters
        if template == "1":
            # 1-gen template only needs the primary individual
            image_buffer = generator_func(selected_individual, chart_parameters)
        else:
            # Other templates need full family data
            image_buffer = generator_func(
                selected_individual, reconstructed_family_data, chart_parameters
            )

        # Automatically download the chart
        response = HttpResponse(image_buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{selected_individual.full_name.replace(" ", "_")}_chart.pdf"'
        )
        return response

    except Exception as e:
        import traceback

        traceback.print_exc()
        return render(request, "generator/error.html", {"error": str(e)})


def get_hud_family_data(request):
    """
    API endpoint to get family data for HUD interface
    """
    try:
        family_data = get_family_data(request)

        if not family_data:
            return JsonResponse(
                {"error": "No family data found. Please upload a GEDCOM file first."},
                status=404,
            )

        # Convert PersonData objects to dicts for JSON serialization
        individuals_list = []
        for ind_id, person_data in family_data["individuals"].items():
            if isinstance(person_data, PersonData):
                individuals_list.append(
                    {
                        "id": ind_id,
                        "full_name": person_data.full_name,
                        "given_name": person_data.given_name,
                        "surname": person_data.surname,
                        "birth_date": person_data.birth_date,
                        "birth_place": person_data.birth_place,
                        "death_date": person_data.death_date,
                        "death_place": person_data.death_place,
                        "sex": person_data.sex,
                    }
                )
            else:
                # Already a dict
                person_data["id"] = ind_id
                individuals_list.append(person_data)

        return JsonResponse(
            {
                "individuals": individuals_list,
                "families": family_data["families"],
                "root_individuals": family_data["root_individuals"],
                "current_individual": request.session.get("selected_individual_id"),
                "current_template": request.session.get("selected_template", "4"),
            }
        )

    except Exception as e:
        logger.error(f"Error in get_hud_family_data: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def get_hud_preview(request):
    """
    API endpoint to generate preview data for HUD
    """
    try:
        # Get parameters from request
        individual_id = request.GET.get("individual_id")
        template_id = request.GET.get("template", "4")
        generations = request.GET.get("generations", "4")

        if not individual_id:
            return JsonResponse(
                {"error": "individual_id parameter is required"}, status=400
            )

        # Get family data
        family_data = get_family_data(request)

        if not family_data:
            return JsonResponse(
                {"error": "No family data found. Please upload a GEDCOM file first."},
                status=404,
            )

        # Get the selected individual
        selected_individual = family_data["individuals"].get(individual_id)

        if not selected_individual:
            return JsonResponse(
                {"error": f"Individual with ID {individual_id} not found"}, status=404
            )

        # Convert to PersonData if needed
        if isinstance(selected_individual, dict):
            selected_individual = PersonData(**selected_individual)

        # Generate preview data
        preview_data = {
            "primary": {
                "id": selected_individual.id,
                "name": selected_individual.full_name,
                "birth_date": selected_individual.birth_date,
                "birth_place": selected_individual.birth_place,
                "death_date": selected_individual.death_date,
                "death_place": selected_individual.death_place,
            },
            "template_id": template_id,
            "template_name": TEMPLATE_MAPPING.get(template_id, {}).get(
                "name", "Unknown Template"
            ),
            "generations": int(generations),
            "family_count": len(family_data["individuals"]),
            "relationships": {
                "father": selected_individual.father,
                "mother": selected_individual.mother,
                "spouse": selected_individual.spouse,
                "children": selected_individual.children,
                "siblings": selected_individual.siblings,
            },
        }

        return JsonResponse(preview_data)

    except Exception as e:
        logger.error(f"Error in get_hud_preview: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def get_hud_settings(request):
    """
    API endpoint to get/save HUD settings
    """
    if request.method == "GET":
        # Return current settings
        return JsonResponse(
            {
                "individual_id": request.session.get("selected_individual_id"),
                "template": request.session.get("selected_template", "4"),
                "generations": request.session.get("generations", "4"),
                "chart_parameters": request.session.get("chart_parameters", {}),
            }
        )
    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            # Update session with new settings
            if "individual_id" in data:
                request.session["selected_individual_id"] = data["individual_id"]
            if "template" in data:
                request.session["selected_template"] = data["template"]
            if "generations" in data:
                request.session["generations"] = data["generations"]
            if "chart_parameters" in data:
                request.session["chart_parameters"] = data["chart_parameters"]

            return JsonResponse({"status": "success", "message": "Settings saved"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def display_tree_hud(request):
    """
    Display the interactive HUD for family tree customization
    """
    try:
        # Get family data
        family_data = get_family_data(request)
        if not family_data:
            return render(
                request,
                "generator/error.html",
                {"error": "No family data found. Please upload a GEDCOM file first."},
            )

        # Get selected individual from session
        selected_individual_id = request.session.get("selected_individual_id")
        if not selected_individual_id:
            return redirect("generator:select_individual")

        # Convert back to PersonData objects
        individuals = {}
        for ind_id, data in family_data["individuals"].items():
            individuals[ind_id] = PersonData(**data)

        # Get the selected individual
        selected_individual = individuals.get(selected_individual_id)
        if not selected_individual:
            return render(
                request,
                "generator/error.html",
                {"error": "Selected individual not found."},
            )

        # Get current settings from session
        current_template = str(request.session.get("selected_template", "4"))
        generations = request.session.get("generations", "4")
        chart_parameters = request.session.get("chart_parameters", {})

        return render(
            request,
            "generator/display_tree.html",
            {
                "individual": selected_individual,
                "family_data": family_data,
                "current_template": current_template,
                "generations": generations,
                "chart_parameters": chart_parameters,
                "TEMPLATE_MAPPING": TEMPLATE_MAPPING,
            },
        )

    except Exception as e:
        logger.error(f"Error in display_tree_hud: {e}")
        return render(request, "generator/error.html", {"error": str(e)})


def save_hud_settings(request):
    """
    Save HUD settings and generate the final chart
    """
    if request.method == "POST":
        try:
            # Get settings from POST data
            individual_id = request.POST.get("individual_id")
            template = request.POST.get("template")
            generations = request.POST.get("generations")

            # Get chart parameters (fonts, sizes, positions, etc.)
            chart_parameters = {
                "font_family": request.POST.get("font_family", "Arial"),
                "font_size": request.POST.get("font_size", "14"),
                "primary_color": request.POST.get("primary_color", "#343a40"),
                "background_color": request.POST.get("background_color", "#ffffff"),
                "line_color": request.POST.get("line_color", "#000000"),
                "line_width": request.POST.get("line_width", "2"),
                "spacing": request.POST.get("spacing", "20"),
                "orientation": request.POST.get("orientation", "portrait"),
            }

            # Save settings to session
            request.session["selected_individual_id"] = individual_id
            request.session["selected_template"] = template
            request.session["generations"] = generations
            request.session["chart_parameters"] = chart_parameters

            # Redirect to generate the final chart
            return redirect("generator:generate_chart")

        except Exception as e:
            logger.error(f"Error saving HUD settings: {e}")
            return render(request, "generator/error.html", {"error": str(e)})

    return redirect("generator:display_tree")
