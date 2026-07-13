# apps/core/middleware.py

import logging
import time
from datetime import datetime, timedelta

from django.contrib.sessions.models import Session
from django.utils import timezone

from apps.core.auth_pkce import prune_expired_verifiers
from apps.generator.models import GedcomFile

logger = logging.getLogger(__name__)

PRUNE_INTERVAL = 300  # 5 minutes


class OIDCStatePruningMiddleware:
    """Prunes expired OIDC PKCE verifiers from the session at most every 5 minutes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session and not request.session.is_empty():
            last_prune = request.session.get("oidc_pruned_at", 0)
            if time.time() - last_prune > PRUNE_INTERVAL:
                count = prune_expired_verifiers(request.session)
                if count:
                    logger.debug("Pruned %d expired OIDC state(s)", count)
                request.session["oidc_pruned_at"] = int(time.time())
        response = self.get_response(request)
        return response


class SessionCleanupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_response(self, request, response):
        if hasattr(request, "user") and not request.user.is_authenticated:
            # Check if the session is about to expire
            if "current_gedcom_file_id" in request.session:
                # Delete anonymous GEDCOM files when the session expires
                self.cleanup_anonymous_files(request)
        return response

    def cleanup_anonymous_files(self, request):
        """Delete anonymous GEDCOM files associated with expired sessions."""
        try:
            file_id = request.session.get("current_gedcom_file_id")
            if file_id:
                # Delete the GEDCOM file if it exists and is anonymous
                gedcom_file = GedcomFile.objects.filter(id=file_id, user=None).first()
                if gedcom_file:
                    logger.info(f"Deleting anonymous GEDCOM file: {gedcom_file.id}")
                    gedcom_file.delete()
                    # Remove the file_id from the session
                    del request.session["current_gedcom_file_id"]
        except Exception as e:
            logger.error(f"Error cleaning up anonymous files: {e}")
            if request.session.get_expire_at_browser_close():
                file_id = request.session.get("current_gedcom_file_id")
                if file_id:
                    try:
                        gedcom_file = GedcomFile.objects.get(id=file_id, user=None)
                        gedcom_file.delete()
                    except GedcomFile.DoesNotExist:
                        pass
        return response
