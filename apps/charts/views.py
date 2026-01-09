import importlib
import json
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


def adjust_output(request):
    """
    View for adjusting chart output settings
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return render(
            request, "charts/error.html", {"error": "No GEDCOM file selected"}
        )

    try:
        # Get current settings from session or use defaults
        chart_settings = request.session.get(
            "chart_settings",
            {
                "template": "4",
                "orientation": "portrait",
                "paper_size": "letter",
                "include_photos": False,
                "color_scheme": "black_and_white",
                "generations": 4,
                "show_spouses": True,
                "show_siblings": False,
            },
        )

        return render(
            request,
            "charts/adjust_output.html",
            {
                "gedcom_file_id": gedcom_file_id,
                "chart_settings": chart_settings,
                "TEMPLATE_MAPPING": get_template_mapping(),
            },
        )

    except Exception as e:
        return render(request, "charts/error.html", {"error": str(e)})


def generate_chart(request):
    """
    View for generating the final chart
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return render(
            request, "charts/error.html", {"error": "No GEDCOM file selected"}
        )

    # Define gedcom_file early to avoid scope issues
    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        logger.debug(f"Retrieved GEDCOM file: {gedcom_file_id}")
        logger.debug(f"parsed_data exists: {gedcom_file.parsed_data is not None}")
        if gedcom_file.parsed_data:
            logger.debug(f"parsed_data keys: {list(gedcom_file.parsed_data.keys())}")
            logger.debug(
                f"individuals key exists: {'individuals' in gedcom_file.parsed_data}"
            )
            if "individuals" in gedcom_file.parsed_data:
                logger.debug(
                    f"Number of individuals: {len(gedcom_file.parsed_data['individuals'])}"
                )
                logger.debug(
                    f"First individual: {list(gedcom_file.parsed_data['individuals'].items())[0] if gedcom_file.parsed_data['individuals'] else 'None'}"
                )
    except GedcomFile.DoesNotExist:
        logger.error(f"GEDCOM file not found: {gedcom_file_id}")
        return render(request, "charts/error.html", {"error": "GEDCOM file not found"})

    logger.debug(f"Starting chart generation for GEDCOM file: {gedcom_file_id}")
    if request.method == "POST":
        try:
            logger.debug(f"POST data: {request.POST}")
            # Get chart settings from POST data
            template_id = request.POST.get("template", "4")
            individual_id = request.POST.get("individual_id")
            orientation = request.POST.get("orientation", "portrait")

            # Save settings to session
            chart_settings = {
                "template": template_id,
                "orientation": orientation,
                "individual_id": individual_id,
            }
            request.session["chart_settings"] = chart_settings
            logger.debug(f"Chart settings saved to session: {chart_settings}")

            # Validate parsed_data structure
            logger.debug(f"Validating parsed_data for GEDCOM file: {gedcom_file_id}")
            logger.debug(f"parsed_data: {gedcom_file.parsed_data}")
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

    # GET request - show the generation form
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

        chart_settings = request.session.get("chart_settings", {})
        template_id = chart_settings.get("template", "4")

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

        individual_id = chart_settings.get("individual_id", gedcom_file.home_person_id)

        if individual_id and individual_id in individuals:
            individual = individuals[individual_id]
        else:
            individual = None
            logger.error(f"Individual not found: {individual_id}")

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
