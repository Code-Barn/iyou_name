import logging
import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.image_1generator import generate_1gen_preview
from apps.generator.utils.settings_helper import extract_generation_settings


def generate_2gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
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

    # Extract PARENT settings for 2gen-specific drawing
    parent_settings = extract_generation_settings(user_settings, "PARENT")
    print(f"DEBUG: Extracted PARENT settings: {parent_settings}")

    print(
        f"DEBUG: Generating 2-generation family tree for: {primary_individual.full_name}"
    )
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    try:
        # First, generate the content image (same for both preview and final)
        preview_template_path = os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "2GEN_PREVIEW.png",
        )

        print(f"DEBUG: Preview template path: {preview_template_path}")
        print(
            f"DEBUG: Preview template exists: {os.path.exists(preview_template_path)}"
        )

        # Generate the content image (this is what the user sees in preview)
        with Image(filename=preview_template_path, resolution=300) as content_img:
            print(f"Content image loaded: {content_img.width}x{content_img.height}")

            # =============================================
            # TRANSLATION SETTINGS TUNING
            # =============================================

            # Initial translation
            INITIAL_TRANSLATE_X = 350
            INITIAL_TRANSLATE_Y = 350

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
            PARENT_STROKE_COLOR = Color(
                user_settings.get("parent_stroke_color", "black")
            )
            INFO_STROKE_COLOR = Color(user_settings.get("info_stroke_color", "black"))
            print(f"DEBUG: DEFAULT_STROKE_WIDTH set to: {DEFAULT_STROKE_WIDTH}")
            print(f"DEBUG: PARENT_STROKE_COLOR set to: {PARENT_STROKE_COLOR}")

            # Drawing quality settings
            STROKE_ANTIALIAS = True

            # =============================================
            # PARENT GENERATION TUNING SETTINGS
            # =============================================

            # Parent colors
            FATHER_FONT_COLOR = Color(user_settings.get("father_font_color", "black"))
            FATHER_BIRTH_COLOR = Color(user_settings.get("father_birth_color", "black"))
            FATHER_BIRTH_PLACE_COLOR = Color(
                user_settings.get("father_birth_place_color", "black")
            )
            FATHER_DEATH_COLOR = Color(user_settings.get("father_death_color", "black"))
            FATHER_DEATH_PLACE_COLOR = Color(
                user_settings.get("father_death_place_color", "black")
            )

            MOTHER_FONT_COLOR = Color(user_settings.get("mother_font_color", "black"))
            MOTHER_BIRTH_COLOR = Color(user_settings.get("mother_birth_color", "black"))
            MOTHER_BIRTH_PLACE_COLOR = Color(
                user_settings.get("mother_birth_place_color", "black")
            )
            MOTHER_DEATH_COLOR = Color(user_settings.get("mother_death_color", "black"))
            MOTHER_DEATH_PLACE_COLOR = Color(
                user_settings.get("mother_death_place_color", "black")
            )

            # Parent font sizes
            PARENT_NAME_FONT_SIZE = int(
                user_settings.get("primary_place_info_font_size", 28)
            )
            PARENT_DATE_INFO_FONT_SIZE = int(
                user_settings.get("primary_place_info_font_size", 28)
            )
            PARENT_PLACE_INFO_FONT_SIZE = int(
                user_settings.get("primary_place_info_font_size", 28)
            )

            # Father coordinates
            FATHER_FIRST_TRANSLATE_X = int(
                user_settings.get("father_first_translate_x", 975)
            )
            FATHER_FIRST_TRANSLATE_Y = int(
                user_settings.get("father_first_translate_y", 1700)
            )
            FATHER_FIRST_ROTATE = int(user_settings.get("father_first_rotate", 0))
            FATHER_MIDDLE_TRANSLATE_X = int(
                user_settings.get("father_middle_translate_x", 0)
            )
            FATHER_MIDDLE_TRANSLATE_Y = int(
                user_settings.get("father_middle_translate_y", 0)
            )
            FATHER_MIDDLE_ROTATE = int(user_settings.get("father_middle_rotate", 0))
            FATHER_LAST_TRANSLATE_X = int(
                user_settings.get("father_last_translate_x", 0)
            )
            FATHER_LAST_TRANSLATE_Y = int(
                user_settings.get("father_last_translate_y", 0)
            )
            FATHER_LAST_ROTATE = int(user_settings.get("father_last_rotate", 0))
            FATHER_BIRTH_TRANSLATE_X = int(
                user_settings.get("father_birth_translate_x", 0)
            )
            FATHER_BIRTH_TRANSLATE_Y = int(
                user_settings.get("father_birth_translate_y", 0)
            )
            FATHER_BIRTH_ROTATE = int(user_settings.get("father_birth_rotate", 0))
            FATHER_BIRTH_PLACE_TRANSLATE_X = int(
                user_settings.get("father_birth_place_translate_x", 0)
            )
            FATHER_BIRTH_PLACE_TRANSLATE_Y = int(
                user_settings.get("father_birth_place_translate_y", 0)
            )
            FATHER_BIRTH_PLACE_ROTATE = int(
                user_settings.get("father_birth_place_rotate", 0)
            )
            FATHER_DEATH_TRANSLATE_X = int(
                user_settings.get("father_death_translate_x", 0)
            )
            FATHER_DEATH_TRANSLATE_Y = int(
                user_settings.get("father_death_translate_y", 280)
            )
            FATHER_DEATH_ROTATE = int(user_settings.get("father_death_rotate", -90))
            FATHER_DEATH_PLACE_TRANSLATE_X = int(
                user_settings.get("father_death_place_translate_x", 0)
            )
            FATHER_DEATH_PLACE_TRANSLATE_Y = int(
                user_settings.get("father_death_place_translate_y", 280)
            )
            FATHER_DEATH_PLACE_ROTATE = int(
                user_settings.get("father_death_place_rotate", -90)
            )

            # Mother coordinates
            MOTHER_FIRST_TRANSLATE_X = int(
                user_settings.get("mother_first_translate_x", 0)
            )
            MOTHER_FIRST_TRANSLATE_Y = int(
                user_settings.get("mother_first_translate_y", 0)
            )
            MOTHER_FIRST_ROTATE = int(user_settings.get("mother_first_rotate", 0))
            MOTHER_MIDDLE_TRANSLATE_X = int(
                user_settings.get("mother_middle_translate_x", 0)
            )
            MOTHER_MIDDLE_TRANSLATE_Y = int(
                user_settings.get("mother_middle_translate_y", 0)
            )
            MOTHER_MIDDLE_ROTATE = int(user_settings.get("mother_middle_rotate", 0))
            MOTHER_LAST_TRANSLATE_X = int(
                user_settings.get("mother_last_translate_x", 0)
            )
            MOTHER_LAST_TRANSLATE_Y = int(
                user_settings.get("mother_last_translate_y", 0)
            )
            MOTHER_LAST_ROTATE = int(user_settings.get("mother_last_rotate", 0))
            MOTHER_BIRTH_TRANSLATE_X = int(
                user_settings.get("mother_birth_translate_x", 0)
            )
            MOTHER_BIRTH_TRANSLATE_Y = int(
                user_settings.get("mother_birth_translate_y", 0)
            )
            MOTHER_BIRTH_ROTATE = int(user_settings.get("mother_birth_rotate", 0))
            MOTHER_BIRTH_PLACE_TRANSLATE_X = int(
                user_settings.get("mother_birth_place_translate_x", 0)
            )
            MOTHER_BIRTH_PLACE_TRANSLATE_Y = int(
                user_settings.get("mother_birth_place_translate_y", 0)
            )
            MOTHER_BIRTH_PLACE_ROTATE = int(
                user_settings.get("mother_birth_place_rotate", 0)
            )
            MOTHER_DEATH_TRANSLATE_X = int(
                user_settings.get("mother_death_translate_x", 0)
            )
            MOTHER_DEATH_TRANSLATE_Y = int(
                user_settings.get("mother_death_translate_y", 280)
            )
            MOTHER_DEATH_ROTATE = int(user_settings.get("mother_death_rotate", -90))
            MOTHER_DEATH_PLACE_TRANSLATE_X = int(
                user_settings.get("mother_death_place_translate_x", 0)
            )
            MOTHER_DEATH_PLACE_TRANSLATE_Y = int(
                user_settings.get("mother_death_place_translate_y", 280)
            )
            MOTHER_DEATH_PLACE_ROTATE = int(
                user_settings.get("mother_death_place_rotate", -90)
            )

            with Drawing() as draw:
                draw.push()

                # Set initial drawing properties
                draw.font = FONT_FAMILY
                draw.font_size = PARENT_NAME_FONT_SIZE
                draw.stroke_antialias = STROKE_ANTIALIAS

                # Initial translation
                print(
                    f"Translating coordinates by (x={INITIAL_TRANSLATE_X}, y={INITIAL_TRANSLATE_Y})"
                )
                draw.translate(x=INITIAL_TRANSLATE_X, y=INITIAL_TRANSLATE_Y)

                # =============================================
                # PARENT GENERATION DRAWING
                # =============================================

                draw.translate(x=PARENT_TRANSLATE_X, y=PARENT_TRANSLATE_Y)

                # draw.fill_color = PARENT_INFO_COLOR
                # print(f"Setting fill_color to: {PARENT_INFO_COLOR}")

                draw.stroke_color = PARENT_STROKE_COLOR
                print(f"Setting stroke_color to: {PARENT_STROKE_COLOR}")

                # Parents
                father = None
                mother = None

                # =============================================
                # Debug prints before drawing
                # =============================================

                print(f"Primary individual: {primary_individual.full_name}")
                print(
                    f"Birth date: {primary_individual.birth_date} (type: {type(primary_individual.birth_date)})"
                )
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
                        FATHER_FIRST_TRANSLATE_X,
                        FATHER_FIRST_TRANSLATE_Y,
                        FATHER_FIRST_ROTATE,
                    )
                    draw.rotate(fr_first)

                    draw.translate(fx_first, fy_first)

                    print(f"Setting fill_color to: {FATHER_FONT_COLOR}")
                    draw.fill_color = FATHER_FONT_COLOR

                    if first_name:  # Only draw if we have a name
                        draw.text(fx_first, fy_first, first_name)
                        print(f"Drawn father's first name: {first_name}")

                    draw.pop()

                    # =============================================
                    # Draw father's middle name (translated upwards and at -45 degrees)
                    # =============================================

                    draw.push()

                    fx_middle, fy_middle, fr_middle = (
                        FATHER_MIDDLE_TRANSLATE_X,
                        FATHER_MIDDLE_TRANSLATE_Y,
                        FATHER_MIDDLE_ROTATE,
                    )

                    draw.translate(fx_middle, fy_middle)

                    draw.rotate(fr_middle)

                    if middle_name:  # Only draw if we have a middle name
                        draw.text(fx_middle, fy_middle, middle_name)
                        print(f"Drawn father's middle name: {middle_name}")

                    draw.pop()

                    # =============================================
                    # Draw father's last name (translated further upwards and at -90 degrees)
                    # =============================================

                    draw.push()

                    fx_last, fy_last, fr_last = (
                        FATHER_LAST_TRANSLATE_X,
                        FATHER_LAST_TRANSLATE_Y,
                        FATHER_LAST_ROTATE,
                    )

                    draw.translate(fx_last, fy_last)

                    draw.rotate(fr_last)

                    if last_name:  # Only draw if we have a last name
                        draw.text(fx_last, fy_last, last_name)
                        print(f"Drawn father's last name: {last_name}")

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

                    # Safe birth date access
                    birth_date = father.birth_date if father and father.birth_date else " "
                    draw.text(0, 0, birth_date)
                    print(f"Drawn father's birth date: {birth_date}")

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
                    print(
                        f"Setting fill_color to: {FATHER_BIRTH_PLACE_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}"
                    )

                    draw.rotate(fr_birth_place)

                    # Safe birth place access
                    birth_place = father.birth_place if father and father.birth_place else " "
                    draw.text(0, 0, birth_place)
                    print(f"Drawn father's birth place: {birth_place}")

                    draw.pop()

                    # =============================================
                    # Draw father's death date
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
                    print(
                        f"Setting fill_color to: {FATHER_DEATH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}"
                    )

                    draw.rotate(fr_death)

                    # Safe death date access
                    death_date = father.death_date if father and father.death_date else " "
                    draw.text(0, 0, death_date)
                    print(f"Drawn father's death date: {death_date}")

                    draw.pop()

                    # =============================================
                    # Draw father's death place
                    # =============================================

                    draw.push()

                    fx_death_place, fy_death_place, fr_death_place = (
                        FATHER_DEATH_PLACE_TRANSLATE_X,
                        FATHER_DEATH_PLACE_TRANSLATE_Y,
                        FATHER_DEATH_PLACE_ROTATE,
                    )

                    draw.translate(fx_death_place, fy_death_place)

                    draw.fill_color = FATHER_DEATH_PLACE_COLOR
                    draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                    print(
                        f"Setting fill_color to: {FATHER_DEATH_PLACE_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}"
                    )

                    draw.rotate(fr_death_place)

                    # Safe death place access
                    death_place = father.death_place if father and father.death_place else " "
                    draw.text(0, 0, death_place)
                    print(f"Drawn father's death place: {death_place}")

                    draw.pop()

                else:
                    print("Father not found - skipping all father drawing")

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
                        MOTHER_FIRST_TRANSLATE_X,
                        MOTHER_FIRST_TRANSLATE_Y,
                        MOTHER_FIRST_ROTATE,
                    )

                    draw.translate(mx_first, my_first)

                    draw.rotate(mr_first)

                    if first_name:  # Only draw if we have a name
                        draw.text(mx_first, my_first, first_name)
                        print(f"Drawn mother's first name: {first_name}")

                    draw.pop()

                    # =============================================
                    # Draw mother's middle name (translated upwards and at -45 degrees)
                    # =============================================

                    draw.push()

                    mx_middle, my_middle, mr_middle = (
                        MOTHER_MIDDLE_TRANSLATE_X,
                        MOTHER_MIDDLE_TRANSLATE_Y,
                        MOTHER_MIDDLE_ROTATE,
                    )

                    draw.translate(mx_middle, my_middle)

                    draw.rotate(mr_middle)

                    if middle_name:  # Only draw if we have a middle name
                        draw.text(mx_middle, my_middle, middle_name)
                        print(f"Drawn mother's middle name: {middle_name}")

                    draw.pop()

                    # =============================================
                    # Draw mother's last name (translated further upwards and at -90 degrees)
                    # =============================================

                    draw.push()

                    mx_last, my_last, mr_last = (
                        MOTHER_LAST_TRANSLATE_X,
                        MOTHER_LAST_TRANSLATE_Y,
                        MOTHER_LAST_ROTATE,
                    )

                    draw.translate(mx_last, my_last)

                    draw.rotate(mr_last)

                    if last_name:  # Only draw if we have a last name
                        draw.text(mx_last, my_last, last_name)
                        print(f"Drawn mother's last name: {last_name}")

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

                    # Safe birth date access
                    birth_date = mother.birth_date if mother and mother.birth_date else " "
                    draw.text(0, 0, birth_date)
                    print(f"Drawn mother's birth date: {birth_date}")

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
                    print(
                        f"Setting fill_color to: {MOTHER_BIRTH_PLACE_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}"
                    )

                    draw.rotate(mr_birth_place)

                    # Safe birth place access
                    birth_place = mother.birth_place if mother and mother.birth_place else " "
                    draw.text(0, 0, birth_place)
                    print(f"Drawn mother's birth place: {birth_place}")

                    draw.pop()

                    # =============================================
                    # Draw mother's death date
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
                    print(
                        f"Setting fill_color to: {MOTHER_DEATH_COLOR} and font_size to: {PARENT_DATE_INFO_FONT_SIZE}"
                    )

                    draw.rotate(mr_death)

                    # Safe death date access
                    death_date = mother.death_date if mother and mother.death_date else " "
                    draw.text(0, 0, death_date)
                    print(f"Drawn mother's death date: {death_date}")

                    draw.pop()

                    # =============================================
                    # Draw mother's death place
                    # =============================================

                    draw.push()

                    mx_death_place, my_death_place, mr_death_place = (
                        MOTHER_DEATH_PLACE_TRANSLATE_X,
                        MOTHER_DEATH_PLACE_TRANSLATE_Y,
                        MOTHER_DEATH_PLACE_ROTATE,
                    )

                    draw.translate(mx_death_place, my_death_place)

                    draw.fill_color = MOTHER_DEATH_PLACE_COLOR
                    draw.font_size = PARENT_PLACE_INFO_FONT_SIZE
                    print(
                        f"Setting fill_color to: {MOTHER_DEATH_PLACE_COLOR} and font_size to: {PARENT_PLACE_INFO_FONT_SIZE}"
                    )

                    draw.rotate(mr_death_place)

                    # Safe death place access
                    death_place = mother.death_place if mother and mother.death_place else " "
                    draw.text(0, 0, death_place)
                    print(f"Drawn mother's death place: {death_place}")

                    draw.pop()

                else:
                    print("Mother not found - skipping all mother drawing")


                # =============================================
                # Generate the 1gen overlay with PRIMARY settings before applying 2gen drawing
                # =============================================

                # Check for stored primary settings first (from JavaScript)
                primary_settings = user_settings.get("primary_settings", {})
                print(f"DEBUG: user_settings keys: {list(user_settings.keys())}")
                print(f"DEBUG: primary_settings from user_settings: {primary_settings}")

                if not primary_settings:
                    # Fallback to extracting PRIMARY from current settings
                    primary_settings = extract_generation_settings(
                        user_settings, "PRIMARY"
                    )
                    print(
                        f"DEBUG: No stored primary settings, using fallback PRIMARY settings: {primary_settings}"
                    )
                else:
                    print(
                        f"DEBUG: Using stored primary settings for 1gen overlay: {primary_settings}"
                    )

                print(
                    f"DEBUG: Generating 1gen overlay with settings: {primary_settings}"
                )
                gen1_img_buffer = generate_1gen_preview(
                    primary_individual, family_data, "preview", primary_settings
                )
                print(f"DEBUG: Generated 1gen overlay buffer")

                # =============================================
                # Apply the drawing to the image
                # =============================================

                draw(content_img)

                # =============================================
                # Composite the 1gen overlay onto the 2gen image
                # =============================================

                gen1_img_buffer.seek(0)  # Reset buffer position
                gen1_bytes = gen1_img_buffer.getvalue()

                # =============================================
                # Create image from blob
                # =============================================

                with Image(blob=gen1_bytes) as gen1_overlay:
                    gen1_overlay.resize(
                        int(gen1_overlay.width * 0.48), int(gen1_overlay.height * 0.48)
                    )
                    content_img.composite(gen1_overlay, left=508, top=508)
                    print(f"DEBUG: Composited 1gen overlay onto 2gen image")

                # =============================================
                # For preview mode, return the content image directly
                # =============================================

                if template == "preview":
                    print("DEBUG: Returning preview image")
                    gen2_image_buffer = BytesIO()
                    content_img.save(file=gen2_image_buffer)
                    gen2_image_buffer.seek(0)
                    return gen2_image_buffer

                # =============================================
                # For final chart mode, composite the content image onto the PDF base template
                # =============================================

                elif template == "final":
                    print("DEBUG: Compositing content onto PDF base template")

                    # =============================================
                    # Load the PDF base template
                    # =============================================

                    base_template_path = os.path.join(
                        settings.BASE_DIR,
                        "apps/charts/static/charts/images/base_image_templates",
                        "US_LETTER_2GEN_BW.pdf",
                    )
                    print(f"DEBUG: Base template path: {base_template_path}")
                    print(
                        f"DEBUG: Base template exists: {os.path.exists(base_template_path)}"
                    )

                    with Image(filename=base_template_path, resolution=300) as base_img:
                        print(
                            f"Base template loaded: {base_img.width}x{base_img.height}"
                        )

                        # =============================================
                        # Composite the content image onto the base template
                        # Position: 300px right, 570px down
                        # =============================================

                        composite_x = 300
                        composite_y = 570

                        print(
                            f"DEBUG: Compositing content image at position ({composite_x}, {composite_y})"
                        )
                        base_img.composite(
                            content_img, left=composite_x, top=composite_y
                        )

                        # =============================================
                        # Save the final result as PDF
                        # =============================================

                        pdf_buffer = BytesIO()
                        base_img.save(file=pdf_buffer)
                        pdf_buffer.seek(0)

                        return pdf_buffer

    except Exception as e:
        print(f"ERROR: Failed to generate chart: {str(e)}")
        import traceback

        traceback.print_exc()
        raise
