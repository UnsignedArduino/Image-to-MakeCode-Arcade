from argparse import ArgumentParser
from math import sqrt
from pathlib import Path
from tempfile import NamedTemporaryFile
from textwrap import indent

from PIL import Image, ImageSequence

parser = ArgumentParser(description="Convert an image to a MakeCode Arcade "
                                    "image!")
parser.add_argument("-i", "--input", metavar="PATH", type=Path, required=True,
                    help="The input image.")
parser.add_argument("-o", "--output", metavar="PATH", type=Path,
                    required=False,
                    help="The output text file which contains a MakeCode "
                         "Arcade image.")
parser.add_argument("-p", "--preview", action="store_true",
                    help="Whether to preview the outputted image in the "
                         "default image viewer instead of writing to a file "
                         "or standard output. ")
parser.add_argument("--width", metavar="W", type=int, required=False,
                    help="The width of the resulting MakeCode Arcade image."
                         "If height is omitted, aspect ratio will be "
                         "respected.")
parser.add_argument("--height", metavar="H", type=int, required=False,
                    help="The height of the resulting MakeCode Arcade image."
                         "If width is omitted, aspect ratio will be "
                         "respected.")
parser.add_argument("--palette", type=str, required=False,
                    default="#000000,#ffffff,#ff2121,#ff93c4,"
                            "#ff8135,#fff609,#249ca3,#78dc52,"
                            "#003fad,#87f2ff,#8e2ec4,#a4839f,"
                            "#5c406c,#e5cdc4,#91463d,#000000",
                    help="The palette to use. Must be a string of comma "
                         "separated 6-digit hex codes. For example: \""
                         "#000000,#ffffff,#ff2121,#ff93c4,"
                         "#ff8135,#fff609,#249ca3,#78dc52,"
                         "#003fad,#87f2ff,#8e2ec4,#a4839f,"
                         "#5c406c,#e5cdc4,#91463d,#000000\" (that is the "
                         "default palette for this tool and MakeCode Arcade)"
                    )
parser.add_argument("-g", "--gif", action="store_true", required=False,
                    help="Whether to try to read the image as a GIF. If "
                         "specified, the output will be a TypeScript list of "
                         "images.")
args = parser.parse_args()

can_log = args.output is not None or args.preview

if can_log:
    print(f"Arguments received: {args}")

is_gif = args.gif

input_path = args.input.expanduser().resolve()
if can_log:
    print(f"Opening {'GIF' if is_gif else 'image'} {input_path}")
input_image = Image.open(input_path)

if is_gif and can_log:
    print(f"First frame is {input_image.info['duration']} ms long")

width, height = input_image.size
if can_log:
    print(f"Size: {width}x{height}")

new_width, new_height = args.width, args.height

if new_width is None and new_height is None:
    print("Width and height were not specified, defaulting to width of 160 "
          "pixels and auto-calculated height!")
    new_width = 160

if can_log:
    print(f"Target size: {new_width if new_width is not None else '(auto)'}x"
          f"{new_height if new_height is not None else '(auto)'}")

# Get new width/height in respect to aspect ratio
if new_height is None:
    new_height = round(new_width * height / width)
elif new_width is None:
    new_width = round(new_height * width / height)

if can_log:
    print(f"New size: {new_width}x{new_height}")

# New resized image
if is_gif:
    resized_gif_frames = []
    frame_count = 0
    for frame in ImageSequence.Iterator(input_image):
        frame_count += 1
        # print(f"On frame {frame_count} {frame.size}")
        resized_gif_frames.append(frame.resize((new_width, new_height),
                                               Image.ANTIALIAS))
    if can_log:
        print(f"Resized {frame_count} frames")
else:
    output_image = input_image.resize((new_width, new_height), Image.ANTIALIAS)
    if can_log:
        print(f"Resized image")
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
        return sorted(p, key=lambda col: distance(col, c))[0]

    new_image = image.copy()
    w, h = new_image.size

    if is_gif:
        index_to_color = {v: k for k, v in input_image.palette.colors.items()}

    for y in range(h):
        for x in range(w):
            pixel = new_image.getpixel((x, y))
            if is_gif:
                if isinstance(pixel, int):
                    pixel_color = index_to_color[pixel]
                elif len(pixel) > 3:
                    pixel_color = pixel[:-1]  # Skip alpha
                new_color = get_closest_color(pixel_color, palette)
                new_image.putpixel((x, y), new_color)
            else:
                new_color = get_closest_color(pixel, palette)
                new_image.putpixel((x, y), new_color)

    return new_image


# palette = (
#     "#000000",
#     "#ffffff",
#     "#ff2121",
#     "#ff93c4",
#     "#ff8135",
#     "#fff609",
#     "#249ca3",
#     "#78dc52",
#     "#003fad",
#     "#87f2ff",
#     "#8e2ec4",
#     "#a4839f",
#     "#5c406c",
#     "#e5cdc4",
#     "#91463d",
#     "#000000",
# )
palette = args.palette.split(",")
# Remove # from colors
palette = [s.replace("#", "") for s in palette]
# Split the hex string into the RGB components
palette = [(n[:2], n[2:4], n[4:]) for n in palette]
# Convert them into actual numbers
palette = [(int(n[0], base=16),
            int(n[1], base=16),
            int(n[2], base=16)) for n in palette]
if can_log:
    print(f"Using palette of {len(palette)} colors")

if is_gif:
    output_images = []
    frame_count = 0
    for frame in resized_gif_frames:
        frame_count += 1
        # print(f"On frame {frame_count} {frame.size}")
        output_images.append(change_palette(frame, palette))
    if can_log:
        print(f"Changed palette of {frame_count} frames")
    if args.preview:
        if can_log:
            print(f"Previewing!")
        preview_image = output_images[0].copy()
        with NamedTemporaryFile(suffix=".gif", delete=False) as gif_bytes:
            preview_image.save(gif_bytes, save_all=True,
                               append_images=output_images[1:],
                               format="GIF")
            gif_path = Path(gif_bytes.name)
            print(f"Saved to {gif_path}")
        preview_image = Image.open(gif_path)
        preview_image.show()
        exit()
else:
    output_image = change_palette(output_image, palette)
    if can_log:
        print(f"Changed palette")
    if args.preview:
        if can_log:
            print(f"Previewing!")
        output_image.show()
        exit(0)


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

    if is_gif and image.palette is not None:
        index_to_color = {v: k for k, v in image.palette.colors.items()}

    for y in range(h):
        for x in range(w):
            if is_gif:
                color = image.getpixel((x, y))
                if isinstance(color, int):
                    color = index_to_color[color]
                elif isinstance(color, tuple) and len(color) > 3:
                    color = color[:-1]
                mkcd_str += palette[color]
            else:
                color = image.getpixel((x, y))
                mkcd_str += palette[color]
        mkcd_str += "\n"

    mkcd_str += "`"
    return mkcd_str


# Convert palette to dictionary mapping from color tuples to string character
arcade_palette_map = {}
for index, color in enumerate(palette):
    arcade_palette_map[color] = hex(index)[2:]

if is_gif:
    text = "[\n"
    for output in output_images:
        original_lines = image_to_makecode_arcade(output, arcade_palette_map).splitlines(keepends=True)
        text += indent(original_lines[0], " " * 4)
        text += indent("".join(original_lines[1:-1]), " " * 8)
        text += indent(original_lines[-1], " " * 4)
        text += ",\n"
    text += "]"
else:
    text = image_to_makecode_arcade(output_image, arcade_palette_map)

if args.output is not None:
    output_path = args.output.expanduser().resolve()
    if can_log:
        print(f"Writing to {output_path}")
    output_path.write_text(text)
else:
    print(text)
