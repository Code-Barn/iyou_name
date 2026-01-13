import logging

from django.shortcuts import redirect

from apps.generator.template_mapping import get_template_mapping
from apps.upload.views import upload_and_generate

logger = logging.getLogger(__name__)

# Use the centralized template mapping
TEMPLATE_MAPPING = get_template_mapping()


def home(request):
    """
    View for the home page.
    """
    if request.method == "POST" and "gedcom_file" in request.FILES:
        return upload_and_generate(request)

    if request.user.is_authenticated:
        return redirect("users:profile")
    else:
        # Check if anonymous user has a file in session
        if request.session.get("current_gedcom_file_id"):
            return redirect("browse:browse_individuals")
        else:
            return redirect("upload:upload_file")
