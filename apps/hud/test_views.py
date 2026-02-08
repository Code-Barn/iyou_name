"""
Test view for enhanced 1-generation generator.

This view allows testing the enhanced generator with proper logging,
settings validation, and buffer management.
"""

import json
import logging
from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.generator.models import GedcomFile
from apps.parser.models import PersonData
from apps.generator.utils.image_1generator import (
    generate_1gen_preview,
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def test_enhanced_1gen_preview(request):
    """
    Test endpoint for enhanced 1-generation preview generator.

    This endpoint tests the enhanced generator with:
    - Settings validation
    - Proper logging
    - Buffer management
    - Error handling
    """
    try:
        # Get individual_id from request
        if request.method == "GET":
            individual_id = request.GET.get("individual_id")
            file_id = request.GET.get("file_id")

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
                    "primary_stroke_color", "#000000"
                ),
                "primary_background_color": hud_settings.get(
                    "primary_background_color", "#ffffff"
                ),
                "primary_font_color": hud_settings.get("primary_font_color", "#000000"),
                "primary_birth_color": hud_settings.get(
                    "primary_birth_color", "#000000"
                ),
                "primary_birth_place_color": hud_settings.get(
                    "primary_birth_place_color", "#000000"
                ),
                "primary_death_color": hud_settings.get(
                    "primary_death_color", "#000000"
                ),
                "primary_death_place_color": hud_settings.get(
                    "primary_death_place_color", "#000000"
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
            }

        elif request.method == "POST":
            data = json.loads(request.body)
            individual_id = data.get("individual_id")
            file_id = data.get("file_id")
            user_settings = data.get("user_settings", {})

        else:
            return HttpResponse("Method not allowed", status=405)

        # Validate required parameters
        if not individual_id:
            return HttpResponse("individual_id is required", status=400)

        if not file_id:
            return HttpResponse("file_id is required", status=400)

        # Get the GEDCOM file
        try:
            gedcom_file = GedcomFile.objects.get(id=file_id)
        except GedcomFile.DoesNotExist:
            return HttpResponse("GEDCOM file not found", status=404)

        # Get the individual data
        individuals = gedcom_file.parsed_data.get("individuals", {})
        if individual_id not in individuals:
            return HttpResponse("Individual not found", status=404)

        individual_data = individuals[individual_id]
        primary_individual = PersonData(**individual_data)

        # Log test information
        logger.info(
            f"Testing enhanced 1gen generator for: {primary_individual.full_name}"
        )
        logger.info(f"Settings provided: {len(user_settings)} settings")
        logger.debug(
            f"Sample settings: font_family={user_settings.get('font_family')}, "
            f"primary_name_font_size={user_settings.get('primary_name_font_size')}"
        )

        # Test the enhanced generator
        preview_buffer = generate_1gen_preview_enhanced(
            primary_individual, gedcom_file.parsed_data, "preview", user_settings
        )

        # Log success
        logger.info("Enhanced 1gen generator completed successfully")

        # Return the preview as an image
        return HttpResponse(preview_buffer, content_type="image/png")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in enhanced 1gen test: {e}")
        return HttpResponse(f"Invalid JSON in request body: {e}", status=400)

    except Exception as e:
        logger.error(f"Error in enhanced 1gen test: {str(e)}", exc_info=True)
        return HttpResponse(f"Error generating enhanced preview: {str(e)}", status=500)


@csrf_exempt
@require_http_methods(["GET"])
def test_enhanced_1gen_comparison(request):
    """
    Test endpoint that generates both original and enhanced versions for comparison.

    Query parameters:
    - individual_id: ID of individual to generate
    - file_id: ID of GEDCOM file
    """
    try:
        individual_id = request.GET.get("individual_id")
        file_id = request.GET.get("file_id")

        if not individual_id or not file_id:
            return HttpResponse("individual_id and file_id are required", status=400)

        # Get the GEDCOM file and individual
        gedcom_file = GedcomFile.objects.get(id=file_id)
        individuals = gedcom_file.parsed_data.get("individuals", {})

        if individual_id not in individuals:
            return HttpResponse("Individual not found", status=404)

        individual_data = individuals[individual_id]
        primary_individual = PersonData(**individual_data)

        # Get session settings
        hud_settings = request.session.get("hud_settings", {})
        user_settings = {
            "font_family": hud_settings.get("font_family", "Arial"),
            "primary_name_font_size": hud_settings.get("primary_name_font_size", 84),
            "primary_date_info_font_size": hud_settings.get(
                "primary_date_info_font_size", 60
            ),
            "primary_place_info_font_size": hud_settings.get(
                "primary_place_info_font_size", 28
            ),
            "default_stroke_width": hud_settings.get("default_stroke_width", 0.5),
            "primary_stroke_color": hud_settings.get("primary_stroke_color", "#000000"),
            "primary_background_color": hud_settings.get(
                "primary_background_color", "#ffffff"
            ),
            "primary_font_color": hud_settings.get("primary_font_color", "#000000"),
            "primary_birth_color": hud_settings.get("primary_birth_color", "#000000"),
            "primary_birth_place_color": hud_settings.get(
                "primary_birth_place_color", "#000000"
            ),
            "primary_death_color": hud_settings.get("primary_death_color", "#000000"),
            "primary_death_place_color": hud_settings.get(
                "primary_death_place_color", "#000000"
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
        }

        # Test both generators
        logger.info(f"Testing comparison for: {primary_individual.full_name}")

        # Generate with enhanced version
        enhanced_buffer = generate_1gen_preview(
            primary_individual, gedcom_file.parsed_data, "preview", user_settings
        )

        # Import original generator for comparison
        from apps.generator.utils.image_1generator import generate_1gen_preview

        # Generate with original version
        original_buffer = generate_1gen_preview(
            primary_individual, gedcom_file.parsed_data, "preview", user_settings
        )

        # Return comparison results as JSON
        comparison_results = {
            "individual_name": primary_individual.full_name,
            "individual_id": individual_id,
            "enhanced_generator": {
                "status": "success",
                "buffer_size": enhanced_buffer.tell() if enhanced_buffer else 0,
                "settings_validated": len(user_settings),
            },
            "original_generator": {
                "status": "success",
                "buffer_size": original_buffer.tell() if original_buffer else 0,
                "settings_used": len(user_settings),
            },
            "settings_sample": {
                "font_family": user_settings.get("font_family"),
                "primary_name_font_size": user_settings.get("primary_name_font_size"),
                "primary_stroke_color": user_settings.get("primary_stroke_color"),
            },
        }

        logger.info(
            f"Comparison completed: Enhanced={comparison_results['enhanced_generator']['buffer_size']} bytes, "
            f"Original={comparison_results['original_generator']['buffer_size']} bytes"
        )

        return JsonResponse(comparison_results)

    except GedcomFile.DoesNotExist:
        return HttpResponse("GEDCOM file not found", status=404)
    except Exception as e:
        logger.error(f"Error in enhanced 1gen comparison: {str(e)}", exc_info=True)
        return HttpResponse(f"Error in comparison: {str(e)}", status=500)
