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

            # Subject translation
            # SUBJECT_TRANSLATE_X = 0
            # SUBJECT_TRANSLATE_Y = 0

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

                draw.rotate(180)

                draw.translate(x=PARENT_TRANSLATE_X, y=PARENT_TRANSLATE_Y)

                print(f"Setting fill_color to: {PARENT_INFO_COLOR}")
                draw.fill_color = PARENT_INFO_COLOR

                print(f"Setting stroke_color to: {PARENT_STROKE_COLOR}")
                draw.stroke_color = PARENT_STROKE_COLOR

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

                    ffx_first, ffy_first, ffr_first = (
                        FATHER_FIRST_X,
                        FATHER_FIRST_Y,
                        FATHER_FIRST_ROTATE,
                    )
                    draw.rotate(ffr_first)

                    print(f"Setting fill_color to: {FATHER_FONT_COLOR}")
                    draw.fill_color = FATHER_FONT_COLOR

                    draw.text(ffx_first, ffy_first, first_name)
                    print(f"Drawn father's first name at ({ffx_first}, {ffy_first}) with rotation {ffr_first}: {first_name}")

                    # =============================================
                    # Draw father's middle name (translated upwards and at -45 degrees)
                    # =============================================

                    ffx_middle, ffy_middle, ffr_middle = (
                        FATHER_MIDDLE_X,
                        FATHER_MIDDLE_Y,
                        FATHER_MIDDLE_ROTATE,
                    )

                    draw.rotate(ffr_middle)

                    draw.text(ffx_middle, ffy_middle, middle_name)
                    print(f"Drawn father's middle name at ({ffx_middle}, {ffy_middle}) with rotation {ffr_middle}: {middle_name}")

                    # =============================================
                    # Draw father's last name (translated further upwards and at -90 degrees)
                    # =============================================

                    ffx_last, ffy_last, ffr_last = (
                        FATHER_LAST_X,
                        FATHER_LAST_Y,
                        FATHER_LAST_ROTATE,
                    )

                    draw.rotate(ffr_last)

                    draw.text(ffx_last, ffy_last, last_name)
                    print(f"Drawn father's last name at ({ffx_last}, {ffy_last}) with rotation {ffr_last}: {last_name}")

                    # Reset rotate for other elements
                    print("Rotating by: 90 degrees")
                    draw.rotate(90)
                    print("Reset rotation to 90 degrees for father's birth date and place")

                    # =============================================
                    # Draw father's birth date
                    # =============================================

                    ffx_birth, ffy_birth, ffr_birth = (
                        FATHER_BIRTH_TRANSLATE_X,
                        FATHER_BIRTH_TRANSLATE_Y,
                        FATHER_BIRTH_ROTATE,
                    )

                    draw.translate(ffx_birth, ffy_birth)

                    draw.fill_color = FATHER_BIRTH_COLOR
                    draw.font_size = PARENT_DATE_INFO_FONT_SIZE
                    print(f"Setting fill_color to: {FATHER_BIRTH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}")

                    draw.rotate(ffr_birth)

                    draw.text(0, 0, father.birth_date or " ")
                    print(f"Drawn text at ({ffx_birth}, {ffy_birth}) with rotation {ffr_birth}: {father.birth_date or ' '}")

                    # =============================================
                    # Draw father's birth place
                    # =============================================

                    ffx_birth_place, ffy_birth_place, ffr_birth_place = (
                        FATHER_BIRTH_PLACE_TRANSLATE_X,
                        FATHER_BIRTH_PLACE_TRANSLATE_Y,
                        FATHER_BIRTH_PLACE_ROTATE,
                    )

                    draw.translate(ffx_birth_place, ffy_birth_place)

                    draw.fill_color = FATHER_BIRTH_PLACE_COLOR
                    draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                    print(f"Setting fill_color to: {FATHER_BIRTH_PLACE_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}")

                    draw.rotate(ffr_place)

                    draw.text(0, 0, father.birth_place or " ")
                    print(f"Drawn text at ({ffx_birth_place}, {ffy_birth_place}) with rotation {ffr_place}: {father.birth_place or ' '}")

                    # =============================================
                    # Draw father's death date (if available)
                    # =============================================

                    ffx_death, ffy_death, ffr_death = (
                        FATHER_DEATH_TRANSLATE_X,
                        FATHER_DEATH_TRANSLATE_Y,
                        FATHER_DEATH_ROTATE,
                    )

                    draw.translate(ffx_death, ffy_death)

                    draw.fill_color = FATHER_DEATH_COLOR
                    draw.font_size = PARENT_DATE_INFO_FONT_SIZE
                    print(f"Setting fill_color to: {FATHER_DEATH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}")

                    draw.rotate(ffr_death)

                    draw.text(0, 0, father.death_date)
                    print(f"Drawn text at ({ffx_death}, {ffy_death}) with rotation {ffr_death}: {death_date_text}")

                    # =============================================
                    # Draw father's death place (if available)
                    # =============================================

                    ffx_death_place, ffy_death_place, ffr_death_place = (
                        FATHER_DEATH_PLACE_TRANSLATE_X,
                        FATHER_DEATH_PLACE_TRANSLATE_Y,
                        FATHER_DEATH_PLACE_ROTATE,
                    )

                    draw.translate(ffx_death_place, ffy_death_place)

                    draw.fill_color = FATHER_DEATH_COLOR
                    draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                    print(f"Setting fill_color to: {FATHER_DEATH_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}")

                    draw.rotate(ffr_death_place)

                    draw.text(0, 0, father.death_place or " ")
                    print(f"Drawn text at ({ffx_death_place}, {ffy_death_place}) with rotation {ffr_death_place}: {father.death_place or ' '}")


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

                    mfx_first, mfy_first, mfr_first = (
                        MOTHER_FIRST_X,
                        MOTHER_FIRST_Y,
                        MOTHER_FIRST_ROTATE,
                    )

                    draw.rotate(mfr_first)

                    print(f"Setting fill_color to: {MOTHER_FONT_COLOR}")
                    draw.fill_color = MOTHER_FONT_COLOR

                    draw.text(mfx_first, mfy_first, first_name)
                    print(f"Drawn mother's first name at ({mfx_first}, {mfy_first}) with rotation {mfr_first}: {first_name}")

                    # =============================================
                    # Draw mother's middle name (at 45 degrees)
                    # =============================================

                    mfx_middle, mfy_middle, mfr_middle = (
                        MOTHER_MIDDLE_X,
                        MOTHER_MIDDLE_Y,
                        MOTHER_MIDDLE_ROTATE,
                    )

                    draw.rotate(mfr_middle)

                    draw.text(mfx_middle, mfy_middle, middle_name)
                    print(f"Drawn mother's middle name at ({mfx_middle}, {mfy_middle}) with rotation {mfr_middle}: {middle_name}")

                    # =============================================
                    # Draw mother's last name (at 90 degrees)
                    # =============================================

                    mfx_last, mfy_last, mfr_last = (
                        MOTHER_LAST_X,
                        MOTHER_LAST_Y,
                        MOTHER_LAST_ROTATE,
                    )

                    draw.rotate(mfr_last)

                    draw.text(mfx_last, mfy_last, last_name)
                    print(f"Drawn mother's last name at ({mfx_last}, {mfy_last}) with rotation {mfr_last}: {last_name}")

                    # Reset rotate for other elements
                    print("Rotating by: 90 degrees")
                    draw.rotate(90)
                    print("Reset rotation to 90 degrees for mother's birth date and place")

                    # =============================================
                    # Draw mother's birth date
                    # =============================================

                    mfx_birth, mfy_birth, mfr_birth = (
                        MOTHER_BIRTH_TRANSLATE_X,
                        MOTHER_BIRTH_TRANSLATE_Y,
                        MOTHER_BIRTH_ROTATE,
                    )

                    draw.translate(mfx_birth, mfy_birth)

                    draw.fill_color = MOTHER_BIRTH_COLOR
                    draw.font_size = PARENT_DATE_INFO_FONT_SIZE
                    print(f"Setting fill_color to: {MOTHER_BIRTH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}")

                    draw.rotate(mfr_birth)

                    draw.text(0, 0, mother.birth_date or " ")
                    print(f"Drawn text at ({mfx_birth}, {mfy_birth}) with rotation {mfr_birth}: {mother.birth_date or ' '}")

                    # =============================================
                    # Draw mother's birth place
                    # =============================================

                    mfx_birth_place, mfy_birth_place, mfr_birth_place = (
                        MOTHER_BIRTH_PLACE_TRANSLATE_X,
                        MOTHER_BIRTH_PLACE_TRANSLATE_Y,
                        MOTHER_BIRTH_PLACE_ROTATE,
                    )

                    draw.translate(mfx_birth_place, mfy_birth_place)

                    draw.fill_color = MOTHER_BIRTH_PLACE_COLOR
                    draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                    print(f"Setting fill_color to: {MOTHER_BIRTH_PLACE_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}")

                    draw.rotate(mfr_birth_place)

                    draw.text(0, 0, mother.birth_place or " ")
                    print(f"Drawn text at ({mfx_birth_place}, {mfy_birth_place}) with rotation {mfr_birth_place}: {mother.birth_place or ' '}")

                    # =============================================
                    # Draw mother's death date (if available)
                    # =============================================

                    mfx_death, mfy_death, mfr_death = (
                        MOTHER_DEATH_TRANSLATE_X,
                        MOTHER_DEATH_TRANSLATE_Y,
                        MOTHER_DEATH_ROTATE,
                    )

                    draw.translate(mfx_death, mfy_death)

                    draw.fill_color = MOTHER_DEATH_COLOR
                    draw.font_size = PARENT_DATE_INFO_FONT_SIZE
                    print(f"Setting fill_color to: {MOTHER_DEATH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}")

                    draw.rotate(mfr_death)

                    draw.text(0, 0, mother.death_date)
                    print(f"Drawn text at ({mfx_death}, {mfy_death}) with rotation {mfr_death}: {death_date_text}")

                    # =============================================
                    # Draw mother's death place (if available)
                    # =============================================

                    mfx_death_place, mfy_death_place, mfr_death_place = (
                        MOTHER_DEATH_PLACE_TRANSLATE_X,
                        MOTHER_DEATH_PLACE_TRANSLATE_Y,
                        MOTHER_DEATH_PLACE_ROTATE,
                    )

                    draw.translate(mfx_death_place, mfy_death_place)

                    draw.fill_color = MOTHER_DEATH_COLOR
                    draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                    print(f"Setting fill_color to: {MOTHER_DEATH_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}")

                    draw.rotate(mfr_death_place)

                    draw.text(0, 0, mother.death_place or " ")
                    print(f"Drawn text at ({mfx_death_place}, {mfy_death_place}) with rotation {mfr_death_place}: {mother.death_place or ' '}")

                # Apply the drawing to the image
                draw(img)

                # 3. Load and composite the 1Gen overlay *after* drawing
                with Image(filename='overlay_image.png') as overlay_img:
                    overlay_img.resize(int(overlay_img.width * 0.48), int(overlay_img.height * 0.5))
                    main_img.composite(overlay_img, left=811, top=1073)

                # For preview mode, return the content image directly
                if template == "preview":
                    print("DEBUG: Returning preview image")
                    img_buffer = BytesIO()
                    content_img.save(file=img_buffer)
                    img_buffer.seek(0)
                    return img_buffer

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
                        img_buffer = BytesIO()
                        base_img.save(file=img_buffer)
                        img_buffer.seek(0)

                        return img_buffer

    except Exception as e:
        print(f"ERROR: Failed to generate chart: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
