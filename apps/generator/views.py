import importlib
import json
import logging

from django.conf import settings
from django.contrib.auth import login
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

# Set up logging
logger = logging.getLogger(__name__)

from .forms import RegisterForm
from .models import GedcomFile, PersonData
from .utils.gedcom_parser import convert_to_utf8, parse_gedcom_data

logger.debug("STATICFILES_DIRS: %s", settings.STATICFILES_DIRS)
logger.debug("STATIC_ROOT: %s", settings.STATIC_ROOT)
logger.debug("STATIC_URL: %s", settings.STATIC_URL)

# Template mapping - kept here as it's used by multiple apps
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
    # Add more templates as you create them
    # '2': {...}, '3': {...}, etc.
}


# Helper functions that are used across multiple apps
def get_spouse_and_children(spouse_id, individual_id, individuals_dict, family):
    """
    Helper function to retrieve a spouse and their shared children.

    Args:
        spouse_id (str): The ID of the spouse.
        individual_id (str): The ID of the individual.
        individuals_dict (dict): Dictionary of all individuals.
        family (dict): Family data.
    """
    # Implementation kept for shared functionality
    pass


def preprocess_family_data(family_data):
    """
    Preprocess family data for consistent display across apps
    """
    # Implementation kept for shared functionality
    pass


# Utility functions that might be needed by other apps
def get_cached_family_data(request):
    """
    Get cached family data for the current session
    """
    gedcom_file_id = request.session.get("current_gedcom_file_id")
    if not gedcom_file_id:
        return None

    try:
        gedcom_file = GedcomFile.objects.get(id=gedcom_file_id)
        return gedcom_file.parsed_data
    except GedcomFile.DoesNotExist:
        return None


# The generator app now primarily serves as a utility/app coordination layer
# Most view functionality has been moved to the specific apps:
# - Upload functionality → apps/upload/
# - Browse functionality → apps/browse/
# - HUD functionality → apps/hud/
# - Chart generation → apps/charts/
# - User management → apps/users/
