"""
File access permission system for GEDCOM files.
Provides centralized permission checking for file access operations.
"""

import logging
from typing import Optional
from django.db import models
from django.http import Http404
from django.contrib.auth.models import User

from apps.generator.models import GedcomFile

logger = logging.getLogger(__name__)


class FileAccessError(Exception):
    """Exception raised when file access is denied."""

    def __init__(self, message, status=403):
        self.message = message
        self.status = status
        super().__init__(self.message)


def can_access_file(user: Optional[User], gedcom_file: GedcomFile) -> bool:
    """
    Check if a user can access a GEDCOM file.

    Args:
        user: The user attempting to access the file (can be None for anonymous)
        gedcom_file: The GedcomFile object being accessed

    Returns:
        True if access is allowed, False otherwise
    """
    if gedcom_file.user is None:
        return True

    if user is None:
        return False

    if not user.is_authenticated:
        return False

    return gedcom_file.user.id == user.id


def can_delete_file(user: Optional[User], gedcom_file: GedcomFile) -> bool:
    """
    Check if a user can delete a GEDCOM file.

    Only the file owner can delete their files.

    Args:
        user: The user attempting to delete the file
        gedcom_file: The GedcomFile object being deleted

    Returns:
        True if deletion is allowed, False otherwise
    """
    if gedcom_file.user is None:
        return True

    if user is None or not user.is_authenticated:
        return False

    return gedcom_file.user.id == user.id


def can_modify_file(user: Optional[User], gedcom_file: GedcomFile) -> bool:
    """
    Check if a user can modify a GEDCOM file's settings/data.

    Only the file owner can modify.

    Args:
        user: The user attempting to modify the file
        gedcom_file: The GedcomFile object being modified

    Returns:
        True if modification is allowed, False otherwise
    """
    if gedcom_file.user is None:
        return True

    if user is None or not user.is_authenticated:
        return False

    return gedcom_file.user.id == user.id


def get_file_or_404(file_id: int, user=None) -> GedcomFile:
    """
    Get a GEDCOM file and check permissions.

    Args:
        file_id: The ID of the file to retrieve
        user: The user requesting the file (optional)

    Returns:
        The GedcomFile if access is allowed

    Raises:
        Http404: If file doesn't exist or access is denied
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
    except GedcomFile.DoesNotExist:
        logger.warning(f"File not found: ID {file_id}")
        raise Http404("File not found")

    if not can_access_file(user, gedcom_file):
        logger.warning(
            f"Unauthorized access attempt for file {file_id}",
            extra={
                "file_id": file_id,
                "user_id": user.id if user and user.is_authenticated else None,
            },
        )
        raise Http404("File not found")

    return gedcom_file


def get_owned_file_or_404(file_id: int, user) -> GedcomFile:
    """
    Get a user-owned GEDCOM file.

    Only works for authenticated users and their own files.

    Args:
        file_id: The ID of the file to retrieve
        user: The authenticated user requesting the file

    Returns:
        The GedcomFile if it belongs to the user

    Raises:
        Http404: If file doesn't exist or doesn't belong to user
    """
    if not user or not user.is_authenticated:
        logger.warning("Attempt to access owned file without authentication")
        raise Http404("File not found")

    try:
        gedcom_file = GedcomFile.objects.get(id=file_id, user=user)
    except GedcomFile.DoesNotExist:
        logger.warning(
            f"File not found or not owned by user: ID {file_id}, user {user.id}"
        )
        raise Http404("File not found")

    return gedcom_file


def get_anonymous_file_or_404(file_id: int) -> GedcomFile:
    """
    Get an anonymous (public) GEDCOM file.

    Args:
        file_id: The ID of the file to retrieve

    Returns:
        The GedcomFile if it's anonymous

    Raises:
        Http404: If file doesn't exist or is not anonymous
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id, user=None)
    except GedcomFile.DoesNotExist:
        logger.warning(f"Anonymous file not found: ID {file_id}")
        raise Http404("File not found")

    return gedcom_file


def check_file_access(file_id: int, user=None, action: str = "view") -> bool:
    """
    Check if user can perform action on file.

    Args:
        file_id: The ID of the file
        user: The user attempting the action
        action: The action ('view', 'delete', 'modify')

    Returns:
        True if allowed, False otherwise
    """
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
    except GedcomFile.DoesNotExist:
        return False

    if action == "delete":
        return can_delete_file(user, gedcom_file)
    elif action == "modify":
        return can_modify_file(user, gedcom_file)
    else:
        return can_access_file(user, gedcom_file)


def get_accessible_files(user) -> list:
    """
    Get all files accessible to a user.

    For authenticated users: returns their files plus any anonymous files.
    For anonymous users: returns only anonymous files.

    Args:
        user: The user (can be None for anonymous)

    Returns:
        QuerySet of accessible GedcomFile objects
    """
    if user and user.is_authenticated:
        return GedcomFile.objects.filter(
            models.Q(user=user) | models.Q(user=None)
        ).order_by("-uploaded_at")
    else:
        return GedcomFile.objects.filter(user=None).order_by("-uploaded_at")
