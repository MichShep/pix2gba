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
    parser = argparse.ArgumentParser(
        prog="pix2gba",
        description="Convert an Image (PNG, JPEG) to GBA-compatible tile data."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("make", help="Build all units found in the project")
    subparsers.add_parser("clean", help="Remove all generated output files")
    subparsers.add_parser("template", help="Create a default TOML template")
    subparsers.add_parser("verify", help="Verify that all units can convert correctly")

    view_parser = subparsers.add_parser("view", help="Preview how a unit will appear on the GBA")
    view_parser.add_argument("unit_name", type=str, help="Name of the unit to view")

    byte_parser = subparsers.add_parser("byte", help="Output raw byte data for a unit")
    byte_parser.add_argument("unit_name", type=str, help="Name of the unit to get byte data for")

    args = parser.parse_args()

    dispatch = {
        "make": lambda: build_outputs(),
        "clean": lambda: clean_outputs(),
        "template": lambda: make_template(),
        "verify": lambda: verify_inputs(),
        "view": lambda: view_output(args.unit_name),
        "byte": lambda: create_byte_data(args.unit_name),
    }

    dispatch[args.command]()


if __name__ == "__main__":
    main()
