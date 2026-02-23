import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from apps.chart_storage.models import IndividualSettings

logger = logging.getLogger(__name__)


# ============================================================================
# Individual Settings API
# ============================================================================


@login_required
@require_http_methods(["GET"])
def list_individual_settings(request):
    """List all individual settings for the current user."""
    gedcom_hash = request.GET.get("gedcom_hash")

    if gedcom_hash:
        settings = IndividualSettings.objects.filter(
            user=request.user, gedcom_hash=gedcom_hash
        )
    else:
        settings = IndividualSettings.objects.filter(user=request.user)

    data = [
        {
            "id": s.id,
            "gedcom_hash": s.gedcom_hash,
            "gedcom_name": s.gedcom_name,
            "individual_id": s.individual_id,
            "individual_name": s.individual_name,
            "is_home_person": s.is_home_person,
            "last_used": s.last_used.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in settings
    ]
    return JsonResponse({"individual_settings": data})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def save_individual_settings(request):
    """Save settings for a specific individual."""
    try:
        data = json.loads(request.body)
        gedcom_hash = data.get("gedcom_hash")
        gedcom_name = data.get("gedcom_name", "")
        individual_id = data.get("individual_id")
        individual_name = data.get("individual_name", "")
        settings_json = data.get("settings_json", {})

        if not gedcom_hash or not individual_id:
            return JsonResponse(
                {"error": "gedcom_hash and individual_id are required"}, status=400
            )

        # Try to get existing or create new
        individual_settings, created = IndividualSettings.objects.get_or_create(
            user=request.user,
            gedcom_hash=gedcom_hash,
            individual_id=individual_id,
            defaults={
                "gedcom_name": gedcom_name,
                "individual_name": individual_name,
                "settings_json": settings_json,
            },
        )

        if not created:
            # Update existing
            individual_settings.settings_json = settings_json
            if gedcom_name:
                individual_settings.gedcom_name = gedcom_name
            if individual_name:
                individual_settings.individual_name = individual_name
            individual_settings.save()

        return JsonResponse(
            {
                "id": individual_settings.id,
                "gedcom_hash": individual_settings.gedcom_hash,
                "individual_id": individual_settings.individual_id,
                "individual_name": individual_settings.individual_name,
                "is_home_person": individual_settings.is_home_person,
                "last_used": individual_settings.last_used.isoformat(),
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error saving individual settings: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_individual_settings(request, gedcom_hash, individual_id):
    """Get settings for a specific individual."""
    try:
        settings = IndividualSettings.objects.get(
            user=request.user, gedcom_hash=gedcom_hash, individual_id=individual_id
        )
        return JsonResponse(
            {
                "id": settings.id,
                "gedcom_hash": settings.gedcom_hash,
                "gedcom_name": settings.gedcom_name,
                "individual_id": settings.individual_id,
                "individual_name": settings.individual_name,
                "settings_json": settings.settings_json,
                "is_home_person": settings.is_home_person,
                "last_used": settings.last_used.isoformat(),
            }
        )
    except IndividualSettings.DoesNotExist:
        return JsonResponse({"settings_json": None})


@login_required
@csrf_protect
@require_http_methods(["DELETE"])
def delete_individual_settings(request, gedcom_hash, individual_id):
    """Delete settings for a specific individual."""
    try:
        settings = IndividualSettings.objects.get(
            user=request.user, gedcom_hash=gedcom_hash, individual_id=individual_id
        )
        settings.delete()
        return JsonResponse({"success": True})
    except IndividualSettings.DoesNotExist:
        return JsonResponse({"error": "Settings not found"}, status=404)


@login_required
@csrf_protect
@require_http_methods(["POST"])
def set_home_person(request):
    """Set an individual as the home person for a gedcom."""
    try:
        data = json.loads(request.body)
        gedcom_hash = data.get("gedcom_hash")
        individual_id = data.get("individual_id")
        individual_name = data.get("individual_name", "")

        if not gedcom_hash or not individual_id:
            return JsonResponse(
                {"error": "gedcom_hash and individual_id are required"}, status=400
            )

        # Unset any existing home person for this gedcom
        IndividualSettings.objects.filter(
            user=request.user, gedcom_hash=gedcom_hash, is_home_person=True
        ).update(is_home_person=False)

        # Set new home person
        settings, created = IndividualSettings.objects.get_or_create(
            user=request.user,
            gedcom_hash=gedcom_hash,
            individual_id=individual_id,
            defaults={
                "individual_name": individual_name,
                "settings_json": {},
                "is_home_person": True,
            },
        )

        if not created:
            settings.is_home_person = True
            settings.save()

        return JsonResponse({"success": True})
    except Exception as e:
        logger.error(f"Error setting home person: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_home_person(request, gedcom_hash):
    """Get the home person for a gedcom."""
    try:
        settings = IndividualSettings.objects.get(
            user=request.user, gedcom_hash=gedcom_hash, is_home_person=True
        )
        return JsonResponse(
            {
                "individual_id": settings.individual_id,
                "individual_name": settings.individual_name,
                "settings_json": settings.settings_json,
            }
        )
    except IndividualSettings.DoesNotExist:
        return JsonResponse({"individual_id": None})
