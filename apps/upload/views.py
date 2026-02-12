import logging
import os
import mimetypes

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from apps.core.rate_limiting import upload_rate_limit, auth_rate_limit
from apps.core.file_validation import validate_uploaded_file
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


@csrf_protect
@upload_rate_limit
def upload_and_generate(request):
    """
    View for handling the main upload and generate workflow.
    """
    if request.method == "POST" and "gedcom_file" in request.FILES:
        gedcom_file = request.FILES["gedcom_file"]

        # Validate file size before processing
        max_file_size = getattr(
            settings, "MAX_FILE_SIZE", 50 * 1024 * 1024
        )  # 50MB default
        if gedcom_file.size > max_file_size:
            logger.warning(
                f"File size validation failed: {gedcom_file.size} bytes exceeds {max_file_size} bytes"
            )
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"File size exceeds maximum allowed size of {max_file_size // (1024 * 1024)}MB",
                },
                status=413,
            )

        # Validate file type
        allowed_types = [".ged", ".gedcom"]
        file_ext = os.path.splitext(gedcom_file.name)[1].lower()
        if file_ext not in allowed_types:
            logger.warning(f"Invalid file type uploaded: {gedcom_file.name}")
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
                },
                status=400,
            )

        # Additional MIME type check
        mime_type, _ = mimetypes.guess_type(gedcom_file.name)
        if mime_type and not mime_type.startswith("text/"):
            logger.warning(
                f"Suspicious MIME type detected: {mime_type} for file {gedcom_file.name}"
            )
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Invalid file format. Only text-based GEDCOM files are allowed.",
                },
                status=400,
            )

        try:
            # Read file content once for parsing
            gedcom_content_bytes = gedcom_file.read()
            logger.info(
                f"Processing uploaded file: {gedcom_file.name} ({len(gedcom_content_bytes)} bytes)"
            )

            # Validate file content for malicious patterns and GEDCOM structure
            is_valid, error_message = validate_uploaded_file(
                gedcom_content_bytes, gedcom_file.name
            )
            if not is_valid:
                logger.warning(
                    f"File validation failed for {gedcom_file.name}: {error_message}"
                )
                return JsonResponse(
                    {"status": "error", "message": f"Invalid file: {error_message}"},
                    status=400,
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
                logger.error(f"Error converting file {gedcom_file.name} to UTF-8: {e}")
                raise

            try:
                family_data = parse_gedcom_data(gedcom_content)
            except Exception as e:
                logger.error(f"Error parsing GEDCOM data from {gedcom_file.name}: {e}")
                raise

            # Validate parsed data structure
            if not isinstance(family_data.get("individuals"), dict):
                logger.error(f"Invalid parsed data structure from {gedcom_file.name}")
                raise ValueError(
                    "Invalid GEDCOM file structure: individuals data is malformed"
                )

            # Store parsed data in GedcomFile model
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
            gedcom_model.last_activity = timezone.now()
            gedcom_model.save()

            # Store reference to the processed file in session
            request.session["current_gedcom_file_id"] = gedcom_model.id
            request.session["selected_template"] = "4"  # Default template

            logger.info(f"Successfully processed GEDCOM file: {gedcom_file.name}")
            return redirect("selector:select_individual", file_id=gedcom_model.id)

        except Exception as e:
            logger.error(f"Error processing GEDCOM file {gedcom_file.name}: {e}")
            return render(
                request,
                "upload/error.html",
                {
                    "error": "Failed to process GEDCOM file. Please ensure the file is valid."
                },
            )

    # Handle GET requests or non-file uploads
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
        logger.info(
            f"User selected GEDCOM file: {gedcom_file.file.name} (ID: {file_id})"
        )
        return redirect("selector:select_individual", file_id=gedcom_file.id)
    except GedcomFile.DoesNotExist:
        logger.warning(f"Attempted to access non-existent GEDCOM file ID: {file_id}")
        return HttpResponse("File not found", status=404)
    except Exception as e:
        logger.error(f"Error selecting GEDCOM file {file_id}: {e}")
        return HttpResponse("Server error", status=500)


def set_current_gedcom_file(request, file_id):
    """
    View for setting the current GEDCOM file in the session and redirecting to select_individual
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
        request.session["current_gedcom_file_id"] = gedcom_file.id
        logger.info(f"Set current GEDCOM file: {gedcom_file.file.name} (ID: {file_id})")
        return redirect("selector:select_individual", file_id=gedcom_file.id)
    except GedcomFile.DoesNotExist:
        logger.warning(f"Attempted to set non-existent GEDCOM file ID: {file_id}")
        return HttpResponse("File not found", status=404)
    except Exception as e:
        logger.error(f"Error setting current GEDCOM file {file_id}: {e}")
        return HttpResponse("Server error", status=500)


@csrf_protect
@require_POST
@upload_rate_limit
def delete_anonymous_file(request):
    """
    Delete an anonymous user's GEDCOM file with proper authorization checks
    """
    file_id = request.POST.get("file_id")
    if not file_id:
        logger.warning("Delete file request missing file_id parameter")
        return JsonResponse(
            {"status": "error", "message": "File ID not provided"}, status=400
        )

    try:
        gedcom_file = GedcomFile.objects.get(id=file_id, user=None)

        # Additional security: verify this file is associated with the current session
        session_file_id = request.session.get("current_gedcom_file_id")
        if session_file_id != int(file_id):
            logger.warning(
                f"Unauthorized delete attempt for file ID {file_id} by session {request.session.session_key}"
            )
            return JsonResponse(
                {"status": "error", "message": "Unauthorized"}, status=403
            )

        file_name = gedcom_file.file.name
        gedcom_file.delete()
        logger.info(f"Deleted anonymous GEDCOM file: {file_name} (ID: {file_id})")

        # Clear from session if it was the current file
        if session_file_id == int(file_id):
            request.session.pop("current_gedcom_file_id", None)

        return JsonResponse({"status": "success"})

    except GedcomFile.DoesNotExist:
        logger.warning(f"Attempted to delete non-existent anonymous file ID: {file_id}")
        return JsonResponse(
            {"status": "error", "message": "File not found"}, status=404
        )
    except Exception as e:
        logger.error(f"Error deleting anonymous file {file_id}: {e}")
        return JsonResponse({"status": "error", "message": "Server error"}, status=500)
