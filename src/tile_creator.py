from PIL import Image as PILImage
import math
from typing import Union

from .gba_utils import rgb24_to_rgb15
from .units import ConversionUnit

def padded_dimensions(width: int, height: int, meta_w: int, meta_h: int) -> tuple[int, int]:
    """
    Rounds image dimensions up to a whole number of metatiles.
    :param width: Image width in pixels.
    :param height: Image height in pixels.
    :param meta_w: Metatile width in 8x8 tiles.
    :param meta_h: Metatile height in 8x8 tiles.
    :return: Padded (width, height) in pixels.
    """
    meta_px_w = meta_w * 8
    meta_px_h = meta_h * 8
    return math.ceil(width / meta_px_w) * meta_px_w, math.ceil(height / meta_px_h) * meta_px_h

def create_tile_data(unit: ConversionUnit, conversion_table: dict[int, int], hex_out: bool = True) -> list[Union[str, int]]:
    """
    Packs an image into GBA tile data, ordered by metatile.
    :param unit: Unit whose image is converted.
    :param conversion_table: Maps each RGB15 image color to a palette index.
    :param hex_out: If True, words are "0x%08x" strings, otherwise plain ints.
    :return: Flat list of packed u32 words.
    """
    file_path = unit.image_path
    meta_w = unit.metatile_width
    meta_h = unit.metatile_height
    bpp = unit.bpp

    # Load the image and ensure it is in RGB format
    img = PILImage.open(file_path).convert("RGB")
    img_width, img_height = img.size

    # Pad the dimensions to whole metatiles; pixels outside the image use palette index 0 (transparent)
    width, height = padded_dimensions(img_width, img_height, meta_w, meta_h)

    # Total pixel dimensions of a single metatile
    meta_total_width = meta_w * 8
    meta_total_height = meta_h * 8

    # Compute overall data size metrics
    num_pxl = width * height              # Total number of pixels
    num_tile_rows = num_pxl // 8          # Total number of 8-pixel tile rows

    # Number of metatiles that fit horizontally
    num_metatiles_width = width // (meta_w * 8)

    # Pixel traversal state
    y = 0
    x_offset = y_offset = 0

    # Counters for tile, metatile, and pixel traversal
    pxl_row_count = meta_row_count = meta_col_count = 0
    metatile_row_count = metatile_col_count = 0

    # Output tile data as a flat list
    tile_data_1d = []

    # Number of pixels packed into a single 32-bit word
    pixels_per_u32 = 32 // bpp

    try:
        # Iterate over each 8-pixel tile row (one or more 32-bit words, depending on bpp)
        for _ in range(num_tile_rows):
            line_offset = 0

            # Process one 8-pixel row of a tile in chunks
            for _ in range(0, 8, pixels_per_u32):
                word = 0

                # Pack palette indices into a 32-bit word
                for x in range(pixels_per_u32):
                    px_x = x + x_offset + line_offset
                    px_y = y + y_offset

                    if px_x >= img_width or px_y >= img_height:
                        # Padding pixel -> transparent palette index
                        idx = 0
                    else:
                        # Convert RGB24 -> RGB15 -> palette index
                        idx = conversion_table[rgb24_to_rgb15(img.getpixel((px_x, px_y)))]

                    # Shift palette index into the correct position
                    shift = bpp * x
                    word |= (idx << shift)

                # Advance horizontally within the tile row
                line_offset += pixels_per_u32

                # Append the packed word to output (hex or raw integer)
                if hex_out:
                    tile_data_1d.append(f"0x{word:08x}")
                else:
                    tile_data_1d.append(word)

            # Move to the next pixel row
            y += 1
            pxl_row_count += 1

            # Finished an 8-pixel-high tile
            if pxl_row_count % 8 == 0:
                y = 0
                meta_col_count += 1

            # Finished a row of tiles within a metatile
            if meta_col_count % meta_w == 0 and meta_col_count != 0:
                meta_row_count += 1
                meta_col_count = 0

            # Finished a full metatile
            if meta_row_count % meta_h == 0 and meta_row_count != 0:
                metatile_col_count += 1
                meta_row_count = 0

            # Move to the next metatile row
            if metatile_col_count % num_metatiles_width == 0 and metatile_col_count != 0:
                metatile_row_count += 1
                metatile_col_count = 0

            # Compute the current pixel offsets based on tile and metatile position
            x_offset = meta_col_count * 8 + metatile_col_count * meta_total_width
            y_offset = meta_row_count * 8 + metatile_row_count * meta_total_height

    except IndexError:
        # Catch out-of-bounds access caused by misaligned traversal
        print("ERROR: Out of bounds for", x_offset, y_offset, "on dimensions", width, height)

    return tile_data_1d
