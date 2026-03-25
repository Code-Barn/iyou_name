"""
GrampsWeb API client for fetching genealogy data.

This module provides utilities for integrating with a GrampsWeb instance,
allowing namechart to fetch GEDCOM data and person information from GrampsWeb.
"""

import logging
from typing import Any, Dict, List, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class GrampsWebAPIError(Exception):
    """Exception raised when GrampsWeb API requests fail."""

    pass


class GrampsWebClient:
    """
    Client for interacting with the Gramps Web API.

    Usage:
        client = GrampsWebClient()
        gedcom_data = client.export_gedcom()
        person = client.get_person(handle)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_token: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = base_url or settings.GRAMPSWEB_API_URL
        self.api_token = api_token or settings.GRAMPSWEB_API_TOKEN
        self.timeout = timeout or settings.GRAMPSWEB_API_TIMEOUT
        self._session = None

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
            if self.api_token:
                self._session.headers.update(
                    {"Authorization": f"Bearer {self.api_token}"}
                )
        return self._session

    def _make_url(self, endpoint: str) -> str:
        base = self.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/api/{endpoint}"

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = self._make_url(endpoint)
        kwargs.setdefault("timeout", self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"GrampsWeb API error: {e}")
            raise GrampsWebAPIError(f"API request failed: {e}") from e

    def is_available(self) -> bool:
        """Check if GrampsWeb API is available and responding."""
        try:
            self._request("GET", "health")
            return True
        except GrampsWebAPIError:
            return False

    def get_person(self, handle: str) -> Dict[str, Any]:
        """Get a single person by their handle."""
        response = self._request("GET", f"people/{handle}")
        return response.json()

    def get_people(
        self, page: int = 1, pagesize: int = 100, keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get a page of people from the family tree.

        Args:
            page: Page number (1-indexed)
            pagesize: Number of results per page
            keys: List of keys to include in the response
        """
        params = {"page": page, "pagesize": pagesize}
        if keys:
            params["keys"] = ",".join(keys)

        response = self._request("GET", "people", params=params)
        return response.json()

    def get_person_families(self, handle: str) -> Dict[str, Any]:
        """Get all families associated with a person."""
        response = self._request("GET", f"people/{handle}/families")
        return response.json()

    def get_family(self, handle: str) -> Dict[str, Any]:
        """Get a single family by its handle."""
        response = self._request("GET", f"families/{handle}")
        return response.json()

    def search_people(self, query: str, page: int = 1) -> Dict[str, Any]:
        """
        Search for people matching a query.

        Args:
            query: Search query string
            page: Page number
        """
        params = {"query": query, "page": page}
        response = self._request("GET", "search", params=params)
        return response.json()

    def export_gedcom(self) -> bytes:
        """
        Export the entire family tree as a GEDCOM file.

        Returns:
            Raw GEDCOM file content as bytes.
        """
        response = self._request("POST", "exporters/gedcom/file")
        task_id = response.json().get("task")

        if not task_id:
            raise GrampsWebAPIError("No task ID returned from export request")

        return self._wait_for_export(task_id)

    def _wait_for_export(self, task_id: str, max_wait: int = 300) -> bytes:
        """
        Wait for an export task to complete and return the result.

        Args:
            task_id: The task ID to wait for
            max_wait: Maximum time to wait in seconds

        Returns:
            The exported file content
        """
        import time

        start_time = time.time()
        while time.time() - start_time < max_wait:
            status = self._request("GET", f"tasks/{task_id}").json()

            if status.get("status") == "success":
                download_url = self._make_url(
                    f"exporters/gedcom/file/processed/{status['result']['filename']}"
                )
                response = self.session.get(download_url, timeout=self.timeout)
                response.raise_for_status()
                return response.content

            if status.get("status") == "failure":
                raise GrampsWebAPIError(
                    f"Export task failed: {status.get('error', 'Unknown error')}"
                )

            time.sleep(2)

        raise GrampsWebAPIError("Export task timed out")

    def get_all_people(self, pagesize: int = 500) -> List[Dict[str, Any]]:
        """
        Generator that yields all people in the family tree.

        Args:
            pagesize: Number of results per page

        Yields:
            Individual person records
        """
        page = 1
        while True:
            data = self.get_people(page=page, pagesize=pagesize)
            people = data.get("data", [])

            if not people:
                break

            for person in people:
                yield person

            if page >= data.get("total_pages", 1):
                break

            page += 1

    def get_tree_info(self) -> Dict[str, Any]:
        """Get information about the current tree."""
        response = self._request("GET", "metadata")
        return response.json()


def get_client() -> Optional[GrampsWebClient]:
    """
    Get a configured GrampsWebClient instance if configuration is available.

    Returns:
        GrampsWebClient instance or None if not configured.
    """
    if not settings.GRAMPSWEB_API_URL:
        return None

    return GrampsWebClient()


def fetch_gedcom_from_grampsweb() -> Optional[bytes]:
    """
    Fetch GEDCOM data from GrampsWeb and return raw bytes.

    This is a convenience function for syncing data from GrampsWeb.

    Returns:
        Raw GEDCOM file content or None if not configured/unavailable.
    """
    client = get_client()
    if not client:
        logger.warning("GrampsWeb not configured")
        return None

    if not client.is_available():
        logger.warning("GrampsWeb API is not available")
        return None

    try:
        return client.export_gedcom()
    except GrampsWebAPIError as e:
        logger.error(f"Failed to fetch GEDCOM from GrampsWeb: {e}")
        return None
