from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color

# Create a blank image (1950x1950)
with Image(width=1950, height=1950, background=Color('white')) as img:
    with Drawing() as draw:
        draw.font = 'Arial'
        draw.font_size = 88
        draw.fill_color = 'green'
        draw.stroke_color = 'black'
        draw.stroke_width = .5
        draw.stroke_antialias = True

        text = "21 Nov 1928" or " "
        print(f"Text to draw: '{text}'")

        # Draw the text unrotated on a temporary image
        with Image(width=500, height=1950, background=Color('transparent')) as text_img:
            print(f"Temporary image dimensions (before rotation): {text_img.width}x{text_img.height}")

            # Draw the text vertically centered in the temporary image
            draw.text(0, (text_img.height // 2) + (88 // 2), text)
            draw(text_img)

            # Rotate the text image by -90 degrees
            text_img.rotate(-90)
            print(f"Temporary image dimensions (after rotation): {text_img.width}x{text_img.height}")

            # Calculate composite position: 150px from the left, vertically centered
            left = 150
            top = (img.height - text_img.height) // 2
            print(f"Compositing rotated text at position: left={left}, top={top}")

            # Draw a red rectangle around the composited area
            with Drawing() as debug_draw:
                debug_draw.stroke_color = Color('red')
                debug_draw.stroke_width = 3
                debug_draw.rectangle(left=left, top=top, width=text_img.width, height=text_img.height)
                debug_draw(img)

            # Composite the rotated text onto the main image
            img.composite(text_img, left=left, top=top)

    # Save the result
    img.save(filename='final_rotated_output.png')
    print("Image saved as final_rotated_output.png. Check for text inside the red rectangle.")
