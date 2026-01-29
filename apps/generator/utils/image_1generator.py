import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

logger = logging.getLogger(__name__)


def generate_family_tree(primary_individual, family_data, template="1gen", user_settings=None):
    """
    Generate a 1-generation family tree chart using Wand (Python ImageMagick binding)

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type (e.g., '1gen' for 1-generation chart)
        user_settings: Dictionary of user settings to override hardcoded defaults

    Returns:
        BytesIO buffer containing the generated image
    """

    # Get user settings or use empty dict if not provided
    user_settings = user_settings or {}

    print(f"DEBUG: generate_family_tree received user_settings: {user_settings}")
    print(f"DEBUG: image_1generator called with template: {template}")
    print(f"DEBUG: Generating 1-generation family tree for: {primary_individual.full_name}")
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    # Construct the full path to the template file
    try:
        template_path = os.path.join(settings.BASE_DIR, "apps/charts/static/charts/images/base_image_templates", "US_LETTER_1GEN_BW.pdf")

        print(f"DEBUG: Template path: {template_path}")
        print(f"DEBUG: File exists: {os.path.exists(template_path)}")

        # Create a new image with the same dimensions as your template
        with Image(filename=template_path, resolution=300) as img:

            print(f"Preview image loaded successfully: {img.width}x{img.height}")

            # =============================================
            # COLORED BACKGROUND COORDINATES
            # =============================================
            # Color square coordinates
            BACKGROUND_LEFT = 7
            BACKGROUND_TOP = 7
            BACKGROUND_WIDTH = 1936
            BACKGROUND_HEIGHT = 1936

            # =============================================
            # TRANSLATION SETTINGS TUNING
            # =============================================

            # Initial translation (not used in final PDF)
            INITIAL_TRANSLATE_X = 0
            INITIAL_TRANSLATE_Y = 0

            # Subject translation (not used in final PDF)
            SUBJECT_TRANSLATE_X = int(user_settings.get("subject_translate_x", 0))
            SUBJECT_TRANSLATE_Y = int(user_settings.get("subject_translate_y", 0))

            print(f"DEBUG: SUBJECT_TRANSLATE_X set to: {SUBJECT_TRANSLATE_X}")
            print(f"DEBUG: SUBJECT_TRANSLATE_Y set to: {SUBJECT_TRANSLATE_Y}")

            # =============================================
            # DRAWING SETTINGS TUNING
            # =============================================

            # Font settings
            FONT_FAMILY = str(user_settings.get("font_family", "Arial"))

            print(f"DEBUG: FONT_FAMILY set to: {FONT_FAMILY}")

            # Stroke settings
            DEFAULT_STROKE_WIDTH = float(user_settings.get("default_stroke_width", 0.5))
            PRIMARY_STROKE_COLOR = Color(user_settings.get("primary_stroke_color", "black"))

            print(f"DEBUG: DEFAULT_STROKE_WIDTH set to: {DEFAULT_STROKE_WIDTH}")
            print(f"DEBUG: PRIMARY_STROKE_COLOR set to: {PRIMARY_STROKE_COLOR}")

            # Drawing quality settings
            STROKE_ANTIALIAS = True

            # =============================================
            # PRIMARY INDIVIDUAL TUNING SETTINGS
            # =============================================

            # Primary individual colors
            PRIMARY_BACKGROUND_COLOR = Color(user_settings.get("primary_background_color", "#FFFFFF"))
            PRIMARY_FONT_COLOR = Color(user_settings.get("primary_font_color", "black"))
            PRIMARY_BIRTH_COLOR = Color(user_settings.get("primary_birth_color", "black"))
            PRIMARY_BIRTH_PLACE_COLOR = Color(user_settings.get("primary_birth_place_color", "black"))
            PRIMARY_DEATH_COLOR = Color(user_settings.get("primary_death_color", "black"))
            PRIMARY_DEATH_PLACE_COLOR = Color(user_settings.get("primary_death_place_color", "black"))
            PRIMARY_STROKE_COLOR = Color(user_settings.get("primary_stroke_color", "black"))

            print(f"DEBUG: PRIMARY_BACKGROUND_COLOR set to: {PRIMARY_BACKGROUND_COLOR}")
            print(f"DEBUG: PRIMARY_FONT_COLOR set to: {PRIMARY_FONT_COLOR}")
            print(f"DEBUG: PRIMARY_BIRTH_COLOR set to: {PRIMARY_BIRTH_COLOR}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_COLOR set to: {PRIMARY_BIRTH_PLACE_COLOR}")
            print(f"DEBUG: PRIMARY_DEATH_COLOR set to: {PRIMARY_DEATH_COLOR}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_COLOR set to: {PRIMARY_DEATH_PLACE_COLOR}")

            # Primary individual coordinates
            PRIMARY_NAME_X = int(user_settings.get("primary_name_x", 0))
            PRIMARY_NAME_Y = int(user_settings.get("primary_name_y", 0))
            PRIMARY_NAME_ROTATE = int(user_settings.get("primary_name_rotate", -45))
            PRIMARY_BIRTH_X = int(user_settings.get("primary_birth_x", 0))
            PRIMARY_BIRTH_Y = int(user_settings.get("primary_birth_y", 0))
            PRIMARY_BIRTH_ROTATE = int(user_settings.get("primary_birth_rotate", -90))
            PRIMARY_BIRTH_PLACE_X = int(user_settings.get("primary_birth_place_x", 0))
            PRIMARY_BIRTH_PLACE_Y = int(user_settings.get("primary_birth_place_y", 0))
            PRIMARY_BIRTH_PLACE_ROTATE = int(user_settings.get("primary_birth_place_rotate", 0))
            PRIMARY_DEATH_X = int(user_settings.get("primary_death_x", 0))
            PRIMARY_DEATH_Y = int(user_settings.get("primary_death_y", 0))
            PRIMARY_DEATH_ROTATE = int(user_settings.get("primary_death_rotate", 0))
            PRIMARY_DEATH_PLACE_X = int(user_settings.get("primary_death_place_x", 0))
            PRIMARY_DEATH_PLACE_Y = int(user_settings.get("primary_death_place_y", 0))
            PRIMARY_DEATH_PLACE_ROTATE = int(user_settings.get("primary_death_place_rotate", -90))

            print(f"DEBUG: PRIMARY_NAME_X set to: {PRIMARY_NAME_X}")
            print(f"DEBUG: PRIMARY_NAME_Y set to: {PRIMARY_NAME_Y}")
            print(f"DEBUG: PRIMARY_NAME_ROTATE set to: {PRIMARY_NAME_ROTATE}")
            print(f"DEBUG: PRIMARY_BIRTH_X set to: {PRIMARY_BIRTH_X}")
            print(f"DEBUG: PRIMARY_BIRTH_Y set to: {PRIMARY_BIRTH_Y}")
            print(f"DEBUG: PRIMARY_BIRTH_ROTATE set to: {PRIMARY_BIRTH_ROTATE}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_X set to: {PRIMARY_BIRTH_PLACE_X}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_Y set to: {PRIMARY_BIRTH_PLACE_Y}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_ROTATE set to: {PRIMARY_BIRTH_PLACE_ROTATE}")
            print(f"DEBUG: PRIMARY_DEATH_X set to: {PRIMARY_DEATH_X}")
            print(f"DEBUG: PRIMARY_DEATH_Y set to: {PRIMARY_DEATH_Y}")
            print(f"DEBUG: PRIMARY_DEATH_ROTATE set to: {PRIMARY_DEATH_ROTATE}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_X set to: {PRIMARY_DEATH_PLACE_X}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_Y set to: {PRIMARY_DEATH_PLACE_Y}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_ROTATE set to: {PRIMARY_DEATH_PLACE_ROTATE}")

            # Primary individual font sizes
            PRIMARY_NAME_FONT_SIZE = int(user_settings.get("primary_name_font_size", 84))
            PRIMARY_DATE_INFO_FONT_SIZE = int(user_settings.get("primary_date_info_font_size", 60))
            PRIMARY_PLACE_INFO_FONT_SIZE = int(user_settings.get("primary_place_info_font_size", 28))

            print(f"DEBUG: PRIMARY_NAME_FONT_SIZE set to: {PRIMARY_NAME_FONT_SIZE}")
            print(f"DEBUG: PRIMARY_DATE_INFO_FONT_SIZE set to: {PRIMARY_DATE_INFO_FONT_SIZE}")
            print(f"DEBUG: PRIMARY_PLACE_INFO_FONT_SIZE set to: {PRIMARY_PLACE_INFO_FONT_SIZE}")


            with Drawing() as draw:

                draw.push()

                # Set initial drawing properties
                print(f"DEBUG: User settings for preview: {user_settings}")

                draw.font = FONT_FAMILY
                draw.font_size = PRIMARY_NAME_FONT_SIZE
                draw.stroke_antialias = STROKE_ANTIALIAS

                # Draw background square
                draw.fill_color = PRIMARY_BACKGROUND_COLOR
                print(f"Drawing rectangle at (left={BACKGROUND_LEFT}, top={BACKGROUND_TOP}, width={BACKGROUND_WIDTH}, height={BACKGROUND_HEIGHT})")
                draw.rectangle(
                    left=BACKGROUND_LEFT,
                    top=BACKGROUND_TOP,
                    width=BACKGROUND_WIDTH,
                    height=BACKGROUND_HEIGHT,
                )

                # Initial translation
                print(f"Translating coordinates by (x={INITIAL_TRANSLATE_X}, y={INITIAL_TRANSLATE_Y})")

                draw.translate(x=INITIAL_TRANSLATE_X, y=INITIAL_TRANSLATE_Y)

                # =============================================
                # PRIMARY INDIVIDUAL DRAWING
                # =============================================

                # Subject translation
                print(f"Translating coordinates by (x={SUBJECT_TRANSLATE_X}, y={SUBJECT_TRANSLATE_Y})")
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
                draw.text(PRIMARY_NAME_X, PRIMARY_NAME_Y, f"{first_name}\n{middle_name}\n{last_name}")
                print(f"Drawn text at ({PRIMARY_NAME_X}, {PRIMARY_NAME_Y}): {first_name}\n{middle_name}\n{last_name}")


                draw.pop()

                draw.font = FONT_FAMILY
                draw.stroke_color = PRIMARY_STROKE_COLOR
                draw.stroke_width = DEFAULT_STROKE_WIDTH
                draw.stroke_antialias = STROKE_ANTIALIAS

                # =============================================
                # DRAW THE PRIMARY_BIRTH INFO
                # =============================================

                # Push the current drawing context
                # draw.push()
                # print("Pushed drawing context.")

                dpi = 300
                pixel_ratio = dpi / 72  # Approx 4.1667

                # Push the current drawing context
                draw.push()
                print("Pushed drawing context.")

                draw.font_size = PRIMARY_DATE_INFO_FONT_SIZE
                draw.fill_color = PRIMARY_BIRTH_COLOR
                print(f"Setting font to: {PRIMARY_DATE_INFO_FONT_SIZE} & fill color to: {PRIMARY_BIRTH_COLOR}")

                text = primary_individual.birth_date or " "
                print(f"Text to draw: '{text}'")

                # Get text metrics
                metrics = draw.get_font_metrics(img, text, False)
                text_width = metrics.text_width
                text_height = metrics.text_height
                print(f"Text dimensions: width={text_width}, height={text_height}")

                # Convert points to pixels
                text_width_px = metrics.text_width * pixel_ratio
                text_height_px = metrics.text_height * pixel_ratio

                print(f"Points: {metrics.text_width}, Actual Pixels: {text_width_px}")
                print(f"Points: {metrics.text_height}, Actual Pixels: {text_height_px}")

                # Translate to the correct position: 58px from the left, vertically centered
                translate_x = 227
                translate_y = img.height // 2
                print(f"Translating to: ({translate_x}, {translate_y})")

                draw.translate(translate_x, translate_y)

                # Rotate the drawing context by -90 degrees
                draw.rotate(-90)
                print("Rotated by -90 degrees.")

                # Adjust the origin to account for the text's width after rotation
                # adjust_y = text_width // 2
                # print(f"Adjusting origin by: (0, {adjust_y})")
                # draw.translate(-705, adjust_y)

                # Adjust the origin to account for the text's width after rotation
                adjust_y = -text_width_px // 2
                print(f"Adjusting origin by: (0, {adjust_y})")
                draw.translate(adjust_y, 0)

                # Draw the text at the new origin (0, 0) after translation and rotation
                print("Drawing text at (0, 0) after transformations.")
                draw.text(0, 0, text)

                # Pop the drawing context
                draw.pop()
                print("Popped drawing context.")

                # =============================================
                # DRAW THE PRIMARY_BIRTH_PLACE INFO
                # =============================================

                draw.push()

                draw.font_size = PRIMARY_PLACE_INFO_FONT_SIZE

                draw.gravity = "south"

                # Draw statements for birthplace
                print(f"Rotating by: {PRIMARY_BIRTH_PLACE_ROTATE} degrees")
                draw.rotate(PRIMARY_BIRTH_PLACE_ROTATE)

                print(f"Setting fill_color to: {PRIMARY_BIRTH_PLACE_COLOR}")
                draw.fill_color = PRIMARY_BIRTH_PLACE_COLOR

                pifx_birth_place, pify_birth_place = PRIMARY_BIRTH_PLACE_X, PRIMARY_BIRTH_PLACE_Y
                draw.text(pifx_birth_place, pify_birth_place, primary_individual.birth_place or " ")
                print(f"Drawn text at ({pifx_birth_place}, {pify_birth_place}): {primary_individual.birth_place or ' '}")

                draw.pop()

                # =============================================
                # DRAW THE PRIMARY_DEATH INFO
                # =============================================

                draw.push()

                draw.font_size = PRIMARY_DATE_INFO_FONT_SIZE
                draw.fill_color = PRIMARY_DEATH_COLOR
                print(f"Setting font to: {PRIMARY_DATE_INFO_FONT_SIZE} & fill color to: {PRIMARY_DEATH_COLOR}")

                draw.gravity = "north"

                # Draw statements for deathdate
                #draw.rotate(180)
                draw.stroke_width = DEFAULT_STROKE_WIDTH



                # Draw primary individual's death date if available
                # Apply death date rotation
                print(f"Rotating by: {PRIMARY_DEATH_ROTATE} degrees")
                draw.rotate(PRIMARY_DEATH_ROTATE)

                pifx_death, pify_death = PRIMARY_DEATH_X, PRIMARY_DEATH_Y
                draw.text(pifx_death, pify_death, primary_individual.death_date or " ")
                print(f"Drawn text at ({pifx_death}, {pify_death}): {primary_individual.death_date or ' '}")

                draw.pop()

                # =============================================
                # DRAW THE PRIMARY_DEATH_PLACE INFO
                # =============================================

                # Push the current drawing context
                draw.push()
                print("Pushed drawing context.")

                draw.font_size = PRIMARY_PLACE_INFO_FONT_SIZE
                draw.fill_color = PRIMARY_DEATH_PLACE_COLOR

                text = primary_individual.death_place or " "
                print(f"Text to draw: '{text}'")

                # Get text metrics
                metrics = draw.get_font_metrics(img, text, False)
                text_width = metrics.text_width
                text_height = metrics.text_height
                print(f"Text dimensions: width={text_width}, height={text_height}")

                # Translate to the correct position: 58px from the left, vertically centered
                translate_x = 1850
                translate_y = img.height // 2
                print(f"Translating to: ({translate_x}, {translate_y})")

                draw.translate(translate_x, translate_y)

                # Rotate the drawing context by -90 degrees
                draw.rotate(-90)
                print("Rotated by -90 degrees.")

                # Adjust the origin to account for the text's width after rotation
                adjust_x = -1500
                #adjust_y = text_width // 2
                print(f"Adjusting origin by: ({adjust_x}, 0)")
                draw.translate(adjust_x, 0)

                # Draw the text at the new origin (0, 0) after translation and rotation
                print("Drawing text at (0, 0) after transformations.")
                draw.text(0, 0, text)

                # Pop the drawing context
                draw.pop()
                print("Popped drawing context.")


                # =============================================
                # DRAW THE IMAGE
                # =============================================

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

    print(f"DEBUG: generate_1gen_preview received user_settings: {user_settings}")

    try:
        # Construct the full path to the preview template file
        template_path = os.path.join(settings.BASE_DIR, "apps/hud/static/hud/images/preview_image_templates", "1GEN_PREVIEW.png")

        print(f"DEBUG: Preview template path: {template_path}")
        print(f"DEBUG: File exists: {os.path.exists(template_path)}")

        # Create a new image with the same dimensions as the preview template
        with Image(filename=template_path, resolution=300) as img:

            print(f"Preview image loaded successfully: {img.width}x{img.height}")

            # =============================================
            # COLORED BACKGROUND COORDINATES
            # =============================================
            # Color square coordinates
            BACKGROUND_LEFT = 7
            BACKGROUND_TOP = 7
            BACKGROUND_WIDTH = 1936
            BACKGROUND_HEIGHT = 1936

            # =============================================
            # TRANSLATION SETTINGS TUNING
            # =============================================

            # Initial translation (not used in final PDF)
            INITIAL_TRANSLATE_X = 0
            INITIAL_TRANSLATE_Y = 0

            # Subject translation (not used in final PDF)
            SUBJECT_TRANSLATE_X = int(user_settings.get("subject_translate_x", 0))
            SUBJECT_TRANSLATE_Y = int(user_settings.get("subject_translate_y", 0))

            print(f"DEBUG: SUBJECT_TRANSLATE_X set to: {SUBJECT_TRANSLATE_X}")
            print(f"DEBUG: SUBJECT_TRANSLATE_Y set to: {SUBJECT_TRANSLATE_Y}")

            # =============================================
            # DRAWING SETTINGS TUNING
            # =============================================

            # Font settings
            FONT_FAMILY = str(user_settings.get("font_family", "Arial"))

            print(f"DEBUG: FONT_FAMILY set to: {FONT_FAMILY}")

            # Stroke settings
            DEFAULT_STROKE_WIDTH = float(user_settings.get("default_stroke_width", 0.5))
            PRIMARY_STROKE_COLOR = Color(user_settings.get("primary_stroke_color", "black"))

            print(f"DEBUG: DEFAULT_STROKE_WIDTH set to: {DEFAULT_STROKE_WIDTH}")
            print(f"DEBUG: PRIMARY_STROKE_COLOR set to: {PRIMARY_STROKE_COLOR}")

            # Drawing quality settings
            STROKE_ANTIALIAS = True

            # =============================================
            # PRIMARY INDIVIDUAL TUNING SETTINGS
            # =============================================

            # Primary individual colors
            PRIMARY_BACKGROUND_COLOR = Color(user_settings.get("primary_background_color", "#FFFFFF"))
            PRIMARY_FONT_COLOR = Color(user_settings.get("primary_font_color", "black"))
            PRIMARY_BIRTH_COLOR = Color(user_settings.get("primary_birth_color", "black"))
            PRIMARY_BIRTH_PLACE_COLOR = Color(user_settings.get("primary_birth_place_color", "black"))
            PRIMARY_DEATH_COLOR = Color(user_settings.get("primary_death_color", "black"))
            PRIMARY_DEATH_PLACE_COLOR = Color(user_settings.get("primary_death_place_color", "black"))
            PRIMARY_STROKE_COLOR = Color(user_settings.get("primary_stroke_color", "black"))

            print(f"DEBUG: PRIMARY_BACKGROUND_COLOR set to: {PRIMARY_BACKGROUND_COLOR}")
            print(f"DEBUG: PRIMARY_FONT_COLOR set to: {PRIMARY_FONT_COLOR}")
            print(f"DEBUG: PRIMARY_BIRTH_COLOR set to: {PRIMARY_BIRTH_COLOR}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_COLOR set to: {PRIMARY_BIRTH_PLACE_COLOR}")
            print(f"DEBUG: PRIMARY_DEATH_COLOR set to: {PRIMARY_DEATH_COLOR}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_COLOR set to: {PRIMARY_DEATH_PLACE_COLOR}")

            # Primary individual coordinates
            PRIMARY_NAME_X = int(user_settings.get("primary_name_x", 0))
            PRIMARY_NAME_Y = int(user_settings.get("primary_name_y", 0))
            PRIMARY_NAME_ROTATE = int(user_settings.get("primary_name_rotate", -45))
            PRIMARY_BIRTH_X = int(user_settings.get("primary_birth_x", 0))
            PRIMARY_BIRTH_Y = int(user_settings.get("primary_birth_y", 0))
            PRIMARY_BIRTH_ROTATE = int(user_settings.get("primary_birth_rotate", -90))
            PRIMARY_BIRTH_PLACE_X = int(user_settings.get("primary_birth_place_x", 0))
            PRIMARY_BIRTH_PLACE_Y = int(user_settings.get("primary_birth_place_y", 0))
            PRIMARY_BIRTH_PLACE_ROTATE = int(user_settings.get("primary_birth_place_rotate", 0))
            PRIMARY_DEATH_X = int(user_settings.get("primary_death_x", 0))
            PRIMARY_DEATH_Y = int(user_settings.get("primary_death_y", 0))
            PRIMARY_DEATH_ROTATE = int(user_settings.get("primary_death_rotate", 0))
            PRIMARY_DEATH_PLACE_X = int(user_settings.get("primary_death_place_x", 0))
            PRIMARY_DEATH_PLACE_Y = int(user_settings.get("primary_death_place_y", 0))
            PRIMARY_DEATH_PLACE_ROTATE = int(user_settings.get("primary_death_place_rotate", -90))

            print(f"DEBUG: PRIMARY_NAME_X set to: {PRIMARY_NAME_X}")
            print(f"DEBUG: PRIMARY_NAME_Y set to: {PRIMARY_NAME_Y}")
            print(f"DEBUG: PRIMARY_NAME_ROTATE set to: {PRIMARY_NAME_ROTATE}")
            print(f"DEBUG: PRIMARY_BIRTH_X set to: {PRIMARY_BIRTH_X}")
            print(f"DEBUG: PRIMARY_BIRTH_Y set to: {PRIMARY_BIRTH_Y}")
            print(f"DEBUG: PRIMARY_BIRTH_ROTATE set to: {PRIMARY_BIRTH_ROTATE}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_X set to: {PRIMARY_BIRTH_PLACE_X}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_Y set to: {PRIMARY_BIRTH_PLACE_Y}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_ROTATE set to: {PRIMARY_BIRTH_PLACE_ROTATE}")
            print(f"DEBUG: PRIMARY_DEATH_X set to: {PRIMARY_DEATH_X}")
            print(f"DEBUG: PRIMARY_DEATH_Y set to: {PRIMARY_DEATH_Y}")
            print(f"DEBUG: PRIMARY_DEATH_ROTATE set to: {PRIMARY_DEATH_ROTATE}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_X set to: {PRIMARY_DEATH_PLACE_X}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_Y set to: {PRIMARY_DEATH_PLACE_Y}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_ROTATE set to: {PRIMARY_DEATH_PLACE_ROTATE}")

            # Primary individual font sizes
            PRIMARY_NAME_FONT_SIZE = int(user_settings.get("primary_name_font_size", 84))
            PRIMARY_DATE_INFO_FONT_SIZE = int(user_settings.get("primary_date_info_font_size", 60))
            PRIMARY_PLACE_INFO_FONT_SIZE = int(user_settings.get("primary_place_info_font_size", 28))

            print(f"DEBUG: PRIMARY_NAME_FONT_SIZE set to: {PRIMARY_NAME_FONT_SIZE}")
            print(f"DEBUG: PRIMARY_DATE_INFO_FONT_SIZE set to: {PRIMARY_DATE_INFO_FONT_SIZE}")
            print(f"DEBUG: PRIMARY_PLACE_INFO_FONT_SIZE set to: {PRIMARY_PLACE_INFO_FONT_SIZE}")


            with Drawing() as draw:

                draw.push()

                # Set initial drawing properties
                print(f"DEBUG: User settings for preview: {user_settings}")

                draw.font = FONT_FAMILY
                draw.font_size = PRIMARY_NAME_FONT_SIZE
                draw.stroke_antialias = STROKE_ANTIALIAS

                # Draw background square
                draw.fill_color = PRIMARY_BACKGROUND_COLOR
                print(f"Drawing rectangle at (left={BACKGROUND_LEFT}, top={BACKGROUND_TOP}, width={BACKGROUND_WIDTH}, height={BACKGROUND_HEIGHT})")
                draw.rectangle(
                    left=BACKGROUND_LEFT,
                    top=BACKGROUND_TOP,
                    width=BACKGROUND_WIDTH,
                    height=BACKGROUND_HEIGHT,
                )

                # Initial translation
                print(f"Translating coordinates by (x={INITIAL_TRANSLATE_X}, y={INITIAL_TRANSLATE_Y})")

                draw.translate(x=INITIAL_TRANSLATE_X, y=INITIAL_TRANSLATE_Y)

                # =============================================
                # PRIMARY INDIVIDUAL DRAWING
                # =============================================

                # Subject translation
                print(f"Translating coordinates by (x={SUBJECT_TRANSLATE_X}, y={SUBJECT_TRANSLATE_Y})")
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
                draw.text(PRIMARY_NAME_X, PRIMARY_NAME_Y, f"{first_name}\n{middle_name}\n{last_name}")
                print(f"Drawn text at ({PRIMARY_NAME_X}, {PRIMARY_NAME_Y}): {first_name}\n{middle_name}\n{last_name}")


                draw.pop()

                draw.font = FONT_FAMILY
                draw.stroke_color = PRIMARY_STROKE_COLOR
                draw.stroke_width = DEFAULT_STROKE_WIDTH
                draw.stroke_antialias = STROKE_ANTIALIAS

                # =============================================
                # DRAW THE PRIMARY_BIRTH INFO
                # =============================================

                # Push the current drawing context
                # draw.push()
                # print("Pushed drawing context.")

                dpi = 300
                pixel_ratio = dpi / 72  # Approx 4.1667

                # Push the current drawing context
                draw.push()
                print("Pushed drawing context.")

                draw.font_size = PRIMARY_DATE_INFO_FONT_SIZE
                draw.fill_color = PRIMARY_BIRTH_COLOR
                print(f"Setting font to: {PRIMARY_DATE_INFO_FONT_SIZE} & fill color to: {PRIMARY_BIRTH_COLOR}")

                text = primary_individual.birth_date or " "
                print(f"Text to draw: '{text}'")

                # Get text metrics
                metrics = draw.get_font_metrics(img, text, False)
                text_width = metrics.text_width
                text_height = metrics.text_height
                print(f"Text dimensions: width={text_width}, height={text_height}")

                # Convert points to pixels
                text_width_px = metrics.text_width * pixel_ratio
                text_height_px = metrics.text_height * pixel_ratio

                print(f"Points: {metrics.text_width}, Actual Pixels: {text_width_px}")
                print(f"Points: {metrics.text_height}, Actual Pixels: {text_height_px}")

                # Translate to the correct position: 58px from the left, vertically centered
                translate_x = 200
                translate_y = img.height // 2
                print(f"Translating to: ({translate_x}, {translate_y})")

                draw.translate(translate_x, translate_y)

                # Rotate the drawing context by -90 degrees
                draw.rotate(-90)
                print("Rotated by -90 degrees.")

                # Adjust the origin to account for the text's width after rotation
                adjust_y = -text_width_px // 2
                print(f"Adjusting origin by: (0, {adjust_y})")
                draw.translate(adjust_y, 0)

                # Draw the text at the new origin (0, 0) after translation and rotation
                print("Drawing text at (0, 0) after transformations.")
                draw.text(0, 0, text)

                # Pop the drawing context
                draw.pop()
                print("Popped drawing context.")

                # =============================================
                # DRAW THE PRIMARY_BIRTH_PLACE INFO
                # =============================================

                draw.push()

                draw.font_size = PRIMARY_PLACE_INFO_FONT_SIZE

                draw.gravity = "south"

                # Draw statements for birthplace
                print(f"Rotating by: {PRIMARY_BIRTH_PLACE_ROTATE} degrees")
                draw.rotate(PRIMARY_BIRTH_PLACE_ROTATE)

                print(f"Setting fill_color to: {PRIMARY_BIRTH_PLACE_COLOR}")
                draw.fill_color = PRIMARY_BIRTH_PLACE_COLOR

                pifx_birth_place, pify_birth_place = PRIMARY_BIRTH_PLACE_X, PRIMARY_BIRTH_PLACE_Y
                draw.text(pifx_birth_place, pify_birth_place, primary_individual.birth_place or " ")
                print(f"Drawn text at ({pifx_birth_place}, {pify_birth_place}): {primary_individual.birth_place or ' '}")

                draw.pop()

                # =============================================
                # DRAW THE PRIMARY_DEATH INFO
                # =============================================

                draw.push()

                draw.font_size = PRIMARY_DATE_INFO_FONT_SIZE
                draw.fill_color = PRIMARY_DEATH_COLOR
                print(f"Setting font to: {PRIMARY_DATE_INFO_FONT_SIZE} & fill color to: {PRIMARY_DEATH_COLOR}")

                draw.gravity = "north"

                # Draw statements for deathdate
                #draw.rotate(180)
                draw.stroke_width = DEFAULT_STROKE_WIDTH



                # Draw primary individual's death date if available
                # Apply death date rotation
                print(f"Rotating by: {PRIMARY_DEATH_ROTATE} degrees")
                draw.rotate(PRIMARY_DEATH_ROTATE)

                pifx_death, pify_death = PRIMARY_DEATH_X, PRIMARY_DEATH_Y
                draw.text(pifx_death, pify_death, primary_individual.death_date or " ")
                print(f"Drawn text at ({pifx_death}, {pify_death}): {primary_individual.death_date or ' '}")

                draw.pop()

                # =============================================
                # DRAW THE PRIMARY_DEATH_PLACE INFO
                # =============================================

                # Push the current drawing context
                draw.push()
                print("Pushed drawing context.")

                draw.font_size = PRIMARY_PLACE_INFO_FONT_SIZE
                draw.fill_color = PRIMARY_DEATH_PLACE_COLOR

                text = primary_individual.death_place or " "
                print(f"Text to draw: '{text}'")

                # Get text metrics
                metrics = draw.get_font_metrics(img, text, False)
                text_width = metrics.text_width
                text_height = metrics.text_height
                print(f"Text dimensions: width={text_width}, height={text_height}")

                # Convert points to pixels
                text_width_px = metrics.text_width * pixel_ratio
                text_height_px = metrics.text_height * pixel_ratio

                print(f"Points: {metrics.text_width}, Actual Pixels: {text_width_px}")
                print(f"Points: {metrics.text_height}, Actual Pixels: {text_height_px}")

                # Translate to the correct position: 1850px from the left, vertically centered
                translate_x = 1850
                translate_y = img.height // 2
                print(f"Translating to: ({translate_x}, {translate_y})")

                draw.translate(translate_x, translate_y)

                # Rotate the drawing context by -90 degrees
                draw.rotate(-90)
                print("Rotated by -90 degrees.")

                # Adjust the origin to account for the text's width after rotation
                adjust_y = -text_width_px // 2
                print(f"Adjusting origin by: (0, {adjust_y})")
                draw.translate(adjust_y, 0)

                # Draw the text at the new origin (0, 0) after translation and rotation
                print("Drawing text at (0, 0) after transformations.")
                draw.text(0, 0, text)

                # Pop the drawing context
                draw.pop()
                print("Popped drawing context.")


                # =============================================
                # DRAW THE IMAGE
                # =============================================

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
