import argparse
from cgi import parse

from .api import build_outputs, clean_outputs, make_template, view_output, verify_inputs, create_byte_data

def main():
    """
    Main entry point for pix2gba and uses the CLI arguments to choose the action.
    """
    parser = argparse.ArgumentParser(description="Convert an Image (PNG, JPEG) to GBA-compatible tile data.")

    # Gather the first argument (starting command)
    parser.add_argument('command_name', type=str, help='Command of pix2gba to run')
    raw_args, raw_extra = parser.parse_known_args()

    # 'make' is for running the conversing on all the toml units
    if raw_args.command_name == 'make':
        build_outputs()

    # 'clean' removes all the generated units
    elif raw_args.command_name == 'clean':
        clean_outputs()

    # 'template' creates a template toml in the project root
    elif raw_args.command_name == 'template':
        make_template()

    # 'view' creates a window that shows what the unit will look like on the GBA
    elif raw_args.command_name == 'view':
        parser.add_argument('image_name', type=str, help='Name of the image to view')

        # Make sure that the unit name is passed in
        if len(raw_extra) == 0:
            print("ERROR: `view` requires the name of the image file")
            parser.print_help()
            exit(1)

        # Make sure that only one unit is given
        if len(raw_extra) > 1:
            print("ERROR: `view` takes only one unit name")
            parser.print_help()
            exit(1)

        view_output(raw_extra[0])

    # 'verify' checks that all units can be converted and outputs the errors
    elif raw_args.command_name == 'verify':
        verify_inputs()

    # 'byte' outputs the raw byte data of the given unit
    elif raw_args.command_name == 'byte':
        parser.add_argument('image_name', type=str, help='Name of the image to get the byte data')

        # Make sure that a unit is provided
        if len(raw_extra) == 0:
            print("ERROR: `byte` requires the name of the image file")
            parser.print_help()
            exit(1)
        # Make sure only one unit is provided
        if len(raw_extra) > 1:
            print("ERROR: `byte` takes only one unit name")
            parser.print_help()
            exit(1)

        create_byte_data(raw_extra[0])



if __name__ == "__main__":
    main()
