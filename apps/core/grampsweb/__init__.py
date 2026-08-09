"""
GrampsWeb integration module.

This module provides utilities for integrating Namecharts (aka iyou_name) with a GrampsWeb instance,
allowing users to sync their genealogy data from GrampsWeb.
"""

from apps.core.grampsweb.client import (
    GrampsWebAPIError,
    GrampsWebClient,
    fetch_gedcom_from_grampsweb,
    get_client,
)

__all__ = [
    "GrampsWebAPIError",
    "GrampsWebClient",
    "fetch_gedcom_from_grampsweb",
    "get_client",
]
