import importlib
import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from apps.generator.models import GedcomFile
from apps.generator.template_mapping import get_template_mapping
from apps.parser.models import PersonData

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@require_http_methods(["GET", "POST"])
def generate_chart(request, file_id, individual_id):
    """
    View for generating a family tree chart
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)

        if not gedcom_file.parsed_data:
            return render(
                request, "charts/error.html", {"error": "File not processed yet"}
            )

        # Get the selected individual
        individuals = gedcom_file.parsed_data.get("individuals", {})
        if individual_id not in individuals:
            return render(
                request, "charts/error.html", {"error": "Individual not found"}
            )

        individual = individuals[individual_id]
        if isinstance(individual, dict):
            individual = PersonData(**individual)
        elif not isinstance(individual, PersonData):
            # Convert to PersonData if it's not already
            individual = PersonData(**individual.__dict__)

        # Get template ID from request or use default
        template_id = request.POST.get("template", "4")  # Default to 4-generation chart

        # Get the template configuration
        template_mapping = get_template_mapping()
        if template_id not in template_mapping:
            return render(
                request, "charts/error.html", {"error": "Invalid template selected"}
            )

        template_config = template_mapping[template_id]

        logger.debug(f"Template ID: {template_id}")
        logger.debug(f"Template Config: {template_config}")

        # Dynamically import the generator module
        try:
            module = importlib.import_module(template_config["module"])
            generator_function = getattr(module, template_config["function"])
        except ImportError as e:
            logger.error(f"Failed to import generator module: {e}")
            return render(
                request,
                "charts/error.html",
                {"error": f"Failed to import generator module: {e}"},
            )
        except AttributeError as e:
            logger.error(f"Generator function not found: {e}")
            return render(
                request,
                "charts/error.html",
                {"error": f"Generator function not found: {e}"},
            )

        # Prepare data for the generator
        individuals_data = gedcom_file.parsed_data.get("individuals", {})
        families_data = gedcom_file.parsed_data.get("families", {})

        # Generate the family tree
        try:
            result = generator_function(
                individual_id,
                individuals_data,
                families_data,
                template_config["filename"],
            )

            if result.get("status") == "success":
                # Return the generated file
                file_content = result.get("file_content")
                if file_content:
                    response = HttpResponse(
                        file_content, content_type="application/pdf"
                    )
                    response["Content-Disposition"] = (
                        f'attachment; filename="{template_config["filename"]}"'
                    )
                    return response
                else:
                    return render(
                        request,
                        "charts/error.html",
                        {"error": "Failed to generate chart: No file content"},
                    )
            else:
                return render(
                    request,
                    "charts/error.html",
                    {"error": f"Failed to generate chart: {result.get('error')}"},
                )
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return render(
                request, "charts/error.html", {"error": f"Error generating chart: {e}"}
            )

    except GedcomFile.DoesNotExist:
        return render(request, "charts/error.html", {"error": "GEDCOM file not found"})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return render(request, "charts/error.html", {"error": f"Unexpected error: {e}"})


def chart_selection(request, file_id, individual_id):
    """
    View for selecting a chart template
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)

        if not gedcom_file.parsed_data:
            return render(
                request, "charts/error.html", {"error": "File not processed yet"}
            )

        # Get the selected individual
        individuals = gedcom_file.parsed_data.get("individuals", {})
        if individual_id not in individuals:
            return render(
                request, "charts/error.html", {"error": "Individual not found"}
            )

        individual = individuals[individual_id]
        if isinstance(individual, dict):
            individual = PersonData(**individual)
        elif not isinstance(individual, PersonData):
            # Convert to PersonData if it's not already
            individual = PersonData(**individual.__dict__)

        # Get template ID from session or use default
        template_id = request.session.get("selected_template", "4")

        return render(
            request,
            "charts/generate_chart.html",
            {
                "gedcom_file_id": file_id,
                "individual": individual,
                "individuals": individuals.values(),
                "template_id": template_id,
                "TEMPLATE_MAPPING": get_template_mapping(),
            },
        )

    except GedcomFile.DoesNotExist:
        return render(request, "charts/error.html", {"error": "GEDCOM file not found"})
    except Exception as e:
        return render(request, "charts/error.html", {"error": f"Unexpected error: {e}"})
