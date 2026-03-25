from django.conf import settings


def grampsweb_url(request):
    """Add GrampsWeb URL to template context."""
    return {
        "grampsweb_url": getattr(settings, "GRAMPSWEB_BASE_URL", ""),
    }
