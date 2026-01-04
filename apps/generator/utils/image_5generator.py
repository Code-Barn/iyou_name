import os
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


def generate_family_tree(primary_individual, family_data, template="5gen"):
    """
    Generate a 5-generation family tree chart using Wand (Python ImageMagick binding)

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        template: Template type (e.g., '5gen' for 5-generation chart)

    Returns:
        BytesIO buffer containing the generated image
    """
    print(
        f"DEBUG: Generating 5-generation family tree for: {primary_individual.full_name}"
    )
    print(f"DEBUG: Primary individual ID: {primary_individual.id}")

    # Construct the full path to the template file
    try:
        template_path = os.path.join(
            settings.BASE_DIR,
            "apps/charts/static/charts/images/base_image_templates",
            "US_LETTER_5GEN_BW.pdf",
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

            # Grandparent translation
            GRANDPARENT_TRANSLATE_X = 0
            GRANDPARENT_TRANSLATE_Y = 0

            # Great-grandparent translation
            GREAT_GRANDPARENT_TRANSLATE_X = 0
            GREAT_GRANDPARENT_TRANSLATE_Y = 0

            # =============================================
            # DRAWING SETTINGS TUNING
            # =============================================

            # Font settings
            FONT_FAMILY = "Arial"
            DEFAULT_FONT_SIZE = 14
            SMALL_FONT_SIZE = 11

            # Stroke settings
            DIVIDING_LINE_STROKE_WIDTH = 13
            DEFAULT_STROKE_WIDTH = 0.5
            PRIMARY_STROKE_COLOR = Color("green")
            DEFAULT_STROKE_COLOR = Color("black")

            # Drawing quality settings
            STROKE_ANTIALIAS = True
            FONT_RESOLUTION = (600, 600)
            TEXT_INTERLINE_SPACING = -15

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

            # =============================================
            # GRANDPARENT GENERATION TUNING SETTINGS
            # =============================================

            # Grandparent colors
            GRANDPARENT_FONT_COLOR = Color("black")
            GRANDPARENT_INFO_COLOR = Color("black")

            # Grandparents coordinates and rotations
            PATERNAL_GRANDFATHER_X = 0
            PATERNAL_GRANDFATHER_Y = 380
            PATERNAL_GRANDFATHER_ROTATE = 180
            PATERNAL_GRANDFATHER_BIRTH_X = 0
            PATERNAL_GRANDFATHER_BIRTH_Y = 480
            PATERNAL_GRANDFATHER_DEATH_X = 0
            PATERNAL_GRANDFATHER_DEATH_Y = 580
            PATERNAL_GRANDFATHER_PLACE_X = 0
            PATERNAL_GRANDFATHER_PLACE_Y = 630

            PATERNAL_GRANDMOTHER_X = 0
            PATERNAL_GRANDMOTHER_Y = 380
            PATERNAL_GRANDMOTHER_ROTATE = -90
            PATERNAL_GRANDMOTHER_BIRTH_X = 0
            PATERNAL_GRANDMOTHER_BIRTH_Y = 480
            PATERNAL_GRANDMOTHER_DEATH_X = 0
            PATERNAL_GRANDMOTHER_DEATH_Y = 580
            PATERNAL_GRANDMOTHER_PLACE_X = 0
            PATERNAL_GRANDMOTHER_PLACE_Y = 630

            MATERNAL_GRANDFATHER_X = 0
            MATERNAL_GRANDFATHER_Y = 380
            MATERNAL_GRANDFATHER_ROTATE = -90
            MATERNAL_GRANDFATHER_BIRTH_X = 0
            MATERNAL_GRANDFATHER_BIRTH_Y = 480
            MATERNAL_GRANDFATHER_DEATH_X = 0
            MATERNAL_GRANDFATHER_DEATH_Y = 580
            MATERNAL_GRANDFATHER_PLACE_X = 0
            MATERNAL_GRANDFATHER_PLACE_Y = 630

            MATERNAL_GRANDMOTHER_X = 0
            MATERNAL_GRANDMOTHER_Y = 380
            MATERNAL_GRANDMOTHER_ROTATE = -90
            MATERNAL_GRANDMOTHER_BIRTH_X = 0
            MATERNAL_GRANDMOTHER_BIRTH_Y = 480
            MATERNAL_GRANDMOTHER_DEATH_X = 0
            MATERNAL_GRANDMOTHER_DEATH_Y = 580
            MATERNAL_GRANDMOTHER_PLACE_X = 0
            MATERNAL_GRANDMOTHER_PLACE_Y = 630

            # =============================================
            # GREAT-GRANDPARENT GENERATION TUNING SETTINGS
            # =============================================

            # Great-grandparent colors
            GREAT_GRANDPARENT_FONT_COLOR = Color("black")
            GREAT_GRANDPARENT_INFO_COLOR = Color("black")

            # Great-grandparents coordinates and rotations
            FATHERS_PATERNAL_GRANDFATHER_TRANSLATE_X = 600
            FATHERS_PATERNAL_GRANDFATHER_TRANSLATE_Y = 350
            FATHERS_PATERNAL_GRANDFATHER_X = 0
            FATHERS_PATERNAL_GRANDFATHER_Y = 100
            FATHERS_PATERNAL_GRANDFATHER_ROTATE = -90
            FATHERS_PATERNAL_GRANDFATHER_BIRTH_X = 0
            FATHERS_PATERNAL_GRANDFATHER_BIRTH_Y = 200
            FATHERS_PATERNAL_GRANDFATHER_DEATH_X = 0
            FATHERS_PATERNAL_GRANDFATHER_DEATH_Y = 300
            FATHERS_PATERNAL_GRANDFATHER_PLACE_X = 0
            FATHERS_PATERNAL_GRANDFATHER_PLACE_Y = 350

            FATHERS_PATERNAL_GRANDMOTHER_TRANSLATE_X = 700
            FATHERS_PATERNAL_GRANDMOTHER_TRANSLATE_Y = 0
            FATHERS_PATERNAL_GRANDMOTHER_X = 0
            FATHERS_PATERNAL_GRANDMOTHER_Y = 100
            FATHERS_PATERNAL_GRANDMOTHER_ROTATE = 0
            FATHERS_PATERNAL_GRANDMOTHER_BIRTH_X = 0
            FATHERS_PATERNAL_GRANDMOTHER_BIRTH_Y = 200
            FATHERS_PATERNAL_GRANDMOTHER_DEATH_X = 0
            FATHERS_PATERNAL_GRANDMOTHER_DEATH_Y = 300
            FATHERS_PATERNAL_GRANDMOTHER_PLACE_X = 0
            FATHERS_PATERNAL_GRANDMOTHER_PLACE_Y = 350

            FATHERS_MATERNAL_GRANDFATHER_TRANSLATE_X = 250
            FATHERS_MATERNAL_GRANDFATHER_TRANSLATE_Y = -250
            FATHERS_MATERNAL_GRANDFATHER_X = 0
            FATHERS_MATERNAL_GRANDFATHER_Y = 100
            FATHERS_MATERNAL_GRANDFATHER_ROTATE = -90
            FATHERS_MATERNAL_GRANDFATHER_BIRTH_X = 0
            FATHERS_MATERNAL_GRANDFATHER_BIRTH_Y = 200
            FATHERS_MATERNAL_GRANDFATHER_DEATH_X = 0
            FATHERS_MATERNAL_GRANDFATHER_DEATH_Y = 300
            FATHERS_MATERNAL_GRANDFATHER_PLACE_X = 0
            FATHERS_MATERNAL_GRANDFATHER_PLACE_Y = 350

            FATHERS_MATERNAL_GRANDMOTHER_TRANSLATE_X = 700
            FATHERS_MATERNAL_GRANDMOTHER_TRANSLATE_Y = 0
            FATHERS_MATERNAL_GRANDMOTHER_X = 0
            FATHERS_MATERNAL_GRANDMOTHER_Y = 100
            FATHERS_MATERNAL_GRANDMOTHER_ROTATE = 0
            FATHERS_MATERNAL_GRANDMOTHER_BIRTH_X = 0
            FATHERS_MATERNAL_GRANDMOTHER_BIRTH_Y = 200
            FATHERS_MATERNAL_GRANDMOTHER_DEATH_X = 0
            FATHERS_MATERNAL_GRANDMOTHER_DEATH_Y = 300
            FATHERS_MATERNAL_GRANDMOTHER_PLACE_X = 0
            FATHERS_MATERNAL_GRANDMOTHER_PLACE_Y = 350

            MOTHERS_PATERNAL_GRANDFATHER_TRANSLATE_X = 250
            MOTHERS_PATERNAL_GRANDFATHER_TRANSLATE_Y = -240
            MOTHERS_PATERNAL_GRANDFATHER_X = 0
            MOTHERS_PATERNAL_GRANDFATHER_Y = 100
            MOTHERS_PATERNAL_GRANDFATHER_ROTATE = -90
            MOTHERS_PATERNAL_GRANDFATHER_BIRTH_X = 0
            MOTHERS_PATERNAL_GRANDFATHER_BIRTH_Y = 200
            MOTHERS_PATERNAL_GRANDFATHER_DEATH_X = 0
            MOTHERS_PATERNAL_GRANDFATHER_DEATH_Y = 300
            MOTHERS_PATERNAL_GRANDFATHER_PLACE_X = 0
            MOTHERS_PATERNAL_GRANDFATHER_PLACE_Y = 350

            MOTHERS_PATERNAL_GRANDMOTHER_TRANSLATE_X = 715
            MOTHERS_PATERNAL_GRANDMOTHER_TRANSLATE_Y = 0
            MOTHERS_PATERNAL_GRANDMOTHER_X = 0
            MOTHERS_PATERNAL_GRANDMOTHER_Y = 100
            MOTHERS_PATERNAL_GRANDMOTHER_ROTATE = 0
            MOTHERS_PATERNAL_GRANDMOTHER_BIRTH_X = 0
            MOTHERS_PATERNAL_GRANDMOTHER_BIRTH_Y = 200
            MOTHERS_PATERNAL_GRANDMOTHER_DEATH_X = 0
            MOTHERS_PATERNAL_GRANDMOTHER_DEATH_Y = 300
            MOTHERS_PATERNAL_GRANDMOTHER_PLACE_X = 0
            MOTHERS_PATERNAL_GRANDMOTHER_PLACE_Y = 350

            MOTHERS_MATERNAL_GRANDFATHER_TRANSLATE_X = 248
            MOTHERS_MATERNAL_GRANDFATHER_TRANSLATE_Y = -248
            MOTHERS_MATERNAL_GRANDFATHER_X = 0
            MOTHERS_MATERNAL_GRANDFATHER_Y = 100
            MOTHERS_MATERNAL_GRANDFATHER_ROTATE = -90
            MOTHERS_MATERNAL_GRANDFATHER_BIRTH_X = 0
            MOTHERS_MATERNAL_GRANDFATHER_BIRTH_Y = 200
            MOTHERS_MATERNAL_GRANDFATHER_DEATH_X = 0
            MOTHERS_MATERNAL_GRANDFATHER_DEATH_Y = 300
            MOTHERS_MATERNAL_GRANDFATHER_PLACE_X = 0
            MOTHERS_MATERNAL_GRANDFATHER_PLACE_Y = 350

            MOTHERS_MATERNAL_GRANDMOTHER_TRANSLATE_X = 695
            MOTHERS_MATERNAL_GRANDMOTHER_TRANSLATE_Y = 0
            MOTHERS_MATERNAL_GRANDMOTHER_X = 0
            MOTHERS_MATERNAL_GRANDMOTHER_Y = 100
            MOTHERS_MATERNAL_GRANDMOTHER_ROTATE = 0
            MOTHERS_MATERNAL_GRANDMOTHER_BIRTH_X = 0
            MOTHERS_MATERNAL_GRANDMOTHER_BIRTH_Y = 200
            MOTHERS_MATERNAL_GRANDMOTHER_DEATH_X = 0
            MOTHERS_MATERNAL_GRANDMOTHER_DEATH_Y = 300
            MOTHERS_MATERNAL_GRANDMOTHER_PLACE_X = 0
            MOTHERS_MATERNAL_GRANDMOTHER_PLACE_Y = 350

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
                print(f"Setting gravity to: center")
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
                    print(f"Rotating by: 90 degrees")
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
                    print(f"Rotating by: 90 degrees")
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

                # =============================================
                # GRANDPARENT GENERATION DRAWING
                # =============================================

                print(
                    f"Translating coordinates by (x={GRANDPARENT_TRANSLATE_X}, y={GRANDPARENT_TRANSLATE_Y})"
                )
                draw.translate(x=GRANDPARENT_TRANSLATE_X, y=GRANDPARENT_TRANSLATE_Y)
                print(f"Setting fill_color to: {GRANDPARENT_FONT_COLOR}")
                draw.fill_color = GRANDPARENT_FONT_COLOR

                paternal_grandfather = None
                paternal_grandmother = None
                maternal_grandfather = None
                maternal_grandmother = None
                # Dad's parents
                if father:
                    if father.father:
                        paternal_grandfather = family_data["individuals"].get(
                            father.father
                        )
                    if father.mother:
                        paternal_grandmother = family_data["individuals"].get(
                            father.mother
                        )

                if mother:
                    if mother.father:
                        maternal_grandfather = family_data["individuals"].get(
                            mother.father
                        )
                    if mother.mother:
                        maternal_grandmother = family_data["individuals"].get(
                            mother.mother
                        )
                # Surname 0, Paternal-Grandfather
                if paternal_grandfather:
                    print(
                        f"Drawing paternal grandfather: {paternal_grandfather.full_name}"
                    )
                    pgfx, pgfy, pgfr = (
                        PATERNAL_GRANDFATHER_X,
                        PATERNAL_GRANDFATHER_Y,
                        PATERNAL_GRANDFATHER_ROTATE,
                    )
                    draw.rotate(pgfr)
                    draw.text(pgfx, pgfy, paternal_grandfather.full_name)
                    print(
                        f"Drawn text at ({pgfx}, {pgfy}): {paternal_grandfather.full_name}"
                    )
                    pgfx_birth, pgfy_birth = (
                        PATERNAL_GRANDFATHER_BIRTH_X,
                        PATERNAL_GRANDFATHER_BIRTH_Y,
                    )
                    draw.text(
                        pgfx_birth, pgfy_birth, paternal_grandfather.birth_date or " "
                    )
                    print(
                        f"Drawn text at ({pgfx_birth}, {pgfy_birth}): {paternal_grandfather.birth_date or ' '}"
                    )
                    pgfx_death, pgfy_death = (
                        PATERNAL_GRANDFATHER_DEATH_X,
                        PATERNAL_GRANDFATHER_DEATH_Y,
                    )
                    death_date_text = paternal_grandfather.death_date or " "
                    print(f"Paternal grandfather's death date: {death_date_text}")
                    draw.text(pgfx_death, pgfy_death, death_date_text)
                    print(
                        f"Drawn text at ({pgfx_death}, {pgfy_death}): {death_date_text}"
                    )
                    pgfx_place, pgfy_place = (
                        PATERNAL_GRANDFATHER_PLACE_X,
                        PATERNAL_GRANDFATHER_PLACE_Y,
                    )
                    draw.text(
                        pgfx_place, pgfy_place, paternal_grandfather.birth_place or " "
                    )
                    print(
                        f"Drawn text at ({pgfx_place}, {pgfy_place}): {paternal_grandfather.birth_place or ' '}"
                    )

                # Surname 2, Paternal-Grandmother
                if paternal_grandmother:
                    print(
                        f"Drawing paternal grandmother: {paternal_grandmother.full_name}"
                    )
                    pgmfx, pgmfy, pgmfr = (
                        PATERNAL_GRANDMOTHER_X,
                        PATERNAL_GRANDMOTHER_Y,
                        PATERNAL_GRANDMOTHER_ROTATE,
                    )
                    draw.rotate(pgmfr)
                    draw.text(pgmfx, pgmfy, paternal_grandmother.full_name)
                    print(
                        f"Drawn text at ({pgmfx}, {pgmfy}): {paternal_grandmother.full_name}"
                    )
                    pgmfx_birth, pgmfy_birth = (
                        PATERNAL_GRANDMOTHER_BIRTH_X,
                        PATERNAL_GRANDMOTHER_BIRTH_Y,
                    )
                    draw.text(
                        pgmfx_birth, pgmfy_birth, paternal_grandmother.birth_date or " "
                    )
                    print(
                        f"Drawn text at ({pgmfx_birth}, {pgmfy_birth}): {paternal_grandmother.birth_date or ' '}"
                    )
                    pgmfx_death, pgmfy_death = (
                        PATERNAL_GRANDMOTHER_DEATH_X,
                        PATERNAL_GRANDMOTHER_DEATH_Y,
                    )
                    death_date_text = paternal_grandmother.death_date or " "
                    print(f"Paternal grandmother's death date: {death_date_text}")
                    draw.text(pgmfx_death, pgmfy_death, death_date_text)
                    print(
                        f"Drawn text at ({pgmfx_death}, {pgmfy_death}): {death_date_text}"
                    )
                    pgmfx_place, pgmfy_place = (
                        PATERNAL_GRANDMOTHER_PLACE_X,
                        PATERNAL_GRANDMOTHER_PLACE_Y,
                    )
                    draw.text(
                        pgmfx_place,
                        pgmfy_place,
                        paternal_grandmother.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({pgmfx_place}, {pgmfy_place}): {paternal_grandmother.birth_place or ' '}"
                    )
                # Mom's parents
                # Surname 1, Maternal-Grandfather
                if maternal_grandfather:
                    print(
                        f"Drawing maternal grandfather: {maternal_grandfather.full_name}"
                    )
                    mgfx, mgfy, mgfr = (
                        MATERNAL_GRANDFATHER_X,
                        MATERNAL_GRANDFATHER_Y,
                        MATERNAL_GRANDFATHER_ROTATE,
                    )
                    draw.rotate(mgfr)
                    draw.text(mgfx, mgfy, maternal_grandfather.full_name)
                    print(
                        f"Drawn text at ({mgfx}, {mgfy}): {maternal_grandfather.full_name}"
                    )
                    mgfx_birth, mgfy_birth = (
                        MATERNAL_GRANDFATHER_BIRTH_X,
                        MATERNAL_GRANDFATHER_BIRTH_Y,
                    )
                    draw.text(
                        mgfx_birth, mgfy_birth, maternal_grandfather.birth_date or " "
                    )
                    print(
                        f"Drawn text at ({mgfx_birth}, {mgfy_birth}): {maternal_grandfather.birth_date or ' '}"
                    )
                    mgfx_death, mgfy_death = (
                        MATERNAL_GRANDFATHER_DEATH_X,
                        MATERNAL_GRANDFATHER_DEATH_Y,
                    )
                    death_date_text = maternal_grandfather.death_date or " "
                    print(f"Maternal grandfather's death date: {death_date_text}")
                    draw.text(mgfx_death, mgfy_death, death_date_text)
                    print(
                        f"Drawn text at ({mgfx_death}, {mgfy_death}): {death_date_text}"
                    )
                    mgfx_place, mgfy_place = (
                        MATERNAL_GRANDFATHER_PLACE_X,
                        MATERNAL_GRANDFATHER_PLACE_Y,
                    )
                    draw.text(
                        mgfx_place, mgfy_place, maternal_grandfather.birth_place or " "
                    )
                    print(
                        f"Drawn text at ({mgfx_place}, {mgfy_place}): {maternal_grandfather.birth_place or ' '}"
                    )

                # Surname 3, Maternal-Grandmother
                if maternal_grandmother:
                    print(
                        f"Drawing maternal grandmother: {maternal_grandmother.full_name}"
                    )
                    mgmfx, mgmfy, mgmfr = (
                        MATERNAL_GRANDMOTHER_X,
                        MATERNAL_GRANDMOTHER_Y,
                        MATERNAL_GRANDMOTHER_ROTATE,
                    )
                    draw.rotate(mgmfr)
                    draw.text(mgmfx, mgmfy, maternal_grandmother.full_name)
                    print(
                        f"Drawn text at ({mgmfx}, {mgmfy}): {maternal_grandmother.full_name}"
                    )
                    mgmfx_birth, mgmfy_birth = (
                        MATERNAL_GRANDMOTHER_BIRTH_X,
                        MATERNAL_GRANDMOTHER_BIRTH_Y,
                    )
                    draw.text(
                        mgmfx_birth, mgmfy_birth, maternal_grandmother.birth_date or " "
                    )
                    print(
                        f"Drawn text at ({mgmfx_birth}, {mgmfy_birth}): {maternal_grandmother.birth_date or ' '}"
                    )
                    mgmfx_death, mgmfy_death = (
                        MATERNAL_GRANDMOTHER_DEATH_X,
                        MATERNAL_GRANDMOTHER_DEATH_Y,
                    )
                    death_date_text = maternal_grandmother.death_date or " "
                    print(f"Maternal grandmother's death date: {death_date_text}")
                    draw.text(mgmfx_death, mgmfy_death, death_date_text)
                    print(
                        f"Drawn text at ({mgmfx_death}, {mgmfy_death}): {death_date_text}"
                    )
                    mgmfx_place, mgmfy_place = (
                        MATERNAL_GRANDMOTHER_PLACE_X,
                        MATERNAL_GRANDMOTHER_PLACE_Y,
                    )
                    draw.text(
                        mgmfx_place,
                        mgmfy_place,
                        maternal_grandmother.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({mgmfx_place}, {mgmfy_place}): {maternal_grandmother.birth_place or ' '}"
                    )

                # =============================================
                # GREAT-GRANDPARENT GENERATION DRAWING
                # =============================================

                print(
                    f"Translating coordinates by (x={GREAT_GRANDPARENT_TRANSLATE_X}, y={GREAT_GRANDPARENT_TRANSLATE_Y})"
                )
                draw.translate(
                    x=GREAT_GRANDPARENT_TRANSLATE_X, y=GREAT_GRANDPARENT_TRANSLATE_Y
                )
                print(f"Setting fill_color to: {GREAT_GRANDPARENT_FONT_COLOR}")
                draw.fill_color = GREAT_GRANDPARENT_FONT_COLOR

                # Initialize variables for great-grandparents
                fathers_paternal_grandfather = None
                fathers_paternal_grandmother = None
                fathers_maternal_grandfather = None
                fathers_maternal_grandmother = None
                mothers_paternal_grandfather = None
                mothers_paternal_grandmother = None
                mothers_maternal_grandfather = None
                mothers_maternal_grandmother = None

                # Get father's grandparents (paternal side)
                if paternal_grandfather:
                    if paternal_grandfather.father:
                        fathers_paternal_grandfather = family_data["individuals"].get(
                            paternal_grandfather.father
                        )
                    if paternal_grandfather.mother:
                        fathers_paternal_grandmother = family_data["individuals"].get(
                            paternal_grandfather.mother
                        )

                if paternal_grandmother:
                    if paternal_grandmother.father:
                        fathers_maternal_grandfather = family_data["individuals"].get(
                            paternal_grandmother.father
                        )
                    if paternal_grandmother.mother:
                        fathers_maternal_grandmother = family_data["individuals"].get(
                            paternal_grandmother.mother
                        )

                # Get mother's grandparents (maternal side)
                if maternal_grandfather:
                    if maternal_grandfather.father:
                        mothers_paternal_grandfather = family_data["individuals"].get(
                            maternal_grandfather.father
                        )
                    if maternal_grandfather.mother:
                        mothers_paternal_grandmother = family_data["individuals"].get(
                            maternal_grandfather.mother
                        )

                if maternal_grandmother:
                    if maternal_grandmother.father:
                        mothers_maternal_grandfather = family_data["individuals"].get(
                            maternal_grandmother.father
                        )
                    if maternal_grandmother.mother:
                        mothers_maternal_grandmother = family_data["individuals"].get(
                            maternal_grandmother.mother
                        )

                # Draw father's paternal grandparents
                if fathers_paternal_grandfather:
                    print(
                        f"Drawing father's paternal grandfather: {fathers_paternal_grandfather.full_name}"
                    )
                    fpgfx, fpgfy, fpgfr = (
                        FATHERS_PATERNAL_GRANDFATHER_X,
                        FATHERS_PATERNAL_GRANDFATHER_Y,
                        FATHERS_PATERNAL_GRANDFATHER_ROTATE,
                    )
                    draw.translate(
                        FATHERS_PATERNAL_GRANDFATHER_TRANSLATE_X,
                        FATHERS_PATERNAL_GRANDFATHER_TRANSLATE_Y,
                    )
                    draw.rotate(fpgfr)
                    draw.text(fpgfx, fpgfy, fathers_paternal_grandfather.full_name)
                    print(
                        f"Drawn text at ({fpgfx}, {fpgfy}): {fathers_paternal_grandfather.full_name}"
                    )
                    fpgfx_birth, fpgfy_birth = (
                        FATHERS_PATERNAL_GRANDFATHER_BIRTH_X,
                        FATHERS_PATERNAL_GRANDFATHER_BIRTH_Y,
                    )
                    draw.text(
                        fpgfx_birth,
                        fpgfy_birth,
                        fathers_paternal_grandfather.birth_date or " ",
                    )
                    print(
                        f"Drawn text at ({fpgfx_birth}, {fpgfy_birth}): {fathers_paternal_grandfather.birth_date or ' '}"
                    )
                    fpgfx_death, fpgfy_death = (
                        FATHERS_PATERNAL_GRANDFATHER_DEATH_X,
                        FATHERS_PATERNAL_GRANDFATHER_DEATH_Y,
                    )
                    draw.text(
                        fpgfx_death,
                        fpgfy_death,
                        fathers_paternal_grandfather.death_date or " ",
                    )
                    print(
                        f"Drawn text at ({fpgfx_death}, {fpgfy_death}): {fathers_paternal_grandfather.death_date or ' '}"
                    )
                    fpgfx_place, fpgfy_place = (
                        FATHERS_PATERNAL_GRANDFATHER_PLACE_X,
                        FATHERS_PATERNAL_GRANDFATHER_PLACE_Y,
                    )
                    draw.text(
                        fpgfx_place,
                        fpgfy_place,
                        fathers_paternal_grandfather.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({fpgfx_place}, {fpgfy_place}): {fathers_paternal_grandfather.birth_place or ' '}"
                    )

                if fathers_paternal_grandmother:
                    print(
                        f"Drawing father's paternal grandmother: {fathers_paternal_grandmother.full_name}"
                    )
                    fpgmfx, fpgmfy, fpgmfr = (
                        FATHERS_PATERNAL_GRANDMOTHER_X,
                        FATHERS_PATERNAL_GRANDMOTHER_Y,
                        FATHERS_PATERNAL_GRANDMOTHER_ROTATE,
                    )
                    draw.translate(
                        FATHERS_PATERNAL_GRANDMOTHER_TRANSLATE_X,
                        FATHERS_PATERNAL_GRANDMOTHER_TRANSLATE_Y,
                    )
                    draw.rotate(fpgmfr)
                    draw.text(fpgmfx, fpgmfy, fathers_paternal_grandmother.full_name)
                    print(
                        f"Drawn text at ({fpgmfx}, {fpgmfy}): {fathers_paternal_grandmother.full_name}"
                    )
                    fpgmfx_birth, fpgmfy_birth = (
                        FATHERS_PATERNAL_GRANDMOTHER_BIRTH_X,
                        FATHERS_PATERNAL_GRANDMOTHER_BIRTH_Y,
                    )
                    draw.text(
                        fpgmfx_birth,
                        fpgmfy_birth,
                        fathers_paternal_grandmother.birth_date or " ",
                    )
                    print(
                        f"Drawn text at ({fpgmfx_birth}, {fpgmfy_birth}): {fathers_paternal_grandmother.birth_date or ' '}"
                    )
                    fpgmfx_death, fpgmfy_death = (
                        FATHERS_PATERNAL_GRANDMOTHER_DEATH_X,
                        FATHERS_PATERNAL_GRANDMOTHER_DEATH_Y,
                    )
                    draw.text(
                        fpgmfx_death,
                        fpgmfy_death,
                        fathers_paternal_grandmother.death_date or " ",
                    )
                    print(
                        f"Drawn text at ({fpgmfx_death}, {fpgmfy_death}): {fathers_paternal_grandmother.death_date or ' '}"
                    )
                    fpgmfx_place, fpgmfy_place = (
                        FATHERS_PATERNAL_GRANDMOTHER_PLACE_X,
                        FATHERS_PATERNAL_GRANDMOTHER_PLACE_Y,
                    )
                    draw.text(
                        fpgmfx_place,
                        fpgmfy_place,
                        fathers_paternal_grandmother.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({fpgmfx_place}, {fpgmfy_place}): {fathers_paternal_grandmother.birth_place or ' '}"
                    )

                # Draw father's maternal grandparents
                if fathers_maternal_grandfather:
                    print(
                        f"Drawing father's maternal grandfather: {fathers_maternal_grandfather.full_name}"
                    )
                    fmgfx, fmgfy, fmgfr = (
                        FATHERS_MATERNAL_GRANDFATHER_X,
                        FATHERS_MATERNAL_GRANDFATHER_Y,
                        FATHERS_MATERNAL_GRANDFATHER_ROTATE,
                    )
                    draw.translate(
                        FATHERS_MATERNAL_GRANDFATHER_TRANSLATE_X,
                        FATHERS_MATERNAL_GRANDFATHER_TRANSLATE_Y,
                    )
                    draw.rotate(fmgfr)
                    draw.text(fmgfx, fmgfy, fathers_maternal_grandfather.full_name)
                    print(
                        f"Drawn text at ({fmgfx}, {fmgfy}): {fathers_maternal_grandfather.full_name}"
                    )
                    fmgfx_birth, fmgfy_birth = (
                        FATHERS_MATERNAL_GRANDFATHER_BIRTH_X,
                        FATHERS_MATERNAL_GRANDFATHER_BIRTH_Y,
                    )
                    draw.text(
                        fmgfx_birth,
                        fmgfy_birth,
                        fathers_maternal_grandfather.birth_date or " ",
                    )
                    print(
                        f"Drawn text at ({fmgfx_birth}, {fmgfy_birth}): {fathers_maternal_grandfather.birth_date or ' '}"
                    )
                    fmgfx_death, fmgfy_death = (
                        FATHERS_MATERNAL_GRANDFATHER_DEATH_X,
                        FATHERS_MATERNAL_GRANDFATHER_DEATH_Y,
                    )
                    draw.text(
                        fmgfx_death,
                        fmgfy_death,
                        fathers_maternal_grandfather.death_date or " ",
                    )
                    print(
                        f"Drawn text at ({fmgfx_death}, {fmgfy_death}): {fathers_maternal_grandfather.death_date or ' '}"
                    )
                    fmgfx_place, fmgfy_place = (
                        FATHERS_MATERNAL_GRANDFATHER_PLACE_X,
                        FATHERS_MATERNAL_GRANDFATHER_PLACE_Y,
                    )
                    draw.text(
                        fmgfx_place,
                        fmgfy_place,
                        fathers_maternal_grandfather.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({fmgfx_place}, {fmgfy_place}): {fathers_maternal_grandfather.birth_place or ' '}"
                    )

                if fathers_maternal_grandmother:
                    print(
                        f"Drawing father's maternal grandmother: {fathers_maternal_grandmother.full_name}"
                    )
                    fmgmfx, fmgmfy, fmgmfr = (
                        FATHERS_MATERNAL_GRANDMOTHER_X,
                        FATHERS_MATERNAL_GRANDMOTHER_Y,
                        FATHERS_MATERNAL_GRANDMOTHER_ROTATE,
                    )
                    draw.translate(
                        FATHERS_MATERNAL_GRANDMOTHER_TRANSLATE_X,
                        FATHERS_MATERNAL_GRANDMOTHER_TRANSLATE_Y,
                    )
                    draw.rotate(fmgmfr)
                    draw.text(fmgmfx, fmgmfy, fathers_maternal_grandmother.full_name)
                    print(
                        f"Drawn text at ({fmgmfx}, {fmgmfy}): {fathers_maternal_grandmother.full_name}"
                    )
                    fmgmfx_birth, fmgmfy_birth = (
                        FATHERS_MATERNAL_GRANDMOTHER_BIRTH_X,
                        FATHERS_MATERNAL_GRANDMOTHER_BIRTH_Y,
                    )
                    draw.text(
                        fmgmfx_birth,
                        fmgmfy_birth,
                        fathers_maternal_grandmother.birth_date or " ",
                    )
                    print(
                        f"Drawn text at ({fmgmfx_birth}, {fmgmfy_birth}): {fathers_maternal_grandmother.birth_date or ' '}"
                    )
                    fmgmfx_death, fmgmfy_death = (
                        FATHERS_MATERNAL_GRANDMOTHER_DEATH_X,
                        FATHERS_MATERNAL_GRANDMOTHER_DEATH_Y,
                    )
                    draw.text(
                        fmgmfx_death,
                        fmgmfy_death,
                        fathers_maternal_grandmother.death_date or " ",
                    )
                    print(
                        f"Drawn text at ({fmgmfx_death}, {fmgmfy_death}): {fathers_maternal_grandmother.death_date or ' '}"
                    )
                    fmgmfx_place, fmgmfy_place = (
                        FATHERS_MATERNAL_GRANDMOTHER_PLACE_X,
                        FATHERS_MATERNAL_GRANDMOTHER_PLACE_Y,
                    )
                    draw.text(
                        fmgmfx_place,
                        fmgmfy_place,
                        fathers_maternal_grandmother.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({fmgmfx_place}, {fmgmfy_place}): {fathers_maternal_grandmother.birth_place or ' '}"
                    )

                # Draw mother's paternal grandparents
                if mothers_paternal_grandfather:
                    print(
                        f"Drawing mother's paternal grandfather: {mothers_paternal_grandfather.full_name}"
                    )
                    mpgfx, mpgfy, mpgfr = (
                        MOTHERS_PATERNAL_GRANDFATHER_X,
                        MOTHERS_PATERNAL_GRANDFATHER_Y,
                        MOTHERS_PATERNAL_GRANDFATHER_ROTATE,
                    )
                    draw.translate(
                        MOTHERS_PATERNAL_GRANDFATHER_TRANSLATE_X,
                        MOTHERS_PATERNAL_GRANDFATHER_TRANSLATE_Y,
                    )
                    draw.rotate(mpgfr)
                    draw.text(mpgfx, mpgfy, mothers_paternal_grandfather.full_name)
                    print(
                        f"Drawn text at ({mpgfx}, {mpgfy}): {mothers_paternal_grandfather.full_name}"
                    )
                    mpgfx_birth, mpgfy_birth = (
                        MOTHERS_PATERNAL_GRANDFATHER_BIRTH_X,
                        MOTHERS_PATERNAL_GRANDFATHER_BIRTH_Y,
                    )
                    draw.text(
                        mpgfx_birth,
                        mpgfy_birth,
                        mothers_paternal_grandfather.birth_date or " ",
                    )
                    print(
                        f"Drawn text at ({mpgfx_birth}, {mpgfy_birth}): {mothers_paternal_grandfather.birth_date or ' '}"
                    )
                    mpgfx_death, mpgfy_death = (
                        MOTHERS_PATERNAL_GRANDFATHER_DEATH_X,
                        MOTHERS_PATERNAL_GRANDFATHER_DEATH_Y,
                    )
                    draw.text(
                        mpgfx_death,
                        mpgfy_death,
                        mothers_paternal_grandfather.death_date or " ",
                    )
                    print(
                        f"Drawn text at ({mpgfx_death}, {mpgfy_death}): {mothers_paternal_grandfather.death_date or ' '}"
                    )
                    mpgfx_place, mpgfy_place = (
                        MOTHERS_PATERNAL_GRANDFATHER_PLACE_X,
                        MOTHERS_PATERNAL_GRANDFATHER_PLACE_Y,
                    )
                    draw.text(
                        mpgfx_place,
                        mpgfy_place,
                        mothers_paternal_grandfather.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({mpgfx_place}, {mpgfy_place}): {mothers_paternal_grandfather.birth_place or ' '}"
                    )

                if mothers_paternal_grandmother:
                    print(
                        f"Drawing mother's paternal grandmother: {mothers_paternal_grandmother.full_name}"
                    )
                    mpgmfx, mpgmfy, mpgmfr = (
                        MOTHERS_PATERNAL_GRANDMOTHER_X,
                        MOTHERS_PATERNAL_GRANDMOTHER_Y,
                        MOTHERS_PATERNAL_GRANDMOTHER_ROTATE,
                    )
                    draw.translate(
                        MOTHERS_PATERNAL_GRANDMOTHER_TRANSLATE_X,
                        MOTHERS_PATERNAL_GRANDMOTHER_TRANSLATE_Y,
                    )
                    draw.rotate(mpgmfr)
                    draw.text(mpgmfx, mpgmfy, mothers_paternal_grandmother.full_name)
                    print(
                        f"Drawn text at ({mpgmfx}, {mpgmfy}): {mothers_paternal_grandmother.full_name}"
                    )
                    mpgmfx_birth, mpgmfy_birth = (
                        MOTHERS_PATERNAL_GRANDMOTHER_BIRTH_X,
                        MOTHERS_PATERNAL_GRANDMOTHER_BIRTH_Y,
                    )
                    draw.text(
                        mpgmfx_birth,
                        mpgmfy_birth,
                        mothers_paternal_grandmother.birth_date or " ",
                    )
                    print(
                        f"Drawn text at ({mpgmfx_birth}, {mpgmfy_birth}): {mothers_paternal_grandmother.birth_date or ' '}"
                    )
                    mpgmfx_death, mpgmfy_death = (
                        MOTHERS_PATERNAL_GRANDMOTHER_DEATH_X,
                        MOTHERS_PATERNAL_GRANDMOTHER_DEATH_Y,
                    )
                    draw.text(
                        mpgmfx_death,
                        mpgmfy_death,
                        mothers_paternal_grandmother.death_date or " ",
                    )
                    print(
                        f"Drawn text at ({mpgmfx_death}, {mpgmfy_death}): {mothers_paternal_grandmother.death_date or ' '}"
                    )
                    mpgmfx_place, mpgmfy_place = (
                        MOTHERS_PATERNAL_GRANDMOTHER_PLACE_X,
                        MOTHERS_PATERNAL_GRANDMOTHER_PLACE_Y,
                    )
                    draw.text(
                        mpgmfx_place,
                        mpgmfy_place,
                        mothers_paternal_grandmother.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({mpgmfx_place}, {mpgmfy_place}): {mothers_paternal_grandmother.birth_place or ' '}"
                    )

                # Draw mother's maternal grandparents
                if mothers_maternal_grandfather:
                    print(
                        f"Drawing mother's maternal grandfather: {mothers_maternal_grandfather.full_name}"
                    )
                    mmgfx, mmgfy, mmgfr = (
                        MOTHERS_MATERNAL_GRANDFATHER_X,
                        MOTHERS_MATERNAL_GRANDFATHER_Y,
                        MOTHERS_MATERNAL_GRANDFATHER_ROTATE,
                    )
                    draw.translate(
                        MOTHERS_MATERNAL_GRANDFATHER_TRANSLATE_X,
                        MOTHERS_MATERNAL_GRANDFATHER_TRANSLATE_Y,
                    )
                    draw.rotate(mmgfr)
                    draw.text(mmgfx, mmgfy, mothers_maternal_grandfather.full_name)
                    print(
                        f"Drawn text at ({mmgfx}, {mmgfy}): {mothers_maternal_grandfather.full_name}"
                    )
                    mmgfx_birth, mmgfy_birth = (
                        MOTHERS_MATERNAL_GRANDFATHER_BIRTH_X,
                        MOTHERS_MATERNAL_GRANDFATHER_BIRTH_Y,
                    )
                    draw.text(
                        mmgfx_birth,
                        mmgfy_birth,
                        mothers_maternal_grandfather.birth_date or " ",
                    )
                    print(
                        f"Drawn text at ({mmgfx_birth}, {mmgfy_birth}): {mothers_maternal_grandfather.birth_date or ' '}"
                    )
                    mmgfx_death, mmgfy_death = (
                        MOTHERS_MATERNAL_GRANDFATHER_DEATH_X,
                        MOTHERS_MATERNAL_GRANDFATHER_DEATH_Y,
                    )
                    draw.text(
                        mmgfx_death,
                        mmgfy_death,
                        mothers_maternal_grandfather.death_date or " ",
                    )
                    print(
                        f"Drawn text at ({mmgfx_death}, {mmgfy_death}): {mothers_maternal_grandfather.death_date or ' '}"
                    )
                    mmgfx_place, mmgfy_place = (
                        MOTHERS_MATERNAL_GRANDFATHER_PLACE_X,
                        MOTHERS_MATERNAL_GRANDFATHER_PLACE_Y,
                    )
                    draw.text(
                        mmgfx_place,
                        mmgfy_place,
                        mothers_maternal_grandfather.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({mmgfx_place}, {mmgfy_place}): {mothers_maternal_grandfather.birth_place or ' '}"
                    )

                if mothers_maternal_grandmother:
                    print(
                        f"Drawing mother's maternal grandmother: {mothers_maternal_grandmother.full_name}"
                    )
                    mmgmfx, mmgmfy, mmgmfr = (
                        MOTHERS_MATERNAL_GRANDMOTHER_X,
                        MOTHERS_MATERNAL_GRANDMOTHER_Y,
                        MOTHERS_MATERNAL_GRANDMOTHER_ROTATE,
                    )
                    draw.translate(
                        MOTHERS_MATERNAL_GRANDMOTHER_TRANSLATE_X,
                        MOTHERS_MATERNAL_GRANDMOTHER_TRANSLATE_Y,
                    )
                    draw.rotate(mmgmfr)
                    draw.text(mmgmfx, mmgmfy, mothers_maternal_grandmother.full_name)
                    print(
                        f"Drawn text at ({mmgmfx}, {mmgmfy}): {mothers_maternal_grandmother.full_name}"
                    )
                    mmgmfx_birth, mmgmfy_birth = (
                        MOTHERS_MATERNAL_GRANDMOTHER_BIRTH_X,
                        MOTHERS_MATERNAL_GRANDMOTHER_BIRTH_Y,
                    )
                    draw.text(
                        mmgmfx_birth,
                        mmgmfy_birth,
                        mothers_maternal_grandmother.birth_date or " ",
                    )
                    print(
                        f"Drawn text at ({mmgmfx_birth}, {mmgmfy_birth}): {mothers_maternal_grandmother.birth_date or ' '}"
                    )
                    mmgmfx_death, mmgmfy_death = (
                        MOTHERS_MATERNAL_GRANDMOTHER_DEATH_X,
                        MOTHERS_MATERNAL_GRANDMOTHER_DEATH_Y,
                    )
                    draw.text(
                        mmgmfx_death,
                        mmgmfy_death,
                        mothers_maternal_grandmother.death_date or " ",
                    )
                    print(
                        f"Drawn text at ({mmgmfx_death}, {mmgmfy_death}): {mothers_maternal_grandmother.death_date or ' '}"
                    )
                    mmgmfx_place, mmgmfy_place = (
                        MOTHERS_MATERNAL_GRANDMOTHER_PLACE_X,
                        MOTHERS_MATERNAL_GRANDMOTHER_PLACE_Y,
                    )
                    draw.text(
                        mmgmfx_place,
                        mmgmfy_place,
                        mothers_maternal_grandmother.birth_place or " ",
                    )
                    print(
                        f"Drawn text at ({mmgmfx_place}, {mmgmfy_place}): {mothers_maternal_grandmother.birth_place or ' '}"
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
