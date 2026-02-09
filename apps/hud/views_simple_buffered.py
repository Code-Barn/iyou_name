"""
Simple buffered HUD views using a clean, simplified buffer system.
"""

import json
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST, require_GET

from apps.generator.models import GedcomFile
from apps.parser.models import PersonData
from apps.generator.utils.simple_buffer_manager import (
    get_chart_buffer,
    apply_settings_change,
    get_buffer_stats,
)

logger = logging.getLogger(__name__)


def display_tree_hud(request):
    """
    View for displaying the interactive HUD interface using simple buffer system.
    """
    # Handle POST requests from individual detail page
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

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        if not gedcom_file.parsed_data:
            return render(
                request, "hud/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})
        if individual_id not in individuals:
            return HttpResponse("Individual not found", status=400)

        # Get individual data and ensure it's a PersonData object
        individual_data = individuals[individual_id]
        if isinstance(individual_data, dict):
            primary_individual = PersonData(**individual_data)
        elif not isinstance(individual_data, PersonData):
            primary_individual = PersonData(**individual_data.__dict__)
        else:
            primary_individual = individual_data

        family_data = {
            "individuals": individuals,
            "families": gedcom_file.parsed_data.get("families", {}),
            "gedcom_file_id": gedcom_file_id,
        }

        # Get HUD settings from session or use defaults
        hud_settings = request.session.get(
            "hud_settings",
            {
                "show_photos": True,
                "show_dates": True,
                "show_locations": True,
                "compact_mode": False,
                "theme": "light",
                "template": "1",
            },
        )

        # Determine which settings template to use based on current template
        current_template = hud_settings.get("template", "1")
        from apps.generator.template_mapping import get_template_mapping

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
        current_settings_template = f"hud/settings/{settings_template_map.get(current_template, 'default_settings.html')}"

        context = {
            "individual": primary_individual,
            "individual_id": individual_id,
            "gedcom_file": gedcom_file,
            "gedcom_file_id": gedcom_file_id,
            "template_mapping": template_mapping,
            "TEMPLATE_MAPPING": template_mapping,
            "current_settings_template": current_settings_template,
            "hud_settings": hud_settings,
            "hud_settings_timestamp": 0,  # Force refresh initially
            "generations": 7,  # Default to 7 generations
        }

        return render(request, "hud/display_tree.html", context)

    except GedcomFile.DoesNotExist:
        return render(request, "hud/error.html", {"error": "GEDCOM file not found"})
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return render(
            request,
            "hud/error.html",
            {"error": f"Error loading data: {str(e)}"},
        )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_template_preview_simple(request, template_id):
    """
    Simple template preview endpoint using simplified buffer system.

    THIS FUNCTION WORKS INDEPENDENTLY and handles all edge cases properly.

    Returns: HttpResponse with chart image (PNG) or error JSON.
    """
    # Handle both GET and POST requests
    if request.method == "GET":
        individual_id = request.GET.get("individual_id")
        # For GET requests, use current session settings
        user_settings = request.session.get("hud_settings", {})
        logger.info(
            f"GET request for template {template_id}: using {len(user_settings)} session settings"
        )
    elif request.method == "POST":
        data = json.loads(request.body)
        individual_id = data.get("individual_id")
        user_settings = data.get("user_settings", {})
    else:
        return HttpResponse("Method not allowed", status=405)

    # Get session data
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return HttpResponse("No GEDCOM file selected", status=400)

    # Get individual data with proper error handling
    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
    except GedcomFile.DoesNotExist:
        return render(request, "hud/error.html", {"error": "GEDCOM file not found"})

    if not gedcom_file.parsed_data:
        return render(request, "hud/error.html", {"error": "File not processed yet"})

    individuals = gedcom_file.parsed_data.get("individuals", {})
    if not individuals:
        return render(request, "hud/error.html", {"error": "No individuals found"})

    if individual_id not in individuals:
        return render(request, "hud/error.html", {"error": "Individual not found"})

    # Get individual data (ensures PersonData object)
    individual_data = individuals[individual_id]
    if not individual_data:
        return render(request, "hud/error.html", {"error": "Invalid individual data"})

    # Convert to PersonData object
    if isinstance(individual_data, dict):
        primary_individual = PersonData(**individual_data)
    elif not isinstance(individual_data, PersonData):
        primary_individual = PersonData(**individual_data.__dict__)
    else:
        primary_individual = individual_data

    # Get family data
    family_data = {
        "individuals": individuals,
        "families": gedcom_file.parsed_data.get("families", {}),
        "gedcom_file_id": gedcom_file_id,
    }

    # Convert template ID to integer
    try:
        generation = int(template_id)
    except ValueError:
        return HttpResponse(f"Invalid template ID: {template_id}", status=400)

    # Generate chart using the standardized buffer system
    try:
        logger.debug(
            f"Generating chart for template {template_id} (generation {generation})"
        )

        buffer = get_chart_buffer(
            primary_individual, family_data, user_settings, generation
        )

        if buffer is None:
            logger.error(f"get_chart_buffer returned None for generation {generation}")
            return HttpResponse("Chart generation failed", status=500)

        # Return the generated image
        buffer.seek(0)
        image_data = buffer.read()
        return HttpResponse(image_data, content_type="image/png")

    except Exception as e:
        logger.error(f"Error generating chart for template {template_id}: {e}")
        return HttpResponse(f"Chart generation failed: {str(e)}", status=500)


@csrf_exempt
@require_POST
def save_hud_settings(request):
    """
    Save HUD settings using the simple buffer system.
    """
    try:
        data = json.loads(request.body)
        settings = data.get("settings", {})

        # Store settings in session
        request.session["hud_settings"] = settings

        # Apply settings change using the simple buffer system
        individual_id = request.session.get("selected_individual_id")
        gedcom_file_id = request.session.get("current_gedcom_file_id")

        if individual_id and gedcom_file_id:
            try:
                gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
                individuals = gedcom_file.parsed_data.get("individuals", {})
                if individual_id in individuals:
                    # Get individual data and ensure it's a PersonData object
                    individual_data = individuals[individual_id]
                    if isinstance(individual_data, dict):
                        primary_individual = PersonData(**individual_data)
                    elif not isinstance(individual_data, PersonData):
                        primary_individual = PersonData(**individual_data.__dict__)
                    else:
                        primary_individual = individual_data

                    family_data = {
                        "individuals": individuals,
                        "families": gedcom_file.parsed_data.get("families", {}),
                        "gedcom_file_id": gedcom_file_id,
                    }

                    # Apply settings change (invalidates cache)
                    apply_settings_change(primary_individual, family_data, settings, 1)

                    # Update settings timestamp
                    request.session["hud_settings_timestamp"] = 0

                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Settings saved successfully",
                            "timestamp": request.session.get("hud_settings_timestamp"),
                        }
                    )
                else:
                    return JsonResponse(
                        {"success": False, "error": "Individual not found"}, status=400
                    )

            except Exception as e:
                logger.error(f"Error saving settings: {e}")
                return JsonResponse({"success": False, "error": str(e)}, status=500)
        else:
            return JsonResponse(
                {"success": False, "error": "No individual or file selected"},
                status=400,
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON data"}, status=400
        )
    except Exception as e:
        logger.error(f"Error in save_hud_settings: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def get_buffer_stats(request):
    """Get simple buffer performance statistics."""
    try:
        stats = get_buffer_stats()
        return JsonResponse(stats)
    except Exception as e:
        logger.error(f"Error getting buffer stats: {e}")
        return JsonResponse({"error": str(e)}, status=500)
