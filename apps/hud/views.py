import json
import logging
import time
from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from apps.generator.models import GedcomFile
from apps.generator.template_mapping import get_template_mapping
from apps.generator.utils.image_1generator import generate_1gen_preview
from apps.parser.models import PersonData

logger = logging.getLogger(__name__)


def display_tree_hud(request):
    """
    View for displaying the interactive HUD interface
    """
    # Handle POST requests from individual detail page (direct chart generation)
    if request.method == "POST":
        gedcom_file_id = request.POST.get("file_id")
        individual_id = request.POST.get("individual_id")

        # Store in session for subsequent requests
        if gedcom_file_id:
            request.session["current_gedcom_file_id"] = gedcom_file_id
        if individual_id:
            request.session["selected_individual_id"] = individual_id
    else:
        gedcom_file_id = request.session.get("current_gedcom_file_id")
        individual_id = request.session.get("selected_individual_id")

    if not gedcom_file_id:
        return render(request, "hud/error.html", {"error": "No GEDCOM file selected"})
    if not individual_id:
        return render(request, "hud/error.html", {"error": "No individual selected"})

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)

        if not gedcom_file.parsed_data:
            return render(
                request, "hud/error.html", {"error": "File not processed yet"}
            )

        # Get the selected individual
        individuals = gedcom_file.parsed_data.get("individuals", {})
        if individual_id not in individuals:
            return render(request, "hud/error.html", {"error": "Individual not found"})

        individual = individuals[individual_id]
        if isinstance(individual, dict):
            individual = PersonData(**individual)
        elif not isinstance(individual, PersonData):
            # Convert to PersonData if it's not already
            individual = PersonData(**individual.__dict__)

        # Get HUD settings from session or use defaults
        hud_settings = request.session.get(
            "hud_settings",
            {
                "show_photos": True,
                "show_dates": True,
                "show_locations": True,
                "compact_mode": False,
                "theme": "light",
                "template": "1",  # Default to 1 Generation Chart
            },
        )

        return render(
            request,
            "hud/display_tree.html",
            {
                "gedcom_file_id": gedcom_file_id,
                "individual": individual,
                "hud_settings": hud_settings,
                "hud_settings_timestamp": request.session.get(
                    "hud_settings_timestamp", "0"
                ),
                "TEMPLATE_MAPPING": get_template_mapping(),
            },
        )

    except GedcomFile.DoesNotExist:
        return render(request, "hud/error.html", {"error": "GEDCOM file not found"})
    except Exception as e:
        return render(request, "hud/error.html", {"error": str(e)})


@require_http_methods(["POST"])
@csrf_exempt
@require_POST
def update_settings_timestamp(request):
    """
    Update the timestamp in the session to force a preview reload.
    """
    try:
        data = json.loads(request.body)
        timestamp = data.get("timestamp")
        if timestamp:
            request.session["hud_settings_timestamp"] = timestamp
            return JsonResponse({"status": "success"})
        return JsonResponse(
            {"status": "error", "message": "No timestamp provided"}, status=400
        )
    except Exception as e:
        logger.error(f"Error updating settings timestamp: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def save_hud_settings(request):
    """
    View for saving HUD settings including template selection
    """
    if request.method == "POST":
        individual_id = request.POST.get("individual_id")
        template = request.POST.get("template")
        generations = request.POST.get("generations")

        # Font settings
        font_family = request.POST.get("font_family") or "Arial"
        primary_name_font_size = request.POST.get("primary_name_font_size")
        primary_date_info_font_size = request.POST.get("primary_date_info_font_size")
        primary_place_info_font_size = request.POST.get("primary_place_info_font_size")

        # Stroke settings
        default_stroke_width = request.POST.get("default_stroke_width")
        primary_stroke_color = request.POST.get("primary_stroke_color") or "#000000"

        # Primary individual colors
        primary_background_color = request.POST.get("primary_background_color") or "#ffffff"
        primary_font_color = request.POST.get("primary_font_color") or "#000000"
        primary_birth_color = request.POST.get("primary_birth_color") or "#000000"
        primary_birth_place_color = request.POST.get("primary_birth_place_color") or "#000000"
        primary_death_color = request.POST.get("primary_death_color") or "#000000"
        primary_death_place_color = request.POST.get("primary_death_place_color") or "#000000"

        # Translation settings (subject_translate only)
        subject_translate_x = request.POST.get("subject_translate_x")
        subject_translate_y = request.POST.get("subject_translate_y")

        if not individual_id:
            return JsonResponse(
                {"status": "error", "message": "Missing individual_id parameter"},
                status=400,
            )

        # Save settings to session
        logger.debug(f"Saving settings to session: {request.POST}")
        request.session["hud_settings"] = {
            "individual_id": individual_id,
            "template": template,
            "generations": generations,
            "font_family": font_family,
            "primary_name_font_size": int(primary_name_font_size)
            if primary_name_font_size
            else 84,
            "primary_date_info_font_size": int(primary_date_info_font_size)
            if primary_date_info_font_size
            else 60,
            "primary_place_info_font_size": int(primary_place_info_font_size)
            if primary_place_info_font_size
            else 48,
            "default_stroke_width": float(default_stroke_width)
            if default_stroke_width
            else 0.5,
            "primary_background_color": primary_background_color,
            "primary_stroke_color": primary_stroke_color,
            "primary_font_color": primary_font_color,
            "primary_birth_color": primary_birth_color,
            "primary_birth_place_color": primary_birth_place_color,
            "primary_death_color": primary_death_color,
            "primary_death_place_color": primary_death_place_color,
            "primary_name_x": int(request.POST.get("primary_name_x", 0)),
            "primary_name_y": int(request.POST.get("primary_name_y", 0)),
            "primary_name_rotate": int(request.POST.get("primary_name_rotate", -45)),
            "primary_birth_x": int(request.POST.get("primary_birth_x", 0)),
            "primary_birth_y": int(request.POST.get("primary_birth_y", 0)),
            "primary_birth_rotate": int(request.POST.get("primary_birth_rotate", -90)),
            "primary_birth_place_x": int(request.POST.get("primary_birth_place_x", 0)),
            "primary_birth_place_y": int(request.POST.get("primary_birth_place_y", 0)),
            "primary_birth_place_rotate": int(request.POST.get("primary_birth_place_rotate", 0)),
            "primary_death_x": int(request.POST.get("primary_death_x", 0)),
            "primary_death_y": int(request.POST.get("primary_death_y", 0)),
            "primary_death_rotate": int(request.POST.get("primary_death_rotate", 0)),
            "primary_death_place_x": int(request.POST.get("primary_death_place_x", 0)),
            "primary_death_place_y": int(request.POST.get("primary_death_place_y", 0)),
            "primary_death_place_rotate": int(request.POST.get("primary_death_place_rotate", -90)),

            "Settings saved to session": request.session.get('hud_settings')
        }
        return JsonResponse({"status": "success"})

    # Fallback for invalid request method
    return JsonResponse(
        {"status": "error", "message": "Invalid request method"},
        status=405,
    )


def get_hud_family_data(request):
    """
    API endpoint for getting family data for HUD display
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return JsonResponse({"error": "No GEDCOM file selected"}, status=400)

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)

        if not gedcom_file.parsed_data:
            return JsonResponse({"error": "File not processed yet"}, status=400)

        # Get the root individual or use the home person
        root_individual_id = request.GET.get("root_id", gedcom_file.home_person_id)
        if not root_individual_id:
            return JsonResponse({"error": "No root individual specified"}, status=400)

        # Extract family data for the HUD
        individuals = gedcom_file.parsed_data.get("individuals", {})
        families = gedcom_file.parsed_data.get("families", {})

        if root_individual_id not in individuals:
            return JsonResponse({"error": "Root individual not found"}, status=404)

        # Build the family tree data structure for the HUD
        family_data = {
            "root": individuals[root_individual_id],
            "individuals": individuals,
            "families": families,
        }

        return JsonResponse(family_data)

    except GedcomFile.DoesNotExist:
        return JsonResponse({"error": "GEDCOM file not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_hud_preview(request):
    """
    API endpoint for getting preview data for HUD
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return JsonResponse({"error": "No GEDCOM file selected"}, status=400)

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)

        if not gedcom_file.parsed_data:
            return JsonResponse({"error": "File not processed yet"}, status=400)

        # Get preview data (simplified version of family data)
        individuals = gedcom_file.parsed_data.get("individuals", {})
        root_individuals = gedcom_file.parsed_data.get("root_individuals", [])

        preview_data = {
            "individual_count": len(individuals),
            "family_count": len(gedcom_file.parsed_data.get("families", {})),
            "root_individuals": [
                individuals.get(id, {}) for id in root_individuals[:5]
            ],  # Top 5 root individuals
            "generation_count": 3,  # This would be calculated based on the data
        }

        return JsonResponse(preview_data)

    except GedcomFile.DoesNotExist:
        return JsonResponse({"error": "GEDCOM file not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_hud_settings(request):
    """
    API endpoint for getting current HUD settings
    """
    try:
        settings = request.session.get(
            "hud_settings",
            {
                "show_photos": True,
                "show_dates": True,
                "show_locations": True,
                "compact_mode": False,
                "theme": "light",
                "font_size": "medium",
                "color_scheme": "default",
                "template": "1",  # Default template
            },
        )
        return JsonResponse(settings)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# THIS IS THE ONE BEING USED/SEEN IN CONSOLE
@csrf_exempt
def get_1gen_preview(request):
    """
    API endpoint for generating the 1-generation preview.
    Supports both GET and POST requests.
    """
    try:
        if request.method == "GET":
            individual_id = request.GET.get("individual_id")
            # Use session settings for GET requests
            hud_settings = request.session.get("hud_settings", {})
            user_settings = {
                "font_family": hud_settings.get("font_family", "Arial"),
                "primary_name_font_size": hud_settings.get("primary_name_font_size", 84),
                "primary_date_info_font_size": hud_settings.get("primary_date_info_font_size", 60),
                "primary_place_info_font_size": hud_settings.get("primary_place_info_font_size", 28),
                "default_stroke_width": hud_settings.get("default_stroke_width", 0.5),
                "primary_stroke_color": hud_settings.get("primary_stroke_color", "#000000"),
                "primary_background_color": hud_settings.get("primary_background_color", "#ffffff"),
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
        elif request.method == "POST":
            data = json.loads(request.body)
            individual_id = data.get("individual_id")
            user_settings = data.get("user_settings", {})
            # Enhanced debugging to trace the exact issue
            logger.debug(f"=== DEBUG: Full POST request body ===")
            logger.debug(f"Raw request body: {request.body}")
            logger.debug(f"Parsed data: {data}")
            logger.debug(f"Individual ID: {individual_id}")
            logger.debug(f"User settings received: {user_settings}")

            # Check if user_settings is empty or contains defaults
            if not user_settings or all(
                v == 84
                or v == 60
                or v == 28
                or v == 0.5
                or v == "#000000"
                or v == "#FFFFFF"
                or v == 0
                or v == -45
                or v == -90
                for v in user_settings.values()
            ):
                logger.warning("WARNING: User settings appear to be default values!")
            else:
                logger.info("SUCCESS: User settings contain non-default values!")
        else:
            return HttpResponse("Method not allowed", status=405)

        # Get the primary individual from the session or GET parameters
        if not individual_id:
            individual_id = request.session.get("selected_individual_id")
        if not individual_id:
            return HttpResponse("No individual selected", status=400)

        gedcom_file_id = request.session.get("current_gedcom_file_id")
        if not gedcom_file_id:
            return HttpResponse("No GEDCOM file selected", status=400)

        from apps.generator.models import GedcomFile

        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        if not gedcom_file.parsed_data:
            return HttpResponse("File not processed yet", status=400)

        individuals = gedcom_file.parsed_data.get("individuals", {})
        if individual_id not in individuals:
            return HttpResponse("Individual not found", status=404)

        individual_data = individuals[individual_id]
        primary_individual = PersonData(**individual_data)

        # Generate the preview
        preview_buffer = generate_1gen_preview(primary_individual, gedcom_file.parsed_data, "preview", user_settings)

        # Return the preview as an image
        return HttpResponse(preview_buffer, content_type="image/png")

    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return HttpResponse(f"Error generating preview: {str(e)}", status=500)
