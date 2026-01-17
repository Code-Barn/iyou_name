"""
Centralized template mapping for the Family Tree Generator.

This module provides a single source of truth for all available
family tree templates in the application.
"""


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
    return {
        "1": {
            "module": "apps.generator.utils.image_1generator",
            "function": "generate_family_tree",
            "filename": "/home/user/CODE_BASE/namechart/apps/charts/static/charts/images/base_image_templates/US_LETTER_1GEN_BW.pdf",
            "name": "1 Generation (Individual Only)",
        },
        "2": {
            "module": "apps.generator.utils.image_2generator",
            "function": "generate_family_tree",
            "filename": "/home/user/CODE_BASE/namechart/apps/charts/static/charts/images/base_image_templates/US_LETTER_2GEN_BW.pdf",
            "name": "2 Generation Chart",
        },
        "3": {
            "module": "apps.generator.utils.image_3generator",
            "function": "generate_family_tree",
            "filename": "/home/user/CODE_BASE/namechart/apps/charts/static/charts/images/base_image_templates/US_LETTER_3GEN_BW.pdf",
            "name": "3 Generation Chart",
        },
        "4": {
            "module": "apps.generator.utils.image_4generator",
            "function": "generate_family_tree",
            "filename": "/home/user/CODE_BASE/namechart/apps/charts/static/charts/images/base_image_templates/US_LETTER_4GEN_BW.pdf",
            "name": "4 Generation Chart",
        },
        "5": {
            "module": "apps.generator.utils.image_5generator",
            "function": "generate_family_tree",
            "filename": "/home/user/CODE_BASE/namechart/apps/charts/static/charts/images/base_image_templates/US_LETTER_5GEN_BW.pdf",
            "name": "5 Generation Chart",
        },
        "6": {
            "module": "apps.generator.utils.image_6generator",
            "function": "generate_family_tree",
            "filename": "/home/user/CODE_BASE/namechart/apps/charts/static/charts/images/base_image_templates/US_LETTER_6GEN_BW.pdf",
            "name": "6 Generation Chart",
        },
        "7": {
            "module": "apps.generator.utils.image_7generator",
            "function": "generate_family_tree",
            "filename": "/home/user/CODE_BASE/namechart/apps/charts/static/charts/images/base_image_templates/US_LETTER_7GEN_BW.pdf",
            "name": "7 Generation Chart",
        },
    }
