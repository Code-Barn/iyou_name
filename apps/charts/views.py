import importlib
import json
import logging

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from apps.generator.models import GedcomFile, PersonData

logger = logging.getLogger(__name__)


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

    if request.method == "POST":
        try:
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

            # Get the template configuration
            template_mapping = get_template_mapping()
            if template_id not in template_mapping:
                return render(
                    request, "charts/error.html", {"error": "Invalid template selected"}
                )

            template_config = template_mapping[template_id]

            # Import the generator module dynamically
            module = importlib.import_module(template_config["module"])
            generator_func = getattr(module, template_config["function"])

            # Get the GEDCOM file and individual data
            gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)

            if not gedcom_file.parsed_data:
                return render(
                    request, "charts/error.html", {"error": "File not processed yet"}
                )

            individuals = gedcom_file.parsed_data.get("individuals", {})
            families = gedcom_file.parsed_data.get("families", {})

            if individual_id not in individuals:
                return render(
                    request, "charts/error.html", {"error": "Individual not found"}
                )

            # Convert the individual dict to a PersonData object
            individual_dict = individuals[individual_id]
            individual = PersonData(**individual_dict)

            # Debug logging
            print(f"Individual: {individual}")
            print(f"Individuals: {individuals}")
            print(f"Families: {families}")

            try:
                # Call the generator function
                chart_data = generator_func(individual, individuals, families)

                # For now, we'll just return a success message
                # In a real implementation, this would generate and return the actual chart file
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
                print(f"Error generating chart: {e}")
                return render(
                    request,
                    "charts/error.html",
                    {"error": f"Chart generation failed: {str(e)}"},
                )

        except GedcomFile.DoesNotExist:
            return render(
                request, "charts/error.html", {"error": "GEDCOM file not found"}
            )
        except Exception as e:
            print(f"Error in generate_chart: {e}")
            return render(request, "charts/error.html", {"error": str(e)})

    # GET request - show the generation form
    try:
        chart_settings = request.session.get("chart_settings", {})
        template_id = chart_settings.get("template", "4")

        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)

        if not gedcom_file.parsed_data:
            return render(
                request, "charts/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})
        individual_id = chart_settings.get("individual_id", gedcom_file.home_person_id)

        if individual_id and individual_id in individuals:
            individual_dict = individuals[individual_id]
            individual = PersonData(**individual_dict)
        else:
            individual = None

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

    except GedcomFile.DoesNotExist:
        return render(request, "charts/error.html", {"error": "GEDCOM file not found"})
    except Exception as e:
        return render(request, "charts/error.html", {"error": str(e)})


def get_template_mapping():
    """Helper function to get template mapping"""
    return {
        "1": {
            "module": "apps.generator.utils.image_1generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_1GEN_BW.pdf",
            "name": "1 Generation (Individual Only)",
        },
        "4": {
            "module": "apps.generator.utils.image_4generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_4GEN_BW.pdf",
            "name": "4 Generation Chart",
        },
    }
