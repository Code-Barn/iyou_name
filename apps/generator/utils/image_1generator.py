import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

logger = logging.getLogger(__name__)


def generate_1gen_preview(primary_individual, family_data, template="preview", user_settings=None):
    """
    Generate a 1-generation chart using Wand (Python ImageMagick binding)

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type ('preview' for PNG preview, 'final' for PDF final chart)
        user_settings: Dictionary of user settings to override hardcoded defaults

    Returns:
        BytesIO buffer containing the generated image (PNG for preview, PDF for final)
    """
    # Get user settings or use empty dict if not provided
    user_settings = user_settings or {}

    print(f"DEBUG: generate_1gen_preview received user_settings: {user_settings}")
    print(f"DEBUG: Generating template type: {template}")

    print(f"DEBUG: Generating 1-generation family tree for: {primary_individual.full_name}")
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    try:
        # First, generate the content image (same for both preview and final)
        preview_template_path = os.path.join(settings.BASE_DIR, "apps/hud/static/hud/images/preview_image_templates", "1GEN_PREVIEW.png")

        print(f"DEBUG: Preview template path: {preview_template_path}")
        print(f"DEBUG: Preview template exists: {os.path.exists(preview_template_path)}")

        # Generate the content image (this is what the user sees in preview)
        with Image(filename=preview_template_path, resolution=300) as content_img:
            print(f"Content image loaded: {content_img.width}x{content_img.height}")

            # =============================================
            # COLORED BACKGROUND COORDINATES
            # =============================================
            # Color square coordinates
            BACKGROUND_LEFT = 13
            BACKGROUND_TOP = 13
            BACKGROUND_WIDTH = 1923
            BACKGROUND_HEIGHT = 1923

            # =============================================
            # TRANSLATION SETTINGS TUNING
            # =============================================

            # Initial translation (not used in final PDF)
            INITIAL_TRANSLATE_X = 0
            INITIAL_TRANSLATE_Y = 0


            # =============================================
            # DRAWING SETTINGS TUNING
            # =============================================

            # Font settings
            FONT_FAMILY = str(user_settings.get("font_family", "Arial"))

            print(f"DEBUG: FONT_FAMILY set to: {FONT_FAMILY}")

            # Stroke settings
            PRIMARY_STROKE_WIDTH = float(user_settings.get("primary_stroke_width", 0.5))
            PRIMARY_STROKE_COLOR = Color(user_settings.get("primary_stroke_color", "black"))
            INFO_STROKE_WIDTH = float(user_settings.get("info_stroke_width", 0.25))
            INFO_STROKE_COLOR = Color(user_settings.get("info_stroke_color", "gray"))

            print(f"DEBUG: PRIMARY_STROKE_WIDTH set to: {PRIMARY_STROKE_WIDTH}")
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

            # Primary individual coordinates (using primary translation instead of direct positioning)
            PRIMARY_TRANSLATE_X = int(user_settings.get("primary_translate_x", 0))
            PRIMARY_TRANSLATE_Y = int(user_settings.get("primary_translate_y", 0))
            PRIMARY_NAME_ROTATE = int(user_settings.get("primary_name_rotate", -45))
            PRIMARY_BIRTH_TRANSLATE_X = int(user_settings.get("primary_birth_translate_x", 0))
            PRIMARY_BIRTH_TRANSLATE_Y = int(user_settings.get("primary_birth_translate_y", 0))
            PRIMARY_BIRTH_ROTATE = int(user_settings.get("primary_birth_rotate", -90))
            PRIMARY_BIRTH_PLACE_TRANSLATE_X = int(user_settings.get("primary_birth_place_translate_x", 0))
            PRIMARY_BIRTH_PLACE_TRANSLATE_Y = int(user_settings.get("primary_birth_place_translate_y", 0))
            PRIMARY_BIRTH_PLACE_ROTATE = int(user_settings.get("primary_birth_place_rotate", 0))
            PRIMARY_DEATH_TRANSLATE_X = int(user_settings.get("primary_death_translate_x", 0))
            PRIMARY_DEATH_TRANSLATE_Y = int(user_settings.get("primary_death_translate_y", 0))
            PRIMARY_DEATH_ROTATE = int(user_settings.get("primary_death_rotate", 0))
            PRIMARY_DEATH_PLACE_TRANSLATE_X = int(user_settings.get("primary_death_place_translate_x", 0))
            PRIMARY_DEATH_PLACE_TRANSLATE_Y = int(user_settings.get("primary_death_place_translate_y", 0))
            PRIMARY_DEATH_PLACE_ROTATE = int(user_settings.get("primary_death_place_rotate", -90))

            print(f"DEBUG: PRIMARY_TRANSLATE_X set to: {PRIMARY_TRANSLATE_X}")
            print(f"DEBUG: PRIMARY_TRANSLATE_Y set to: {PRIMARY_TRANSLATE_Y}")
            print(f"DEBUG: PRIMARY_NAME_ROTATE set to: {PRIMARY_NAME_ROTATE}")
            print(f"DEBUG: PRIMARY_BIRTH_TRANSLATE_X set to: {PRIMARY_BIRTH_TRANSLATE_X}")
            print(f"DEBUG: PRIMARY_BIRTH_TRANSLATE_Y set to: {PRIMARY_BIRTH_TRANSLATE_Y}")
            print(f"DEBUG: PRIMARY_BIRTH_ROTATE set to: {PRIMARY_BIRTH_ROTATE}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_TRANSLATE_X set to: {PRIMARY_BIRTH_PLACE_TRANSLATE_X}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_TRANSLATE_Y set to: {PRIMARY_BIRTH_PLACE_TRANSLATE_Y}")
            print(f"DEBUG: PRIMARY_BIRTH_PLACE_ROTATE set to: {PRIMARY_BIRTH_PLACE_ROTATE}")
            print(f"DEBUG: PRIMARY_DEATH_TRANSLATE_X set to: {PRIMARY_DEATH_TRANSLATE_X}")
            print(f"DEBUG: PRIMARY_DEATH_TRANSLATE_Y set to: {PRIMARY_DEATH_TRANSLATE_Y}")
            print(f"DEBUG: PRIMARY_DEATH_ROTATE set to: {PRIMARY_DEATH_ROTATE}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_TRANSLATE_X set to: {PRIMARY_DEATH_PLACE_TRANSLATE_X}")
            print(f"DEBUG: PRIMARY_DEATH_PLACE_TRANSLATE_Y set to: {PRIMARY_DEATH_PLACE_TRANSLATE_Y}")
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
                # INDI 0 - Surname 0 (Subject) DRAWING aka "Primary Individual"
                # =============================================

                # Subject translation
                draw.translate(x=PRIMARY_TRANSLATE_X, y=PRIMARY_TRANSLATE_Y)
                print(f"Translating coordinates by (x={PRIMARY_TRANSLATE_X}, y={PRIMARY_TRANSLATE_Y})")

                draw.stroke_width = PRIMARY_STROKE_WIDTH
                draw.stroke_color = PRIMARY_STROKE_COLOR
                print(f"Setting stroke_width to: {PRIMARY_STROKE_WIDTH}")
                print(f"Setting stroke_color to: {PRIMARY_STROKE_COLOR}")

                draw.fill_color = PRIMARY_FONT_COLOR
                print(f"Setting fill_color to: {PRIMARY_FONT_COLOR}")

                draw.gravity = "center"
                print("Setting gravity to: center")

                draw.rotate(PRIMARY_NAME_ROTATE)
                print(f"Rotating by: {PRIMARY_NAME_ROTATE} degrees")

                # Surname 0, Self / Subject, Surname 0 (Primary individual)
                print(f"Drawing primary individual: {primary_individual.full_name}")

                # Split the primary individual's name into parts
                name_parts = primary_individual.full_name.split()
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                middle_name = name_parts[1] if len(name_parts) > 1 else ""
                last_name = name_parts[-1] if len(name_parts) > 1 else ""

                # Draw each part of the name with newline characters and centered alignment
                # Using 0,0 coordinates since primary translation handles positioning
                draw.text(0, 0, f"{first_name}\n{middle_name}\n{last_name}")
                print(f"Drawn text at (0, 0) with primary translation ({PRIMARY_TRANSLATE_X}, {PRIMARY_TRANSLATE_Y}): {first_name}\n{middle_name}\n{last_name}")


                draw.pop()

                draw.font = FONT_FAMILY
                draw.stroke_color = INFO_STROKE_COLOR
                draw.stroke_width = INFO_STROKE_WIDTH
                draw.stroke_antialias = STROKE_ANTIALIAS

                # =============================================
                # CALCULATE DPI
                # =============================================

                dpi = 300
                pixel_ratio = dpi / 72  # Approx 4.1667

                # =============================================
                # DRAW THE PRIMARY_BIRTH INFO
                # =============================================

                # Push the current drawing context
                draw.push()
                print("Pushed drawing context.")

                draw.font_size = PRIMARY_DATE_INFO_FONT_SIZE
                draw.fill_color = PRIMARY_BIRTH_COLOR
                print(f"Setting font to: {PRIMARY_DATE_INFO_FONT_SIZE} & fill color to: {PRIMARY_BIRTH_COLOR}")

                text = primary_individual.birth_date or " "
                print(f"Text to draw: '{text}'")

                # Get text metrics
                metrics = draw.get_font_metrics(content_img, text, False)
                text_width = metrics.text_width
                text_height = metrics.text_height
                print(f"Text dimensions: width={text_width}, height={text_height}")

                # Convert points to pixels
                text_width_px = metrics.text_width * pixel_ratio
                text_height_px = metrics.text_height * pixel_ratio

                print(f"Points: {metrics.text_width}, Actual Pixels: {text_width_px}")
                print(f"Points: {metrics.text_height}, Actual Pixels: {text_height_px}")

                # Translate to the correct position: 200px from the left, vertically centered
                translate_x = 200 + PRIMARY_BIRTH_TRANSLATE_X
                translate_y = content_img.height // 2 + PRIMARY_BIRTH_TRANSLATE_Y
                print(f"Translating to: ({translate_x}, {translate_y})")

                draw.translate(translate_x, translate_y)

                # Rotate the drawing context by -90 degrees
                draw.rotate(PRIMARY_BIRTH_ROTATE)
                print(f"Rotated by {PRIMARY_BIRTH_ROTATE} degrees.")

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
                draw.fill_color = PRIMARY_BIRTH_PLACE_COLOR
                print(f"Setting font to: {PRIMARY_PLACE_INFO_FONT_SIZE} & fill color to: {PRIMARY_BIRTH_PLACE_COLOR}")

                text = primary_individual.birth_place or " "
                print(f"Text to draw: '{text}'")

                # Get text metrics
                metrics = draw.get_font_metrics(content_img, text, False)
                text_width = metrics.text_width
                text_height = metrics.text_height
                print(f"Text dimensions: width={text_width}, height={text_height}")

                # Convert points to pixels
                text_width_px = metrics.text_width * pixel_ratio
                text_height_px = metrics.text_height * pixel_ratio

                print(f"Points: {metrics.text_width}, Actual Pixels: {text_width_px}")
                print(f"Points: {metrics.text_height}, Actual Pixels: {text_height_px}")

                # Translate to the correct position: 200px from the left, vertically centered
                translate_x = content_img.width // 2 + PRIMARY_BIRTH_PLACE_TRANSLATE_X
                translate_y = 1875 + PRIMARY_BIRTH_PLACE_TRANSLATE_Y
                print(f"Translating to: ({translate_x}, {translate_y})")

                draw.translate(translate_x, translate_y)

                # Draw statements for birthplace
                print(f"Rotating by: {PRIMARY_BIRTH_PLACE_ROTATE} degrees")
                draw.rotate(PRIMARY_BIRTH_PLACE_ROTATE)

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
                # DRAW THE PRIMARY_DEATH INFO
                # =============================================
                draw.push()

                draw.font_size = PRIMARY_DATE_INFO_FONT_SIZE
                draw.fill_color = PRIMARY_DEATH_COLOR
                print(f"Setting font to: {PRIMARY_PLACE_INFO_FONT_SIZE} & fill color to: {PRIMARY_DEATH_COLOR}")

                text = primary_individual.death_date or " "
                print(f"Text to draw: '{text}'")

                # Get text metrics
                metrics = draw.get_font_metrics(content_img, text, False)
                text_width = metrics.text_width
                text_height = metrics.text_height
                print(f"Text dimensions: width={text_width}, height={text_height}")

                # Convert points to pixels
                text_width_px = metrics.text_width * pixel_ratio
                text_height_px = metrics.text_height * pixel_ratio

                print(f"Points: {metrics.text_width}, Actual Pixels: {text_width_px}")
                print(f"Points: {metrics.text_height}, Actual Pixels: {text_height_px}")

                # Translate to the correct position: 200px from the left, vertically centered
                translate_x = content_img.width // 2 + PRIMARY_DEATH_TRANSLATE_X
                translate_y = 200 + PRIMARY_DEATH_TRANSLATE_Y
                print(f"Translating to: ({translate_x}, {translate_y})")

                draw.translate(translate_x, translate_y)

                # Draw statements for birthplace
                print(f"Rotating by: {PRIMARY_BIRTH_PLACE_ROTATE} degrees")
                draw.rotate(PRIMARY_BIRTH_PLACE_ROTATE)

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
                metrics = draw.get_font_metrics(content_img, text, False)
                text_width = metrics.text_width
                text_height = metrics.text_height
                print(f"Text dimensions: width={text_width}, height={text_height}")

                # Convert points to pixels
                text_width_px = metrics.text_width * pixel_ratio
                text_height_px = metrics.text_height * pixel_ratio

                print(f"Points: {metrics.text_width}, Actual Pixels: {text_width_px}")
                print(f"Points: {metrics.text_height}, Actual Pixels: {text_height_px}")

                # Translate to the correct position: 1850px from the left, vertically centered
                translate_x = 1875 + PRIMARY_DEATH_PLACE_TRANSLATE_X
                translate_y = content_img.height // 2 + PRIMARY_DEATH_PLACE_TRANSLATE_Y
                print(f"Translating to: ({translate_x}, {translate_y})")

                draw.translate(translate_x, translate_y)

                # Rotate the drawing context by -90 degrees
                draw.rotate(PRIMARY_DEATH_PLACE_ROTATE)
                print(f"Rotated by {PRIMARY_DEATH_PLACE_ROTATE} degrees.")

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

                # Apply the drawing to the content image
                draw(content_img)

                # For preview mode, return the content image directly
                if template == "preview":
                    print("DEBUG: Returning preview image")
                    gen1_img_buffer = BytesIO()
                    content_img.save(file=gen1_img_buffer)
                    gen1_img_buffer.seek(0)
                    return gen1_img_buffer

                # For final chart mode, composite the content image onto the PDF base template
                elif template == "final":
                    print("DEBUG: Compositing content onto PDF base template")

                    # Load the PDF base template
                    base_template_path = os.path.join(settings.BASE_DIR, "apps/charts/static/charts/images/base_image_templates", "US_LETTER_1GEN_BW.pdf")
                    print(f"DEBUG: Base template path: {base_template_path}")
                    print(f"DEBUG: Base template exists: {os.path.exists(base_template_path)}")

                    with Image(filename=base_template_path, resolution=300) as base_img:
                        print(f"Base template loaded: {base_img.width}x{base_img.height}")

                        # Composite the content image onto the base template
                        # Position: 300px right, 570px down
                        composite_x = 300
                        composite_y = 570

                        print(f"DEBUG: Compositing content image at position ({composite_x}, {composite_y})")
                        base_img.composite(content_img, left=composite_x, top=composite_y)

                        # Save the final result as PDF
                        gen1_img_buffer = BytesIO()
                        base_img.save(file=gen1_img_buffer)
                        gen1_img_buffer.seek(0)

                        return gen1_img_buffer

    except Exception as e:
        print(f"ERROR: Failed to generate chart: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
