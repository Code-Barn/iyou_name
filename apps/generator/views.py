import json
import logging
import importlib
from itertools import product

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from apps.generator.models import GedcomFile
from apps.generator.template_mapping import get_template_mapping

# from apps.generator.utils import (
#    image_1generator,
#    image_2generator,
#    image_3generator,
#    image_4generator,
#    image_5generator,
#    image_6generator,
#    image_7generator,
# )
from apps.parser.models import PersonData
from apps.upload.views import upload_and_generate

logger = logging.getLogger(__name__)

# Use the centralized template mapping
TEMPLATE_MAPPING = get_template_mapping()

# PyO3 Rust acceleration kernel (native C-extension). When installed, chart
# generation is routed through it for ~10-50ms rendering; otherwise the pure
# Python Wand engine remains the fail-safe fallback.
try:
    import iyou_chart_kernel

    RUST_ENGINE_AVAILABLE = True
    logger.info("PyO3 Rust kernel loaded - accelerated rendering enabled")
except ImportError:
    RUST_ENGINE_AVAILABLE = False
    logger.info("PyO3 Rust kernel not installed - using Python Wand engine")
except Exception as e:  # pragma: no cover - defensive
    RUST_ENGINE_AVAILABLE = False
    logger.warning(
        f"PyO3 Rust kernel import failed: {e} - using Python Wand engine"
    )


def _person_to_kernel_payload(person):
    """Map a Django PersonData onto the Rust kernel's PersonData JSON shape."""
    return {
        "id": person.id or "",
        "full_name": person.full_name or "",
        "given_name": person.given_name or "",
        "surname": person.surname or "",
        "birth_date": person.birth_date,
        "birth_place": person.birth_place,
        "death_date": person.death_date,
        "death_place": person.death_place,
    }


def _ancestor_position_labels(generation):
    """Return the kernel position IDs the given generation expects."""
    if generation == 2:
        return ["1", "2"]
    if generation == 3:
        return ["A", "B", "C", "D"]
    if generation in (4, 5, 6):
        return [
            f"{chr(ord('A') + i)}{d}"
            for i in range(2 ** (generation - 2))
            for d in (1, 2)
        ]
    if generation == 7:
        return [f"{chr(ord('A') + i)}{d}" for i in range(16) for d in (1, 2, 3, 4)]
    return []


def _walk_ancestor(people, start_id, steps):
    """Walk father/mother steps from start_id, returning the terminal person or None."""
    person_id = start_id
    for step in steps:
        person = people.get(person_id)
        if not person:
            return None
        parent_id = getattr(person, "father" if step == "father" else "mother", None)
        if not parent_id:
            return None
        person_id = parent_id
    return people.get(person_id)


def _build_ancestors_payload(people, primary_id, generation):
    """
    Build the kernel AncestorData JSON for all generations 2..N.

    The kernel's strategies compose previous-generation overlays recursively,
    so the payload must contain positions for every generation below N as well
    (Gen2 requires "1"/"2", Gen3 requires A-D, etc.).
    """
    individuals = {}
    if generation <= 1:
        return {"individuals": individuals}
    for gen in range(2, generation + 1):
        steps_list = list(product(("father", "mother"), repeat=gen - 1))
        for label, steps in zip(_ancestor_position_labels(gen), steps_list):
            person = _walk_ancestor(people, primary_id, steps)
            if person:
                individuals[label] = _person_to_kernel_payload(person)
    return {"individuals": individuals}


def _as_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _as_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_settings_payload(user_settings):
    """Map Django user_settings onto the kernel's ChartSettings JSON shape."""
    from apps.generator.utils.settings_validator import resolve_font_path

    return {
        "font_family": resolve_font_path(user_settings.get("font_family", "Arial")),
        "font_color": user_settings.get("primary_font_color", "#000000"),
        "background_color": user_settings.get("primary_background_color", "#FFFFFF"),
        "name_font_size": _as_float(
            user_settings.get("primary_name_font_size"), 84.0
        ),
        "date_font_size": _as_float(
            user_settings.get("primary_date_info_font_size"), 60.0
        ),
        "place_font_size": _as_float(
            user_settings.get("primary_place_info_font_size"), 28.0
        ),
        "use_outside_stroke": _as_bool(user_settings.get("use_outside_stroke")),
        "stroke_width": _as_float(user_settings.get("default_stroke_width"), 0.5),
        "stroke_color": user_settings.get("primary_stroke_color", "#000000"),
        "flag_size": 0,
        "flag_type": user_settings.get("place_flag_type", "birth"),
    }


@csrf_protect
@require_http_methods(["GET", "POST"])
def generate_final_chart(request):
    """
    View for generating the final family tree chart as a PDF.
    Uses the selected template and generation settings.
    Handles both GET and POST requests.
    """
    try:
        # Extract parameters from GET or POST data
        individual_id = request.POST.get("individual_id") or request.GET.get(
            "individual_id"
        )
        template = request.POST.get("template") or request.GET.get("template") or "1"

        logger.info(f"[PDF DEBUG] template parameter received: '{template}'")
        logger.info(f"[PDF DEBUG] POST keys: {list(request.POST.keys())}")

        # Initialize hud_settings early to avoid UnboundLocalError
        default_settings = {
            "place_use_country_abbrev": True,
            "place_use_state_abbrev": True,
            "place_hide_us_counties": True,
            "place_show_country": False,
            "place_hide_usa_with_state": True,
            "place_show_flag": True,
            "place_auto_shorten": False,
            "place_abbreviate_uk_counties": False,
            "place_abbreviate_sweden_counties": False,
            "place_abbreviate_france_departments": False,
            "place_abbreviate_germany_states": False,
            "place_abbreviate_poland_voivodeships": False,
            "place_abbreviate_place_parts": False,
            "place_year_only": False,
            "place_hide_township": False,
            "place_show_uk_flag": False,
            "place_flag_type": "birth",
            "place_flag_format": "png",
            "flag_font": "/usr/share/fonts/truetype/ancient-scripts/Symbola_hint.ttf",
            "date_format": "da_mon_year",
            "date_year_only": True,
            "date_retain_leading_zeros": False,
            "name_use_first_middle_only": True,
            "name_hide_hyphenated_surname": True,
        }
        session_settings = request.session.get("hud_settings", {})
        hud_settings = {**default_settings, **session_settings}

        # Collect ALL form settings (same as live preview) - not just hardcoded 1gen settings
        user_settings = {}
        for key, value in request.POST.items():
            if key.startswith(
                (
                    "primary_",
                    "parent_",
                    "grandparent_",
                    "greatgrandparent_",
                    "twox_great_",
                    "threex_great_",
                    "fourx_great_",
                )
            ) or key in [
                "font_family",
                "default_stroke_width",
                "composite_1gen_scale",
                "composite_overlay_x",
                "composite_overlay_y",
                # Date format settings
                "date_year_only",
                "date_format",
                "date_retain_leading_zeros",
                # Name format settings
                "name_use_first_middle_only",
                "name_hide_hyphenated_surname",
                # Place format settings
                "place_use_country_abbrev",
                "place_use_state_abbrev",
                "place_hide_us_counties",
                "place_show_country",
                "place_hide_usa_with_state",
                "place_show_township",
                "place_auto_shorten",
                "place_abbreviate_uk_counties",
                "place_show_uk_flag",
                "place_show_flag",
                "place_flag_type",
                "place_flag_format",
                "flag_font",
                "place_abbreviate_sweden_counties",
                "place_abbreviate_france_departments",
                "place_abbreviate_germany_states",
                "place_abbreviate_poland_voivodeships",
                "place_abbreviate_place_parts",
                "place_year_only",
            ]:
                # Convert numeric values
                if key.endswith(
                    (
                        "_font_size",
                        "_translate_x",
                        "_translate_y",
                        "_rotate",
                        "_scale",
                        "_stroke_width",
                    )
                ):
                    try:
                        if "." in value:
                            user_settings[key] = float(value)
                        else:
                            user_settings[key] = int(value)
                    except (ValueError, TypeError):
                        user_settings[key] = value
                else:
                    user_settings[key] = value

        logger.debug(
            f"Collected {len(user_settings)} settings from POST for PDF generation"
        )

        # Debug: log use_outside_stroke specifically
        logger.info(
            f"[PDF DEBUG] use_outside_stroke value: {user_settings.get('use_outside_stroke', 'NOT IN SETTINGS')}"
        )
        logger.info(
            f"[PDF DEBUG] place_year_only value: {user_settings.get('place_year_only', 'NOT IN SETTINGS')}"
        )

        # For cumulative inheritance, we need to merge stored settings from previous generations
        # This matches the same logic as the live preview
        if template != "1":
            # Load cumulative settings from localStorage (same as live preview)
            # Note: This is a simplified approach - in production, we'd want session-based storage
            # For now, we'll use the POST data which should contain all the merged settings already
            logger.debug(
                f"Using cumulative settings for template {template} PDF generation"
            )
        else:
            logger.debug(
                f"Using current settings only for template {template} PDF generation"
            )

        # If no POST settings, use session settings
        # Check if we have any POST data for settings (more reliable than checking values)
        has_post_settings = any(
            key in request.POST
            for key in [
                "font_family",
                "primary_name_font_size",
                "primary_date_info_font_size",
                "primary_place_info_font_size",
                "default_stroke_width",
                "primary_background_color",
                "primary_stroke_color",
                "primary_font_color",
                "primary_birth_color",
                "primary_birth_place_color",
                "primary_death_color",
                "primary_death_place_color",
                "primary_translate_x",
                "primary_translate_y",
                "primary_name_rotate",
                "primary_birth_translate_x",
                "primary_birth_translate_y",
                "primary_birth_rotate",
                "primary_birth_place_translate_x",
                "primary_birth_place_translate_y",
                "primary_birth_place_rotate",
                "primary_death_translate_x",
                "primary_death_translate_y",
                "primary_death_rotate",
                "primary_death_place_translate_x",
                "primary_death_place_translate_y",
                "primary_death_place_rotate",
                "date_format",
                "date_year_only",
                "date_retain_leading_zeros",
                "name_use_first_middle_only",
                "name_hide_hyphenated_surname",
                "place_use_country_abbrev",
                "place_use_state_abbrev",
                "place_hide_us_counties",
                "place_show_country",
                "place_hide_usa_with_state",
                "place_hide_township",
                "place_auto_shorten",
                "place_abbreviate_uk_counties",
                "place_show_flag",
                "place_flag_type",
                "place_flag_format",
                "flag_font",
                "place_show_uk_flag",
                "place_abbreviate_sweden_counties",
                "place_abbreviate_france_departments",
                "place_abbreviate_germany_states",
                "place_abbreviate_poland_voivodeships",
                "place_abbreviate_place_parts",
                "place_year_only",
                "use_outside_stroke",
            ]
        )

        if not has_post_settings:
            logger.debug("No POST settings found, using session settings")
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
                "primary_background_color": hud_settings.get(
                    "primary_background_color", "#FFFFFF"
                ),
                "primary_stroke_color": hud_settings.get(
                    "primary_stroke_color", "#000000"
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
                "primary_translate_x": hud_settings.get("primary_translate_x", 0),
                "primary_translate_y": hud_settings.get("primary_translate_y", 0),
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
                "date_format": hud_settings.get("date_format", "da_mon_year"),
                "date_year_only": hud_settings.get("date_year_only", False),
                "date_retain_leading_zeros": hud_settings.get(
                    "date_retain_leading_zeros", False
                ),
                "name_use_first_middle_only": hud_settings.get(
                    "name_use_first_middle_only", False
                ),
                "name_hide_hyphenated_surname": hud_settings.get(
                    "name_hide_hyphenated_surname", False
                ),
                "place_use_country_abbrev": hud_settings.get(
                    "place_use_country_abbrev", False
                ),
                "place_use_state_abbrev": hud_settings.get(
                    "place_use_state_abbrev", False
                ),
                "place_hide_us_counties": hud_settings.get(
                    "place_hide_us_counties", True
                ),
                "place_show_country": hud_settings.get("place_show_country", True),
                "place_hide_usa_with_state": hud_settings.get(
                    "place_hide_usa_with_state", True
                ),
                "place_hide_township": hud_settings.get("place_hide_township", False),
                "place_auto_shorten": hud_settings.get("place_auto_shorten", False),
                "place_abbreviate_uk_counties": hud_settings.get(
                    "place_abbreviate_uk_counties", False
                ),
                "place_show_uk_flag": hud_settings.get("place_show_uk_flag", False),
                "place_show_flag": hud_settings.get("place_show_flag", False),
                "place_flag_type": hud_settings.get("place_flag_type", "birth"),
                "place_abbreviate_sweden_counties": hud_settings.get(
                    "place_abbreviate_sweden_counties", False
                ),
                "place_abbreviate_france_departments": hud_settings.get(
                    "place_abbreviate_france_departments", False
                ),
                "place_abbreviate_germany_states": hud_settings.get(
                    "place_abbreviate_germany_states", False
                ),
                "place_abbreviate_poland_voivodeships": hud_settings.get(
                    "place_abbreviate_poland_voivodeships", False
                ),
                "place_abbreviate_place_parts": hud_settings.get(
                    "place_abbreviate_place_parts", False
                ),
                "place_year_only": hud_settings.get("place_year_only", False),
                "use_outside_stroke": hud_settings.get("use_outside_stroke", False),
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
        logger.info(
            f"[PDF DEBUG] TEMPLATE_MAPPING keys: {list(TEMPLATE_MAPPING.keys())}"
        )

        # Get the appropriate generator configuration
        template_config = TEMPLATE_MAPPING.get(template)
        logger.info(f"[PDF DEBUG] template_config for '{template}': {template_config}")
        if not template_config:
            logger.error("Invalid template parameter: %s", template)
            return JsonResponse(
                {"status": "error", "message": "Invalid template parameter"},
                status=400,
            )

        # Dynamically import the generator module (used by the Python fallback)
        module = importlib.import_module(template_config["module"])
        generator_function = getattr(module, template_config["function"])

        # Determine the template type (default to "final" for chart generation)
        template_type = template_config.get("template_type", "final")

        # PyO3 Rust Kernel Fast Path
        if RUST_ENGINE_AVAILABLE:
            try:
                generation_num = int(template)
                png_bytes = iyou_chart_kernel.render_chart_from_json(
                    str(generation_num),
                    json.dumps(_person_to_kernel_payload(primary_individual)),
                    json.dumps(
                        _build_ancestors_payload(
                            person_data_objects, individual_id, generation_num
                        )
                    ),
                    json.dumps(_build_settings_payload(user_settings)),
                )
                logger.info(
                    f"Rust kernel rendered chart ({len(png_bytes)} bytes) for template {template}"
                )
                return HttpResponse(png_bytes, content_type="image/png")
            except Exception as rust_error:
                logger.error(
                    f"Rust kernel render failed: {rust_error}. Falling back to Python engine."
                )

        # Pure-Python Wand fallback (fail-safe)
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
        from apps.generator.utils.prototype.prototype_image_1generator import (
            generate_prototype_1gen_preview,
        )

        image_buffer = generate_prototype_1gen_preview(
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
    if not request.user.is_authenticated:
        return redirect("oidc_authentication_init")

    if request.method == "POST" and "gedcom_file" in request.FILES:
        return upload_and_generate(request)

    return redirect("users:profile")
