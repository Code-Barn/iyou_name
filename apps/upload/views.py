import logging

from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

logger = logging.getLogger(__name__)
from apps.generator.models import GedcomFile
from apps.parser.models import PersonData
from apps.parser.utils import convert_to_utf8, parse_gedcom_data

# Template mapping
TEMPLATE_MAPPING = {
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


def upload_file(request):
    """
    View for displaying the upload file form.
    """
    return render(
        request,
        "upload/upload_file.html",
        {"TEMPLATE_MAPPING": TEMPLATE_MAPPING},
    )


def upload_and_generate(request):
    """
    View for handling the main upload and generate workflow
    """
    if request.method == "POST" and "gedcom_file" in request.FILES:
        gedcom_file = request.FILES["gedcom_file"]

        try:
            # Read the file content directly for parsing
            gedcom_content_bytes = gedcom_file.read()
            print(
                f"DEBUG: Read file content. Length: {len(gedcom_content_bytes)} bytes"
            )

            # Save the file
            gedcom_model = GedcomFile.objects.create(
                file=ContentFile(gedcom_content_bytes, name=gedcom_file.name),
                user=request.user if request.user.is_authenticated else None,
            )

            # Parse the GEDCOM data
            try:
                gedcom_content = convert_to_utf8(gedcom_content_bytes)
            except Exception as e:
                print(f"DEBUG: Error converting to UTF-8: {e}")
                raise

            try:
                family_data = parse_gedcom_data(gedcom_content)
            except Exception as e:
                print(f"DEBUG: Error parsing GEDCOM data: {e}")
                raise

            # Store parsed data directly in the GedcomFile model
            # Convert PersonData objects to dictionaries for JSONField
            # Ensure parsed_data has the correct structure
            if not isinstance(family_data.get("individuals"), dict):
                logger.error("family_data['individuals'] is not a dictionary")
                raise ValueError("family_data['individuals'] must be a dictionary")

            gedcom_model.parsed_data = {
                "individuals": {
                    ind_id: person.to_dict()
                    for ind_id, person in family_data["individuals"].items()
                },
                "families": family_data.get("families", {}),
                "root_individuals": family_data.get("root_individuals", []),
            }

            # Debug logging to verify parsed_data structure
            logger.debug(
                f"Stored parsed_data keys: {list(gedcom_model.parsed_data.keys())}"
            )
            logger.debug(
                f"Number of individuals: {len(gedcom_model.parsed_data['individuals'])}"
            )

            # Debug logging to verify parsed_data structure
            logger.debug(f"Stored parsed_data keys: {gedcom_model.parsed_data.keys()}")
            logger.debug(
                f"Number of individuals: {len(gedcom_model.parsed_data['individuals'])}"
            )
            gedcom_model.home_person_id = (
                family_data["root_individuals"][0]
                if family_data["root_individuals"]
                else None
            )
            gedcom_model.is_processed = True
            gedcom_model.processing_date = timezone.now()
            gedcom_model.save()

            # Store reference to the processed file in session
            request.session["current_gedcom_file_id"] = gedcom_model.id
            request.session["selected_template"] = "4"  # Default template

            individuals = list(family_data["individuals"].values())
            return render(
                request,
                "upload/select_individual.html",
                {
                    "individuals": individuals,
                    "template": "4",
                    "selected_template": request.session.get("selected_template", "4"),
                    "TEMPLATE_MAPPING": TEMPLATE_MAPPING,
                },
            )

        except Exception as e:
            logger.error(f"Error processing GEDCOM file: {e}")
            return render(request, "upload/error.html", {"error": str(e)})

    if request.user.is_authenticated:
        return redirect("users:profile")
    return render(
        request, "upload/upload_file.html", {"TEMPLATE_MAPPING": TEMPLATE_MAPPING}
    )


def select_gedcom_file(request, file_id):
    """
    View for selecting a GEDCOM file from user's uploaded files
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
        request.session["current_gedcom_file_id"] = gedcom_file.id
        return redirect("upload:home")
    except GedcomFile.DoesNotExist:
        return HttpResponse("File not found", status=404)


def set_current_gedcom_file(request, file_id):
    """
    View for setting the current GEDCOM file in the session and redirecting to select_individual
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
        request.session["current_gedcom_file_id"] = gedcom_file.id
        return redirect("browse:select_individual")
    except GedcomFile.DoesNotExist:
        return HttpResponse("File not found", status=404)


def delete_gedcom_file(request, file_id):
    """
    View for deleting a GEDCOM file
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
        gedcom_file.delete()
        return redirect("upload:home")
    except GedcomFile.DoesNotExist:
        return HttpResponse("File not found", status=404)
