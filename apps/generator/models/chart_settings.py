from django.contrib.auth.models import User
from django.db import models


class ChartSettings(models.Model):
    """
    Model to store tunable variables for the 1-generation family tree chart.
    These settings can be tied to a user's account or a session for logged-out users.
    """

    # User or session association
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    # Translation settings
    initial_translate_x = models.FloatField(default=0)
    initial_translate_y = models.FloatField(default=0)
    subject_translate_x = models.FloatField(default=0)
    subject_translate_y = models.FloatField(default=0)

    # Font settings
    font_family = models.CharField(max_length=100, default="Arial")
    primary_name_font_size = models.FloatField(default=113)
    primary_info_font_size = models.FloatField(default=113)

    # Stroke settings
    default_stroke_width = models.FloatField(default=0.5)
    stroke_antialias = models.BooleanField(default=True)

    # Color settings (stored as hex strings)
    primary_font_color = models.CharField(max_length=20, default="black")
    primary_birth_color = models.CharField(max_length=20, default="black")
    primary_place_color = models.CharField(max_length=20, default="black")
    primary_death_color = models.CharField(max_length=20, default="black")
    primary_stroke_color = models.CharField(max_length=20, default="black")

    # Primary individual coordinates
    primary_name_x = models.FloatField(default=0)
    primary_name_y = models.FloatField(default=0)
    primary_name_rotate = models.FloatField(default=-45)
    primary_birth_x = models.FloatField(default=0)
    primary_birth_y = models.FloatField(default=135)
    primary_birth_rotate = models.FloatField(default=45)
    primary_place_x = models.FloatField(default=0)
    primary_place_y = models.FloatField(default=90)
    primary_place_rotate = models.FloatField(default=-45)

    def __str__(self):
        return f"ChartSettings for {self.user or self.session_key}"

    class Meta:
        verbose_name = "Chart Setting"
        verbose_name_plural = "Chart Settings"
