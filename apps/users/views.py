import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

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


def delete_gedcom_file(request, file_id):
    """
    View for deleting a GEDCOM file
    """
    print(f"delete_gedcom_file called with file_id: {file_id}")
    if not request.user.is_authenticated:
        print("User not authenticated")
        return JsonResponse({"error": "Not authenticated"}, status=401)

    try:
        print(f"Attempting to delete GEDCOM file with ID: {file_id}")
        # Retrieve the file and ensure it belongs to the current user
        gedcom_file = GedcomFile.objects.get(id=file_id)
        print(f"Found GEDCOM file: {gedcom_file.id}, user: {gedcom_file.user}")

        # Verify the file belongs to the current user
        if gedcom_file.user != request.user:
            print(f"File {gedcom_file.id} does not belong to user {request.user}")
            return HttpResponse("File not found", status=404)

        # Delete the file
        file_id_to_delete = gedcom_file.id
        print(f"Before deletion - GEDCOM files count: {GedcomFile.objects.count()}")
        gedcom_file.delete()
        print(f"After deletion - GEDCOM files count: {GedcomFile.objects.count()}")
        print(f"GEDCOM file {file_id_to_delete} deleted successfully")
        return redirect("users:profile")
    except GedcomFile.DoesNotExist:
        print(f"GEDCOM file {file_id} not found")
        return HttpResponse("File not found", status=404)
    except Exception as e:
        print(f"Error deleting GEDCOM file {file_id}: {e}")
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
