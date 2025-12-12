import argparse
from .api import build_outputs, clean_outputs, make_template

def main():
    """
    Main entry point for pix2gba.
    """
    # Gather all arguments
    parser = argparse.ArgumentParser(description="Convert an Image (PNG, JPEG) to GBA-compatible tile data.")

    parser.add_argument('command_name', type=str, help='Command of pix2gba to run')

    raw_args = parser.parse_args()

    if raw_args.command_name == 'build' or raw_args.command_name == 'make':
        build_outputs()

    elif raw_args.command_name == 'clean':
        clean_outputs()

    elif raw_args.command_name == 'template':
        make_template()

if __name__ == "__main__":
    main()
