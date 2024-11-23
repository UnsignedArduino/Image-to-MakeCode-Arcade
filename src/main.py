import logging
from argparse import ArgumentParser
from pathlib import Path

from PIL import Image

from converter import OutputOptions, convert
from utils.logger import create_logger, set_all_stdout_logger_levels

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
parser.add_argument("--debug", action="store_const",
                    const=logging.DEBUG, default=logging.INFO,
                    help="Include debug messages. Defaults to info and "
                         "greater severity messages only.")
args = parser.parse_args()
logger = create_logger(name=__name__, level=logging.INFO)
set_all_stdout_logger_levels(args.debug)
logger.debug(f"Received arguments: {args}")

input_path = args.input.expanduser().resolve()
logger.info(f"Opening {'GIF' if args.gif else 'image'} {input_path}")
input_image = Image.open(input_path)

logger.debug("Converting")
output = convert(input_image,
                 OutputOptions.PIL_IMAGE if args.preview else OutputOptions.MAKECODE_ARCADE_STRING,
                 args.width, args.height, args.palette, args.gif)
if args.preview:
    output.show()
else:
    if args.output is None:
        print(output)
    else:
        output_path = args.output.expanduser().resolve()
        logger.info(f"Writing MakeCode Arcade image to {args.output}")
        output_path.write_text(output)
