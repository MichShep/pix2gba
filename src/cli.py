import argparse
import os.path

from django.db.models.expressions import NoneType

from converter import run_conversion

ACCEPTED_TYPES = [
    ".png",
    ".jpg",
    ".jpeg"
]

ACCEPTED_OUTPUT_TYPES = {
    "both",
    "c",
    "h"
}

def is_power_of_two(n):
  return n > 0 and (n & (n - 1) == 0)

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def main():
    """
    Main entry point for pix2gba.
    """
    # Gather all arguments
    parser = argparse.ArgumentParser(description="Convert an Image (PNG, JPEG) to GBA-compatible tile data.")
    parser.add_argument("-i", "--input", required=True,
                        help="Input Image file to be converted")
    parser.add_argument("-mw", "--meta_width", required=True, type=int,
                        help="Number of 8x8pxl tile to fill 1 meta tile width")
    parser.add_argument("-mh", "--meta_height", required=True, type=int,
                        help="Number of 8x8pxl tile to fill 1 meta tile height")
    parser.add_argument("-bpp", "--bpp", required=True, type=int,
                        help="The number of bits each pixel has to index into a palette")
    parser.add_argument("-o", "--output", required=True, choices=["both", "h", "c"],
                        help="Specify the output format (Header:h, C:c, Both:b")
    parser.add_argument("-p", "--palette", required=False,
                        help="Specify the palette to use; if blank will pull it from source image")
    parser.add_argument("-ip", "--include_palette", required=False, action="store_true",
                        help="Include the palette in the output")
    parser.add_argument("-gp", "--generate_palette", required=False, action="store_true",
                        help="Generate a PNG of the palette used for the input image")
    parser.add_argument("-d", "--destination", required=False,
                        help="Specify the destination directory to create output in")
    parser.add_argument("-t", "--transparent", required=False, type=str,
                        help="Specify the transparent RGB15 color to use; if blank will default to 0x5D53")

    raw_args = parser.parse_args()

    # File checking
    if not os.path.exists(raw_args.input):
        print("ERROR: Input image does not exist")
        exit(1)
    if not os.path.isfile(raw_args.input):
        print("ERROR: Input image is not a file")
        exit(1)
    if  os.path.splitext(raw_args.input)[1] not in ACCEPTED_TYPES:
        print("ERROR: Input image type is not accepted")
        exit(1)

    if not os.path.exists(raw_args.destination):
        print("ERROR: Output directory does not exist")
        exit(1)
    if not os.path.isdir(raw_args.destination):
        print("ERROR: Output directory is not a directory")
        exit(1)

    if raw_args.palette is not None: # Only check palette if one was provided
        if not os.path.isfile(raw_args.palette):
            print("ERROR: Palette is not a file")
            exit(1)
        if os.path.splitext(raw_args.palette)[1] not in ACCEPTED_TYPES:
            print("ERROR: Palette type is not accepted")
            exit(1)

    # Number checking
    if raw_args.meta_height < 1 or raw_args.meta_width < 1:
        print("ERROR: Meta tile height/width must be greater than or equal to 1")
        exit(1)
    if not is_power_of_two(raw_args.bpp):
        print(f"ERROR: Bpp is not power of two (was given {raw_args.bpp})")
        exit(1)

    # Output Type checking
    if raw_args.output not in ACCEPTED_OUTPUT_TYPES:
        print("ERROR: Output type is not accepted (acceptable are `both`, `c`, `h`)")
        exit(1)

    # Color Checking
    if raw_args.transparent is not None: #If provided
        if not is_hex(raw_args.transparent): # Check if it can be turned into hex
            print("ERROR: Transparent RGB15 color is not hex")
            exit(1)
        if int(raw_args.transparent, 16) > 0x7FFF:
            print("ERROR: Transparent RGB15 color is not a valid color (max value is 0x7FFF)")
            exit(1)
        raw_args.transparent = int(raw_args.transparent, 16)
    else: # If not provided then set to default
        raw_args.transparent = 0x5D53

    args = {
        # Base img
        "image_path" : raw_args.input,

        # GBA specs
        "meta_width" : raw_args.meta_width,
        "meta_height" : raw_args.meta_height,
        "bpp" : raw_args.bpp,
        "transparent" : raw_args.transparent,

        # Palette input
        "palette_path" : raw_args.palette,

        # Output
        "palette_included" : raw_args.include_palette,
        "generate_palette" : raw_args.generate_palette,
        "destination_path" : raw_args.destination,
        "output_type" : raw_args.output,
    }

    run_conversion(args)

if __name__ == "__main__":
    main()
