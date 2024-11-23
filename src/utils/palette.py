from math import sqrt

from PIL import Image


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


def change_palette(image: Image.Image,
                   palette: list[tuple[int, int, int], ...]) -> Image:
    """
    Get every pixel in the image and find the closest color to it.

    :param image: A PIL image.
    :param palette: A list of a tuple of 3 integers for every color allowed.
    :return: A new PIL image.
    """

    new_image = image.copy().convert("RGB")
    w, h = new_image.size

    for y in range(h):
        for x in range(w):
            pixel = new_image.getpixel((x, y))
            new_color = get_closest_color(pixel, palette)
            new_image.putpixel((x, y), new_color)

    return new_image


def change_palette_in_gif(image: Image.Image,
                          palette: list[tuple[int, int, int], ...],
                          original_input_image: Image.Image) -> Image:
    """
    Get every pixel in the image and find the closest color to it

    :param image: A PIL image.
    :param palette: A list of a tuple of 3 integers for every color allowed.
    :param original_input_image: The original input image, which should be a GIF so we
     can reference the palette.
    :return: A new PIL image.
    """
    new_image = image.copy().convert("RGB")
    w, h = new_image.size

    index_to_color = {v: k for k, v in original_input_image.palette.colors.items()}

    for y in range(h):
        for x in range(w):
            pixel = new_image.getpixel((x, y))
            if isinstance(pixel, int):
                pixel_color = index_to_color[pixel]
            elif len(pixel) > 3:
                pixel_color = pixel[:-1]  # Skip alpha
            else:
                pixel_color = pixel
            new_color = get_closest_color(pixel_color, palette)
            new_image.putpixel((x, y), new_color)

    return new_image
