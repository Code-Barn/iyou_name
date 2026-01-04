from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render

from apps.generator.forms import RegisterForm
from apps.generator.models import GedcomFile


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
