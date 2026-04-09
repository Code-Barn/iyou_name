from django.conf import settings


def genealogy(request):
    """Add genealogy configuration to template context."""
    mode = getattr(settings, "GENEALOGY_MODE", "disabled")

    if mode == "grampsweb":
        genealogy_url = getattr(settings, "GRAMPSWEB_BASE_URL", "")
    elif mode == "webtrees":
        genealogy_url = getattr(settings, "WEBTREES_URL", "")
    elif mode == "external":
        genealogy_url = getattr(settings, "GENEALOGY_EXTERNAL_URL", "")
    else:
        genealogy_url = ""

    return {
        "genealogy_mode": mode,
        "genealogy_url": genealogy_url,
    }
