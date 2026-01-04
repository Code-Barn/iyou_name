from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.generator.models import GedcomFile
from apps.generator.utils.gedcom_parser import PersonData


def browse_individuals(request):
    """
    View for browsing all individuals in the uploaded GEDCOM file
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return render(
            request, "browse/error.html", {"error": "No GEDCOM file selected"}
        )

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        if not gedcom_file.parsed_data:
            return render(
                request, "browse/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})
        return render(
            request,
            "browse/browse_individuals.html",
            {"individuals": individuals.values()},
        )

    except GedcomFile.DoesNotExist:
        return render(request, "browse/error.html", {"error": "GEDCOM file not found"})


def select_individual(request):
    """
    View for selecting an individual from the GEDCOM file
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return render(
            request, "browse/error.html", {"error": "No GEDCOM file selected"}
        )

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        if not gedcom_file.parsed_data:
            return render(
                request, "browse/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})
        return render(
            request,
            "browse/select_individual.html",
            {
                "individuals": individuals.values(),
                "template": request.session.get("selected_template", "4"),
            },
        )

    except GedcomFile.DoesNotExist:
        return render(request, "browse/error.html", {"error": "GEDCOM file not found"})


def individual_detail(request, ind_id):
    """
    View for displaying detailed information about an individual
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return render(
            request, "browse/error.html", {"error": "No GEDCOM file selected"}
        )

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        if not gedcom_file.parsed_data:
            return render(
                request, "browse/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})
        if ind_id not in individuals:
            return render(
                request, "browse/error.html", {"error": "Individual not found"}
            )

        individual = individuals[ind_id]
        return render(
            request, "browse/individual_detail.html", {"individual": individual}
        )

    except GedcomFile.DoesNotExist:
        return render(request, "browse/error.html", {"error": "GEDCOM file not found"})
