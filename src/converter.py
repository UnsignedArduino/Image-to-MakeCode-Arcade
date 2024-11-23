import logging
from enum import Enum
from sys import stdout
from textwrap import indent
from typing import Optional, Union

from PIL import Image, ImageSequence
from PIL.Image import Resampling
from tqdm import tqdm

# from utils.palette import change_palette
from utils.fast_palette import change_palette
from utils.logger import create_logger

logger = create_logger(name=__name__, level=logging.DEBUG)


class OutputOptions(Enum):
    MAKECODE_ARCADE_STRING = "makecode_arcade_string"
    PIL_IMAGE = "pil_image"


def image_to_makecode_arcade(image: Image.Image,
                             palette: dict[tuple[int, int, int], str],
                             is_gif: bool = False) -> str:
    """
    Converts a PIL image to a MakeCode Arcade string.

    :param image: The image to convert.
    :param palette: A dictionary with keys being a color and values being the
     new color value.
    :param is_gif: Whether the image is a GIF. Defaults to False.
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


def convert(input: Image, output: OutputOptions,
            width: Optional[int] = None, height: Optional[int] = None,
            palette: Optional[str] = None,
            is_gif: Optional[bool] = False) -> Union[str, Image]:
    """
    Convert a PIL image to a string or another PIL image that previews the MakeCode
    Arcade image.

    :param input: Input PIL image
    :param output: An OutputOptions enum value, either MAKECODE_ARCADE_STRING or
     PIL_IMAGE.
    :param width: Width. If not provided, will be the width of the input image or auto
     calculated from height to keep aspect ratio.
    :param height: Height. If not provided, will be the height of the input image or
     auto calculated from width to keep aspect ratio.
    :param palette: A string of comma separated hex colors. Defaults to the MakeCode
     Arcade palette.
    :param is_gif: Whether the input is a GIF and we should try to create a list of
     MakeCode Arcade images. If output is PIL_IMAGE, then we will only return the first
     frame. Defaults to False.
    :return: Either a string with the MakeCode Arcade image or a PIL image that will
     preview.
    """
    # First calculate the new width and height
    img_width, img_height = input.size
    new_width, new_height = width, height
    if new_width is None and new_height is None:
        new_width, new_height = img_width, img_height
    logger.debug(f"Target size: {new_width if new_width is not None else '(auto)'}x"
                 f"{new_height if new_height is not None else '(auto)'}")
    if new_height is None:
        new_height = round(new_width * img_height / img_width)
    elif new_width is None:
        new_width = round(new_height * img_width / img_height)
    logger.debug(f"New size: {new_width}x{new_height}")

    # Resize
    if is_gif:
        output_frames = []
        frame_count = 0
        for frame in tqdm(ImageSequence.Iterator(input), desc="Resizing frames",
                          file=stdout):
            frame_count += 1
            output_frames.append(
                frame.resize((new_width, new_height), Resampling.LANCZOS))
            if output == OutputOptions.PIL_IMAGE:
                # We only return the first frame anyways
                break
        logger.debug(f"Resized {frame_count} frames")
    else:
        output_image = input.resize((new_width, new_height), Resampling.LANCZOS)
        logger.debug(f"Resized image")

    # Convert to desired palette
    if palette is None:
        palette = "#000000,#ffffff,#ff2121,#ff93c4,#ff8135,#fff609,#249ca3,#78dc52,#003fad,#87f2ff,#8e2ec4,#a4839f,#5c406c,#e5cdc4,#91463d,#000000"
    palette = palette.split(",")
    # Remove the hash from the hex strings
    palette = [s.replace("#", "") for s in palette]
    # Split the hex string into the RGB components
    palette = [(n[:2], n[2:4], n[4:]) for n in palette]
    # Convert them into actual numbers
    palette = [(int(n[0], base=16),
                int(n[1], base=16),
                int(n[2], base=16)) for n in palette]
    logger.debug(f"Using palette of {len(palette)} colors")

    if is_gif:
        if output == OutputOptions.PIL_IMAGE:
            logger.debug("Quantizing first frame with palette")
            logger.debug("Returning PIL image of first frame")
            return change_palette(output_frames[0], palette)
        logger.debug("Quantizing frames with palette")
        i = 0
        for frame in tqdm(output_frames, desc="Quantizing frames", file=stdout):
            output_frames[i] = change_palette(frame, palette)
            i += 1
    else:
        logger.debug("Quantizing image with palette")
        output_image = change_palette(output_image, palette)
        if output == OutputOptions.PIL_IMAGE:
            logger.debug("Returning PIL image")
            return output_image

    # Convert palette to dictionary mapping from color tuples to string character
    arcade_palette_map = {}
    for index, color in enumerate(palette):
        arcade_palette_map[color] = hex(index)[2:]

    # Convert image to MakeCode Arcade string
    if is_gif:
        logger.debug("Returning TypeScript code of list of MakeCode Arcade strings")
        output_str = "[\n"
        for frame in tqdm(output_frames, desc="Converting frames", file=stdout):
            original_lines = image_to_makecode_arcade(
                frame, arcade_palette_map).splitlines(keepends=True)
            text = indent(original_lines[0], " " * 4)
            text += indent("".join(original_lines[1:-1]), " " * 8)
            text += indent(original_lines[-1], " " * 4)
            text += ",\n"
            output_str += text
        output_str += "]"
        return output_str
    else:
        logger.debug("Returning TypeScript code of MakeCode Arcade string")
        return image_to_makecode_arcade(output_image, arcade_palette_map)
