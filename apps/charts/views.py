import importlib
import logging

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from apps.generator.models import GedcomFile
from apps.parser.models import PersonData

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_template_mapping():
    """Helper function to get template mapping"""
    return {
        "1": {
            "module": "apps.generator.utils.image_1generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_1GEN_BW.pdf",
            "name": "1 Generation (Individual Only)",
        },
        "2": {
            "module": "apps.generator.utils.image_2generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_2GEN_BW.pdf",
            "name": "2 Generation Chart",
        },
        "3": {
            "module": "apps.generator.utils.image_3generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_3GEN_BW.png",
            "name": "3 Generation Chart",
        },
        "4": {
            "module": "apps.generator.utils.image_4generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_4GEN_BW.pdf",
            "name": "4 Generation Chart",
        },
        "5": {
            "module": "apps.generator.utils.image_5generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_5GEN_BW.pdf",
            "name": "5 Generation Chart",
        },
        "6": {
            "module": "apps.generator.utils.image_6generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_6GEN_BW.pdf",
            "name": "6 Generation Chart",
        },
        "7": {
            "module": "apps.generator.utils.image_7generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_7GEN_BW.pdf",
            "name": "7 Generation Chart",
        },
    }


def generate_chart(request):
    """
    View for generating the final chart from HUD
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    individual_id = request.session.get("selected_individual_id")

    if not gedcom_file_id:
        return render(
            request, "charts/error.html", {"error": "No GEDCOM file selected"}
        )
    if not individual_id:
        return render(request, "charts/error.html", {"error": "No individual selected"})

    # Define gedcom_file early to avoid scope issues
    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        logger.debug(f"Retrieved GEDCOM file: {gedcom_file_id}")
    except GedcomFile.DoesNotExist:
        logger.error(f"GEDCOM file not found: {gedcom_file_id}")
        return render(request, "charts/error.html", {"error": "GEDCOM file not found"})

    logger.debug(f"Starting chart generation for GEDCOM file: {gedcom_file_id}")
    if request.method == "POST":
        try:
            logger.debug(f"POST data: {request.POST}")
            # Get chart settings from POST data or session
            template_id = request.POST.get(
                "template", request.session.get("hud_settings", {}).get("template", "4")
            )
            # orientation = request.POST.get("orientation", "portrait")  # Currently unused

            # Validate parsed_data structure
            logger.debug(f"Validating parsed_data for GEDCOM file: {gedcom_file_id}")
            if not gedcom_file.parsed_data:
                logger.error("parsed_data is None")
                return render(
                    request,
                    "charts/error.html",
                    {"error": "Invalid or missing parsed data"},
                )
            if "individuals" not in gedcom_file.parsed_data:
                logger.error(
                    f"'individuals' key missing from parsed_data. Keys: {list(gedcom_file.parsed_data.keys())}"
                )
                return render(
                    request,
                    "charts/error.html",
                    {"error": "'individuals' key missing from parsed data"},
                )

            # Convert dictionaries to PersonData objects
            logger.debug(f"Converting individuals to PersonData objects")
            individuals = {}
            for ind_id, ind_data in gedcom_file.parsed_data["individuals"].items():
                logger.debug(f"Processing individual {ind_id}: {type(ind_data)}")
                if isinstance(ind_data, dict):
                    individuals[ind_id] = PersonData(**ind_data)
                    logger.debug(
                        f"Created PersonData for {ind_id}: {individuals[ind_id].full_name}"
                    )
                else:
                    individuals[ind_id] = ind_data
                    logger.debug(
                        f"Using existing PersonData for {ind_id}: {individuals[ind_id].full_name}"
                    )

            families = gedcom_file.parsed_data.get("families", {})

            if individual_id not in individuals:
                logger.error(f"Individual not found: {individual_id}")
                return render(
                    request, "charts/error.html", {"error": "Individual not found"}
                )

            individual = individuals[individual_id]

            logger.debug(f"Template ID: {template_id}")
            # Get the template configuration
            template_mapping = get_template_mapping()
            if template_id not in template_mapping:
                return render(
                    request, "charts/error.html", {"error": "Invalid template selected"}
                )

            template_config = template_mapping[template_id]

            logger.debug(
                f"Using generator: {template_config['module']}.{template_config['function']}"
            )
            # Import the generator module dynamically
            module = importlib.import_module(template_config["module"])
            generator_func = getattr(module, template_config["function"])

            # Call the generator function
            chart_data = generator_func(individual, individuals, families)

            # Return success message
            return render(
                request,
                "charts/generate_success.html",
                {
                    "individual": individual,
                    "template_name": template_config["name"],
                    "filename": template_config["filename"],
                },
            )

        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return render(
                request,
                "charts/error.html",
                {"error": f"Chart generation failed: {str(e)}"},
            )

    # GET request - show the generation form (should come from HUD)
    try:
        logger.debug(
            f"GET request - Checking parsed_data for GEDCOM file: {gedcom_file_id}"
        )
        if not gedcom_file.parsed_data:
            logger.error("parsed_data is None in GET request")
            return render(
                request,
                "charts/error.html",
                {"error": "Invalid or missing parsed data"},
            )
        if "individuals" not in gedcom_file.parsed_data:
            logger.error(
                f"'individuals' key missing from parsed_data in GET request. Keys: {list(gedcom_file.parsed_data.keys())}"
            )
            return render(
                request,
                "charts/error.html",
                {"error": "'individuals' key missing from parsed data"},
            )

        # Convert dictionaries to PersonData objects
        logger.debug(f"GET request - Converting individuals to PersonData objects")
        individuals = {}
        for ind_id, ind_data in gedcom_file.parsed_data["individuals"].items():
            logger.debug(
                f"GET request - Processing individual {ind_id}: {type(ind_data)}"
            )
            if isinstance(ind_data, dict):
                individuals[ind_id] = PersonData(**ind_data)
                logger.debug(
                    f"GET request - Created PersonData for {ind_id}: {individuals[ind_id].full_name}"
                )
            else:
                individuals[ind_id] = ind_data
                logger.debug(
                    f"GET request - Using existing PersonData for {ind_id}: {individuals[ind_id].full_name}"
                )

        individual = individuals[individual_id]
        template_id = request.session.get("hud_settings", {}).get("template", "4")

        return render(
            request,
            "charts/generate_chart.html",
            {
                "gedcom_file_id": gedcom_file_id,
                "individual": individual,
                "individuals": individuals.values(),
                "template_id": template_id,
                "TEMPLATE_MAPPING": get_template_mapping(),
            },
        )

    except Exception as e:
        logger.error(f"Error in generate_chart: {e}")
        return render(request, "charts/error.html", {"error": str(e)})
