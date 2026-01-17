import logging

from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.generator.models import GedcomFile
from apps.generator.template_mapping import get_template_mapping
from apps.parser.utils import convert_to_utf8, parse_gedcom_data

logger = logging.getLogger(__name__)

# Template mapping moved to HUD


def upload_file(request):
    """
    View for displaying the upload file form.
    """
    return render(
        request,
        "upload/upload_file.html",
        {"TEMPLATE_MAPPING": get_template_mapping()},
    )


def upload_and_generate(request):
    """
    View for handling the main upload and generate workflow.
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

            # Set the home person ID
            gedcom_model.home_person_id = (
                family_data["root_individuals"][0]
                if family_data["root_individuals"]
                else None
            )
            gedcom_model.is_processed = True
            gedcom_model.processing_date = timezone.now()
            gedcom_model.save()

            # Update last_activity to track when the file was last accessed
            gedcom_model.last_activity = timezone.now()
            gedcom_model.save()

            # Store reference to the processed file in session
            request.session["current_gedcom_file_id"] = gedcom_model.id
            request.session["selected_template"] = "4"  # Default template

            return redirect("selector:select_individual", file_id=gedcom_model.id)

        except Exception as e:
            logger.error(f"Error processing GEDCOM file: {e}")
            return render(request, "upload/error.html", {"error": str(e)})

    if request.user.is_authenticated:
        return redirect("users:profile")
    else:
        # Check if anonymous user has a file in session
        if request.session.get("current_gedcom_file_id"):
            return redirect("browse:browse_individuals")
        else:
            return render(
                request,
                "upload/upload_file.html",
                {"TEMPLATE_MAPPING": get_template_mapping()},
            )


def select_gedcom_file(request, file_id):
    """
    View for selecting a GEDCOM file from user's uploaded files
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
        request.session["current_gedcom_file_id"] = gedcom_file.id
        return redirect("selector:select_individual", file_id=gedcom_file.id)
    except GedcomFile.DoesNotExist:
        return HttpResponse("File not found", status=404)


def set_current_gedcom_file(request, file_id):
    """
    View for setting the current GEDCOM file in the session and redirecting to select_individual
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
        request.session["current_gedcom_file_id"] = gedcom_file.id
        return redirect("selector:select_individual", file_id=gedcom_file.id)
    except GedcomFile.DoesNotExist:
        return HttpResponse("File not found", status=404)


@require_POST
def delete_anonymous_file(request):
    file_id = request.POST.get("file_id")
    if not file_id:
        return JsonResponse(
            {"status": "error", "message": "File ID not provided"}, status=400
        )

    try:
        gedcom_file = GedcomFile.objects.get(id=file_id, user=None)
        gedcom_file.delete()
        return JsonResponse({"status": "success"})
    except GedcomFile.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "File not found"}, status=404
        )
