# gba_converter/converter.py

import palette
import tile_output

def run_conversion(args: dict) -> None:
    """
    Main conversion workflow.

    :param args: Namespace from argparse.
    """
    print("=== GBA Image Converter ===")

    # Step 1: Create GBA palette
    print("* Extracting Palette...")
    if args["palette_path"]:
        gba_palette = palette.extract_palette_img(
            filename=args["palette_path"],
            bpp=args["bpp"]
        )
    else:
        gba_palette = palette.palette_from_img(
            filename=args["image_path"],
            bpp=args["bpp"]
        )

    # Step 2: Create conversion table
    print("* Creating Color Conversion Table...")
    conversion_table = palette.create_conversion_table(
        input_img=args["image_path"],
        gba_palette=gba_palette,
    )

    # Step 3: Generate .h and/or .c output
    print("* Generating C/Header Output...")
    tile_output.make_output(
        arguments=args,
        conversion_table=conversion_table,
        gba_palette=gba_palette
    )


    print("* Done.")
