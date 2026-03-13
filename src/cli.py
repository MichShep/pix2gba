import argparse
from . import cli_log as log
from .api import build_outputs, clean_outputs, make_template, view_output, verify_inputs, create_byte_data

def print_help():
    """
    Prints the pix2gba command help.
    """
    print("""
pix2gba - Convert images into GBA tile data

Usage:
    pix2gba <command> [arguments]

Commands:
    make                Build all units found in the project
    clean               Remove all generated output files
    template            Create a default TOML template
    verify              Verify that all units can convert correctly
    view <unit name>    Preview how a unit will appear on the GBA
    byte <unit name>    Output raw byte data for a unit
    help                Show this help message

Examples:
    pix2gba make
    pix2gba clean
    pix2gba template
    pix2gba view sprite6
    pix2gba byte sprite7
""")

def main():
    """
    Main entry point for pix2gba and uses the CLI arguments to choose the action.
    """
    parser = argparse.ArgumentParser(description="Convert an Image (PNG, JPEG) to GBA-compatible tile data.")

    # Gather the first argument (starting command)
    parser.add_argument('command_name', type=str, help='Command of pix2gba to run')
    raw_args, raw_extra = parser.parse_known_args()

    if raw_args.command_name in ("help", "-h", "--help"):
        print_help()

    # 'make' is for running the conversing on all the toml units
    elif raw_args.command_name == 'make':
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
            log.error("`view` requires the name of the image file")
            parser.print_help()
            exit(1)

        # Make sure that only one unit is given
        if len(raw_extra) > 1:
            log.error("`view` takes only one unit name")
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
            log.error("`byte` requires the name of the image file")
            parser.print_help()
            exit(1)
        # Make sure only one unit is provided
        if len(raw_extra) > 1:
            log.error("`byte` takes only one unit name")
            parser.print_help()
            exit(1)

        create_byte_data(raw_extra[0])
    else:
        log.warn("No valid command given")
        print_help()



if __name__ == "__main__":
    main()
