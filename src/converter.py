# gba_converter/converter.py
import os

from .palette import extract_palette_img, palette_from_img, create_conversion_table
from .tile_output import make_output
from .tile_creator import create_tile_data
from .compress_output import make_compress_output

def run_conversion(args: dict) -> bool:
    """
    Main conversion workflow.

    :param args: Namespace from argparse.
    """
    file_name = args["image_name"]
    input_dir = os.path.dirname(args["image_path"])
    print(f"* Converting {file_name}... in {input_dir}")

    # Step 1: Create GBA palette
    #print("* Extracting Palette...")
    if args["palette_path"]:
        gba_palette = extract_palette_img(
            filename=args["palette_path"],
            bpp=args["bpp"],
            transparent=args["transparent"]
        )
        if gba_palette is None:
            return True
    else:
        gba_palette = palette_from_img(
            filename=args["image_path"],
            bpp=args["bpp"],
            transparent=args["transparent"]
        )

    # Step 2: Create conversion table
    #print("* Creating Color Conversion Table...")
    conversion_table = create_conversion_table(
        input_img=args["image_path"],
        gba_palette=gba_palette,
    )

    # Step 3: Generate .h and/or .c output
    #print("* Generating C/Header Output...")
    if args["compress"]:
        make_compress_output(
            arguments=args,
            conversion_table=conversion_table,
            gba_palette=gba_palette
        )
    else:
        make_output(
            arguments=args,
            conversion_table=conversion_table,
            gba_palette=gba_palette
        )

    print("* Done.\n")

    return False


def clean_conversion(args: dict) -> None:
    output_path = args["destination_path"]
    image_name = args["image_name"]

    # Clear h files
    if os.path.exists(f"{output_path}/{image_name}.h"):
        os.remove(f"{output_path}/{image_name}.h")

    # Clear c files
    if os.path.exists(f"{output_path}/{image_name}.c"):
        os.remove(f"{output_path}/{image_name}.c")

    # Clear palette files
    if os.path.exists(f"{output_path}/{image_name}_palette.png"):
        os.remove(f"{output_path}/{image_name}_palette.png")

def simulate_conversion(args: dict) -> tuple[list, list]:
    # Step 1: Create GBA palette
    if args["palette_path"]:
        gba_palette = extract_palette_img(
            filename=args["palette_path"],
            bpp=args["bpp"],
            transparent=args["transparent"]
        )
        if gba_palette is None:
            exit(1)
    else:
        gba_palette = palette_from_img(
            filename=args["image_path"],
            bpp=args["bpp"],
            transparent=args["transparent"]
        )

    # Step 2: Create conversion table
    conversion_table = create_conversion_table(
        input_img=args["image_path"],
        gba_palette=gba_palette,
    )

    # Step 3: Generate tile data
    meta_w = args["meta_width"]
    meta_h = args["meta_height"]
    bpp = args["bpp"]

    file_path = args["image_path"]

    final_array = create_tile_data(file_path, conversion_table, meta_w, meta_h, bpp)

    # Step 4: Return the tile data and the palette data
    return final_array, gba_palette
