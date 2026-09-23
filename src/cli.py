import argparse
from . import cli_log as log
from .api import build_outputs, clean_outputs, make_template, view_output, verify_inputs, create_byte_data
from .cache import VERSION

def print_help() -> None:
    """
    Prints the pix2gba command help.
    """
    print(f"""
pix2gba v{VERSION} - Convert images into GBA tile data

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

Options:
    -h, --help          Show this help message
    -v, --version       Show the pix2gba version
    --verbose           Print every step instead of just warnings, errors, and the summary

Examples:
    pix2gba make
    pix2gba make --verbose
    pix2gba clean
    pix2gba template
    pix2gba view sprite6
    pix2gba byte sprite7
""")

def main() -> None:
    """
    Parses the command line and runs the matching pix2gba command.
    """
    parser = argparse.ArgumentParser(
        prog="pix2gba",
        description=f"pix2gba v{VERSION} - Convert an Image (PNG, JPEG) to GBA-compatible tile data."
    )
    parser.add_argument("-v", "--version", action="version", version=f"pix2gba {VERSION}")
    parser.add_argument("--verbose", action="store_true", help="Print every step instead of just the summary")

    # Lets --verbose also go after the command; SUPPRESS keeps it from overwriting the top-level value
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--verbose", action="store_true", default=argparse.SUPPRESS, help="Print every step instead of just the summary")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("make", parents=[common], help="Build all units found in the project")
    subparsers.add_parser("clean", parents=[common], help="Remove all generated output files")
    subparsers.add_parser("template", parents=[common], help="Create a default TOML template")
    subparsers.add_parser("verify", parents=[common], help="Verify that all units can convert correctly")

    view_parser = subparsers.add_parser("view", parents=[common], help="Preview how a unit will appear on the GBA")
    view_parser.add_argument("unit_name", type=str, help="Name of the unit to view")

    byte_parser = subparsers.add_parser("byte", parents=[common], help="Output raw byte data for a unit")
    byte_parser.add_argument("unit_name", type=str, help="Name of the unit to get byte data for")

    subparsers.add_parser("help", help="Show this help message")

    args = parser.parse_args()
    log.set_verbose(args.verbose)

    dispatch = {
        "make": lambda: build_outputs(),
        "clean": lambda: clean_outputs(),
        "template": lambda: make_template(),
        "verify": lambda: verify_inputs(),
        "view": lambda: view_output(args.unit_name),
        "byte": lambda: create_byte_data(args.unit_name),
        "help": lambda: print_help(),
    }

    dispatch[args.command]()


if __name__ == "__main__":
    main()
