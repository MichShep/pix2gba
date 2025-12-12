#!/usr/bin/env python3

import sys
import os

# Ensure imports work anywhere
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import cmnd_arg
import palette_maker
import output

def main():
    # Collect all Arguments
    input_png, input_palette, input_mw, input_mh, input_bpp, input_output, input_inclusion, input_destination, input_generate = cmnd_arg.get_args()

    # Create the target palette from input pal
    print("\t Making Palette...")
    gba_palette = palette_maker.extract_palette_img(input_palette, input_bpp) if input_palette is not None \
        else palette_maker.palette_from_img(input_png, input_bpp)

    # Create the conversion table from the colors in the img to the pal
    print("\t Making Converted Image...")
    conversion_table = palette_maker.create_conversion_table(input_png, gba_palette, input_bpp)

    # Go through the input_img and write the output
    print("\t Making Output...")
    output.make_output(input_png, input_palette, conversion_table, input_mw, input_mh, input_bpp, input_output, gba_palette, input_inclusion, input_destination)

    if input_generate:
        print("\t\t Generating Palette...")
        output.create_palette_png(input_png, gba_palette, input_destination, input_bpp)

    print("\t Done.")

if __name__ == '__main__':
    main()