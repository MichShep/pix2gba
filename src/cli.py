import argparse
from cgi import parse

from .api import build_outputs, clean_outputs, make_template, view_output

def main():
    """
    Main entry point for pix2gba.
    """
    # Gather all arguments
    parser = argparse.ArgumentParser(description="Convert an Image (PNG, JPEG) to GBA-compatible tile data.")

    parser.add_argument('command_name', type=str, help='Command of pix2gba to run')

    raw_args, raw_extra = parser.parse_known_args()
    if raw_args.command_name == 'build' or raw_args.command_name == 'make':
        build_outputs()

    elif raw_args.command_name == 'clean':
        clean_outputs()

    elif raw_args.command_name == 'template':
        make_template()

    elif raw_args.command_name == 'view':
        parser.add_argument('image_name', type=str, help='Name of the image to view')

        if len(raw_extra) == 0:
            print("ERROR: `view` requires the name of the image file")
            parser.print_help()
            exit(1)

        view_output(raw_extra[0])

if __name__ == "__main__":
    main()
