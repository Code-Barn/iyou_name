import logging

from django.shortcuts import redirect, render

from apps.generator.models import GedcomFile
from apps.parser.models import PersonData

# Configure logger
logger = logging.getLogger(__name__)


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
        logger.debug(f"Retrieved GEDCOM file: {gedcom_file_id}")
        logger.debug(f"parsed_data exists: {gedcom_file.parsed_data is not None}")
        if gedcom_file.parsed_data:
            logger.debug(f"parsed_data keys: {list(gedcom_file.parsed_data.keys())}")
            logger.debug(
                f"'individuals' key exists: {'individuals' in gedcom_file.parsed_data}"
            )

        if not gedcom_file.parsed_data:
            logger.error("parsed_data is None")
            return render(
                request, "browse/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})
        logger.debug(f"Number of individuals: {len(individuals)}")
        logger.debug(
            f"First individual: {list(individuals.items())[0] if individuals else 'None'}"
        )

        # Convert dictionaries to PersonData objects
        processed_individuals = []
        for ind_id, individual in individuals.items():
            logger.debug(f"Processing individual {ind_id}: {type(individual)}")
            if isinstance(individual, dict):
                person = PersonData(**individual)
                processed_individuals.append(person)
                logger.debug(f"Created PersonData for {ind_id}: {person.full_name}")
            else:
                processed_individuals.append(individual)
                logger.debug(
                    f"Using existing PersonData for {ind_id}: {individual.full_name}"
                )
        return render(
            request,
            "browse/browse_individuals.html",
            {"individuals": processed_individuals},
        )

    except GedcomFile.DoesNotExist:
        return render(request, "browse/error.html", {"error": "GEDCOM file not found"})


def select_individual(request):
    """
    View for selecting an individual from the GEDCOM file
    This now redirects to the unified selector
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return render(
            request, "browse/error.html", {"error": "No GEDCOM file selected"}
        )

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        return redirect("selector:select_individual", file_id=gedcom_file.id)
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
        logger.debug(f"Retrieved GEDCOM file: {gedcom_file_id}")
        logger.debug(f"parsed_data exists: {gedcom_file.parsed_data is not None}")
        if gedcom_file.parsed_data:
            logger.debug(f"parsed_data keys: {list(gedcom_file.parsed_data.keys())}")
            logger.debug(
                f"'individuals' key exists: {'individuals' in gedcom_file.parsed_data}"
            )

        if not gedcom_file.parsed_data:
            logger.error("parsed_data is None")
            return render(
                request, "browse/error.html", {"error": "File not processed yet"}
            )

        individuals = gedcom_file.parsed_data.get("individuals", {})
        logger.debug(f"Looking for individual: {ind_id}")
        logger.debug(f"Available individuals: {list(individuals.keys())}")

        if ind_id not in individuals:
            logger.error(f"Individual {ind_id} not found in individuals")
            return render(
                request, "browse/error.html", {"error": "Individual not found"}
            )

        individual_data = individuals[ind_id]
        logger.debug(f"Individual data type: {type(individual_data)}")
        if isinstance(individual_data, dict):
            individual = PersonData(**individual_data)
            logger.debug(f"Created PersonData for {ind_id}: {individual.full_name}")
        else:
            individual = individual_data
            logger.debug(
                f"Using existing PersonData for {ind_id}: {individual.full_name}"
            )
        return render(
            request,
            "browse/individual_detail.html",
            {"individual": individual, "file_id": gedcom_file_id},
        )

    except GedcomFile.DoesNotExist:
        return render(request, "browse/error.html", {"error": "GEDCOM file not found"})
