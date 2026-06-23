from django.conf import settings


def satellite_urls(request):
    """Expose ecosystem satellite URLs to all templates."""
    return {
        "idp_home_url": getattr(settings, "IDP_HOME_URL", "https://iyou.me"),
        "idp_home_ws_url": getattr(settings, "IDP_HOME_WS_URL", "wss://home.iyou.me:9001/"),
        "SOCIALFEED_URL": getattr(settings, "WUN_URL", "https://wun.iyou.me"),
        "POLY_URL": getattr(settings, "POLY_URL", "https://poly.iyou.me"),
        "HIVE_URL": getattr(settings, "HIVE_URL", "https://hive.iyou.me"),
    }


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
