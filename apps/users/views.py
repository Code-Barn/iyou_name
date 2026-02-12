import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from apps.generator.forms import RegisterForm
from apps.generator.models import GedcomFile

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


def user_login(request):
    """
    Custom login view
    """
    if request.user.is_authenticated:
        return redirect("upload:home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("upload:home")
    else:
        form = AuthenticationForm()

    return render(request, "users/auth/login.html", {"form": form})


@csrf_protect
@require_POST
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
