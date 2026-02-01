import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


def generate_2gen_preview(primary_individual, family_data, template="preview", user_settings=None):
    """
    Generate a 2-generation family tree chart using Wand (Python ImageMagick binding)

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type (e.g., '2gen' for 2-generation chart)
        user_settings: Dictionary of user settings to override hardcoded defaults

    Returns:
        BytesIO buffer containing the generated image (PNG for preview, PDF for final)
    """

    # Get user settings or use empty dict if not provided
    user_settings = user_settings or {}

    print(f"DEBUG: generate_2gen_preview received user_settings: {user_settings}")
    print(f"DEBUG: Generating template type: {template}")

    print(f"DEBUG: Generating 2-generation family tree for: {primary_individual.full_name}")
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    try:
        # First, generate the content image (same for both preview and final)
        preview_template_path = os.path.join(settings.BASE_DIR, "apps/hud/static/hud/images/preview_image_templates", "2GEN_PREVIEW.png")

        print(f"DEBUG: Preview template path: {preview_template_path}")
        print(f"DEBUG: Preview template exists: {os.path.exists(preview_template_path)}")

        # Generate the content image (this is what the user sees in preview)
        with Image(filename=preview_template_path, resolution=300) as content_img:
            print(f"Content image loaded: {content_img.width}x{content_img.height}")

            # =============================================
            # TRANSLATION SETTINGS TUNING
            # =============================================

            # Initial translation
            INITIAL_TRANSLATE_X = 0
            INITIAL_TRANSLATE_Y = 0

            # Parent translation
            PARENT_TRANSLATE_X = int(user_settings.get("parent_translate_x", 0))
            PARENT_TRANSLATE_Y = int(user_settings.get("parent_translate_x", 0))

            # =============================================
            # DRAWING SETTINGS TUNING
            # =============================================

            # Font settings
            FONT_FAMILY = str(user_settings.get("font_family", "Arial"))

            print(f"DEBUG: FONT_FAMILY set to: {FONT_FAMILY}")

            # Stroke settings
            DEFAULT_STROKE_WIDTH = float(user_settings.get("default_stroke_width", 0.5))
            PARENT_STROKE_COLOR = Color(user_settings.get("primary_stroke_color", "black"))

            print(f"DEBUG: DEFAULT_STROKE_WIDTH set to: {DEFAULT_STROKE_WIDTH}")
            print(f"DEBUG: PRIMARY_STROKE_COLOR set to: {PRIMARY_STROKE_COLOR}")

            # Drawing quality settings
            STROKE_ANTIALIAS = True

            # =============================================
            # PARENT GENERATION TUNING SETTINGS
            # =============================================

            # Parent colors
            FATHER_FONT_COLOR = Color(user_settings.get("father_font_color", "black"))
            FATHER_BIRTH_COLOR = Color(user_settings.get("father_birth_color", "black"))
            FATHER_BIRTH_PLACE_COLOR = Color(user_settings.get("father_birth_place_color", "black"))
            FATHER_DEATH_COLOR = Color(user_settings.get("father_death_color", "black"))
            FATHER_DEATH_PLACE_COLOR = Color(user_settings.get("father_death_place_color", "black"))

            MOTHER_FONT_COLOR = Color(user_settings.get("mother_font_color", "black"))
            MOTHER_BIRTH_COLOR = Color(user_settings.get("mother_birth_color", "black"))
            MOTHER_BIRTH_PLACE_COLOR = Color(user_settings.get("mother_birth_place_color", "black"))
            MOTHER_DEATH_COLOR = Color(user_settings.get("mother_death_color", "black"))
            MOTHER_DEATH_PLACE_COLOR = Color(user_settings.get("mother_death_place_color", "black"))

            # Parent font sizes
            PARENT_NAME_FONT_SIZE = int(user_settings.get("primary_place_info_font_size", 28))
            PARENT_DATE_INFO_FONT_SIZE = int(user_settings.get("primary_place_info_font_size", 28))
            PARENT_PLACE_INFO_FONT_SIZE = int(user_settings.get("primary_place_info_font_size", 28))


            # Father coordinates
            FATHER_FIRST_X = 0
            FATHER_FIRST_Y = 225
            FATHER_FIRST_ROTATE = 45
            FATHER_MIDDLE_X = 0
            FATHER_MIDDLE_Y = 260
            FATHER_MIDDLE_ROTATE = -45
            FATHER_LAST_X = 0
            FATHER_LAST_Y = 225
            FATHER_LAST_ROTATE = -45
            FATHER_BIRTH_TRANSLATE_X = int(user_settings.get("father_birth_translate_x", 0))
            FATHER_BIRTH_TRANSLATE_Y = int(user_settings.get("father_birth_translate_y", 0))
            FATHER_BIRTH_ROTATE = int(user_settings.get("father_birth_rotate", 0))
            FATHER_BIRTH_PLACE_TRANSLATE_X = int(user_settings.get("father_birth_place_translate_x", 0))
            FATHER_BIRTH_PLACE_TRANSLATE_Y = int(user_settings.get("father_birth_place_translate_y", 0))
            FATHER_BIRTH_PLACE_ROTATE = int(user_settings.get("father_birth_place_rotate", 0))
            FATHER_DEATH_TRANSLATE_X = int(user_settings.get("father_death_translate_x", 0))
            FATHER_DEATH_TRANSLATE_Y = int(user_settings.get("father_death_translate_y", 280))
            FATHER_DEATH_ROTATE = int(user_settings.get("father_death_rotate", -90))
            FATHER_DEATH_PLACE_TRANSLATE_X = int(user_settings.get("father_death_place_translate_x", 0))
            FATHER_DEATH_PLACE_TRANSLATE_Y = int(user_settings.get("father_death_place_translate_y", 280))
            FATHER_DEATH_PLACE_ROTATE = int(user_settings.get("father_death_place_rotate", -90))

            # Mother coordinates
            MOTHER_FIRST_X = 0
            MOTHER_FIRST_Y = 225
            MOTHER_FIRST_ROTATE = -90
            MOTHER_MIDDLE_X = 0
            MOTHER_MIDDLE_Y = 260
            MOTHER_MIDDLE_ROTATE = -45
            MOTHER_LAST_X = 0
            MOTHER_LAST_Y = 225
            MOTHER_LAST_ROTATE = -45
            MOTHER_BIRTH_TRANSLATE_X = int(user_settings.get("mother_birth_translate_x", 0))
            MOTHER_BIRTH_TRANSLATE_Y = int(user_settings.get("mother_birth_translate_y", 0))
            MOTHER_BIRTH_ROTATE = int(user_settings.get("mother_birth_rotate", 0))
            MOTHER_BIRTH_PLACE_TRANSLATE_X = int(user_settings.get("mother_birth_place_translate_x", 0))
            MOTHER_BIRTH_PLACE_TRANSLATE_Y = int(user_settings.get("mother_birth_place_translate_y", 0))
            MOTHER_BIRTH_PLACE_ROTATE = int(user_settings.get("mother_birth_place_rotate", 0))
            MOTHER_DEATH_TRANSLATE_X = int(user_settings.get("mother_death_translate_x", 0))
            MOTHER_DEATH_TRANSLATE_Y = int(user_settings.get("mother_death_translate_y", 280))
            MOTHER_DEATH_ROTATE = int(user_settings.get("mother_death_rotate", -90))
            MOTHER_DEATH_PLACE_TRANSLATE_X = int(user_settings.get("mother_death_place_translate_x", 0))
            MOTHER_DEATH_PLACE_TRANSLATE_Y = int(user_settings.get("mother_death_place_translate_y", 280))
            MOTHER_DEATH_PLACE_ROTATE = int(user_settings.get("mother_death_place_rotate", -90))

            with Drawing() as draw:

                draw.push()

                # Set initial drawing properties
                draw.font = FONT_FAMILY
                draw.font_size = PARENT_NAME_FONT_SIZE
                draw.stroke_antialias = STROKE_ANTIALIAS

                # Initial translation
                print(f"Translating coordinates by (x={INITIAL_TRANSLATE_X}, y={INITIAL_TRANSLATE_Y})")
                draw.translate(x=INITIAL_TRANSLATE_X, y=INITIAL_TRANSLATE_Y)


                # =============================================
                # PARENT GENERATION DRAWING
                # =============================================

                draw.translate(x=PARENT_TRANSLATE_X, y=PARENT_TRANSLATE_Y)

                draw.fill_color = PARENT_INFO_COLOR
                print(f"Setting fill_color to: {PARENT_INFO_COLOR}")

                draw.stroke_color = PARENT_STROKE_COLOR
                print(f"Setting stroke_color to: {PARENT_STROKE_COLOR}")

                # Parents
                father = None
                mother = None

                # =============================================
                # Debug prints before drawing
                # =============================================

                print(f"Primary individual: {primary_individual.full_name}")
                print(f"Birth date: {primary_individual.birth_date} (type: {type(primary_individual.birth_date)})")
                print(f"Birth place: {primary_individual.birth_place}")
                print(f"Father ID: {primary_individual.father}")
                print(f"Mother ID: {primary_individual.mother}")

                if primary_individual.father:
                    father = family_data["individuals"].get(primary_individual.father)
                    print(f"Father: {father.full_name if father else 'None'}")
                    if father:
                        print(f"Father's father ID: {father.father}")
                        print(f"Father's mother ID: {father.mother}")

                if primary_individual.mother:
                    mother = family_data["individuals"].get(primary_individual.mother)
                    print(f"Mother: {mother.full_name if mother else 'None'}")
                    if mother:
                        print(f"Mother's father ID: {mother.father}")
                        print(f"Mother's mother ID: {mother.mother}")

                # =============================================
                # INDI 1 - Surname 0 (Father) DRAWING
                # =============================================

                if primary_individual.father:
                    father = family_data["individuals"].get(primary_individual.father)
                if primary_individual.mother:
                    mother = family_data["individuals"].get(primary_individual.mother)

                if father:
                    print(f"Drawing father: {father.full_name}")
                    # Split father's name into parts
                    name_parts = father.full_name.split()
                    first_name = name_parts[0] if len(name_parts) > 0 else ""
                    middle_name = name_parts[1] if len(name_parts) > 1 else ""
                    last_name = name_parts[-1] if len(name_parts) > 1 else ""

                # =============================================
                # Draw father's first name (default orientation)
                # =============================================

                draw.push()

                fx_first, fy_first, fr_first = (
                    FATHER_FIRST_X,
                    FATHER_FIRST_Y,
                    FATHER_FIRST_ROTATE,
                )
                draw.rotate(fr_first)

                print(f"Setting fill_color to: {FATHER_FONT_COLOR}")
                draw.fill_color = FATHER_FONT_COLOR

                draw.text(fx_first, fy_first, first_name)
                print(f"Drawn father's first name at ({fx_first}, {fy_first}) with rotation {fr_first}: {first_name}")

                draw.pop()

                # =============================================
                # Draw father's middle name (translated upwards and at -45 degrees)
                # =============================================

                draw.push()

                fx_middle, fy_middle, fr_middle = (
                    FATHER_MIDDLE_X,
                    FATHER_MIDDLE_Y,
                    FATHER_MIDDLE_ROTATE,
                )

                draw.rotate(fr_middle)

                draw.text(fx_middle, fy_middle, middle_name)
                print(f"Drawn father's middle name at ({fx_middle}, {fy_middle}) with rotation {fr_middle}: {middle_name}")

                draw.pop()

                # =============================================
                # Draw father's last name (translated further upwards and at -90 degrees)
                # =============================================

                draw.push()

                fx_last, fy_last, fr_last = (
                    FATHER_LAST_X,
                    FATHER_LAST_Y,
                    FATHER_LAST_ROTATE,
                )

                draw.translate(fx_last, fy_last)

                draw.rotate(fr_last)

                draw.text(fx_last, fy_last, last_name)
                print(f"Drawn father's last name at ({fx_last}, {fy_last}) with rotation {fr_last}: {last_name}")

                draw.pop()

                # =============================================
                # Draw father's birth date
                # =============================================

                draw.push()

                fx_birth, fy_birth, fr_birth = (
                    FATHER_BIRTH_TRANSLATE_X,
                    FATHER_BIRTH_TRANSLATE_Y,
                    FATHER_BIRTH_ROTATE,
                )

                draw.translate(fx_birth, fy_birth)

                draw.fill_color = FATHER_BIRTH_COLOR
                draw.font_size = PARENT_DATE_INFO_FONT_SIZE
                print(f"Setting fill_color to: {FATHER_BIRTH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}")

                draw.rotate(fr_birth)

                draw.text(0, 0, father.birth_date or " ")
                print(f"Drawn text at ({fx_birth}, {fy_birth}) with rotation {fr_birth}: {father.birth_date or ' '}")

                draw.pop()

                # =============================================
                # Draw father's birth place
                # =============================================

                draw.push()

                fx_birth_place, fy_birth_place, fr_birth_place = (
                    FATHER_BIRTH_PLACE_TRANSLATE_X,
                    FATHER_BIRTH_PLACE_TRANSLATE_Y,
                    FATHER_BIRTH_PLACE_ROTATE,
                )

                draw.translate(fx_birth_place, fy_birth_place)

                draw.fill_color = FATHER_BIRTH_PLACE_COLOR
                draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                print(f"Setting fill_color to: {FATHER_BIRTH_PLACE_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}")

                draw.rotate(fr_place)

                draw.text(0, 0, father.birth_place or " ")
                print(f"Drawn text at ({fx_birth_place}, {fy_birth_place}) with rotation {fr_place}: {father.birth_place or ' '}")

                draw.pop()

                # =============================================
                # Draw father's death date (if available)
                # =============================================

                draw.push()

                fx_death, fy_death, fr_death = (
                    FATHER_DEATH_TRANSLATE_X,
                    FATHER_DEATH_TRANSLATE_Y,
                    FATHER_DEATH_ROTATE,
                )

                draw.translate(fx_death, fy_death)

                draw.fill_color = FATHER_DEATH_COLOR
                draw.font_size = PARENT_DATE_INFO_FONT_SIZE
                print(f"Setting fill_color to: {FATHER_DEATH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}")

                draw.rotate(fr_death)

                draw.text(0, 0, father.death_date)
                print(f"Drawn text at ({fx_death}, {fy_death}) with rotation {fr_death}: {death_date_text}")

                draw.pop()

                # =============================================
                # Draw father's death place (if available)
                # =============================================

                draw.push()

                fx_death_place, fy_death_place, fr_death_place = (
                    FATHER_DEATH_PLACE_TRANSLATE_X,
                    FATHER_DEATH_PLACE_TRANSLATE_Y,
                    FATHER_DEATH_PLACE_ROTATE,
                )

                draw.translate(fx_death_place, fy_death_place)

                draw.fill_color = FATHER_DEATH_COLOR
                draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                print(f"Setting fill_color to: {FATHER_DEATH_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}")

                draw.rotate(fr_death_place)

                draw.text(0, 0, father.death_place or " ")
                print(f"Drawn text at ({fx_death_place}, {fy_death_place}) with rotation {fr_death_place}: {father.death_place or ' '}")

                draw.pop()

                # =============================================
                # INDI 2 - Surname 1 (Mother) DRAWING
                # =============================================

                if mother:
                    print(f"Drawing mother: {mother.full_name}")
                    # Split mother's name into parts
                    name_parts = mother.full_name.split()
                    first_name = name_parts[0] if len(name_parts) > 0 else ""
                    middle_name = name_parts[1] if len(name_parts) > 1 else ""
                    last_name = name_parts[-1] if len(name_parts) > 1 else ""

                # =============================================
                # Draw mother's first name (flipped upside-down)
                # =============================================

                draw.push()

                mx_first, my_first, mr_first = (
                    MOTHER_FIRST_X,
                    MOTHER_FIRST_Y,
                    MOTHER_FIRST_ROTATE,
                )

                draw.rotate(mr_first)

                print(f"Setting fill_color to: {MOTHER_FONT_COLOR}")
                draw.fill_color = MOTHER_FONT_COLOR

                draw.text(mx_first, my_first, first_name)
                print(f"Drawn mother's first name at ({mx_first}, {my_first}) with rotation {mr_first}: {first_name}")

                draw.pop()

                # =============================================
                # Draw mother's middle name (at 45 degrees)
                # =============================================

                draw.push()

                mx_middle, my_middle, mr_middle = (
                    MOTHER_MIDDLE_X,
                    MOTHER_MIDDLE_Y,
                    MOTHER_MIDDLE_ROTATE,
                )

                draw.rotate(mr_middle)

                draw.text(mx_middle, my_middle, middle_name)
                print(f"Drawn mother's middle name at ({mx_middle}, {my_middle}) with rotation {mr_middle}: {middle_name}")

                draw.pop()

                # =============================================
                # Draw mother's last name (at 90 degrees)
                # =============================================

                draw.push()

                mx_last, my_last, mr_last = (
                    MOTHER_LAST_X,
                    MOTHER_LAST_Y,
                    MOTHER_LAST_ROTATE,
                )

                draw.rotate(mr_last)

                draw.text(mx_last, my_last, last_name)
                print(f"Drawn mother's last name at ({mx_last}, {my_last}) with rotation {mr_last}: {last_name}")

                draw.pop()

                # =============================================
                # Draw mother's birth date
                # =============================================

                draw.push()

                mx_birth, my_birth, mr_birth = (
                    MOTHER_BIRTH_TRANSLATE_X,
                    MOTHER_BIRTH_TRANSLATE_Y,
                    MOTHER_BIRTH_ROTATE,
                )

                draw.translate(mx_birth, my_birth)

                draw.fill_color = MOTHER_BIRTH_COLOR
                draw.font_size = PARENT_DATE_INFO_FONT_SIZE
                print(f"Setting fill_color to: {MOTHER_BIRTH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}")

                draw.rotate(mr_birth)

                draw.text(0, 0, mother.birth_date or " ")
                print(f"Drawn text at ({mx_birth}, {my_birth}) with rotation {mr_birth}: {mother.birth_date or ' '}")

                draw.pop()

                # =============================================
                # Draw mother's birth place
                # =============================================

                draw.push()

                mx_birth_place, my_birth_place, mr_birth_place = (
                    MOTHER_BIRTH_PLACE_TRANSLATE_X,
                    MOTHER_BIRTH_PLACE_TRANSLATE_Y,
                    MOTHER_BIRTH_PLACE_ROTATE,
                )

                draw.translate(mx_birth_place, my_birth_place)

                draw.fill_color = MOTHER_BIRTH_PLACE_COLOR
                draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                print(f"Setting fill_color to: {MOTHER_BIRTH_PLACE_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}")

                draw.rotate(mr_birth_place)

                draw.text(0, 0, mother.birth_place or " ")
                print(f"Drawn text at ({mx_birth_place}, {my_birth_place}) with rotation {mr_birth_place}: {mother.birth_place or ' '}")

                draw.pop()

                # =============================================
                # Draw mother's death date (if available)
                # =============================================

                draw.push()

                mx_death, my_death, mr_death = (
                    MOTHER_DEATH_TRANSLATE_X,
                    MOTHER_DEATH_TRANSLATE_Y,
                    MOTHER_DEATH_ROTATE,
                )

                draw.translate(mx_death, my_death)

                draw.fill_color = MOTHER_DEATH_COLOR
                draw.font_size = PARENT_DATE_INFO_FONT_SIZE
                print(f"Setting fill_color to: {MOTHER_DEATH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}")

                draw.rotate(mr_death)

                draw.text(0, 0, mother.death_date)
                print(f"Drawn text at ({mx_death}, {my_death}) with rotation {mr_death}: {death_date_text}")

                draw.pop()

                # =============================================
                # Draw mother's death place (if available)
                # =============================================

                draw.push()

                mx_death_place, my_death_place, mr_death_place = (
                    MOTHER_DEATH_PLACE_TRANSLATE_X,
                    MOTHER_DEATH_PLACE_TRANSLATE_Y,
                    MOTHER_DEATH_PLACE_ROTATE,
                )

                draw.translate(mx_death_place, my_death_place)

                draw.fill_color = MOTHER_DEATH_COLOR
                draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                print(f"Setting fill_color to: {MOTHER_DEATH_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}")

                draw.rotate(mr_death_place)

                draw.text(0, 0, mother.death_place or " ")
                print(f"Drawn text at ({mx_death_place}, {my_death_place}) with rotation {mr_death_place}: {mother.death_place or ' '}")

                draw.pop()

                # Apply the drawing to the image
                draw(content_img)

                # 3. Load and composite the 1Gen overlay *after* drawing
                with Image(filename='gen1_img_buffer') as gen1_overlay:
                    gen1_overlay.resize(int(gen1_overlay.width * 0.48), int(gen1_overlay.height * 0.48))
                    content_img.composite(gen1_overlay, left=800, top=1070)

                # For preview mode, return the content image directly
                if template == "preview":
                    print("DEBUG: Returning preview image")
                    gen2_image_buffer = BytesIO()
                    content_img.save(file=gen2_image_buffer)
                    gen2_image_buffer.seek(0)
                    return gen2_image_buffer

                # For final chart mode, composite the content image onto the PDF base template
                elif template == "final":
                    print("DEBUG: Compositing content onto PDF base template")

                    # Load the PDF base template
                    base_template_path = os.path.join(settings.BASE_DIR, "apps/charts/static/charts/images/base_image_templates", "US_LETTER_2GEN_BW.pdf")
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
                        pdf_buffer = BytesIO()
                        base_img.save(file=pdf_buffer)
                        pdf_buffer.seek(0)

                        return pdf_buffer

    except Exception as e:
        print(f"ERROR: Failed to generate chart: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
