from django.conf import settings
from django.db import models


class UserStorageQuota(models.Model):
    """
    Tracks per-user storage usage for buffers.
    Default quota: 500MB per user.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="storage_quota"
    )
    bytes_used = models.PositiveBigIntegerField(default=0)
    bytes_limit = models.PositiveBigIntegerField(
        default=500 * 1024 * 1024  # 500MB default
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Storage Quota"
        verbose_name_plural = "User Storage Quotas"

    def __str__(self):
        return f"{self.user.username}: {self.bytes_used}/{self.bytes_limit} bytes"

    def can_store(self, size_bytes: int) -> bool:
        """Check if user can store additional bytes"""
        return (self.bytes_used + size_bytes) <= self.bytes_limit

    def add_usage(self, size_bytes: int) -> bool:
        """Add to used bytes if within quota. Returns success."""
        if self.can_store(size_bytes):
            self.bytes_used += size_bytes
            self.save(update_fields=["bytes_used", "updated_at"])
            return True
        return False

    def release_usage(self, size_bytes: int):
        """Release bytes from deleted buffer"""
        self.bytes_used = max(0, self.bytes_used - size_bytes)
        self.save(update_fields=["bytes_used", "updated_at"])

    @property
    def usage_percentage(self) -> float:
        if self.bytes_limit == 0:
            return 0.0
        return (self.bytes_used / self.bytes_limit) * 100


class UserSettingsPreset(models.Model):
    """
    Named preset configurations that users can save and recall.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settings_presets",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    settings_json = models.JSONField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "name"]
        unique_together = ["user", "name"]

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class GedcomInfo(models.Model):
    """
    Metadata about uploaded gedcom files.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gedcom_files"
    )
    gedcom_hash = models.CharField(max_length=64, unique=True)
    filename = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    individual_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-last_accessed"]

    def __str__(self):
        return f"{self.display_name} ({self.user.username})"


class IndividualSettings(models.Model):
    """
    Settings associated with a specific individual within a gedcom file.

    Key: {gedcom_hash}:{individual_id}
    - gedcom_hash: SHA256 of gedcom filename (not contents)
    - individual_id: The gedcom-level ID (e.g., @I1@)

    This ensures:
    - Same person in different gedcom files = different settings
    - Same gedcom re-uploaded = settings preserved
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="individual_settings",
    )
    gedcom_hash = models.CharField(max_length=64)
    gedcom_name = models.CharField(max_length=255)
    individual_id = models.CharField(max_length=100)
    individual_name = models.CharField(max_length=255)
    settings_json = models.JSONField()
    is_home_person = models.BooleanField(default=False)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Individual Settings"
        unique_together = ["user", "gedcom_hash", "individual_id"]
        indexes = [
            models.Index(fields=["user", "gedcom_hash"]),
            models.Index(fields=["user", "gedcom_hash", "is_home_person"]),
        ]

    def __str__(self):
        return f"{self.individual_name} ({self.gedcom_name})"


class ChartBuffer(models.Model):
    """
    Long-term stored chart buffer images.

    Cache key: {user_id}:{gedcom_hash}:{individual_id}:{generation}:{settings_hash}

    Invalidated when:
    - Settings change (settings_hash differs)
    - Chart algorithm changes (chart_version differs)
    - User deletes gedcom or individual
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chart_buffers"
    )
    gedcom_hash = models.CharField(max_length=64)
    individual_id = models.CharField(max_length=100)
    generation = models.PositiveSmallIntegerField()
    settings_hash = models.CharField(max_length=32)
    chart_version = models.CharField(max_length=16)
    buffer_file = models.FileField(upload_to="buffers/")
    file_size = models.PositiveIntegerField()
    width = models.PositiveIntegerField(default=1950)
    height = models.PositiveIntegerField(default=1950)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "gedcom_hash", "individual_id", "generation"]
        indexes = [
            models.Index(fields=["user", "gedcom_hash", "individual_id"]),
            models.Index(fields=["user", "last_accessed"]),
        ]

    def __str__(self):
        return f"{self.generation}gen for {self.individual_id}"


import os
import uuid


def user_photo_upload_path(instance, filename):
    """Generate user-specific upload path for individual photos."""
    ext = os.path.splitext(filename)[1].lower()
    unique_filename = f"photo{uuid.uuid4().hex[:8]}{ext}"
    short_hash = instance.gedcom_hash[:16]
    return f"photos/{instance.user.id}/{short_hash}/{instance.individual_id}/{unique_filename}"


class IndividualPhoto(models.Model):
    """
    Profile photo for a specific individual within a gedcom file.

    Key: {gedcom_hash}:{individual_id}
    - gedcom_hash: SHA256 of gedcom filename (not contents)
    - individual_id: The gedcom-level ID (e.g., @I1@)
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="individual_photos",
    )
    gedcom_hash = models.CharField(max_length=64)
    gedcom_name = models.CharField(max_length=255)
    individual_id = models.CharField(max_length=100)
    individual_name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to=user_photo_upload_path, max_length=255)
    file_size = models.PositiveIntegerField()
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Individual Photos"
        unique_together = ["user", "gedcom_hash", "individual_id"]
        indexes = [
            models.Index(fields=["user", "gedcom_hash"]),
        ]

    def __str__(self):
        return f"Photo: {self.individual_name} ({self.gedcom_name})"
