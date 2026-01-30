import json
import logging
import importlib
from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.generator.models import GedcomFile
from apps.generator.template_mapping import get_template_mapping
from apps.generator.utils import (
    image_1generator,
    image_2generator,
    image_3generator,
    image_4generator,
    image_5generator,
    image_6generator,
    image_7generator,
)
from apps.parser.models import PersonData

logger = logging.getLogger(__name__)

# Use the centralized template mapping
TEMPLATE_MAPPING = get_template_mapping()


@csrf_exempt
@require_http_methods(["GET", "POST"])
def generate_final_chart(request):
    """
    View for generating the final family tree chart as a PDF.
    Uses the selected template and generation settings.
    Handles both GET and POST requests.
    """
    try:
        # Extract parameters from GET or POST data
        individual_id = request.POST.get("individual_id") or request.GET.get("individual_id")
        template = request.POST.get("template") or request.GET.get("template") or "1"

        # Initialize hud_settings early to avoid UnboundLocalError
        hud_settings = request.session.get("hud_settings", {})

        # Collect user settings from POST or session with proper type conversion
        def get_int(name, default):
            try:
                return int(request.POST.get(name, default))
            except (TypeError, ValueError):
                return default

        def get_float(name, default):
            try:
                return float(request.POST.get(name, default))
            except (TypeError, ValueError):
                return default

        user_settings = {
            "font_family": request.POST.get("font_family", "Arial"),
            "primary_name_font_size": get_int("primary_name_font_size", 84),
            "primary_date_info_font_size": get_int("primary_date_info_font_size", 60),
            "primary_place_info_font_size": get_int("primary_place_info_font_size", 28),
            "default_stroke_width": get_float("default_stroke_width", 0.5),
            "primary_background_color": request.POST.get("primary_background_color", "#FFFFFF"),
            "primary_stroke_color": request.POST.get("primary_stroke_color", "#000000"),
            "primary_font_color": request.POST.get("primary_font_color", "#000000"),
            "primary_birth_color": request.POST.get("primary_birth_color", "#000000"),
            "primary_birth_place_color": request.POST.get("primary_birth_place_color", "#000000"),
            "primary_death_color": request.POST.get("primary_death_color", "#000000"),
            "primary_death_place_color": hud_settings.get("primary_death_place_color", "#000000"),
            "primary_name_x": get_int("primary_name_x", 0),
            "primary_name_y": get_int("primary_name_y", 0),
            "primary_name_rotate": get_int("primary_name_rotate", -45),
            "primary_birth_x": get_int("primary_birth_x", 0),
            "primary_birth_y": get_int("primary_birth_y", 0),
            "primary_birth_rotate": get_int("primary_birth_rotate", -90),
            "primary_birth_place_x": get_int("primary_place_x", 0),
            "primary_birth_place_y": get_int("primary_place_y", 0),
            "primary_birth_place_rotate": get_int("primary_place_rotate", 0),
            "primary_death_x": get_int("primary_death_x", 0),
            "primary_death_y": get_int("primary_death_y", 0),
            "primary_death_rotate": get_int("primary_death_rotate", 0),
            "primary_death_place_x": get_int("primary_death_place_x", 0),
            "primary_death_place_y": get_int("primary_death_place_y", 0),
            "primary_death_place_rotate": get_int("primary_death_place_rotate", -90),
            "subject_translate_x": get_int("subject_translate_x", 0),
            "subject_translate_y": get_int("subject_translate_y", 0),
        }

        # If no POST settings, use session settings
        # Check if we have any POST data for settings (more reliable than checking values)
        has_post_settings = any(key in request.POST for key in [
            "font_family", "primary_name_font_size", "primary_date_info_font_size",
            "primary_place_info_font_size", "default_stroke_width", "primary_background_color",
            "primary_stroke_color", "primary_font_color", "primary_birth_color",
            "primary_birth_place_color", "primary_death_color", "primary_death_place_color",
            "primary_name_x", "primary_name_y", "primary_name_rotate", "primary_birth_x",
            "primary_birth_y", "primary_birth_rotate", "primary_birth_place_x",
            "primary_birth_place_y", "primary_birth_place_rotate", "primary_death_x",
            "primary_death_y", "primary_death_rotate", "primary_death_place_x",
            "primary_death_place_y", "primary_death_place_rotate", "subject_translate_x",
            "subject_translate_y"
        ])

        if not has_post_settings:
            logger.debug("No POST settings found, using session settings")
            user_settings = {
                "font_family": hud_settings.get("font_family", "Arial"),
                "primary_name_font_size": hud_settings.get("primary_name_font_size", 84),
                "primary_date_info_font_size": hud_settings.get("primary_date_info_font_size", 60),
                "primary_place_info_font_size": hud_settings.get("primary_place_info_font_size", 28),
                "default_stroke_width": hud_settings.get("default_stroke_width", 0.5),
                "primary_background_color": hud_settings.get("primary_background_color", "#FFFFFF"),
                "primary_stroke_color": hud_settings.get("primary_stroke_color", "#000000"),
                "primary_font_color": hud_settings.get("primary_font_color", "#000000"),
                "primary_birth_color": hud_settings.get("primary_birth_color", "#000000"),
                "primary_birth_place_color": hud_settings.get("primary_birth_place_color", "#000000"),
                "primary_death_color": hud_settings.get("primary_death_color", "#000000"),
                "primary_death_place_color": hud_settings.get("primary_death_place_color", "#000000"),
                "primary_name_x": hud_settings.get("primary_name_x", 0),
                "primary_name_y": hud_settings.get("primary_name_y", 0),
                "primary_name_rotate": hud_settings.get("primary_name_rotate", -45),
                "primary_birth_x": hud_settings.get("primary_birth_x", 0),
                "primary_birth_y": hud_settings.get("primary_birth_y", 0),
                "primary_birth_rotate": hud_settings.get("primary_birth_rotate", -90),
                "primary_birth_place_x": hud_settings.get("primary_birth_place_x", 0),
                "primary_birth_place_y": hud_settings.get("primary_birth_place_y", 0),
                "primary_birth_place_rotate": hud_settings.get("primary_birth_place_rotate", 0),
                "primary_death_x": hud_settings.get("primary_death_x", 0),
                "primary_death_y": hud_settings.get("primary_death_y", 0),
                "primary_death_rotate": hud_settings.get("primary_death_rotate", 0),
                "primary_death_place_x": hud_settings.get("primary_death_place_x", 0),
                "primary_death_place_y": hud_settings.get("primary_death_place_y", 0),
                "primary_death_place_rotate": hud_settings.get("primary_death_place_rotate", -90),
                "subject_translate_x": hud_settings.get("subject_translate_x", 0),
                "subject_translate_y": hud_settings.get("subject_translate_y", 0),
            }
        else:
            logger.debug("Using POST settings for final chart generation")

        # Validate parameters
        if not individual_id:
            logger.error("Missing individual_id parameter")
            return JsonResponse(
                {"status": "error", "message": "Missing individual_id parameter"},
                status=400,
            )
        if not template:
            logger.error("Missing template parameter")
            return JsonResponse(
                {"status": "error", "message": "Missing template parameter"},
                status=400,
            )

        # Get the current GEDCOM file from session
        file_id = request.session.get("current_gedcom_file_id")
        if not file_id:
            logger.error("No GEDCOM file selected")
            return JsonResponse(
                {"status": "error", "message": "No GEDCOM file selected"},
                status=400,
            )

        # Get the GEDCOM file and parsed data
        gedcom_file = GedcomFile.objects.get(id=file_id)
        if not gedcom_file.parsed_data:
            logger.error("File not processed yet")
            return JsonResponse(
                {"status": "error", "message": "File not processed yet"},
                status=400,
            )

        # Use parsed_data directly (already a dictionary)
        family_data = gedcom_file.parsed_data
        if not family_data:
            logger.error("No family data found")
            return JsonResponse(
                {"status": "error", "message": "No family data found"},
                status=400,
            )

        # Get the primary individual from family_data['individuals']
        individuals = family_data.get("individuals", {})
        if not individuals:
            logger.error("No individuals found in the family data")
            return JsonResponse(
                {"status": "error", "message": "No individuals found in the file"},
                status=400,
            )

        # Convert all individuals to PersonData objects
        person_data_objects = {}
        for person_id, person_data in individuals.items():
            person_data_objects[person_id] = PersonData(**person_data)

        # Get the primary individual
        primary_individual = person_data_objects.get(individual_id)
        if not primary_individual:
            logger.error("Individual %s not found in the file", individual_id)
            return JsonResponse(
                {"status": "error", "message": "Individual not found in the file"},
                status=404,
            )

        # Update family_data with PersonData objects
        family_data["individuals"] = person_data_objects

        # Use the centralized template mapping
        TEMPLATE_MAPPING = get_template_mapping()

        # Get the appropriate generator configuration
        template_config = TEMPLATE_MAPPING.get(template)
        if not template_config:
            logger.error("Invalid template parameter: %s", template)
            return JsonResponse(
                {"status": "error", "message": "Invalid template parameter"},
                status=400,
            )

        # Dynamically import the generator module
        module = importlib.import_module(template_config["module"])
        generator_function = getattr(module, template_config["function"])

        logger.debug(f"Using generator: {generator_function.__name__}")
        logger.debug(f"User settings for final chart: {user_settings}")
        logger.debug(f"Request POST data keys: {list(request.POST.keys())}")
        logger.debug(f"HUD settings from session: {hud_settings}")

        # Determine the template type (default to "final" for chart generation)
        template_type = template_config.get("template_type", "final")
        logger.debug(f"Template type: {template_type}")

        # Generate the family tree with the selected template
        logger.debug("Calling generator function with user_settings...")
        image_buffer = generator_function(
            primary_individual,
            family_data,
            template_type,
            user_settings=user_settings,
        )
        logger.debug("Generator function completed successfully")
        image_buffer.seek(0)

        # Return the image as a PDF
        response = HttpResponse(image_buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="family_tree_{individual_id}.pdf"'
        )
        return response

    except Exception as e:
        logger.error("Error in generate_final_chart: %s", str(e), exc_info=True)
        return JsonResponse(
            {"status": "error", "message": "Internal server error"},
            status=500,
        )



def test_template_selection(request):
    """
    Test view to verify template selection is working.
    """
    template = request.GET.get("template", "4")
    return HttpResponse(f"Selected template: {template}")


def test_pdf_generation(request):
    """
    Test view for generating a PDF directly.
    This bypasses all frontend issues and verifies the backend works.
    """
    try:
        # Get the first GEDCOM file
        gedcom_file = GedcomFile.objects.first()
        if not gedcom_file or not gedcom_file.parsed_data:
            return HttpResponse(
                "No GEDCOM file found or file not processed", status=400
            )

        # Get the first individual
        individuals = gedcom_file.parsed_data.get("individuals", {})
        if not individuals:
            return HttpResponse("No individuals found in GEDCOM file", status=400)

        first_individual_id = next(iter(individuals))
        first_individual_data = individuals[first_individual_id]

        # Convert to PersonData object
        primary_individual = PersonData(**first_individual_data)

        # Generate PDF
        image_buffer = image_1generator.generate_1gen_preview(
            primary_individual, gedcom_file.parsed_data, template="1gen"
        )
        image_buffer.seek(0)

        # Return PDF
        response = HttpResponse(image_buffer, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="test_family_tree.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)


def home(request):
    """
    View for the home page.
    """
    if request.method == "POST" and "gedcom_file" in request.FILES:
        return upload_and_generate(request)

    if request.user.is_authenticated:
        return redirect("users:profile")
    else:
        # Check if anonymous user has a file in session
        if request.session.get("current_gedcom_file_id"):
            return redirect("browse:browse_individuals")
        else:
            return redirect("upload:upload_file")
