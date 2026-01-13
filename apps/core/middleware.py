# apps/core/middleware.py

from apps.generator.models import GedcomFile


class SessionCleanupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_response(self, request, response):
        if hasattr(request, "user") and not request.user.is_authenticated:
            # Check if the session is about to expire
            if request.session.get_expire_at_browser_close():
                file_id = request.session.get("current_gedcom_file_id")
                if file_id:
                    try:
                        gedcom_file = GedcomFile.objects.get(id=file_id, user=None)
                        gedcom_file.delete()
                    except GedcomFile.DoesNotExist:
                        pass
        return response
