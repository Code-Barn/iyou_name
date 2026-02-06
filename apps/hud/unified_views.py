"""
Unified HUD Views with Clean Settings Management

This replaces the complex, competing settings implementations
with a single, consistent approach.
"""

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.parser.models import GedcomFile, PersonData
from apps.generator.utils.unified_settings_helper import (
    get_unified_settings,
    categorize_setting,
    flatten_settings,
    get_default_settings,
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def save_hud_settings(request):
    """
    Unified settings save function - REPLACES ALL COMPETING IMPLEMENTATIONS

    This single function handles ALL settings saving with proper categorization.
    """
    try:
        data = json.loads(request.body)
        logger.info(f"UNIFIED: Received settings data with {len(data)} fields")

        # Get current settings from session
        hud_settings = request.session.get("hud_settings", {})

        # Initialize with default structure if needed
        if not hud_settings or not isinstance(hud_settings, dict):
            hud_settings = get_default_settings()

        # Process each setting and categorize it
        for key, value in data.items():
            category, clean_key, categorized_value = categorize_setting(key, value)

            if category == "base":
                # Base settings stored directly
                hud_settings[clean_key] = categorized_value
            else:
                # Generation-specific settings stored in nested dict
                if category not in hud_settings:
                    hud_settings[category] = {}
                hud_settings[category][clean_key] = categorized_value

            logger.debug(
                f"UNIFIED: Categorized {key} -> {category}.{clean_key} = {categorized_value}"
            )

        # Save unified settings to session
        request.session["hud_settings"] = hud_settings
        request.session.modified = True

        logger.info(
            f"UNIFIED: Settings saved successfully. Structure: {list(hud_settings.keys())}"
        )

        return JsonResponse(
            {
                "status": "success",
                "message": "Settings applied and preview updated successfully",
            }
        )

    except Exception as e:
        logger.error(f"UNIFIED: Error saving settings: {e}")
        return JsonResponse(
            {"status": "error", "message": f"Error saving settings: {str(e)}"},
            status=400,
        )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_template_preview(request, template_id):
    """
    Unified template preview function with clean settings access.

    REPLACES: Multiple competing settings extraction in preview functions
    """
    try:
        if request.method == "GET":
            individual_id = request.GET.get("individual_id")
        elif request.method == "POST":
            data = json.loads(request.body)
            individual_id = data.get("individual_id")
        else:
            return HttpResponse("Method not allowed", status=405)

        # Get individual from session or parameters
        if not individual_id:
            individual_id = request.session.get("selected_individual_id")
        if not individual_id:
            return HttpResponse("No individual selected", status=400)

        # Get GEDCOM file
        gedcom_file_id = request.session.get("current_gedcom_file_id")
        if not gedcom_file_id:
            return HttpResponse("No GEDCOM file selected", status=400)

        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        if not gedcom_file.parsed_data:
            return HttpResponse("File not processed yet", status=400)

        # Get individual data
        individuals = gedcom_file.parsed_data.get("individuals", {})
        if individual_id not in individuals:
            return HttpResponse("Individual not found", status=404)

        individual_data = individuals[individual_id]
        primary_individual = PersonData(**individual_data)

        # Convert all individuals to PersonData objects
        person_data_objects = {}
        for person_id, person_data in individuals.items():
            person_data_objects[person_id] = PersonData(**person_data)

        # Update family data with PersonData objects
        family_data_with_person_objects = gedcom_file.parsed_data.copy()
        family_data_with_person_objects["individuals"] = person_data_objects

        # UNIFIED SETTINGS ACCESS - REPLACES ALL COMPETING EXTRACTION
        session_settings = request.session.get("hud_settings", {})

        # Map template IDs to generation names
        template_generation_map = {
            "1": "primary",
            "2": "parent",
            "3": "grandparent",
            "4": "grandparent",
            "5": "grandparent",
            "6": "grandparent",
            "7": "grandparent",
        }

        generation = template_generation_map.get(template_id, "primary")
        user_settings = get_unified_settings(session_settings, generation)

        logger.info(f"UNIFIED: Template {template_id} -> Generation {generation}")
        logger.info(
            f"UNIFIED: Retrieved {len(user_settings)} settings for {generation}"
        )

        # Get template mapping and generator
        from apps.generator.template_mapping import get_template_mapping
        import importlib

        template_mapping = get_template_mapping()
        template_config = template_mapping.get(template_id)

        if not template_config:
            return HttpResponse(f"Template {template_id} not found", status=404)

        # Dynamically import and call generator
        module = importlib.import_module(template_config["module"])
        generator_function = getattr(module, template_config["function"])

        # Generate preview with unified settings
        preview_buffer = generator_function(
            primary_individual,
            family_data_with_person_objects,
            "preview",
            user_settings,
        )

        return HttpResponse(preview_buffer, content_type="image/png")

    except Exception as e:
        logger.error(f"UNIFIED: Error generating template {template_id} preview: {e}")
        return HttpResponse(f"Error generating preview: {str(e)}", status=500)


@require_http_methods(["GET"])
def get_settings_panel(request, template_name):
    """
    Unified settings panel with clean settings access for forms.

    REPLACES: Multiple settings access patterns in templates
    """
    try:
        # Get unified settings from session
        session_settings = request.session.get("hud_settings", {})
        all_settings = get_unified_settings(session_settings)

        # Flatten settings for template form usage
        flat_settings = flatten_settings(all_settings)

        # Map template names to generation for context
        template_generation_map = {
            "1gen": "primary",
            "2gen": "parent",
            "3gen": "grandparent",
            "4gen": "grandparent",
            "5gen": "grandparent",
            "6gen": "grandparent",
            "7gen": "grandparent",
        }

        generation = template_generation_map.get(template_name, "primary")

        context = {
            "hud_settings": flat_settings,
            "current_generation": generation,
            "all_settings": all_settings,
        }

        # Render appropriate settings template
        template_path = f"hud/settings/{template_name}_settings.html"
        return render(request, template_path, context)

    except Exception as e:
        logger.error(f"UNIFIED: Error getting settings panel for {template_name}: {e}")
        return HttpResponse(f"Error loading settings panel: {str(e)}", status=500)


# Keep existing non-settings functions unchanged
def display_tree_hud(request):
    """Main HUD display - unchanged"""
    # ... existing implementation ...
    pass


def update_settings_timestamp(request):
    """Update settings timestamp - unchanged"""
    # ... existing implementation ...
    pass


def get_hud_family_data(request):
    """Get family data - unchanged"""
    # ... existing implementation ...
    pass


def get_1gen_preview(request):
    """1gen preview - now handled by get_template_preview"""
    # ... existing implementation ...
    pass


def get_file_individuals(request):
    """Get file individuals - unchanged"""
    # ... existing implementation ...
    pass


def get_template_preview(request, template_id):
    """Template preview - now handled by unified function above"""
    # ... existing implementation ...
    pass
