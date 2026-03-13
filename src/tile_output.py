import os
from PIL import Image as PILImage
from pathlib import Path
from .gba_utils import rgb15_to_rgb888
from .units import ConversionUnit, UnitOutput

# Type alias for a loaded PIL image
LoadedImage = PILImage.Image

OUTPUT_VAR_NAMES = {
    "tiles": "_TILES",
    "tile count": "_TILE_COUNT",
    "tile bytes": "_TILE_BYTES",
    "dedupe mapping": "_TILE_MAPPING",
    "palette length": "_PAL_LEN",
    "compression" : "_COMPRESSION",
    "compression length" : "_COMPRESSION_LEN",
    "palette": "_PAL"
}

def create_header_file(unit_data: ConversionUnit, output_data : UnitOutput) -> None:
    image = PILImage.open(unit_data.image_path)

    # Extract metatile and color depth configuration
    meta_w = unit_data.metatile_width
    meta_h = unit_data.metatile_height
    bpp = unit_data.bpp

    # Extract image dimensions
    img_w = image.width
    img_h = image.height

    # Output destination and input paths
    dest = unit_data.output_dir

    file_name = unit_data.name
    pal_name = Path(unit_data.palette_path).name

    # Calculate raw data sizes
    num_u32 = len(output_data.u32_data)

    # Calculate number of 8x8 tiles
    num_tiles = output_data.num_tiles
    num_bytes = len(output_data.u32_data) * 4

    # File header comments and include guard
    file_str = "// " + file_name
    if pal_name != "":
        file_str += f"; on palette {pal_name}"
    if unit_data.dedupe:
        file_str += "; Deduped"
    if unit_data.compress:
        file_str += "; Compressed"
    file_str += "\n"

    file_str += "#pragma once\n\n"

    num_tile_output = str(num_tiles) + f" -> {output_data.unique_tiles} (deduped)" if unit_data.dedupe else str(num_tiles)
    num_bytes_output = str(num_bytes) + f" -> {len(output_data.compress_data)} (compressed)" if unit_data.compress else str(
        num_bytes)

    # Detailed metadata block
    file_str += (
        "//======================================================================\n" +
                 "//	" + file_name + ", " + str(img_w) + "pxl by " + str(img_h) + "pxl @ " + str(bpp) + "bpp\n" +
                 "//\t+ Number of Tiles : " + str(num_tile_output) + "\n" +
                 "//\t+ Metatile Shape  : " + str(meta_w) + "w by " + str(meta_h) + "h\n" +
                 "//\t+ Dimensions in MT: " + str(img_w // (8 * meta_w)) + "w by " + str(img_h // (8 * meta_h)) + "h\n" +
                 "//\t+ Number of Bytes : " + num_bytes_output + "\n" +
                 "//\t+ Number of U32   : " + str(num_u32) + "\n" +
                 "//\t+ Blank Color     : " + hex(output_data.gba_palette[0]) + "\n" +
                 "//======================================================================\n\n"
                 )
    # Tile count macro
    file_str += ("/**\n" +
                 " * @brief The number of tiles to make " + file_name + ". \n" +
                 " * \n" +
                 " */\n")
    file_str += "#define " + file_name + OUTPUT_VAR_NAMES["tile count"] + " " + str( num_tiles) + "\n\n"

    # Tile data length macro
    file_str += ("/**\n" +
                 " * @brief The number of bytes " + file_name + " occupies. \n" +
                 " * \n" +
                 " */\n")
    file_str += "#define " + file_name + OUTPUT_VAR_NAMES["tile bytes"] + " " + str(num_bytes) + "\n\n"

    if unit_data.compress:
        num_bytes = len(output_data.compress_data)

        file_str += ("/**\n" +
                     " * @brief The number of bytes in the compression stream for " + file_name + ". \n" +
                     " * \n" +
                     " */\n")
        file_str += "#define " + file_name + OUTPUT_VAR_NAMES["compression length"] + " " + str(num_bytes) + "\n\n"

        file_str += ("/**\n" +
                     " * @brief The byte stream to decompress " + file_name + " to tile data. \n" +
                     " * \n" +
                     " */\n")
        file_str += "extern const unsigned char " + file_name + "" + OUTPUT_VAR_NAMES["compression"] + "[" + str(num_bytes) + "];\n"

    else:
        # External tile data declaration
        file_str += ("/**\n" +
                     " * @brief The array of Palette indices (4 packed into one uint) to create " +
                     file_name + " in Tiles. \n" +
                     " * \n" +
                     " */\n")
        file_str += "extern const unsigned int " + file_name + OUTPUT_VAR_NAMES["tiles"] + "[" + str(num_u32) + "];\n"

    if unit_data.dedupe:
        # External tile mapping data declaration
        file_str += ("\n/**\n" +
                     " * @brief The array of Tile indices to create " +
                     file_name + " from other Tiles after deduping. \n" +
                     " * \n" +
                     " */\n")
        file_str += "extern const unsigned short " + file_name + f"_TILE_MAPPING[{num_tiles}];\n"

    # Palette declarations if palette output is enabled
    if unit_data.palette_include:
        file_str += ("\n/**\n" +
                     f" * @brief The number of bytes the Palette for {file_name} occupies. \n" +
                     " * \n" +
                     " */\n")
        file_str += "#define " + file_name + "_PAL_LEN " + str(len(output_data.gba_palette) * 2) + "\n"

        file_str += ("\n/**\n" +
                     f" * @brief The array of rgb5 (short) numbers that create {file_name}'s Palette. \n" +
                     " */\n")
        file_str += "extern const unsigned short " + file_name + "_PAL[" + str(len(output_data.gba_palette)) + "];\n"

    # Write the header file to disk
    new_file_name = f"{dest}/" if dest is not None else ""
    new_file_name += file_name + ".h"
    with open(new_file_name, "w") as file:
        file.write(file_str)

def create_c_file(unit_data: ConversionUnit, output_data : UnitOutput) -> None:
    num_u32 = len(output_data.u32_data)

    # Begin C array definition with alignment attributes
    if unit_data.compress:
        # Data Size Calc
        num_chars = len(output_data.compress_data)

        file_str = "const unsigned char " + unit_data.name + OUTPUT_VAR_NAMES["compression"] + "[" + str(
            num_chars) + "] __attribute__((aligned(4))) __attribute__((visibility(\"hidden\")))=\n{\n"

        lc = 0
        for i in range(0, len(output_data.compress_data), 8):
            # Take a slice of 8 elements
            line = output_data.compress_data[i:i + 8]
            file_str += "\t" + ", ".join(f"0x{b:02X}" for b in line) + ",\n"
            lc += 1

            if lc % 8 == 0:
                file_str += "\n"  # blank line after every 8 lines

        file_str += "};\n"

    else:
        file_str = (
            "const unsigned int " + unit_data.name + OUTPUT_VAR_NAMES["tiles"] +"[" + str(num_u32) + "] "
            "__attribute__((aligned(4))) __attribute__((visibility(\"hidden\")))=\n{\n"
        )

        # Format output into readable blocks
        lc = 0
        for i in range(0, len(output_data.u32_data), 8):
            line = output_data.u32_data[i:i + 8]
            file_str += "\t" + (", ".join(line)) + ",\n"
            lc += 1

            # Insert blank line every 8 rows
            if lc % 8 == 0:
                file_str += "\n"

        file_str += "};\n"

    # If deduped add the tile_mapping table
    if unit_data.dedupe:
        file_str += (
            f"\nconst unsigned short {unit_data.name}"+ OUTPUT_VAR_NAMES["dedupe mapping"] + f"[{output_data.num_tiles}] = \n{{\n\t"
        )
        count = 0
        for index in output_data.tile_mapping:
            file_str += f"{index}, "
            count += 1
            if count % 8 == 0 and count != 0:
                file_str += "\n\t"
        file_str = file_str[:-2]
        file_str += "\n};\n"

    # Append palette data if included
    if unit_data.palette_include:
        file_str += (
            f"\nconst unsigned short {unit_data.name}" + OUTPUT_VAR_NAMES["palette"] + f"[{2**unit_data.bpp}] "
            "__attribute__((aligned(2))) __attribute__((visibility(\"hidden\")))= \n{\n"
        )

        for i in range(0, len(output_data.gba_palette), 8):
            line = output_data.gba_palette[i:i + 8]
            line = (f"0x{n:04x}" for n in line)
            file_str += "\t" + (", ".join(line)) + ",\n"

        # Remove trailing comma
        file_str = file_str[0:file_str.rfind(',')]
        file_str += "\n};\n"


    # Write the C file to disk
    new_file_name = f"{unit_data.output_dir}/" if unit_data.output_dir is not None else ""
    new_file_name += unit_data.name + ".c"
    with open(new_file_name, "w") as file:
        file.write(file_str)

def create_palette_png(unit: ConversionUnit, output_data : UnitOutput) -> None:
    # Determine the palette image dimensions (square)
    bpp = unit.bpp

    side_length = 2 ** (bpp // 2)
    pal_img = PILImage.new(mode="RGB", size=(side_length, side_length))

    # Pad palette to full size if needed
    gba_pal = output_data.gba_palette + [0x0] * (2 ** bpp - len(output_data.gba_palette))

    # Write palette colors into the image
    break_out = False
    for i in range(side_length):
        for j in range(side_length):
            if i * side_length + j >= len(gba_pal):
                break_out = True
                break
            pal_img.putpixel(
                (j, i),
                rgb15_to_rgb888(gba_pal[i * side_length + j])
            )
        if break_out:
            break

    # Save the palette PNG
    file_name = unit.name
    file_path = f"{unit.output_dir}/" if unit.output_dir is not None else ""
    file_path += file_name + "_palette.png"

    pal_img.save(file_path)

def make_output(unit_data: ConversionUnit, output_data : UnitOutput) -> None:
    # Determine which output files to generate
    output_type = unit_data.output_type

    # Generate C source file if requested
    if output_type == "both" or output_type == "c":
        create_c_file(unit_data, output_data)

    # Generate header file if requested
    if output_type == "both" or output_type == "h":
        create_header_file(unit_data, output_data)
        pass

    # Generate palette preview PNG if enabled
    if unit_data.generate_palette:
        create_palette_png(unit_data, output_data)