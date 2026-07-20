import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from apps.chart_storage.models import UserStorageQuota, ChartBuffer

logger = logging.getLogger(__name__)


# ============================================================================
# Storage Management API
# ============================================================================


@login_required
@require_http_methods(["GET"])
def get_storage_usage(request):
    """Get storage usage for the current user."""
    quota, created = UserStorageQuota.objects.get_or_create(user=request.user)

    buffer_count = ChartBuffer.objects.filter(user=request.user).count()

    return JsonResponse(
        {
            "bytes_used": quota.bytes_used,
            "bytes_limit": quota.bytes_limit,
            "usage_percentage": quota.usage_percentage,
            "buffer_count": buffer_count,
        }
    )


@login_required
@csrf_protect
@require_http_methods(["POST"])
def clear_all_buffers(request):
    """Clear all cached buffers for the current user."""
    try:
        # Get all buffers for this user
        buffers = ChartBuffer.objects.filter(user=request.user)
        buffer_count = buffers.count()

        # Delete files
        for buffer in buffers:
            if buffer.buffer_file:
                buffer.buffer_file.delete()

        # Delete records and reset quota
        buffers.delete()

        quota = UserStorageQuota.objects.get(user=request.user)
        quota.bytes_used = 0
        quota.save()

        logger.info(f"User {request.user.username} cleared {buffer_count} buffers")

        return JsonResponse(
            {
                "success": True,
                "buffers_deleted": buffer_count,
            }
        )
    except Exception as e:
        logger.error(f"Error clearing buffers: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_buffer_list(request):
    """Get list of stored buffers."""
    gedcom_hash = request.GET.get("gedcom_hash")
    individual_id = request.GET.get("individual_id")

    buffers = ChartBuffer.objects.filter(user=request.user)

    if gedcom_hash:
        buffers = buffers.filter(gedcom_hash=gedcom_hash)
    if individual_id:
        buffers = buffers.filter(individual_id=individual_id)

    data = [
        {
            "id": b.id,
            "gedcom_hash": b.gedcom_hash,
            "individual_id": b.individual_id,
            "generation": b.generation,
            "settings_hash": b.settings_hash,
            "file_size": b.file_size,
            "created_at": b.created_at.isoformat(),
            "last_accessed": b.last_accessed.isoformat(),
        }
        for b in buffers
    ]

    return JsonResponse({"buffers": data})
