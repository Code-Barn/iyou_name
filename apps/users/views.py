import hashlib
import logging
import os

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from apps.core.rate_limiting import auth_rate_limit, user_rate_limit, upload_rate_limit
from apps.core.auth_security import (
    check_login_security,
    record_authentication_result,
    get_client_ip,
    get_user_agent,
)
from apps.core.file_validation import validate_uploaded_file
from apps.generator.forms import RegisterForm
from apps.chart_storage.models import IndividualPhoto
from apps.generator.models import GedcomFile
from apps.parser.utils import convert_to_utf8, parse_gedcom_data

logger = logging.getLogger(__name__)


def profile(request):
    """
    View for user profile page
    """
    if not request.user.is_authenticated:
        return redirect("users:login")

    try:
        # Get user's uploaded files
        gedcom_files = GedcomFile.objects.filter(user=request.user).order_by(
            "-uploaded_at"
        )

        # Get current session file
        current_file_id = request.session.get("current_gedcom_file_id")
        current_file = None
        if current_file_id:
            try:
                current_file = GedcomFile.objects.get(
                    id=current_file_id, user=request.user
                )
            except GedcomFile.DoesNotExist:
                current_file_id = None
                request.session["current_gedcom_file_id"] = None

        return render(
            request,
            "users/profile.html",
            {
                "user": request.user,
                "gedcom_files": gedcom_files,
                "current_file": current_file,
            },
        )

    except Exception as e:
        return render(
            request, "users/error.html", {"error": f"Error loading profile: {str(e)}"}
        )


@csrf_protect
@auth_rate_limit
def register(request):
    """
    View for user registration
    """
    if request.user.is_authenticated:
        return redirect("upload:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("upload:home")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


@csrf_protect
@auth_rate_limit
def user_login(request):
    """
    Custom login view with security monitoring
    """
    if request.user.is_authenticated:
        return redirect("upload:home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            # Get client info for security monitoring
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)

            # Check security before authentication
            is_allowed, error_message = check_login_security(
                username, password, ip_address, user_agent
            )
            if not is_allowed:
                logger.warning(
                    f"Login blocked by security: {error_message} (user: {username}, IP: {ip_address})"
                )
                form.add_error(None, error_message)
                return render(request, "users/auth/login.html", {"form": form})

            # Attempt authentication
            user = authenticate(username=username, password=password)
            if user is not None:
                # Record successful login
                record_authentication_result(username, True, ip_address, user_agent)
                login(request, user)
                logger.info(f"User logged in: {username} from {ip_address}")
                return redirect("upload:home")
            else:
                # Record failed login attempt
                record_authentication_result(username, False, ip_address, user_agent)
                logger.warning(
                    f"Failed login attempt for user: {username} from {ip_address}"
                )
                form.add_error(None, "Invalid username or password")
    else:
        form = AuthenticationForm()

    return render(request, "users/auth/login.html", {"form": form})


@csrf_protect
@require_POST
@user_rate_limit(limit=20, window=60)
def delete_gedcom_file(request, file_id):
    """
    View for deleting a GEDCOM file
    """
    logger.info(
        f"Delete GEDCOM file requested",
        extra={
            "file_id": file_id,
            "user_id": request.user.id if request.user.is_authenticated else None,
        },
    )
    if not request.user.is_authenticated:
        logger.warning("User not authenticated")
        return JsonResponse({"error": "Not authenticated"}, status=401)

    try:
        logger.info(
            f"Attempting to delete GEDCOM file",
            extra={
                "file_id": file_id,
                "user_id": request.user.id if request.user.is_authenticated else None,
            },
        )
        # Retrieve the file and ensure it belongs to the current user
        gedcom_file = GedcomFile.objects.get(id=file_id)
        logger.info(
            f"Found GEDCOM file for deletion: {gedcom_file.file.name} (ID: {gedcom_file.id})"
        )

        # Verify the file belongs to the current user
        if gedcom_file.user != request.user:
            logger.warning(
                f"Unauthorized access attempt for file {gedcom_file.id}",
                extra={
                    "file_id": gedcom_file.id,
                    "user_id": request.user.id
                    if request.user.is_authenticated
                    else None,
                    "file_name": gedcom_file.file.name
                    if gedcom_file.file
                    else "unnamed",
                    "ip_address": request.META.get("REMOTE_ADDR", "unknown"),
                },
            )
            return HttpResponse("File not found", status=404)

        # Delete the file
        file_id_to_delete = gedcom_file.id
        file_name = gedcom_file.file.name if gedcom_file.file else "unnamed"
        gedcom_file.delete()
        logger.info(
            f"User {request.user.username} deleted GEDCOM file: {file_name} (ID: {file_id_to_delete})"
        )
        return redirect("users:profile")
    except GedcomFile.DoesNotExist:
        logger.error(f"GEDCOM file not found: {file_id}")
        return HttpResponse("File not found", status=404)
    except Exception as e:
        logger.error(f"Error deleting GEDCOM file {file_id}: {e}")
        return HttpResponse(f"Error deleting file: {e}", status=500)


def get_user_files(request):
    """
    API endpoint for getting user's uploaded files
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    try:
        user_files = GedcomFile.objects.filter(user=request.user).values(
            "id", "file", "uploaded_at", "is_processed"
        )
        return JsonResponse(list(user_files), safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_protect
@require_POST
@upload_rate_limit
def sync_gedcom_file(request, file_id):
    """
    Sync an existing GEDCOM file with a new version.
    Preserves:
    - All IndividualSettings (via gedcom_hash based on filename)
    - All ChartBuffers (via gedcom_hash)
    - The GedcomFile ID and user ownership

    Updates:
    - File content
    - Parsed data
    - processing_date
    - home_person_id (if still valid in new data)
    """
    logger.info(
        f"Sync GEDCOM file requested",
        extra={
            "file_id": file_id,
            "user_id": request.user.id if request.user.is_authenticated else None,
        },
    )

    if not request.user.is_authenticated:
        logger.warning("User not authenticated for sync")
        return JsonResponse({"error": "Not authenticated"}, status=401)

    if "gedcom_file" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    gedcom_file_obj = request.FILES["gedcom_file"]

    allowed_types = [".ged", ".gedcom"]
    file_ext = os.path.splitext(gedcom_file_obj.name)[1].lower()
    if file_ext not in allowed_types:
        return JsonResponse(
            {"error": f"Invalid file type. Allowed types: {', '.join(allowed_types)}"},
            status=400,
        )

    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
    except GedcomFile.DoesNotExist:
        logger.error(f"GEDCOM file not found for sync: {file_id}")
        return JsonResponse({"error": "File not found"}, status=404)

    if gedcom_file.user != request.user:
        logger.warning(
            f"Unauthorized sync attempt for file {gedcom_file.id} by user {request.user.id}"
        )
        return JsonResponse({"error": "File not found"}, status=404)

    existing_home_person_id = gedcom_file.home_person_id

    # Get old gedcom_hash before updating (short version for photo storage)
    old_gedcom_hash = (
        hashlib.sha256(gedcom_file.file.name.encode()).hexdigest()[:16]
        if gedcom_file.file
        else None
    )

    try:
        gedcom_content_bytes = gedcom_file_obj.read()
        logger.info(
            f"Syncing file: {gedcom_file_obj.name} ({len(gedcom_content_bytes)} bytes)"
        )

        is_valid, error_message = validate_uploaded_file(
            gedcom_content_bytes, gedcom_file_obj.name
        )
        if not is_valid:
            logger.warning(f"File validation failed for sync: {error_message}")
            return JsonResponse({"error": f"Invalid file: {error_message}"}, status=400)

        gedcom_content = convert_to_utf8(gedcom_content_bytes)
        family_data = parse_gedcom_data(gedcom_content)

        if not isinstance(family_data.get("individuals"), dict):
            return JsonResponse(
                {"error": "Invalid GEDCOM file structure"},
                status=400,
            )

        parsed_data = {
            "individuals": {
                ind_id: person.to_dict()
                for ind_id, person in family_data["individuals"].items()
            },
            "families": family_data.get("families", {}),
            "root_individuals": family_data.get("root_individuals", []),
        }

        gedcom_file.file.save(
            gedcom_file_obj.name, ContentFile(gedcom_content_bytes), save=True
        )
        gedcom_file.parsed_data = parsed_data
        gedcom_file.is_processed = True
        gedcom_file.processing_date = timezone.now()
        gedcom_file.last_activity = timezone.now()

        if (
            existing_home_person_id
            and existing_home_person_id in parsed_data["individuals"]
        ):
            gedcom_file.home_person_id = existing_home_person_id
        else:
            gedcom_file.home_person_id = (
                family_data["root_individuals"][0]
                if family_data["root_individuals"]
                else None
            )

        gedcom_file.save()

        # Update photo gedcom_hash if it changed
        if old_gedcom_hash and gedcom_file.file:
            new_gedcom_hash = hashlib.sha256(
                gedcom_file.file.name.encode()
            ).hexdigest()[:16]
            if old_gedcom_hash != new_gedcom_hash:
                IndividualPhoto.objects.filter(
                    user=request.user, gedcom_hash=old_gedcom_hash
                ).update(gedcom_hash=new_gedcom_hash)

        logger.info(
            f"Successfully synced GEDCOM file: {gedcom_file.file.name} (ID: {gedcom_file.id})"
        )

        return redirect("users:profile")

    except Exception as e:
        logger.error(f"Error syncing GEDCOM file {file_id}: {e}")
        return JsonResponse({"error": str(e)}, status=500)
