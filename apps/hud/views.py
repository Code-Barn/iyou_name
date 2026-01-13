import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.generator.models import GedcomFile
from apps.generator.template_mapping import get_template_mapping
from apps.parser.models import PersonData


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
                "template": "4",  # Default template
            },
        )

        return render(
            request,
            "hud/display_tree.html",
            {
                "gedcom_file_id": gedcom_file_id,
                "individual": individual,
                "hud_settings": hud_settings,
                "TEMPLATE_MAPPING": get_template_mapping(),
            },
        )

    except GedcomFile.DoesNotExist:
        return render(request, "hud/error.html", {"error": "GEDCOM file not found"})
    except Exception as e:
        return render(request, "hud/error.html", {"error": str(e)})


@require_http_methods(["POST"])
@csrf_exempt
def save_hud_settings(request):
    """
    View for saving HUD settings including template selection
    """
    try:
        data = json.loads(request.body)
        request.session["hud_settings"] = data
        return JsonResponse({"status": "success", "message": "Settings saved"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


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
                "template": "4",  # Default template
            },
        )
        return JsonResponse(settings)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
