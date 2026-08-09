import hashlib
import logging
import uuid
from io import BytesIO

import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from PIL import Image

from apps.chart_storage.models import IndividualPhoto

logger = logging.getLogger(__name__)


def compute_gedcom_hash(gedcom_filename: str) -> str:
    """Compute SHA256 hash of gedcom filename."""
    return hashlib.sha256(gedcom_filename.encode()).hexdigest()


@login_required
@require_http_methods(["GET"])
def get_photo(request, gedcom_hash, individual_id):
    """Get photo for a specific individual."""
    try:
        photo = IndividualPhoto.objects.get(
            user=request.user, gedcom_hash=gedcom_hash, individual_id=individual_id
        )
        return JsonResponse(
            {
                "id": photo.id,
                "gedcom_hash": photo.gedcom_hash,
                "gedcom_name": photo.gedcom_name,
                "individual_id": photo.individual_id,
                "individual_name": photo.individual_name,
                "photo_url": photo.photo.url,
                "file_size": photo.file_size,
                "width": photo.width,
                "height": photo.height,
                "created_at": photo.created_at.isoformat(),
            }
        )
    except IndividualPhoto.DoesNotExist:
        return JsonResponse({"photo": None})


@login_required
@csrf_protect
@require_http_methods(["POST"])
def upload_photo(request):
    """Upload a photo for a specific individual."""
    try:
        gedcom_hash = request.POST.get("gedcom_hash")
        gedcom_name = request.POST.get("gedcom_name", "")
        individual_id = request.POST.get("individual_id")
        individual_name = request.POST.get("individual_name", "")
        photo_file = request.FILES.get("photo")
        photo_url = request.POST.get("photo_url")

        if not gedcom_hash or not individual_id:
            return JsonResponse(
                {"error": "gedcom_hash and individual_id are required"}, status=400
            )

        if not photo_file and not photo_url:
            return JsonResponse({"error": "No photo file or URL provided"}, status=400)

        # Delete existing photo if any
        IndividualPhoto.objects.filter(
            user=request.user, gedcom_hash=gedcom_hash, individual_id=individual_id
        ).delete()

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024

        if photo_url:
            # Handle URL upload
            try:
                response = requests.get(photo_url, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                return JsonResponse(
                    {"error": f"Failed to download image from URL: {str(e)}"},
                    status=400,
                )

            content_type = response.headers.get("content-type", "")
            allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if content_type not in allowed_types:
                return JsonResponse(
                    {
                        "error": "Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed."
                    },
                    status=400,
                )

            if len(response.content) > max_size:
                return JsonResponse(
                    {"error": "File too large. Maximum size is 10MB."}, status=400
                )

            # Determine file extension
            ext_map = {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/gif": ".gif",
                "image/webp": ".webp",
            }
            ext = ext_map.get(content_type, ".jpg")

            # Create a Django UploadedFile from the response content
            from django.core.files.uploadedfile import SimpleUploadedFile

            filename = f"photo{uuid.uuid4().hex[:8]}{ext}"
            photo_file = SimpleUploadedFile(
                filename, response.content, content_type=content_type
            )

            # Get image dimensions
            image = Image.open(BytesIO(response.content))
            width, height = image.size
            file_size = len(response.content)

        else:
            # Handle file upload
            allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if photo_file.content_type not in allowed_types:
                return JsonResponse(
                    {
                        "error": "Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed."
                    },
                    status=400,
                )

            if photo_file.size > max_size:
                return JsonResponse(
                    {"error": "File too large. Maximum size is 10MB."}, status=400
                )

            # Get image dimensions
            image = Image.open(photo_file)
            width, height = image.size
            file_size = photo_file.size

        # Create new photo
        photo = IndividualPhoto.objects.create(
            user=request.user,
            gedcom_hash=gedcom_hash,
            gedcom_name=gedcom_name,
            individual_id=individual_id,
            individual_name=individual_name,
            photo=photo_file,
            file_size=file_size,
            width=width,
            height=height,
        )

        return JsonResponse(
            {
                "id": photo.id,
                "gedcom_hash": photo.gedcom_hash,
                "gedcom_name": photo.gedcom_name,
                "individual_id": photo.individual_id,
                "individual_name": photo.individual_name,
                "photo_url": photo.photo.url,
                "file_size": photo.file_size,
                "width": photo.width,
                "height": photo.height,
                "created_at": photo.created_at.isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Error uploading photo: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_protect
@require_http_methods(["DELETE"])
def delete_photo(request, gedcom_hash, individual_id):
    """Delete photo for a specific individual."""
    try:
        photo = IndividualPhoto.objects.get(
            user=request.user, gedcom_hash=gedcom_hash, individual_id=individual_id
        )
        photo.delete()
        return JsonResponse({"success": True})
    except IndividualPhoto.DoesNotExist:
        return JsonResponse({"error": "Photo not found"}, status=404)
