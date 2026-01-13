# apps/generator/management/commands/cleanup_anonymous_files.py
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.generator.models import GedcomFile


class Command(BaseCommand):
    help = "Delete anonymous files older than 1 hour"

    def handle(self, *args, **options):
        one_hour_ago = timezone.now() - timedelta(hours=1)
        deleted_count, _ = GedcomFile.objects.filter(
            user=None, last_activity__lt=one_hour_ago
        ).delete()
        self.stdout.write(f"Deleted {deleted_count} inactive anonymous files.")
