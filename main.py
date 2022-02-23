from argparse import ArgumentParser
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

if new_height is None:
    new_height = round(new_width * height / width)
elif new_width is None:
    new_width = round(new_height * width / height)

print(f"New size: {new_width}x{new_height}")

output_image = input_image.resize((new_width, new_height), Image.ANTIALIAS)
# output_image.show()
