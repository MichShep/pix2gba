import os

from django.template.defaultfilters import upper

import gba_utils as gf
from PIL import Image as PILImage
from datetime import datetime
import tile_creator

LoadedImage = PILImage.Image

def get_filename_from_path(file_path:str) -> str:
    """
    Extracts the filename from a file path.
    :param file_path: The total path
    :return: The name of the file
    """
    file_name_with_extension = os.path.basename(file_path)
    file_name = os.path.splitext(file_name_with_extension)[0]

    return file_name

def create_header_file(arguments:dict, image:LoadedImage, conversion_table:dict, gba_palette:list) -> None:
    """
    Creates the header file for the tile output.
    :param arguments: Command line arguments
    :param image: The PIL image
    :param conversion_table: Dictionary of rgb24 colors to rgb15 colors (native GBA color)
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

    file_name = get_filename_from_path(file_path)
    pal_name = get_filename_from_path(pal_path if pal_path is not None else file_path)

    # Data Size Calc
    num_pxl = img_w * img_h
    num_bits =num_pxl * bpp
    num_bytes = num_bits // 8
    num_u32 = num_bytes // 4

    # Num Tiles Calc
    num_tiles = num_pxl // (8*8)

    # Comments and stuff
    file_str = "// " + file_name + " on " + pal_name + " Palette\n"
    file_str += "#pragma once\n\n"

    file_str += ("//======================================================================\n" +
                 "//	" + file_name + ", " + str(img_w) + "pxl by " + str(img_h) + "pxl @ " + str(bpp) + "bpp\n" +
                 "//\t+ Number of Tiles : " + str(num_tiles) + "\n" +
                 "//\t+ Metatile Shape  : " + str(meta_w) + "w by " + str(meta_h) + "h\n" +
                 "//\t+ Dimensions in MT: " + str(img_w//(8*meta_w)) + "w by " + str(img_h // (8*meta_h)) + "h\n" +
                 "//\t+ Number of Bytes : " + str(num_bytes) + "\n" +
                 "//\t+ Number of U32   : " + str(num_u32) + "\n" +
                 "//\t+ Blank Color     : " + hex(gba_palette[0]) + "\n" +
                 "//\t" + str(datetime.now()) + "\n" +
                 "//======================================================================\n\n"
                 )

    # Action externs and defines of the image
    file_str += ("/**\n" +
                 " * @brief The number of tiles to make " + file_name + ". \n" +
                 " * \n" +
                 " */\n")
    file_str += "#define " + file_name + "TileAmount " + str(num_tiles) + "\n\n"
    file_str += ("/**\n" +
                  " * @brief The number of bytes " + file_name + " occupies. \n" +
                  " * \n" +
                  " */\n")
    file_str += "#define " + file_name + "TilesLen " + str(num_bytes) + "\n\n"

    file_str += ("/**\n" +
                 " * @brief The array of Palette indices (4 packed into one uint) to create " + file_name + " in Tiles. \n" +
                 " * \n" +
                 " */\n")
    file_str += "extern const unsigned int "  + file_name + "Tiles[" + str(num_u32) + "];\n"

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

def create_c_file(arguments:dict, image:LoadedImage, conversion_table:dict, gba_palette:list) -> None:
    """
    Creates the C file for the tile output.
    :param arguments: Command line arguments
    :param image: The PIL image
    :param conversion_table: Dictionary of rgb24 colors to rgb15 colors (native GBA color)
    :param gba_palette: The 2^bpp wide palette for the image (palette that will be in the GBA)
    """
    # Extract needed data
    meta_w = arguments["meta_width"]
    meta_h = arguments["meta_height"]
    bpp    = arguments["bpp"]

    img_w = image.width
    img_h = image.height

    dest = arguments["destination_path"]

    file_path = arguments["image_path"]

    # Make the Top Comments
    final_array = tile_creator.create_tile_data(file_path, conversion_table, meta_w, meta_h, bpp)
    file_name = get_filename_from_path(file_path)

    # Data Size Calc
    num_pxl = img_w * img_h
    num_bits = num_pxl * bpp
    num_bytes = num_bits // 8
    num_u32 = num_bytes // 4

    file_str = "const unsigned int "+ file_name +"Tiles["+ str(num_u32) +"] __attribute__((aligned(4))) __attribute__((visibility(\"hidden\")))=\n{\n"

    lc = 0
    for i in range(0, len(final_array), 8):
        # Take a slice of 8 elements
        line = final_array[i:i + 8]
        file_str += "\t" + (", ".join(line)) + ",\n"
        lc += 1

        if lc % 8 == 0:
            file_str += "\n"  # blank line after every 8 lines

    file_str += "};\n"

    if arguments["palette_included"]:
        file_str += (f"\nconst unsigned short {file_name}Pal[{len(gba_palette)}] "
                     f"__attribute__((aligned(4))) __attribute__((visibility(\"hidden\")))= \n{{\n")
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

def create_palette_png(file_path:str, gba_pal:list, dest:str, bpp:int):
    """
    Creates a palette for the tile output as a PNG.
    :param file_path: Path of the source image
    :param gba_pal: The 2^bpp wide palette for the image (palette that will be in the GBA)
    :param dest: The destination path
    :param bpp: Bits per pixel
    """
    side_length = 2**(bpp//2)
    pal_img = PILImage.new(mode="RGB", size=(side_length, side_length))

    gba_pal = gba_pal + [0x0] * (2**bpp - len(gba_pal))

    break_out = False
    for i in range(side_length):
        for j in range(side_length):
            if i*side_length+j >= len(gba_pal):
                break_out = True
                break
            pal_img.putpixel((j, i), gf.rgb15_to_rgb888(gba_pal[i*side_length+j]))
        if break_out:
            break

    file_name = get_filename_from_path(file_path)
    file_path = f"{dest}/" if dest is not None else ""
    file_path += file_name + "_palette.png"

    pal_img.save(file_path)

def make_output(arguments:dict, conversion_table:dict, gba_palette:list) -> None:
    """
    Creates the output files that the user indicated as wanted
    :param arguments: Dictionary of command line arguments
    :param conversion_table: Dictionary of rgb24 colors to rgb15 colors (native GBA color)
    :param gba_palette: The 2^bpp wide palette for the image (palette that will be in the GBA)
    """
    img = PILImage.open(arguments["image_path"]).convert("RGB")

    output_type = arguments["output_type"]

    if output_type == "both" or output_type == "h":
        create_header_file(arguments, img, conversion_table, gba_palette)

    if output_type == "both" or output_type == "c":
        create_c_file(arguments, img, conversion_table, gba_palette)

    if arguments["generate_palette"]:
        print("* Creating Palette PNG Preview...")
        create_palette_png(
            gba_pal=gba_palette,
            dest=arguments["destination_path"],
            file_path=arguments["image_path"],
            bpp=arguments["bpp"]
    )