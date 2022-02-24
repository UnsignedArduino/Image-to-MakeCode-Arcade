from argparse import ArgumentParser
from math import sqrt
from pathlib import Path

from PIL import Image

parser = ArgumentParser(description="Convert an image to a MakeCode Arcade "
                                    "image!")
parser.add_argument("-i", "--input", metavar="PATH", type=Path, required=True,
                    help="The input image.")
parser.add_argument("-o", "--output", metavar="PATH", type=Path,
                    required=True,  # TODO: Do not require - if not passed in
                    #  output the output image to stdout
                    help="The output text file which contains a MakeCode "
                         "Arcade image.")
# TODO: Can resize to specified width/height with -s (width)x(height) or
#  --size (width)x(height)
# TODO: Can show preview image and not write anything when passed in -p or
#  --preview
args = parser.parse_args()
print(f"Arguments received: {args}")

input_path = args.input.expanduser().resolve()
print(f"Opening image {input_path}")
input_image = Image.open(input_path)

width, height = input_image.size
print(f"Size: {width}x{height}")

new_width, new_height = 160, None
print(f"Target size: {new_width}x{new_height}")

# Get new width/height in respect to aspect ratio
if new_height is None:
    new_height = round(new_width * height / width)
elif new_width is None:
    new_width = round(new_height * width / height)

print(f"New size: {new_width}x{new_height}")

# New resized image
output_image = input_image.resize((new_width, new_height), Image.ANTIALIAS)
# output_image.show()


def change_palette(image: Image.Image,
                   palette: list[tuple[int, int, int], ...]
                   ) -> Image.Image:
    """
    Get every pixel in the image and find the closest color to

    :param image: A PIL image.
    :param palette: A list of a tuple of 3 integers for every color allowed.
    :return: A new PIL image.
    """
    # https://stackoverflow.com/a/34367441/10291933

    def distance(c1: tuple[int, int, int],
                 c2: tuple[int, int, int]) -> float:
        """
        Gets the "distance" between the colors.

        :param c1: A tuple of 3 integers.
        :param c2: A tuple of 3 integers.
        :return: A float.
        """
        (r1, g1, b1) = c1
        (r2, g2, b2) = c2
        return sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

    def get_closest_color(c: tuple[int, int, int],
                          p: list[tuple[int, int, int], ...]
                          ) -> tuple[int, int, int]:
        """
        Gets the closest color to your color.

        :param c: The original color as a tuple of 3 integers.
        :param p: The palette as a list of tuples of 3 integers.
        :return: A tuple of 3 integers being a color in the palette.
        """
        return sorted(p, key=lambda color: distance(color, c))[0]

    new_image = image.copy()
    w, h = image.size

    for y in range(h):
        for x in range(w):
            new_color = get_closest_color(new_image.getpixel((x, y)), palette)
            new_image.putpixel((x, y), new_color)

    return new_image


arcade_palette = (
    "#000000",
    "#ffffff",
    "#ff2121",
    "#ff93c4",
    "#ff8135",
    "#fff609",
    "#249ca3",
    "#78dc52",
    "#003fad",
    "#87f2ff",
    "#8e2ec4",
    "#a4839f",
    "#5c406c",
    "#e5cdc4",
    "#91463d",
    "#000000",
)
# Remove # from colors
arcade_palette = [s.replace("#", "") for s in arcade_palette]
# Split the hex string into the RGB components
arcade_palette = [(n[:2], n[2:4], n[4:]) for n in arcade_palette]
# Convert them into actual numbers
arcade_palette = [(int(n[0], base=16),
                   int(n[1], base=16),
                   int(n[2], base=16)) for n in arcade_palette]
print(f"Using palette of {len(arcade_palette)} colors")

output_image = change_palette(output_image, arcade_palette)
# output_image.show()


def image_to_makecode_arcade(image: Image.Image,
                             palette: dict[tuple[int, int, int], str]) -> str:
    """
    Converts a PIL image to a MakeCode Arcade string.

    :param image: The image to convert.
    :param palette: A dictionary with keys being a color and values being the
     new color value.
    :return: A string which is a MakeCode Arcade image.
    """
    w, h = image.size

    mkcd_str = "img`\n"

    for y in range(h):
        for x in range(w):
            color = image.getpixel((x, y))
            mkcd_str += palette[color]
        mkcd_str += "\n"

    mkcd_str += "`"
    return mkcd_str


output_path = args.output.expanduser().resolve()
print(f"Writing to {output_path}")

# Convert palette to dictionary mapping from color tuples to string character
arcade_palette_map = {}
for index, color in enumerate(arcade_palette):
    arcade_palette_map[color] = hex(index)[2:]

output_path.write_text(image_to_makecode_arcade(output_image,
                                                arcade_palette_map))
