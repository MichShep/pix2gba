from PIL import Image as PILImage
import gba_utils as gf
import numpy as np

MAGENTA = 0x5d53


def extract_palette_img(filename:str, bpp:int) -> list:
    """
    Extract a GBA palette directly from an image where each pixel represents
    a palette entry.

    :param filename: Path to the palette image file.
    :param bpp: Bits per pixel; palette size is 2^bpp.
    :return: List of GBA RGB15 palette entries.
    """
    img = PILImage.open(filename).convert("RGB")
    width, height = img.size

    if (width * height) > (1 << bpp):
        print(f"ERROR: Too many pixels for bpp (curr: {width * height}; max: {(1 << bpp)}) ")
        exit(1)

    gba_palette = []
    for j in range(height):
        for i in range(width):
            pxl = img.getpixel((i, j))
            gba_palette.append(
                gf.rgb24_to_rgb15(pxl)
            )

    # Force magenta as palette index 0 (transparency key)
    gba_palette[0] = MAGENTA

    return gba_palette


def palette_from_img(filename:str, bpp:int) -> list:
    """
    Generate a GBA palette from an image by selecting the most frequently
    used colors and enforcing GBA palette constraints.

    :param filename: Path to the source image file.
    :param bpp: Bits per pixel; palette size is 2^bpp.
    :return: List of GBA RGB15 palette entries.
    """
    img = PILImage.open(filename).convert("RGB")
    width, height = img.size

    colors = img.getcolors()
    colors.sort(key=lambda c: c[0], reverse=True)

    top_col = [color for count, color in colors[:2**bpp]]
    gba_palette = [gf.rgb24_to_rgb15(color) for color in top_col]

    gba_palette = list(set(gba_palette))

    old_first = gba_palette[0] if len(gba_palette) > 0 else None

    if MAGENTA in gba_palette:
        gba_palette.remove(MAGENTA)

    gba_palette.insert(0, MAGENTA)

    if old_first is not None and old_first != MAGENTA:
        gba_palette.append(old_first)

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
    target = gf.unpack_gba_color(color)
    colors = np.array(
        [gf.unpack_gba_color(c) for c in gba_palette],
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
        gba_col = gf.rgb24_to_rgb15(color)

        closest_idx = closest_gba_color(gba_col, gba_palette)
        img24_to_gba15[gba_col] = closest_idx

    return img24_to_gba15
