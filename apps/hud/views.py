import importlib
import json
import logging
import time
import importlib
from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods, require_POST

from apps.generator.models import GedcomFile
from apps.generator.template_mapping import get_template_mapping
from apps.generator.utils.image_1generator import generate_1gen_preview
from apps.parser.models import PersonData

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
                # Chart-wide place formatting defaults
                "place_use_country_abbrev": True,
                "place_use_state_abbrev": True,
                "place_show_county": False,
                "place_show_country": True,
                "place_hide_usa_with_state": True,
                "place_show_township": False,
                "place_show_flag": True,
                "place_flag_type": "birth",
                "place_flag_format": "png",
                "place_flag_size": 48,
                "flag_font": "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
                # Chart-wide date formatting defaults
                "date_format": "da_mon_year",
                "date_year_only": True,
                "date_retain_leading_zeros": False,
                # Chart-wide name formatting defaults
                "name_use_first_middle_only": True,
                "name_hide_hyphenated_surname": True,
            },
        )

        # Determine which settings template to use based on current template
        current_template = hud_settings.get("template", "1")
        template_mapping = get_template_mapping()
        template_config = template_mapping.get(current_template, {})
        template_name = template_config.get("name", f"Template {current_template}")

        # Map template IDs to settings templates
        settings_template_map = {
            "1": "1gen_settings.html",
            "2": "2gen_settings.html",
            "3": "3gen_settings.html",
            "4": "4gen_settings.html",
            "5": "5gen_settings.html",
            "6": "6gen_settings.html",
            "7": "7gen_settings.html",
        }
        current_settings_template = settings_template_map.get(
            current_template, "default_settings.html"
        )

        # Add template context for default template
        if current_settings_template == "default_settings.html":
            generations = current_template  # Use template ID as generations count
        else:
            generations = current_template

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
                "current_settings_template": current_settings_template,
                "template_name": template_name,
                "generations": generations,
            },
        )

    except GedcomFile.DoesNotExist:
        return render(request, "hud/error.html", {"error": "GEDCOM file not found"})
    except Exception as e:
        return render(request, "hud/error.html", {"error": str(e)})


@csrf_protect
@require_http_methods(["POST"])
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

        # Debug logging
        logger.debug(f"POST data received: {dict(request.POST)}")
        logger.debug(f"primary_name_font_size raw: '{primary_name_font_size}'")
        logger.debug(
            f"primary_date_info_font_size raw: '{primary_date_info_font_size}'"
        )
        logger.debug(
            f"primary_place_info_font_size raw: '{primary_place_info_font_size}'"
        )

        # Stroke settings
        default_stroke_width = request.POST.get("default_stroke_width")
        primary_stroke_color = request.POST.get("primary_stroke_color") or "#000000"

        # Primary individual colors
        primary_background_color = (
            request.POST.get("primary_background_color") or "#ffffff"
        )
        primary_font_color = request.POST.get("primary_font_color") or "#000000"
        primary_birth_color = request.POST.get("primary_birth_color") or "#000000"
        primary_birth_place_color = (
            request.POST.get("primary_birth_place_color") or "#000000"
        )
        primary_death_color = request.POST.get("primary_death_color") or "#000000"
        primary_death_place_color = (
            request.POST.get("primary_death_place_color") or "#000000"
        )

        # Translation settings (subject_translate only)
        subject_translate_x = request.POST.get("subject_translate_x")
        subject_translate_y = request.POST.get("subject_translate_y")

        if not individual_id:
            return JsonResponse(
                {"status": "error", "message": "Missing individual_id parameter"},
                status=400,
            )

        # Debug logging
        logger.debug(f"POST data received: {dict(request.POST)}")
        logger.debug(f"primary_name_font_size raw: '{primary_name_font_size}'")
        logger.debug(
            f"primary_date_info_font_size raw: '{primary_date_info_font_size}'"
        )
        logger.debug(
            f"primary_place_info_font_size raw: '{primary_place_info_font_size}'"
        )

        # Check for validation issues
        try:
            if primary_name_font_size:
                int(primary_name_font_size)
            if primary_date_info_font_size:
                int(primary_date_info_font_size)
            if primary_place_info_font_size:
                int(primary_place_info_font_size)
            logger.debug("Field validation passed")
        except ValueError as e:
            logger.error(f"Field validation failed: {e}")
            return JsonResponse(
                {"status": "error", "message": f"Invalid field value: {e}"},
                status=400,
            )

        # Save settings to session
        logger.debug(f"Saving settings to session: {request.POST}")
        hud_settings = {
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
            "subject_translate_x": int(request.POST.get("subject_translate_x", 0)),
            "subject_translate_y": int(request.POST.get("subject_translate_y", 0)),
            "primary_name_rotate": int(request.POST.get("primary_name_rotate", -45)),
            "primary_birth_translate_x": int(
                request.POST.get("primary_birth_translate_x", 0)
            ),
            "primary_birth_translate_y": int(
                request.POST.get("primary_birth_translate_y", 0)
            ),
            "primary_birth_rotate": int(request.POST.get("primary_birth_rotate", -90)),
            "primary_birth_place_translate_x": int(
                request.POST.get("primary_birth_place_translate_x", 0)
            ),
            "primary_birth_place_translate_y": int(
                request.POST.get("primary_birth_place_translate_y", 0)
            ),
            "primary_birth_place_rotate": int(
                request.POST.get("primary_birth_place_rotate", 0)
            ),
            "primary_death_translate_x": int(
                request.POST.get("primary_death_translate_x", 0)
            ),
            "primary_death_translate_y": int(
                request.POST.get("primary_death_translate_y", 0)
            ),
            "primary_death_rotate": int(request.POST.get("primary_death_rotate", 0)),
            "primary_death_place_translate_x": int(
                request.POST.get("primary_death_place_translate_x", 0)
            ),
            "primary_death_place_translate_y": int(
                request.POST.get("primary_death_place_translate_y", 0)
            ),
            "primary_death_place_rotate": int(
                request.POST.get("primary_death_place_rotate", -90)
            ),
            # Date format settings
            "date_format": request.POST.get("date_format", "da_mon_year"),
            "date_year_only": request.POST.get("date_year_only") == "on",
            "date_retain_leading_zeros": request.POST.get("date_retain_leading_zeros")
            == "on",
            # Name formatting settings
            "name_use_first_middle_only": request.POST.get("name_use_first_middle_only")
            == "on",
            "name_hide_hyphenated_surname": request.POST.get(
                "name_hide_hyphenated_surname"
            )
            == "on",
            # Place name formatting settings
            "place_use_country_abbrev": request.POST.get("place_use_country_abbrev")
            == "on",
            "place_use_state_abbrev": request.POST.get("place_use_state_abbrev")
            == "on",
            "place_show_county": request.POST.get("place_show_county") == "on",
            "place_show_country": request.POST.get("place_show_country") == "on",
            "place_hide_usa_with_state": request.POST.get("place_hide_usa_with_state")
            == "on",
            "place_show_township": request.POST.get("place_show_township") == "on",
            "place_show_flag": request.POST.get("place_show_flag") == "on",
            "place_flag_type": request.POST.get("place_flag_type", "birth"),
            "place_flag_format": request.POST.get("place_flag_format", "png"),
            "place_flag_size": int(request.POST.get("place_flag_size", 48)),
            "flag_font": request.POST.get(
                "flag_font",
                "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
            ),
        }

        # Add 2gen specific settings if present
        if template == "2 Generation Chart":
            hud_settings.update(
                {
                    # Parent generation colors
                    "father_font_color": request.POST.get(
                        "father_font_color", "#000000"
                    ),
                    "mother_font_color": request.POST.get(
                        "mother_font_color", "#000000"
                    ),
                    "father_birth_color": request.POST.get(
                        "father_birth_color", "#000000"
                    ),
                    "mother_birth_color": request.POST.get(
                        "mother_birth_color", "#000000"
                    ),
                    "father_death_color": request.POST.get(
                        "father_death_color", "#000000"
                    ),
                    "mother_death_color": request.POST.get(
                        "mother_death_color", "#000000"
                    ),
                    "father_birth_place_color": request.POST.get(
                        "father_birth_place_color", "#000000"
                    ),
                    "mother_birth_place_color": request.POST.get(
                        "mother_birth_place_color", "#000000"
                    ),
                    "father_death_place_color": request.POST.get(
                        "father_death_place_color", "#000000"
                    ),
                    "mother_death_place_color": request.POST.get(
                        "mother_death_place_color", "#000000"
                    ),
                    # Parent generation font sizes
                    "parent_father_name_font_size": int(
                        request.POST.get("parent_father_name_font_size", 60)
                    ),
                    "parent_mother_name_font_size": int(
                        request.POST.get("parent_mother_name_font_size", 60)
                    ),
                    "parent_date_info_font_size": int(
                        request.POST.get("parent_date_info_font_size", 40)
                    ),
                    "parent_place_info_font_size": int(
                        request.POST.get("parent_place_info_font_size", 28)
                    ),
                    # Parent generation positioning
                    "parent_translate_x": int(
                        request.POST.get("parent_translate_x", 0)
                    ),
                    "parent_translate_y": int(
                        request.POST.get("parent_translate_y", 0)
                    ),
                    "parent_rotate": int(request.POST.get("parent_rotate", 0)),
                    # Father positioning
                    "father_first_translate_x": int(
                        request.POST.get("father_first_translate_x", 975)
                    ),
                    "father_first_translate_y": int(
                        request.POST.get("father_first_translate_y", 1700)
                    ),
                    "father_first_rotate": int(
                        request.POST.get("father_first_rotate", 0)
                    ),
                    "father_middle_translate_x": int(
                        request.POST.get("father_middle_translate_x", 0)
                    ),
                    "father_middle_translate_y": int(
                        request.POST.get("father_middle_translate_y", 0)
                    ),
                    "father_middle_rotate": int(
                        request.POST.get("father_middle_rotate", 0)
                    ),
                    "father_last_translate_x": int(
                        request.POST.get("father_last_translate_x", 0)
                    ),
                    "father_last_translate_y": int(
                        request.POST.get("father_last_translate_y", 0)
                    ),
                    "father_last_rotate": int(
                        request.POST.get("father_last_rotate", 0)
                    ),
                    "father_birth_translate_x": int(
                        request.POST.get("father_birth_translate_x", 0)
                    ),
                    "father_birth_translate_y": int(
                        request.POST.get("father_birth_translate_y", 0)
                    ),
                    "father_birth_rotate": int(
                        request.POST.get("father_birth_rotate", 0)
                    ),
                    "father_birth_place_translate_x": int(
                        request.POST.get("father_birth_place_translate_x", 0)
                    ),
                    "father_birth_place_translate_y": int(
                        request.POST.get("father_birth_place_translate_y", 0)
                    ),
                    "father_birth_place_rotate": int(
                        request.POST.get("father_birth_place_rotate", 0)
                    ),
                    "father_death_translate_x": int(
                        request.POST.get("father_death_translate_x", 0)
                    ),
                    "father_death_translate_y": int(
                        request.POST.get("father_death_translate_y", 280)
                    ),
                    "father_death_rotate": int(
                        request.POST.get("father_death_rotate", -90)
                    ),
                    "father_death_place_translate_x": int(
                        request.POST.get("father_death_place_translate_x", 0)
                    ),
                    "father_death_place_translate_y": int(
                        request.POST.get("father_death_place_translate_y", 280)
                    ),
                    "father_death_place_rotate": int(
                        request.POST.get("father_death_place_rotate", -90)
                    ),
                    # Mother positioning
                    "mother_first_translate_x": int(
                        request.POST.get("mother_first_translate_x", 0)
                    ),
                    "mother_first_translate_y": int(
                        request.POST.get("mother_first_translate_y", 0)
                    ),
                    "mother_first_rotate": int(
                        request.POST.get("mother_first_rotate", 0)
                    ),
                    "mother_middle_translate_x": int(
                        request.POST.get("mother_middle_translate_x", 0)
                    ),
                    "mother_middle_translate_y": int(
                        request.POST.get("mother_middle_translate_y", 0)
                    ),
                    "mother_middle_rotate": int(
                        request.POST.get("mother_middle_rotate", 0)
                    ),
                    "mother_last_translate_x": int(
                        request.POST.get("mother_last_translate_x", 0)
                    ),
                    "mother_last_translate_y": int(
                        request.POST.get("mother_last_translate_y", 0)
                    ),
                    "mother_last_rotate": int(
                        request.POST.get("mother_last_rotate", 0)
                    ),
                    "mother_birth_translate_x": int(
                        request.POST.get("mother_birth_translate_x", 0)
                    ),
                    "mother_birth_translate_y": int(
                        request.POST.get("mother_birth_translate_y", 0)
                    ),
                    "mother_birth_rotate": int(
                        request.POST.get("mother_birth_rotate", 0)
                    ),
                    "mother_birth_place_translate_x": int(
                        request.POST.get("mother_birth_place_translate_x", 0)
                    ),
                    "mother_birth_place_translate_y": int(
                        request.POST.get("mother_birth_place_translate_y", 0)
                    ),
                    "mother_birth_place_rotate": int(
                        request.POST.get("mother_birth_place_rotate", 0)
                    ),
                    "mother_death_translate_x": int(
                        request.POST.get("mother_death_translate_x", 0)
                    ),
                    "mother_death_translate_y": int(
                        request.POST.get("mother_death_translate_y", 280)
                    ),
                    "mother_death_rotate": int(
                        request.POST.get("mother_death_rotate", -90)
                    ),
                    "mother_death_place_translate_x": int(
                        request.POST.get("mother_death_place_translate_x", 0)
                    ),
                    "mother_death_place_translate_y": int(
                        request.POST.get("mother_death_place_translate_y", 280)
                    ),
                    "mother_death_place_rotate": int(
                        request.POST.get("mother_death_place_rotate", -90)
                    ),
                    # Composite settings
                    "composite_1gen_scale": float(
                        request.POST.get("composite_1gen_scale", 48)
                    ),
                    "composite_overlay_x": int(
                        request.POST.get("composite_overlay_x", 508)
                    ),
                    "composite_overlay_y": int(
                        request.POST.get("composite_overlay_y", 508)
                    ),
                    # Stroke settings
                    "parent_stroke_color": request.POST.get(
                        "parent_stroke_color", "#000000"
                    ),
                    "info_stroke_color": request.POST.get(
                        "info_stroke_color", "#666666"
                    ),
                }
            )

        # Save to session
        request.session["hud_settings"] = hud_settings
        logger.debug(f"Settings saved to session: {hud_settings}")

        return JsonResponse(
            {
                "status": "success",
                "message": "Settings saved successfully",
                "Settings saved to session": hud_settings,
            }
        )

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

    try:
        # Fallback: try to get file_id from GET parameters
        if not gedcom_file_id:
            gedcom_file_id = request.GET.get("file_id")

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

        # Convert all individuals to PersonData objects for multi-generational charts
        person_data_objects = {}
        for person_id, person_data in individuals.items():
            person_data_objects[person_id] = PersonData(**person_data)

        # Update family_data with PersonData objects
        family_data_with_person_objects = gedcom_file.parsed_data.copy()
        family_data_with_person_objects["individuals"] = person_data_objects

        # Get the template mapping to find the right generator
        template_mapping = get_template_mapping()
        template_config = template_mapping.get(template_id)

        if not template_config:
            return HttpResponse(f"Template {template_id} not found", status=404)

        # Dynamically import the generator module
        module = importlib.import_module(template_config["module"])
        generator_function = getattr(module, template_config["function"])

        # Generate the preview
        preview_buffer = generator_function(
            primary_individual,
            family_data_with_person_objects,
            "preview",
            user_settings,
        )

        # Return the preview as an image
        return HttpResponse(preview_buffer, content_type="image/png")

    except Exception as e:
        logger.error(f"Error generating template {template_id} preview: {str(e)}")
        return HttpResponse(f"Error generating preview: {str(e)}", status=500)


# THIS IS THE ONE BEING USED/SEEN IN CONSOLE (kept for backward compatibility)
@csrf_protect
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
                "primary_name_font_size": hud_settings.get(
                    "primary_name_font_size", 84
                ),
                "primary_date_info_font_size": hud_settings.get(
                    "primary_date_info_font_size", 60
                ),
                "primary_place_info_font_size": hud_settings.get(
                    "primary_place_info_font_size", 28
                ),
                "default_stroke_width": hud_settings.get("default_stroke_width", 0.5),
                "primary_stroke_color": hud_settings.get(
                    "primary_stroke_color", "#ffffff"
                ),
                "primary_background_color": hud_settings.get(
                    "primary_background_color", "#000000"
                ),
                "primary_font_color": hud_settings.get("primary_font_color", "#ffffff"),
                "primary_birth_color": hud_settings.get(
                    "primary_birth_color", "#ffffff"
                ),
                "primary_birth_place_color": hud_settings.get(
                    "primary_birth_place_color", "#ffffff"
                ),
                "primary_death_color": hud_settings.get(
                    "primary_death_color", "#ffffff"
                ),
                "primary_death_place_color": hud_settings.get(
                    "primary_death_place_color", "#ffffff"
                ),
                "primary_name_rotate": hud_settings.get("primary_name_rotate", -45),
                "primary_birth_translate_x": hud_settings.get(
                    "primary_birth_translate_x", 0
                ),
                "primary_birth_translate_y": hud_settings.get(
                    "primary_birth_translate_y", 0
                ),
                "primary_birth_rotate": hud_settings.get("primary_birth_rotate", -90),
                "primary_birth_place_translate_x": hud_settings.get(
                    "primary_birth_place_translate_x", 0
                ),
                "primary_birth_place_translate_y": hud_settings.get(
                    "primary_birth_place_translate_y", 0
                ),
                "primary_birth_place_rotate": hud_settings.get(
                    "primary_birth_place_rotate", 0
                ),
                "primary_death_translate_x": hud_settings.get(
                    "primary_death_translate_x", 0
                ),
                "primary_death_translate_y": hud_settings.get(
                    "primary_death_translate_y", 0
                ),
                "primary_death_rotate": hud_settings.get("primary_death_rotate", 0),
                "primary_death_place_translate_x": hud_settings.get(
                    "primary_death_place_translate_x", 0
                ),
                "primary_death_place_translate_y": hud_settings.get(
                    "primary_death_place_translate_y", 0
                ),
                "primary_death_place_rotate": hud_settings.get(
                    "primary_death_place_rotate", -90
                ),
                "subject_translate_x": hud_settings.get("subject_translate_x", 0),
                "subject_translate_y": hud_settings.get("subject_translate_y", 0),
                # Chart-wide place formatting settings
                "place_use_country_abbrev": hud_settings.get(
                    "place_use_country_abbrev", True
                ),
                "place_use_state_abbrev": hud_settings.get(
                    "place_use_state_abbrev", True
                ),
                "place_show_county": hud_settings.get("place_show_county", False),
                "place_show_country": hud_settings.get("place_show_country", True),
                "place_hide_usa_with_state": hud_settings.get(
                    "place_hide_usa_with_state", True
                ),
                "place_show_township": hud_settings.get("place_show_township", False),
                "place_show_flag": hud_settings.get("place_show_flag", True),
                "place_flag_type": hud_settings.get("place_flag_type", "birth"),
                "place_flag_format": hud_settings.get("place_flag_format", "png"),
                "place_flag_size": hud_settings.get("place_flag_size", 48),
                "flag_font": hud_settings.get(
                    "flag_font",
                    "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
                ),
                # Chart-wide date formatting settings
                "date_format": hud_settings.get("date_format", "da_mon_year"),
                "date_year_only": hud_settings.get("date_year_only", True),
                "date_retain_leading_zeros": hud_settings.get(
                    "date_retain_leading_zeros", False
                ),
                # Chart-wide name formatting settings
                "name_use_first_middle_only": hud_settings.get(
                    "name_use_first_middle_only", True
                ),
                "name_hide_hyphenated_surname": hud_settings.get(
                    "name_hide_hyphenated_surname", True
                ),
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
        preview_buffer = generate_1gen_preview(
            primary_individual, gedcom_file.parsed_data, "preview", user_settings
        )

        # Return the preview as an image
        return HttpResponse(preview_buffer, content_type="image/png")

    except Exception as e:
        logger.error(f"Error generating template {template_id} preview: {str(e)}")
        return HttpResponse(f"Error generating preview: {str(e)}", status=500)


def get_file_individuals(request):
    """
    API endpoint to get list of valid individuals from a GEDCOM file.
    Used for fallback when current individual_id is invalid.
    """
    try:
        file_id = request.GET.get("file_id")
        if not file_id:
            return JsonResponse(
                {"success": False, "error": "Missing file_id parameter"}, status=400
            )

        from apps.generator.models import GedcomFile

        gedcom_file = GedcomFile.objects.get(id=file_id)
        if not gedcom_file.parsed_data:
            return JsonResponse(
                {"success": False, "error": "File not processed yet"}, status=400
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})

        # Create list of individuals with id and name
        individual_list = []
        for ind_id, ind_data in individuals.items():
            individual_list.append(
                {
                    "id": ind_id,
                    "name": ind_data.get("full_name", "Unknown"),
                    "birth_date": ind_data.get("birth_date", ""),
                    "death_date": ind_data.get("death_date", ""),
                }
            )

        # Sort by name for consistency
        individual_list.sort(key=lambda x: x["name"])

        return JsonResponse(
            {
                "success": True,
                "file_id": file_id,
                "total_count": len(individual_list),
                "individuals": individual_list[:10],  # Return first 10 for fallback
            }
        )

    except GedcomFile.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "GEDCOM file not found"}, status=404
        )
    except Exception as e:
        logger.error(f"Error getting file individuals: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def get_settings_panel(request, template_name):
    """
    AJAX endpoint to return settings panel HTML for dynamic template switching.
    """
    try:
        # Debug logging
        logger.info(f"get_settings_panel called with template_name: {template_name}")
        logger.info(f"Request GET params: {dict(request.GET)}")
        logger.info(f"Template path will be: hud/settings/{template_name}")

        # Get template information for context
        template_id = request.GET.get("template", "1")
        template_mapping = get_template_mapping()
        template_config = template_mapping.get(template_id, {})
        display_name = template_config.get("name", f"Template {template_id}")

        logger.debug(f"Template ID: {template_id}, Display Name: {display_name}")

        # Determine generations count
        if template_id == "1":
            generations = "1"
        elif template_id == "2":
            generations = "2"
        else:
            generations = template_id  # Use template ID for higher generations

        # Render the settings template (use template_name from URL parameter)
        template_path = f"hud/settings/{template_name}"
        logger.info(f"Template path: {template_path}")

        # Check if template exists
        from django.template.loader import get_template

        try:
            get_template(template_path)
            logger.info(f"Template {template_path} found successfully")
        except Exception as e:
            logger.error(f"Template {template_path} not found: {e}")
            # Fallback to default template
            template_path = "hud/settings/default_settings.html"
            logger.info(f"Falling back to {template_path}")

        context = {
            "hud_settings": request.session.get("hud_settings", {}),
            "template_name": display_name,  # Use display name for context
            "generations": generations,
        }

        return render(request, template_path, context)

    except Exception as e:
        logger.error(f"Error loading settings panel {template_name}: {str(e)}")
        logger.error(f"Exception details: {type(e).__name__}: {e}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")

        # Return error HTML for AJAX requests
        return HttpResponse(
            f'<div class="alert alert-danger">Error loading settings: {str(e)}<br><small>Template: {template_name}</small></div>',
            content_type="text/html",
        )


@csrf_protect
def get_template_preview(request, template_id):
    """
    Generic template preview endpoint that handles all template types.
    Now uses the buffer system for efficient generation.

    Args:
        request: HTTP request object
        template_id: Template identifier ('1', '2', '3', etc.)

    Returns:
        HttpResponse with generated image or error message
    """
    try:
        if request.method == "GET":
            individual_id = request.GET.get("individual_id")
            user_settings = {}
        elif request.method == "POST":
            data = json.loads(request.body)
            individual_id = data.get("individual_id")
            user_settings = data.get("user_settings", {})
        else:
            return HttpResponse("Method not allowed", status=405)

        # Get the primary individual from the session or GET parameters
        if not individual_id:
            individual_id = request.session.get("selected_individual_id")
        if not individual_id:
            return HttpResponse("No individual selected", status=400)

        gedcom_file_id = request.session.get("current_gedcom_file_id")

        # Fallback: try to get file_id from GET parameters
        if not gedcom_file_id:
            gedcom_file_id = request.GET.get("file_id")

        if not gedcom_file_id:
            return HttpResponse("No GEDCOM file selected", status=400)

        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        if not gedcom_file.parsed_data:
            return HttpResponse("File not processed yet", status=400)

        individuals = gedcom_file.parsed_data.get("individuals", {})
        if individual_id not in individuals:
            return HttpResponse("Individual not found", status=404)

        individual_data = individuals[individual_id]
        primary_individual = PersonData(**individual_data)

        # Convert all individuals to PersonData objects for multi-generational charts
        person_data_objects = {}
        for person_id, person_data in individuals.items():
            person_data_objects[person_id] = PersonData(**person_data)

        # Update family_data with PersonData objects
        family_data_with_person_objects = gedcom_file.parsed_data.copy()
        family_data_with_person_objects["individuals"] = person_data_objects

        # Get the template mapping to find the right generator
        template_mapping = get_template_mapping()
        template_config = template_mapping.get(template_id)

        if not template_config:
            return HttpResponse(f"Template {template_id} not found", status=404)

        # Dynamically import the generator module
        module = importlib.import_module(template_config["module"])
        generator_function = getattr(module, template_config["function"])

        # Generate the preview
        preview_buffer = generator_function(
            primary_individual,
            family_data_with_person_objects,
            "preview",
            user_settings,
        )

        # Return the preview as an image
        return HttpResponse(preview_buffer, content_type="image/png")

    except Exception as e:
        logger.error(f"Error generating template {template_id} preview: {str(e)}")
        return HttpResponse(f"Error generating preview: {str(e)}", status=500)
