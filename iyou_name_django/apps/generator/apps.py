from django.apps import AppConfig


class GeneratorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.generator"
    verbose_name = "Generator Application (Core Utility)"

    def ready(self):
        # Import and register any signals here
        pass
