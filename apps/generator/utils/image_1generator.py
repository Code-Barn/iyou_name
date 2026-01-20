import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

logger = logging.getLogger(__name__)


def generate_family_tree(
    primary_individual, family_data, template="1gen", user_settings=None
):
    """
    Generate a 1-generation family tree chart using Wand (Python ImageMagick binding)

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type (e.g., '1gen' for 1-generation chart)
        user_settings: Dictionary of user settings to override hardcoded defaults
    """
    # Get user settings or use empty dict if not provided
    user_settings = user_settings or {}
    """
    Generate a 1-generation family tree chart using Wand (Python ImageMagick binding)

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type (e.g., '1gen' for 1-generation chart)

    Returns:
        BytesIO buffer containing the generated image
    """
    print(f"DEBUG: image_1generator called with template: {template}")

    print(
        f"DEBUG: Generating 1-generation family tree for: {primary_individual.full_name}"
    )
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    # Construct the full path to the template file
    try:
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/charts/static/charts/images/base_image_templates",
            "US_LETTER_1GEN_BW.pdf",
        )
        print(f"DEBUG: Template path: {template_path}")
        print(f"DEBUG: File exists: {os.path.exists(template_path)}")

        # Create a new image with the same dimensions as your template
        with Image(filename=template_path, resolution=300) as img:
            print(f"Image loaded successfully: {img.width}x{img.height}")

            # =============================================
            # TRANSLATION SETTINGS TUNING
            # =============================================

            # Initial translation (not used in final PDF)
            INITIAL_TRANSLATE_X = 0
            INITIAL_TRANSLATE_Y = 0

            # Subject translation (not used in final PDF)
            SUBJECT_TRANSLATE_X = 0
            SUBJECT_TRANSLATE_Y = 0

            # =============================================
            # DRAWING SETTINGS TUNING
            # =============================================

            # Font settings
            FONT_FAMILY = str(user_settings.get("font_family", "Arial"))

            # Stroke settings
            DEFAULT_STROKE_WIDTH = user_settings.get("default_stroke_width", 0.5)
            PRIMARY_STROKE_COLOR = Color(
                user_settings.get("primary_stroke_color", "black")
            )

            # Drawing quality settings
            STROKE_ANTIALIAS = True

            # =============================================
            # PRIMARY INDIVIDUAL TUNING SETTINGS
            # =============================================

            # Primary individual colors
            PRIMARY_FONT_COLOR = Color(user_settings.get("primary_font_color", "black"))
            PRIMARY_BIRTH_COLOR = Color(
                user_settings.get("primary_birth_color", "black")
            )
            PRIMARY_PLACE_COLOR = Color(
                user_settings.get("primary_place_color", "black")
            )
            PRIMARY_DEATH_COLOR = Color(
                user_settings.get("primary_death_color", "black")
            )
            PRIMARY_STROKE_COLOR = Color(
                user_settings.get("primary_stroke_color", "black")
            )

            # Primary individual coordinates
            PRIMARY_NAME_X = user_settings.get("primary_name_x", 0)
            PRIMARY_NAME_Y = user_settings.get("primary_name_y", 0)
            PRIMARY_NAME_ROTATE = user_settings.get("primary_name_rotate", -45)
            PRIMARY_BIRTH_X = user_settings.get("primary_birth_x", 0)
            PRIMARY_BIRTH_Y = user_settings.get("primary_birth_y", 135)
            PRIMARY_BIRTH_ROTATE = user_settings.get("primary_birth_rotate", 45)
            PRIMARY_PLACE_X = user_settings.get("primary_place_x", 0)
            PRIMARY_PLACE_Y = user_settings.get("primary_place_y", 90)
            PRIMARY_PLACE_ROTATE = user_settings.get("primary_place_rotate", -45)

            # Primary individual font sizes
            PRIMARY_NAME_FONT_SIZE = user_settings.get("primary_name_font_size", 88)
            PRIMARY_INFO_FONT_SIZE = user_settings.get("primary_info_font_size", 88)

            with Drawing() as draw:
                # Set initial drawing properties
                print(f"DEBUG: User settings for final chart: {user_settings}")
                draw.font = FONT_FAMILY
                draw.font_size = PRIMARY_NAME_FONT_SIZE
                draw.stroke_antialias = STROKE_ANTIALIAS

                # Initial translation
                print(
                    f"Translating coordinates by (x={INITIAL_TRANSLATE_X}, y={INITIAL_TRANSLATE_Y})"
                )
                draw.translate(x=INITIAL_TRANSLATE_X, y=INITIAL_TRANSLATE_Y)

                # =============================================
                # PRIMARY INDIVIDUAL DRAWING
                # =============================================

                # Subject translation
                print(
                    f"Translating coordinates by (x={SUBJECT_TRANSLATE_X}, y={SUBJECT_TRANSLATE_Y})"
                )
                draw.translate(x=SUBJECT_TRANSLATE_X, y=SUBJECT_TRANSLATE_Y)
                print(f"Setting stroke_width to: {DEFAULT_STROKE_WIDTH}")
                draw.stroke_width = DEFAULT_STROKE_WIDTH
                print(f"Setting stroke_color to: {PRIMARY_STROKE_COLOR}")
                draw.stroke_color = PRIMARY_STROKE_COLOR
                print(f"Setting fill_color to: {PRIMARY_FONT_COLOR}")
                draw.fill_color = PRIMARY_FONT_COLOR
                print("Setting gravity to: center")
                draw.gravity = "center"
                print(f"Rotating by: {PRIMARY_NAME_ROTATE} degrees")
                draw.rotate(PRIMARY_NAME_ROTATE)

                # Surname 0, Self / Subject, Surname 0 (Primary individual)
                print(f"Drawing primary individual: {primary_individual.full_name}")

                # Split the primary individual's name into parts
                name_parts = primary_individual.full_name.split()
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                middle_name = name_parts[1] if len(name_parts) > 1 else ""
                last_name = name_parts[-1] if len(name_parts) > 1 else ""

                # Draw each part of the name with newline characters and centered alignment
                draw.text(
                    PRIMARY_NAME_X,
                    PRIMARY_NAME_Y,
                    f"{first_name}\n{middle_name}\n{last_name}",
                )
                print(
                    f"Drawn text at ({PRIMARY_NAME_X}, {PRIMARY_NAME_Y}): {first_name}\n{middle_name}\n{last_name}"
                )

                # Draw statements for birthdate at center bottom
                print(f"Rotating by: {PRIMARY_BIRTH_ROTATE} degrees")
                draw.rotate(PRIMARY_BIRTH_ROTATE)
                print(f"Setting font_size to: {PRIMARY_INFO_FONT_SIZE}")
                draw.font_size = PRIMARY_INFO_FONT_SIZE
                print(f"Setting fill_color to: {PRIMARY_BIRTH_COLOR}")
                draw.fill_color = PRIMARY_BIRTH_COLOR

                pifx_birth, pify_birth = PRIMARY_BIRTH_X, PRIMARY_BIRTH_Y
                draw.text(pifx_birth, pify_birth, primary_individual.birth_date or " ")
                print(
                    f"Drawn text at ({pifx_birth}, {pify_birth}): {primary_individual.birth_date or ' '}"
                )

                print(f"Setting fill_color to: {PRIMARY_PLACE_COLOR}")
                draw.fill_color = PRIMARY_PLACE_COLOR
                pifx_place, pify_place = PRIMARY_PLACE_X, PRIMARY_PLACE_Y
                print(f"Rotating by: {PRIMARY_PLACE_ROTATE} degrees")
                draw.rotate(PRIMARY_PLACE_ROTATE)
                draw.text(pifx_place, pify_place, primary_individual.birth_place or " ")
                print(
                    f"Drawn text at ({pifx_place}, {pify_place}): {primary_individual.birth_place or ' '}"
                )

                # Draw statements for deathdate at center top
                draw.rotate(180)
                draw.stroke_width = DEFAULT_STROKE_WIDTH
                print(f"Setting fill_color to: {PRIMARY_DEATH_COLOR}")
                draw.fill_color = PRIMARY_DEATH_COLOR

                # Draw primary individual's death date if available
                pifx_death, pify_death = 0, 0
                draw.text(pifx_death, pify_death, primary_individual.death_date or " ")
                print(
                    f"Drawn text at ({pifx_death}, {pify_death}): {primary_individual.death_date or ' '}"
                )

                # Apply the drawing to the image
                draw(img)

                # Save the result to a BytesIO buffer
                img_buffer = BytesIO()
                img.save(file=img_buffer)
                img_buffer.seek(0)

                return img_buffer

    except Exception as e:
        print(f"ERROR: Failed to generate family tree: {str(e)}")
        raise


def generate_1gen_preview(primary_individual, user_settings=None):
    """
    Generate a 1-generation preview chart using Wand (Python ImageMagick binding)

    Args:
        primary_individual: PersonData object for the primary individual
        user_settings: Dictionary of user settings to override hardcoded defaults

    Returns:
        BytesIO buffer containing the generated preview image
    """
    # Get user settings or use empty dict if not provided
    user_settings = user_settings or {}

    try:
        # Construct the full path to the preview template file
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "1GEN_PREVIEW.png",
        )
        print(f"DEBUG: Preview template path: {template_path}")
        print(f"DEBUG: File exists: {os.path.exists(template_path)}")

        # Create a new image with the same dimensions as the preview template
        with Image(filename=template_path, resolution=300) as img:
            print(f"Preview image loaded successfully: {img.width}x{img.height}")

            # =============================================
            # TRANSLATION SETTINGS TUNING
            # =============================================

            # Initial translation (not used in final PDF)
            INITIAL_TRANSLATE_X = 0
            INITIAL_TRANSLATE_Y = 0

            # Subject translation (not used in final PDF)
            SUBJECT_TRANSLATE_X = user_settings.get("subject_translate_x", 0)
            SUBJECT_TRANSLATE_Y = user_settings.get("subject_translate_y", 0)

            # =============================================
            # DRAWING SETTINGS TUNING
            # =============================================

            # Font settings
            FONT_FAMILY = str(user_settings.get("font_family", "Arial"))

            # Stroke settings
            DEFAULT_STROKE_WIDTH = user_settings.get("default_stroke_width", 0.5)
            PRIMARY_STROKE_COLOR = Color(
                user_settings.get("primary_stroke_color", "black")
            )

            # Drawing quality settings
            STROKE_ANTIALIAS = True

            # =============================================
            # PRIMARY INDIVIDUAL TUNING SETTINGS
            # =============================================

            # Primary individual colors
            PRIMARY_FONT_COLOR = Color(user_settings.get("primary_font_color", "black"))
            PRIMARY_BIRTH_COLOR = Color(
                user_settings.get("primary_birth_color", "black")
            )
            PRIMARY_PLACE_COLOR = Color(
                user_settings.get("primary_place_color", "black")
            )
            PRIMARY_DEATH_COLOR = Color(
                user_settings.get("primary_death_color", "black")
            )
            PRIMARY_STROKE_COLOR = Color(
                user_settings.get("primary_stroke_color", "black")
            )

            # Primary individual coordinates
            PRIMARY_NAME_X = user_settings.get("primary_name_x", 0)
            PRIMARY_NAME_Y = user_settings.get("primary_name_y", 0)
            PRIMARY_NAME_ROTATE = user_settings.get("primary_name_rotate", -45)
            PRIMARY_BIRTH_X = user_settings.get("primary_birth_x", 0)
            PRIMARY_BIRTH_Y = user_settings.get("primary_birth_y", 135)
            PRIMARY_BIRTH_ROTATE = user_settings.get("primary_birth_rotate", 45)
            PRIMARY_PLACE_X = user_settings.get("primary_place_x", 0)
            PRIMARY_PLACE_Y = user_settings.get("primary_place_y", 90)
            PRIMARY_PLACE_ROTATE = user_settings.get("primary_place_rotate", -45)

            # Primary individual font sizes
            PRIMARY_NAME_FONT_SIZE = user_settings.get("primary_name_font_size", 88)
            PRIMARY_INFO_FONT_SIZE = user_settings.get("primary_info_font_size", 88)

            with Drawing() as draw:
                # Set initial drawing properties
                print(f"DEBUG: User settings for preview: {user_settings}")
                draw.font = FONT_FAMILY
                draw.font_size = PRIMARY_NAME_FONT_SIZE
                draw.stroke_antialias = STROKE_ANTIALIAS

                # Initial translation
                print(
                    f"Translating coordinates by (x={INITIAL_TRANSLATE_X}, y={INITIAL_TRANSLATE_Y})"
                )
                draw.translate(x=INITIAL_TRANSLATE_X, y=INITIAL_TRANSLATE_Y)

                # =============================================
                # PRIMARY INDIVIDUAL DRAWING
                # =============================================

                # Subject translation
                print(
                    f"Translating coordinates by (x={SUBJECT_TRANSLATE_X}, y={SUBJECT_TRANSLATE_Y})"
                )
                draw.translate(x=SUBJECT_TRANSLATE_X, y=SUBJECT_TRANSLATE_Y)
                print(f"Setting stroke_width to: {DEFAULT_STROKE_WIDTH}")
                draw.stroke_width = DEFAULT_STROKE_WIDTH
                print(f"Setting stroke_color to: {PRIMARY_STROKE_COLOR}")
                draw.stroke_color = PRIMARY_STROKE_COLOR
                print(f"Setting fill_color to: {PRIMARY_FONT_COLOR}")
                draw.fill_color = PRIMARY_FONT_COLOR
                print("Setting gravity to: center")
                draw.gravity = "center"
                print(f"Rotating by: {PRIMARY_NAME_ROTATE} degrees")
                draw.rotate(PRIMARY_NAME_ROTATE)

                # Surname 0, Self / Subject, Surname 0 (Primary individual)
                print(f"Drawing primary individual: {primary_individual.full_name}")

                # Split the primary individual's name into parts
                name_parts = primary_individual.full_name.split()
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                middle_name = name_parts[1] if len(name_parts) > 1 else ""
                last_name = name_parts[-1] if len(name_parts) > 1 else ""

                # Draw each part of the name with newline characters and centered alignment
                draw.text(
                    PRIMARY_NAME_X,
                    PRIMARY_NAME_Y,
                    f"{first_name}\n{middle_name}\n{last_name}",
                )
                print(
                    f"Drawn text at ({PRIMARY_NAME_X}, {PRIMARY_NAME_Y}): {first_name}\n{middle_name}\n{last_name}"
                )

                # Draw statements for birthdate at center bottom
                print(f"Rotating by: {PRIMARY_BIRTH_ROTATE} degrees")
                draw.rotate(PRIMARY_BIRTH_ROTATE)
                print(f"Setting font_size to: {PRIMARY_INFO_FONT_SIZE}")
                draw.font_size = PRIMARY_INFO_FONT_SIZE
                print(f"Setting fill_color to: {PRIMARY_BIRTH_COLOR}")
                draw.fill_color = PRIMARY_BIRTH_COLOR

                pifx_birth, pify_birth = PRIMARY_BIRTH_X, PRIMARY_BIRTH_Y
                draw.text(pifx_birth, pify_birth, primary_individual.birth_date or " ")
                print(
                    f"Drawn text at ({pifx_birth}, {pify_birth}): {primary_individual.birth_date or ' '}"
                )

                print(f"Setting fill_color to: {PRIMARY_PLACE_COLOR}")
                draw.fill_color = PRIMARY_PLACE_COLOR
                pifx_place, pify_place = PRIMARY_PLACE_X, PRIMARY_PLACE_Y
                print(f"Rotating by: {PRIMARY_PLACE_ROTATE} degrees")
                draw.rotate(PRIMARY_PLACE_ROTATE)
                draw.text(pifx_place, pify_place, primary_individual.birth_place or " ")
                print(
                    f"Drawn text at ({pifx_place}, {pify_place}): {primary_individual.birth_place or ' '}"
                )

                # Draw statements for deathdate at center top
                draw.rotate(180)
                draw.stroke_width = DEFAULT_STROKE_WIDTH
                print(f"Setting fill_color to: {PRIMARY_DEATH_COLOR}")
                draw.fill_color = PRIMARY_DEATH_COLOR

                # Draw primary individual's death date if available
                pifx_death, pify_death = 0, 0
                draw.text(pifx_death, pify_death, primary_individual.death_date or " ")
                print(
                    f"Drawn text at ({pifx_death}, {pify_death}): {primary_individual.death_date or ' '}"
                )

                # Apply the drawing to the image
                draw(img)

                # Save the result to a BytesIO buffer
                img_buffer = BytesIO()
                img.save(file=img_buffer)
                img_buffer.seek(0)

                return img_buffer

    except Exception as e:
        print(f"ERROR: Failed to generate preview: {str(e)}")
        raise
