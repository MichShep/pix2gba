from PIL import Image as PILImage
import math

from .gba_utils import rgb24_to_rgb15

def create_tile_data(file_path:str, conversion_table:dict, meta_w:int, meta_h:int, bpp:int, hex_out:bool=True) -> list:
    """
    Takes the input image path and based on meta height and width separates them by GBA tiles (8x8 pixels)
    and given a conversion table form rgb24 to rgb15, creates the VRAM data of palette indices.
    :param file_path: Path to the input image
    :param conversion_table: Dictionary of rgb24 colors to rgb15 colors (native GBA color)
    :param meta_w: Number of tiles one meta tile's width consists of
    :param meta_h: Number of tiles one meta tile's height consists of
    :param bpp: The number of bits per pixel into a palette
    :param hex_out: If the data should be converted to HEX format
    :return: A list of the created VRAM data
    """

    # Load the image and ensure it is in RGB format
    img = PILImage.open(file_path).convert("RGB")
    width, height = img.size

    # Pad the image dimensions so they are multiples of 8 (GBA tile size)
    round_width = math.ceil(width / 8) * 8
    round_height = math.ceil(height / 8) * 8
    if (round_width, round_height) != (width, height):
        # Create a padded image using magenta as the filler color
        padded = PILImage.new("RGB", (round_width, round_height), (255, 0, 255))
        padded.paste(img, (0, 0))
        img = padded
        width, height = round_width, round_height

    # Total pixel dimensions of a single metatile
    meta_total_width = meta_w * 8
    meta_total_height = meta_h * 8

    # Compute overall data size metrics
    num_pxl = width * height              # Total number of pixels
    num_bits = num_pxl * bpp              # Total number of bits
    num_bytes = num_bits // 8             # Total number of bytes
    num_u32 = num_bytes // 4              # Total number of 32-bit words

    # Number of metatiles that fit horizontally
    num_metatiles_width = width // (meta_w * 8)

    # Pixel traversal state
    y = 0
    x_offset = y_offset = 0

    # Counters for tile, metatile, and pixel traversal
    pxl_bit_count = pxl_row_count = meta_row_count = meta_col_count = 0
    metatile_row_count = metatile_col_count = 0
    total_meta_tiles = 0

    # Output tile data as a flat list
    tile_data_1d = []

    # Number of pixels packed into a single 32-bit word
    pixels_per_u32 = 32 // bpp

    # Number of bytes per pixel row segment (used implicitly)
    bits_per_pixel_row = bpp // 4
    # 8bpp -> 2
    # 4bpp -> 1

    try:
        # Iterate over each 32-bit word of output data
        for i in range(0, num_u32):  # Each U32 contains (32 / bpp) pixels
            line_offset = 0

            # Process one 8-pixel row of a tile in chunks
            for j in range(0, 8, pixels_per_u32):
                word = 0

                # Pack palette indices into a 32-bit word
                for x in range(pixels_per_u32):
                    # Read the pixel from the image
                    px = img.getpixel((x + x_offset + line_offset, y + y_offset))

                    # Convert RGB24 -> RGB15 -> palette index
                    idx = conversion_table[rgb24_to_rgb15(px)]

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
                total_meta_tiles += 1
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
