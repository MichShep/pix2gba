from os import write
from pathlib import Path
from .tile_output import create_tile_data
from .deduper import dedupe_tiles
import ctypes
import struct
from PIL import Image as PILImage
from datetime import datetime
LoadedImage = PILImage.Image

lib = ctypes.CDLL("./bin/lz77.so")

lib.GBA_LZ77CompressBound.argtypes = [ctypes.c_size_t]
lib.GBA_LZ77CompressBound.restype  = ctypes.c_size_t

lib.GBA_LZ77Compress.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t
]
lib.GBA_LZ77Compress.restype = ctypes.c_ssize_t


def gba_lz77_compress(data: bytes) -> bytes:
    """
    The compression function that invokes a cpp bin to compress the data
    :param data: Uncompressed byte stream of the unit
    :return: Compressed byte stream of the unit
    """
    # Ensure we have an immutable bytes object for from_buffer_copy
    if isinstance(data, bytearray):
        data = bytes(data)
    elif not isinstance(data, (bytes, bytearray)):
        data = bytes(data)

    in_len = len(data)
    in_buf = (ctypes.c_ubyte * in_len).from_buffer_copy(data)

    # Use the *bound* function (not the compressor) to size the output buffer
    out_cap = lib.GBA_LZ77CompressBound(in_len)
    out_py  = bytearray(out_cap)
    out_buf = (ctypes.c_ubyte * out_cap).from_buffer(out_py)

    # Call the correct function name
    n = lib.GBA_LZ77Compress(in_buf, in_len, out_buf, out_cap)
    if n < 0:
        raise RuntimeError(f"GBA_LZ77Compress failed: {n}")
    return bytes(out_py[:n])

def create_compressed_header_file(arguments:dict, image:LoadedImage, compressed_bytes:int, gba_palette:list) -> None:
    """
    Creates the header file for the tile output.
    :param arguments: Command line arguments
    :param image: The PIL image
    :param compressed_bytes: Number of bytes the compressed image occupies
    :param gba_palette: The 2^bpp wide palette for the image (palette that will be in the GBA)
    """
    # Extract needed data
    meta_w = arguments["meta_width"]
    meta_h = arguments["meta_height"]
    bpp = arguments["bpp"]

    img_w = image.width
    img_h = image.height

    dest = arguments["destination_path"]
    file_path = arguments["image_path"]
    pal_path = arguments["palette_path"]

    file_name = Path(file_path).stem
    pal_name = Path(pal_path if pal_path is not None else file_path).stem

    # Data Size Calc
    num_pxl = img_w * img_h
    num_bits = num_pxl * bpp
    num_bytes = num_bits // 8
    num_u32 = num_bytes // 4

    # Num Tiles Calc
    num_tiles = num_pxl // (8*8)

    # Comments and stuff
    if arguments["dedupe"]:
        file_str = "// " + file_name + " on " + pal_name + " Palette; Compressed with LZ77; Deduped\n"
    else:
        file_str = "// " + file_name + " on " + pal_name + " Palette; Compressed with LZ77\n"
    file_str += "#pragma once\n\n"

    file_str += ("//======================================================================\n" +
                 "//	" + file_name + ", " + str(img_w) + "pxl by " + str(img_h) + "pxl @ " + str(bpp) + "bpp\n" +
                 "//\t+ Number of Tiles : " + str(num_tiles) + "\n" +
                 "//\t+ Metatile Shape  : " + str(meta_w) + "w by " + str(meta_h) + "h\n" +
                 "//\t+ Dimensions in MT: " + str(img_w//(8*meta_w)) + "w by " + str(img_h // (8*meta_h)) + "h\n" +
                 "//\t+ Compressed number of bytes   : " + str(compressed_bytes) + "\n" +
                 "//\t+ Decompressed number of bytes : " +  str(num_bytes) + "\n" +
                 "//\t+ Blank Color     : " + hex(gba_palette[0]) + "\n" +
                 "//\t" + str(datetime.now()) + "\n" +
                 "//======================================================================\n\n"
                 )

    # Action externs and defines of the image
    file_str += ("/**\n" +
                  " * @brief The number of bytes " + file_name + " occupies. \n" +
                  " * \n" +
                  " */\n")
    file_str += "#define " + file_name + "Len " + str(num_bytes) + "\n\n"

    file_str += ("/**\n" +
                 " * @brief The number of bytes in the compression stream for " + file_name + ". \n" +
                 " * \n" +
                 " */\n")
    file_str += "#define " + file_name + "CompressedLen " + str(compressed_bytes) + "\n\n"

    file_str += ("/**\n" +
                 " * @brief The byte stream to decompress " + file_name + " to tile data. \n" +
                 " * \n" +
                 " */\n")
    file_str += "extern const unsigned char "  + file_name + "Compression[" + str(compressed_bytes) + "];\n"

    # Do the declaration for palette if included
    if arguments["palette_included"]:
        file_str += ("\n/**\n" +
                     f" * @brief The number of bytes the Palette for {file_name} occupies. \n" +
                     " * \n" +
                     " */\n")
        file_str += "#define " + file_name + "PalLen " + str(len(gba_palette) * 2) + "\n"
        file_str += ("\n/**\n" +
                     f" * @brief The array of rgb5 (short) numbers that create {file_name}'s Palette. \n" +
                     " */\n")
        file_str += "extern const unsigned short " + file_name + "Pal[" + str(len(gba_palette)) + "];\n"

    new_file_name = f"{dest}/" if dest is not None else ""
    new_file_name += file_name + ".h"
    with open(new_file_name, "w") as file:
        file.write(file_str)

def create_compressed_c_file(arguments:dict, image:LoadedImage, gba_palette:list, byte_data:bytes) -> None:
    """
    Creates the C file for the tile output.
    :param arguments: Command line arguments
    :param image: The PIL image
    :param conversion_table: Dictionary of rgb24 colors to rgb15 colors (native GBA color)
    :param gba_palette: The 2^bpp wide palette for the image (palette that will be in the GBA)
    :param byte_data: The byte data
    """
    # Extract needed data
    bpp    = arguments["bpp"]

    dest = arguments["destination_path"]

    file_path = arguments["image_path"]

    # Make the Top Comments
    file_name = Path(file_path).stem

    # Data Size Calc
    num_chars = len(byte_data)

    file_str = "const unsigned char "+ file_name +"Compression["+ str(num_chars) +"] __attribute__((aligned(4))) __attribute__((visibility(\"hidden\")))=\n{\n"

    lc = 0
    for i in range(0, len(byte_data), 8):
        # Take a slice of 8 elements
        line = byte_data[i:i + 8]
        file_str += "\t" + ", ".join(f"0x{b:02X}" for b in line) + ",\n"
        lc += 1

        if lc % 8 == 0:
            file_str += "\n"  # blank line after every 8 lines

    file_str += "};\n"

    if arguments["palette_included"]:
        file_str += (f"\nconst unsigned short {file_name}Pal[{2**bpp}] "
                     f"__attribute__((aligned(2))) __attribute__((visibility(\"hidden\")))= \n{{\n")
        for i in range(0, len(gba_palette), 8):
            # Take a slice of 8 elements
            line = gba_palette[i:i + 8]
            line = (f"0x{n:04x}" for n in line)
            file_str += "\t" + (", ".join(line)) + ",\n"
        file_str = file_str[0:file_str.rfind(',')]

        file_str += "\n};\n"

    new_file_name = f"{dest}/" if dest is not None else ""
    new_file_name += file_name + ".c"
    with open(new_file_name, "w") as file:
        file.write(file_str)

def make_compress_output(arguments:dict, conversion_table:dict, gba_palette:list) -> None:
    """
    Makes the compressed output (.h and .c) of the tiles for the unit
    :param arguments: The options for outputting the unit
    :param conversion_table: The conversion table of rgb888 to rgb555
    :param gba_palette: The 2^bpp wide palette for the image (palette that will be in the GBA)
    :return: None
    """
    meta_w = arguments["meta_width"]
    meta_h = arguments["meta_height"]
    bpp = arguments["bpp"]
    file_path = arguments["image_path"]

    print(f" \t Compressing...")

    # Create the uncompressed data and make byte data

    if arguments["dedupe"]:
        raw_array = create_tile_data(file_path, conversion_table, meta_w, meta_h, bpp, True)
        raw_array, tile_mapping = dedupe_tiles(raw_array, bpp)
        raw_array = [int(s, 16) for s in raw_array]

    else:
        raw_array = create_tile_data(file_path, conversion_table, meta_w, meta_h, bpp, False)

    byte_array = struct.pack("<%dI" % len(raw_array), *raw_array)

    # Run compression algorithm
    compressed_bytes = gba_lz77_compress(byte_array)

    print(f" \t\t Compressed from {len(raw_array) * 4} bytes to {len(compressed_bytes)} bytes!")

    # Load in image
    img = PILImage.open(arguments["image_path"]).convert("RGB")

    # Create the header file
    create_compressed_header_file(arguments, img, len(compressed_bytes), gba_palette)

    # Create the C file
    create_compressed_c_file(arguments, img, gba_palette, compressed_bytes)