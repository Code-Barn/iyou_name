from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from apps.generator.models import GedcomFile
from apps.parser.models import PersonData


def select_individual(request, file_id):
    """
    Unified view for selecting an individual from the GEDCOM file
    This replaces both the dropdown and full-page selection views
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)

        # Check if user has access to this file
        if gedcom_file.user and gedcom_file.user != request.user:
            return HttpResponse(b"Unauthorized", status=403)

        if not gedcom_file.parsed_data:
            return render(
                request, "selector/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})

        # Convert dictionaries to PersonData objects
        processed_individuals = []
        for ind_id, individual in individuals.items():
            if isinstance(individual, dict):
                person = PersonData(**individual)
                processed_individuals.append(person)
            else:
                # Ensure that non-dict individuals are PersonData objects
                if isinstance(individual, PersonData):
                    processed_individuals.append(individual)
                else:
                    # Convert to PersonData if it's not already
                    person = PersonData(**individual.__dict__)
                    processed_individuals.append(person)

        # Store the file ID in session for subsequent steps
        request.session["current_gedcom_file_id"] = gedcom_file.id

        return render(
            request,
            "selector/select_individual.html",
            {
                "individuals": processed_individuals,
                "gedcom_file": gedcom_file,
                "is_logged_in": request.user.is_authenticated
                if request.user
                else False,
            },
        )

    except GedcomFile.DoesNotExist:
        return render(
            request, "selector/error.html", {"error": "GEDCOM file not found"}
        )


@csrf_protect
@require_POST
def confirm_selection(request, file_id):
    """
    Handle the confirmation of individual selection
    """
    if request.method == "POST":
        individual_id = request.POST.get("individual_id")
        action = request.POST.get("action")  # "set_home" or "generate"

        try:
            gedcom_file = GedcomFile.objects.get(id=file_id)

            # Check if user has access to this file
            if gedcom_file.user and gedcom_file.user != request.user:
                return HttpResponse(b"Unauthorized", status=403)

            if action == "set_home":
                # Get individual name for storage
                individuals = gedcom_file.parsed_data.get("individuals", {})
                individual_data = individuals.get(individual_id, {})
                individual_name = individual_data.get("full_name", "Unknown")

                # Compute gedcom_hash from filename
                import hashlib

                gedcom_hash = hashlib.sha256(gedcom_file.file.name.encode()).hexdigest()

                # Set home person in GedcomFile (for navigation)
                gedcom_file.home_person_id = individual_id
                gedcom_file.save()

                # Also sync to chart_storage IndividualSettings
                if request.user and request.user.is_authenticated:
                    from apps.chart_storage.models import IndividualSettings

                    # Unset any existing home person first
                    IndividualSettings.objects.filter(
                        user=request.user, gedcom_hash=gedcom_hash, is_home_person=True
                    ).update(is_home_person=False)

                    # Create/update IndividualSettings for this person
                    # Don't set settings_json yet - just mark as home person
                    settings, created = IndividualSettings.objects.get_or_create(
                        user=request.user,
                        gedcom_hash=gedcom_hash,
                        individual_id=individual_id,
                        defaults={
                            "gedcom_name": gedcom_file.file.name,
                            "individual_name": individual_name,
                            "settings_json": {},
                            "is_home_person": True,
                        },
                    )
                    if not created:
                        settings.is_home_person = True
                        settings.save()

                if request.user and request.user.is_authenticated:
                    return redirect("users:profile")
                else:
                    return redirect("upload:home")

            elif action == "generate":
                # Store selected individual in session and go to HUD
                request.session["selected_individual_id"] = individual_id
                return redirect("hud:display_tree")

        except GedcomFile.DoesNotExist:
            return render(
                request, "selector/error.html", {"error": "GEDCOM file not found"}
            )

    return redirect("selector:select_individual", file_id=file_id)
