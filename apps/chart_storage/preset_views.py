import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from apps.chart_storage.models import (
    UserSettingsPreset,
    IndividualSettings,
    GedcomInfo,
    UserStorageQuota,
    ChartBuffer,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Settings Presets API
# ============================================================================


@login_required
@require_http_methods(["GET"])
def list_presets(request):
    """List all presets for the current user."""
    presets = UserSettingsPreset.objects.filter(user=request.user)
    data = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "is_default": p.is_default,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat(),
        }
        for p in presets
    ]
    return JsonResponse({"presets": data})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def create_preset(request):
    """Create a new preset."""
    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        description = data.get("description", "")
        settings_json = data.get("settings_json", {})

        if not name:
            return JsonResponse({"error": "Preset name is required"}, status=400)

        # Check if preset with same name exists
        if UserSettingsPreset.objects.filter(user=request.user, name=name).exists():
            return JsonResponse(
                {"error": "Preset with this name already exists"}, status=400
            )

        preset = UserSettingsPreset.objects.create(
            user=request.user,
            name=name,
            description=description,
            settings_json=settings_json,
        )

        return JsonResponse(
            {
                "id": preset.id,
                "name": preset.name,
                "description": preset.description,
                "is_default": preset.is_default,
                "created_at": preset.created_at.isoformat(),
            }
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error creating preset: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_preset(request, preset_id):
    """Get a specific preset."""
    try:
        preset = UserSettingsPreset.objects.get(id=preset_id, user=request.user)
        return JsonResponse(
            {
                "id": preset.id,
                "name": preset.name,
                "description": preset.description,
                "settings_json": preset.settings_json,
                "is_default": preset.is_default,
                "created_at": preset.created_at.isoformat(),
                "updated_at": preset.updated_at.isoformat(),
            }
        )
    except UserSettingsPreset.DoesNotExist:
        return JsonResponse({"error": "Preset not found"}, status=404)


@login_required
@csrf_protect
@require_http_methods(["PUT"])
def update_preset(request, preset_id):
    """Update a preset."""
    try:
        preset = UserSettingsPreset.objects.get(id=preset_id, user=request.user)
        data = json.loads(request.body)

        if "name" in data:
            new_name = data["name"].strip()
            # Check for duplicate name (excluding self)
            if (
                UserSettingsPreset.objects.filter(user=request.user, name=new_name)
                .exclude(id=preset_id)
                .exists()
            ):
                return JsonResponse(
                    {"error": "Preset with this name already exists"}, status=400
                )
            preset.name = new_name

        if "description" in data:
            preset.description = data["description"]

        if "settings_json" in data:
            preset.settings_json = data["settings_json"]

        if "is_default" in data:
            # If setting as default, unset other defaults
            if data["is_default"]:
                UserSettingsPreset.objects.filter(
                    user=request.user, is_default=True
                ).exclude(id=preset_id).update(is_default=False)
            preset.is_default = data["is_default"]

        preset.save()

        return JsonResponse(
            {
                "id": preset.id,
                "name": preset.name,
                "description": preset.description,
                "is_default": preset.is_default,
                "updated_at": preset.updated_at.isoformat(),
            }
        )
    except UserSettingsPreset.DoesNotExist:
        return JsonResponse({"error": "Preset not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error updating preset: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["DELETE"])
def delete_preset(request, preset_id):
    """Delete a preset."""
    try:
        preset = UserSettingsPreset.objects.get(id=preset_id, user=request.user)
        preset.delete()
        return JsonResponse({"success": True})
    except UserSettingsPreset.DoesNotExist:
        return JsonResponse({"error": "Preset not found"}, status=404)


@login_required
@require_http_methods(["POST"])
def set_default_preset(request, preset_id):
    """Set a preset as the default."""
    try:
        preset = UserSettingsPreset.objects.get(id=preset_id, user=request.user)

        # Unset all other defaults
        UserSettingsPreset.objects.filter(user=request.user, is_default=True).exclude(
            id=preset_id
        ).update(is_default=False)

        preset.is_default = True
        preset.save()

        return JsonResponse({"success": True, "is_default": True})
    except UserSettingsPreset.DoesNotExist:
        return JsonResponse({"error": "Preset not found"}, status=404)
