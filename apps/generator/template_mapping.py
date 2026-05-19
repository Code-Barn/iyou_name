"""
Centralized template mapping for the Family Tree Generator.

This module provides a single source of truth for all available
family tree templates in the application.
"""

from django.conf import settings


def get_template_mapping():
    """
    Returns a dictionary mapping template IDs to their configuration.

    Each template configuration includes:
    - module: The Python module containing the generator function
    - function: The function name to call for generation
    - filename: The default output filename pattern
    - name: Human-readable name for the template

    Returns:
        dict: Template mapping dictionary
    """
    templates_dir = settings.BASE_DIR / "staticfiles" / "charts" / "images" / "base_image_templates"
    return {
        "1": {
            "module": "apps.generator.utils.prototype.prototype_image_1generator",
            "function": "generate_prototype_1gen_preview",
            "filename": str(templates_dir / "US_LETTER_1GEN_BW.pdf"),
            "name": "1 Generation (Individual Only)",
            "template_type": "final",
        },
        "2": {
            "module": "apps.generator.utils.prototype.prototype_image_2generator",
            "function": "generate_prototype_2gen_preview",
            "filename": str(templates_dir / "US_LETTER_2GEN_BW.pdf"),
            "name": "2 Generation Chart",
            "template_type": "final",
        },
        "3": {
            "module": "apps.generator.utils.prototype.prototype_image_3generator",
            "function": "generate_prototype_3gen_preview",
            "filename": str(templates_dir / "US_LETTER_3GEN_BW.pdf"),
            "name": "3 Generation Chart",
            "template_type": "final",
        },
        "4": {
            "module": "apps.generator.utils.prototype.prototype_image_4generator",
            "function": "generate_prototype_4gen_preview",
            "filename": str(templates_dir / "US_LETTER_4GEN_BW.pdf"),
            "name": "4 Generation Chart",
            "template_type": "final",
        },
        "5": {
            "module": "apps.generator.utils.prototype.prototype_image_5generator",
            "function": "generate_prototype_5gen_preview",
            "filename": str(templates_dir / "US_LETTER_5GEN_BW.pdf"),
            "name": "5 Generation Chart",
            "template_type": "final",
        },
        "6": {
            "module": "apps.generator.utils.prototype.prototype_image_6generator",
            "function": "generate_prototype_6gen_preview",
            "filename": str(templates_dir / "US_LETTER_6GEN_BW.pdf"),
            "name": "6 Generation Chart",
            "template_type": "final",
        },
        "7": {
            "module": "apps.generator.utils.prototype.prototype_image_7generator",
            "function": "generate_prototype_7gen_preview",
            "filename": str(templates_dir / "US_LETTER_7GEN_BW.pdf"),
            "name": "7 Generation Chart",
            "template_type": "final",
        },
    }
