import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


def generate_family_tree(primary_individual, family_data, template="2gen"):
    """
    Generate a 2-generation family tree chart using Wand (Python ImageMagick binding)

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type (e.g., '2gen' for 2-generation chart)

    Returns:
        BytesIO buffer containing the generated image
    """
    print(
        f"DEBUG: Generating 2-generation family tree for: {primary_individual.full_name}"
    )
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    # Construct the full path to the template file
    try:
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/charts/static/charts/images/base_image_templates",
            "US_LETTER_2GEN_BW.pdf",  # Using 4GEN template as base for 2GEN
        )
        print(f"DEBUG: Template path: {template_path}")
        print(f"DEBUG: File exists: {os.path.exists(template_path)}")

        # Create a new image with the same dimensions as your template
        with Image(filename=template_path, resolution=300) as img:
            print(f"Image loaded successfully: {img.width}x{img.height}")

            # =============================================
            # TRANSLATION SETTINGS TUNING
            # =============================================

            # Initial translation
            INITIAL_TRANSLATE_X = 0
            INITIAL_TRANSLATE_Y = -106

            # Subject translation
            SUBJECT_TRANSLATE_X = 0
            SUBJECT_TRANSLATE_Y = 0

            # Parent translation
            PARENT_TRANSLATE_X = 0
            PARENT_TRANSLATE_Y = 0

            # =============================================
            # DRAWING SETTINGS TUNING
            # =============================================

            # Font settings
            FONT_FAMILY = "Arial"

            # Stroke settings
            DEFAULT_STROKE_WIDTH = 0.5
            PRIMARY_STROKE_COLOR = Color("green")

            # Drawing quality settings
            STROKE_ANTIALIAS = True

            # =============================================
            # PRIMARY INDIVIDUAL TUNING SETTINGS
            # =============================================

            # Primary individual colors
            PRIMARY_FONT_COLOR = Color("white")
            PRIMARY_BIRTH_COLOR = Color("white")
            PRIMARY_PLACE_COLOR = Color("white")
            PRIMARY_DEATH_COLOR = Color("white")
            PRIMARY_STROKE_COLOR = Color("white")

            # Primary individual coordinates
            PRIMARY_NAME_X = 0
            PRIMARY_NAME_Y = 0
            PRIMARY_NAME_ROTATE = -45
            PRIMARY_BIRTH_X = 0
            PRIMARY_BIRTH_Y = 135
            PRIMARY_BIRTH_ROTATE = 45
            PRIMARY_PLACE_X = 0
            PRIMARY_PLACE_Y = 90
            PRIMARY_PLACE_ROTATE = -45

            # Primary individual font sizes
            PRIMARY_NAME_FONT_SIZE = 13
            PRIMARY_INFO_FONT_SIZE = 13

            # =============================================
            # PARENT GENERATION TUNING SETTINGS
            # =============================================

            # Parent colors
            FATHER_FONT_COLOR = Color("black")
            MOTHER_FONT_COLOR = Color("black")
            PARENT_INFO_COLOR = Color("black")

            # Father coordinates
            FATHER_FIRST_X = 0
            FATHER_FIRST_Y = 225
            FATHER_FIRST_ROTATION = 45
            FATHER_MIDDLE_X = 0
            FATHER_MIDDLE_Y = 260
            FATHER_MIDDLE_ROTATION = -45
            FATHER_LAST_X = 0
            FATHER_LAST_Y = 225
            FATHER_LAST_ROTATION = -45
            FATHER_BIRTH_X = 0
            FATHER_BIRTH_Y = 285
            FATHER_BIRTH_ROTATION = 0
            FATHER_PLACE_X = 0
            FATHER_PLACE_Y = 0
            FATHER_PLACE_ROTATION = 0
            FATHER_DEATH_X = 0
            FATHER_DEATH_Y = 280
            FATHER_DEATH_ROTATION = -90

            # Mother coordinates
            MOTHER_FIRST_X = 0
            MOTHER_FIRST_Y = 225
            MOTHER_FIRST_ROTATION = -90
            MOTHER_MIDDLE_X = 0
            MOTHER_MIDDLE_Y = 260
            MOTHER_MIDDLE_ROTATION = -45
            MOTHER_LAST_X = 0
            MOTHER_LAST_Y = 225
            MOTHER_LAST_ROTATION = -45
            MOTHER_BIRTH_X = 0
            MOTHER_BIRTH_Y = 285
            MOTHER_BIRTH_ROTATION = 0
            MOTHER_PLACE_X = 0
            MOTHER_PLACE_Y = 0
            MOTHER_PLACE_ROTATION = 0
            MOTHER_DEATH_X = 0
            MOTHER_DEATH_Y = 280
            MOTHER_DEATH_ROTATION = -90

            with Drawing() as draw:
                # Set initial drawing properties
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

                # =============================================
                # PARENT GENERATION DRAWING
                # =============================================

                draw.rotate(180)
                draw.translate(x=PARENT_TRANSLATE_X, y=PARENT_TRANSLATE_Y)
                print(f"Setting fill_color to: {PARENT_INFO_COLOR}")
                draw.fill_color = PARENT_INFO_COLOR
                print(f"Setting stroke_color to: {PARENT_INFO_COLOR}")
                draw.stroke_color = PARENT_INFO_COLOR

                # Parents
                father = None
                mother = None

                # Debug prints before drawing
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

                # Surname 0, Father
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

                    # Draw father's first name (default orientation)
                    ffx_first, ffy_first, ffr_first = (
                        FATHER_FIRST_X,
                        FATHER_FIRST_Y,
                        FATHER_FIRST_ROTATION,
                    )
                    draw.rotate(ffr_first)
                    print(f"Setting fill_color to: {FATHER_FONT_COLOR}")
                    draw.fill_color = FATHER_FONT_COLOR
                    draw.text(ffx_first, ffy_first, first_name)
                    print(
                        f"Drawn father's first name at ({ffx_first}, {ffy_first}) with rotation {ffr_first}: {first_name}"
                    )

                    # Draw father's middle name (translated upwards and at -45 degrees)
                    ffx_middle, ffy_middle, ffr_middle = (
                        FATHER_MIDDLE_X,
                        FATHER_MIDDLE_Y,
                        FATHER_MIDDLE_ROTATION,
                    )
                    draw.rotate(ffr_middle)
                    draw.text(ffx_middle, ffy_middle, middle_name)
                    print(
                        f"Drawn father's middle name at ({ffx_middle}, {ffy_middle}) with rotation {ffr_middle}: {middle_name}"
                    )

                    # Draw father's last name (translated further upwards and at -90 degrees)
                    ffx_last, ffy_last, ffr_last = (
                        FATHER_LAST_X,
                        FATHER_LAST_Y,
                        FATHER_LAST_ROTATION,
                    )
                    draw.rotate(ffr_last)
                    draw.text(ffx_last, ffy_last, last_name)
                    print(
                        f"Drawn father's last name at ({ffx_last}, {ffy_last}) with rotation {ffr_last}: {last_name}"
                    )

                    # Reset rotate for other elements
                    print("Rotating by: 90 degrees")
                    draw.rotate(90)
                    print(
                        "Reset rotation to 90 degrees for father's birth date and place"
                    )

                    # Draw father's birth date and place
                    ffx_birth, ffy_birth, ffr_birth = (
                        FATHER_BIRTH_X,
                        FATHER_BIRTH_Y,
                        FATHER_BIRTH_ROTATION,
                    )
                    print(f"Setting fill_color to: {PARENT_INFO_COLOR}")
                    draw.fill_color = PARENT_INFO_COLOR
                    draw.rotate(ffr_birth)
                    draw.text(ffx_birth, ffy_birth, father.birth_date or " ")
                    print(
                        f"Drawn text at ({ffx_birth}, {ffy_birth}) with rotation {ffr_birth}: {father.birth_date or ' '}"
                    )
                    ffx_place, ffy_place, ffr_place = (
                        FATHER_PLACE_X,
                        FATHER_PLACE_Y,
                        FATHER_PLACE_ROTATION,
                    )
                    draw.rotate(ffr_place)
                    draw.text(ffx_place, ffy_place, father.birth_place or " ")
                    print(
                        f"Drawn text at ({ffx_place}, {ffy_place}) with rotation {ffr_place}: {father.birth_place or ' '}"
                    )

                    # Draw father's death date if available
                    ffx_death, ffy_death, ffr_death = (
                        FATHER_DEATH_X,
                        FATHER_DEATH_Y,
                        FATHER_DEATH_ROTATION,
                    )
                    draw.rotate(ffr_death)
                    death_date_text = father.death_date or " "
                    print(f"Father's death date: {death_date_text}")
                    draw.text(ffx_death, ffy_death, death_date_text)
                    print(
                        f"Drawn text at ({ffx_death}, {ffy_death}) with rotation {ffr_death}: {death_date_text}"
                    )

                # Surname 1, Mother
                if mother:
                    print(f"Drawing mother: {mother.full_name}")
                    # Split mother's name into parts
                    name_parts = mother.full_name.split()
                    first_name = name_parts[0] if len(name_parts) > 0 else ""
                    middle_name = name_parts[1] if len(name_parts) > 1 else ""
                    last_name = name_parts[-1] if len(name_parts) > 1 else ""

                    # Draw mother's first name (flipped upside-down)
                    mfx_first, mfy_first, mfr_first = (
                        MOTHER_FIRST_X,
                        MOTHER_FIRST_Y,
                        MOTHER_FIRST_ROTATION,
                    )
                    draw.rotate(mfr_first)
                    print(f"Setting fill_color to: {MOTHER_FONT_COLOR}")
                    draw.fill_color = MOTHER_FONT_COLOR
                    draw.text(mfx_first, mfy_first, first_name)
                    print(
                        f"Drawn mother's first name at ({mfx_first}, {mfy_first}) with rotation {mfr_first}: {first_name}"
                    )

                    # Draw mother's middle name (at 45 degrees)
                    mfx_middle, mfy_middle, mfr_middle = (
                        MOTHER_MIDDLE_X,
                        MOTHER_MIDDLE_Y,
                        MOTHER_MIDDLE_ROTATION,
                    )
                    draw.rotate(mfr_middle)
                    draw.text(mfx_middle, mfy_middle, middle_name)
                    print(
                        f"Drawn mother's middle name at ({mfx_middle}, {mfy_middle}) with rotation {mfr_middle}: {middle_name}"
                    )

                    # Draw mother's last name (at 90 degrees)
                    mfx_last, mfy_last, mfr_last = (
                        MOTHER_LAST_X,
                        MOTHER_LAST_Y,
                        MOTHER_LAST_ROTATION,
                    )
                    draw.rotate(mfr_last)
                    draw.text(mfx_last, mfy_last, last_name)
                    print(
                        f"Drawn mother's last name at ({mfx_last}, {mfy_last}) with rotation {mfr_last}: {last_name}"
                    )

                    # Reset rotate for other elements
                    print("Rotating by: 90 degrees")
                    draw.rotate(90)
                    print(
                        "Reset rotation to 90 degrees for mother's birth date and place"
                    )

                    # Draw mother's birth date and place
                    mfx_birth, mfy_birth, mfr_birth = (
                        MOTHER_BIRTH_X,
                        MOTHER_BIRTH_Y,
                        MOTHER_BIRTH_ROTATION,
                    )
                    print(f"Setting fill_color to: {PARENT_INFO_COLOR}")
                    draw.fill_color = PARENT_INFO_COLOR
                    draw.rotate(mfr_birth)
                    draw.text(mfx_birth, mfy_birth, mother.birth_date or " ")
                    print(
                        f"Drawn text at ({mfx_birth}, {mfy_birth}) with rotation {mfr_birth}: {mother.birth_date or ' '}"
                    )
                    mfx_place, mfy_place, mfr_place = (
                        MOTHER_PLACE_X,
                        MOTHER_PLACE_Y,
                        MOTHER_PLACE_ROTATION,
                    )
                    draw.rotate(mfr_place)
                    draw.text(mfx_place, mfy_place, mother.birth_place or " ")
                    print(
                        f"Drawn text at ({mfx_place}, {mfy_place}) with rotation {mfr_place}: {mother.birth_place or ' '}"
                    )

                    # Draw mother's death date if available
                    mfx_death, mfy_death, mfr_death = (
                        MOTHER_DEATH_X,
                        MOTHER_DEATH_Y,
                        MOTHER_DEATH_ROTATION,
                    )
                    draw.rotate(mfr_death)
                    death_date_text = mother.death_date or " "
                    print(f"Mother's death date: {death_date_text}")
                    draw.text(mfx_death, mfy_death, death_date_text)
                    print(
                        f"Drawn text at ({mfx_death}, {mfy_death}) with rotation {mfr_death}: {death_date_text}"
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
