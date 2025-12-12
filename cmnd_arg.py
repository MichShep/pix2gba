import argparse
import os

def check_file(file):
    if os.path.exists(file):
        return True
    return False

def get_file_extension(file):
    _, ext = os.path.splitext(file)
    return ext.lower()

def get_args():
    parser = argparse.ArgumentParser(
        description="Convert a PNG image to GBA-compatible C code using a palette."
    )
    parser.add_argument("-i", "--input", required=True, help="Input PNG image")
    parser.add_argument("-mw", "--meta_width", required=True, type=int, help="Meta-tile width in tiles")
    parser.add_argument("-mh", "--meta_height", required=True, type=int, help="Meta-tile height in tiles")
    parser.add_argument("-bpp", "--bpp", required=True, type=int, help="Bits per pixel (4 or 8)")
    parser.add_argument("-o", "--output", required=True, choices=["both", "h", "c"],
                        help="Output type: h (header), c (c-code), or both")
    parser.add_argument("-p", "--palette", required=False, help="Input palette PNG, if none are provide will pull from image")
    parser.add_argument("-ip", "--include_palette", action="store_true", help="If the palette array should be inlcuded in the output")
    parser.add_argument("-gp", "--generate_palette", action="store_true", help="If the palette array should be inlcuded in the output")
    parser.add_argument("-d", "--destination", required=False, help="Where to save the output file(s), if blank will write in current folder")

    args = parser.parse_args()

    # Validate files
    if not check_file(args.input):
        print("Input PNG file not found")
        exit(1)

    if args.destination is not None and not os.path.isdir(args.destination):
        print("Destination folder not found")
        exit(1)

    if args.palette is not None:
        if not check_file(args.palette):
            print("Input palette file not found")
            exit(1)

        if get_file_extension(args.input) != ".png" or get_file_extension(args.palette) != ".png":
            print("Input files must be PNG")
            exit(1)

    # Validate integers
    if args.meta_width <= 0 or args.meta_height <= 0 or args.bpp <= 0:
        print("Meta dimensions and BPP must be positive")
        exit(1)

    # Validate BPP power of 2
    if not ((args.bpp & (args.bpp - 1)) == 0):
        print("BPP must be a power of 2")
        exit(1)

    return args.input, args.palette, args.meta_width, args.meta_height, args.bpp, args.output, args.include_palette, args.destination, args.generate_palette
