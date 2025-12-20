import os.path

from PIL import Image as PILImage
from .gba_utils import rgb24_to_rgb15, unpack_gba_color
import numpy as np

def float_transparent_color(gba_palette:list, transparent:int) -> list:
    """
    Will take the transparent color and will force it to be the first color in palette.
    The old first color will become the last color.
    :param gba_palette: The current palette of the input image.
    :param transparent: The RGB15 value of the transparent color.
    :return: The palette with the transparent color at index 0
    """
    old_first = gba_palette[0] if len(gba_palette) > 0 else None

    if transparent in gba_palette:
        gba_palette.remove(transparent)

    gba_palette.insert(0, transparent)

    if old_first is not None and old_first != transparent:
        gba_palette.append(old_first)

    return gba_palette

def extract_palette_img(filename:str, bpp:int, transparent:int) -> list:
    """
    Extract a GBA palette directly from an image where each pixel represents
    a palette entry.

    :param transparent: The RGB15 value of the transparent color
    :param filename: Path to the palette image file.
    :param bpp: Bits per pixel; palette size is 2^bpp.
    :return: List of GBA RGB15 palette entries.
    """
    if not os.path.exists(filename):
        print("ERROR: Path to palette image file doesn't exist")
        return None

    img = PILImage.open(filename).convert("RGB")
    width, height = img.size

    if (width * height) > (1 << bpp):
        print(f"ERROR: Too many pixels for bpp (curr: {width * height}; max: {(1 << bpp)}) ")
        return None

    gba_palette = []
    for j in range(height):
        for i in range(width):
            pxl = img.getpixel((i, j))
            gba_palette.append(
                rgb24_to_rgb15(pxl)
            )

    # Force magenta as palette index 0 (transparency key)
    float_transparent_color(gba_palette, transparent)

    return gba_palette


def palette_from_img(filename:str, bpp:int, transparent:int) -> list:
    """
    Generate a GBA palette from an image by selecting the most frequently
    used colors and enforcing GBA palette constraints.

    :param filename: Path to the source image file.
    :param bpp: Bits per pixel; palette size is 2^bpp.
    :param transparent: The RGB15 value of the transparent color
    :return: List of GBA RGB15 palette entries.
    """
    img = PILImage.open(filename).convert("RGB")

    colors = img.getcolors()
    colors.sort(key=lambda c: c[0], reverse=True)

    top_col = [color for count, color in colors[:2**bpp]]
    gba_palette = [rgb24_to_rgb15(color) for color in top_col]

    gba_palette = list(set(gba_palette))

    float_transparent_color(gba_palette, transparent)

    gba_palette = gba_palette[:2**bpp]

    return gba_palette


def closest_gba_color(color:int, gba_palette:list) -> int:
    """
    Find the closest matching GBA palette color using Euclidean distance
    in RGB space.

    :param color: GBA RGB15 color to match.
    :param gba_palette: List of GBA RGB15 palette entries.
    :return: Index of the closest matching palette color.
    """
    target = unpack_gba_color(color)
    colors = np.array(
        [unpack_gba_color(c) for c in gba_palette],
        dtype=np.int16
    )

    distances = np.sqrt(np.sum((colors - target) ** 2, axis=1))
    return int(np.argmin(distances))


def create_conversion_table(input_img, gba_palette):
    """
    Create a lookup table mapping image colors to palette indices based
    on closest GBA color matching.

    :param input_img: Path to the input image file.
    :param gba_palette: List of GBA RGB15 palette entries.
    :return: Dictionary mapping RGB15 colors to palette indices.
    """
    img = PILImage.open(input_img).convert("RGB")
    img_palette = img.getcolors()

    img24_to_gba15 = {}

    for junk, color in img_palette:
        gba_col = rgb24_to_rgb15(color)

        closest_idx = closest_gba_color(gba_col, gba_palette)
        img24_to_gba15[gba_col] = closest_idx

    return img24_to_gba15
