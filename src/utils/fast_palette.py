# Since I'm bad at coding thanks Copilot

import numpy as np
from PIL import Image
from scipy.spatial import KDTree


def change_palette(image: Image.Image,
                   palette: list[tuple[int, int, int], ...]) -> Image:
    """
    Get every pixel in the image and find the closest color to it using KD-Tree.

    :param image: A PIL image.
    :param palette: A list of a tuple of 3 integers for every color allowed.
    :return: A new PIL image.
    """
    new_image = image.copy().convert("RGB")
    w, h = new_image.size

    # Convert image to NumPy array
    pixels = np.array(new_image)

    # Flatten the array for easier processing
    pixels_flat = pixels.reshape(-1, 3)

    # Create KD-Tree for the palette
    palette_array = np.array(palette)
    tree = KDTree(palette_array)

    # Find the closest palette color for each pixel
    _, indices = tree.query(pixels_flat)
    new_pixels_flat = palette_array[indices]

    # Reshape back to the original image shape
    new_pixels = new_pixels_flat.reshape(h, w, 3)

    # Convert back to PIL image
    new_image = Image.fromarray(new_pixels.astype('uint8'), 'RGB')

    return new_image


def change_palette_in_gif(image: Image.Image, palette: list[tuple[int, int, int], ...],
                          original_input_image: Image.Image) -> Image:
    """
    Get every pixel in the image and find the closest color to it using KD-Tree.

    :param image: A PIL image.
    :param palette: A list of a tuple of 3 integers for every color allowed.
    :param original_input_image: The original input image, which should be a GIF so we can reference the palette.
    :return: A new PIL image.
    """
    new_image = image.copy().convert("RGB")
    w, h = new_image.size

    # Convert image to NumPy array
    pixels = np.array(new_image)

    # Flatten the array for easier processing
    pixels_flat = pixels.reshape(-1, 3)

    # Create KD-Tree for the palette
    palette_array = np.array(palette)
    tree = KDTree(palette_array)

    # Get the original palette colors
    index_to_color = {v: k for k, v in original_input_image.palette.colors.items()}

    # Convert pixel indices to colors
    pixel_colors = np.array(
        [index_to_color[pixel] if isinstance(pixel, int) else pixel[:3] for pixel in
         pixels_flat])

    # Find the closest palette color for each pixel
    _, indices = tree.query(pixel_colors)
    new_pixels_flat = palette_array[indices]

    # Reshape back to the original image shape
    new_pixels = new_pixels_flat.reshape(h, w, 3)

    # Convert back to PIL image
    new_image = Image.fromarray(new_pixels.astype('uint8'), 'RGB')

    return new_image
