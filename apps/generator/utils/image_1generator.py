from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


def generate_family_tree(primary_individual):
    """
    Generate a family tree chart using Wand (Python ImageMagick binding)

    Args:
        primary_individual: Dict with name, birth_date, birth_place, death_date

    """  # Create a new image with the same dimensions as your template
    import os

    from django.conf import settings

    template_path = os.path.join(
        settings.BASE_DIR,
        "apps/generator/static/generator/images/base_image_templates",
        "US_LETTER_1GEN_BW.pdf",
    )
    with Image(filename=template_path, resolution=300) as img:
        with Drawing() as draw:
            # Set font (you'll need to specify the actual font you want to use)
            draw.gravity = "center"
            draw.font = "Arial"
            draw.font_size = 124

            # Draw the black square (center area)
            draw.fill_color = Color("black")
            draw.rectangle(left=1111, top=1381, width=327, height=327)

            # Draw the dividing lines
            draw.stroke_color = Color("black")
            draw.stroke_width = 10
            draw.line((1424, 1395), (1601, 1218))  # Diagonal line for father's side
            draw.line((949, 1870), (1125, 1694))  # Diagonal line for mother's side

            # Apply the drawing to the image
            draw(img)

            # Surname 0, Self / Subject, Surname 0 (Primary individual)
            draw.fill_color = Color("white")

            # 1. Move the drawing origin to your desired text location
            draw.translate(x=-34, y=-138)

            # 2. Rotate the coordinate system by 315 degrees
            draw.rotate(315)

            draw.text(0, 131, primary_individual["name"])
            draw.text(0, 98, primary_individual["birth_date"])
            draw.text(0, 67, primary_individual["birth_place"])

            # Apply the text drawing
            draw(img)

            # Save the final image
            img.save(filename="US_LETTER_4GEN_BW-output.pdf")
