from email.policy import default

import toml
import os

from .units import ConversionUnit
from pathlib import Path
from . import cli_log as log

ACCEPTED_OUTPUT_TYPES = [
    "both",
    "c",
    "h"
]

TOML_ARGUMENTS = [
    "bpp",
    "transparent",
    "output_type",
    "destination",
    "name" ,
    "metatile_width",
    "metatile_height",
    "palette",
    "palette_include",
    "generate_palette",
    "compress",
    "dedupe",
    "cache"
]

def _print_error(message: str) -> None:
    """
    Prints the string to the terminal as red (usually for error messages).
    :param message: The string to be printed.
    :return: None
    """
    log.error(message)

def discover_build_roots(root: Path) -> list[Path]:
    """
    Recursively searches for directories containing a pix2gba.toml file.
    :param root: Root directory to begin the search from.
    :return: A list of directories that contain a pix2gba.toml file.
    """
    root = root.resolve()
    results: list[Path] = []

    toml_file = root / "pix2gba.toml"
    if toml_file.is_file():
        return [root]

    for entry in root.iterdir():
        if entry.is_dir():
            results.extend(discover_build_roots(entry))

    return results

def _is_power_of_two(n):
    """
    Determines whether a number is a power of two.
    :param n: Integer value to check.
    :return: True if n is a power of two, False otherwise.
    """
    return n > 0 and (n & (n - 1) == 0)

def _is_hex(s):
    """
    Checks whether a string represents a valid hexadecimal number.
    :param s: String to validate.
    :return: True if the string is valid hexadecimal, False otherwise.
    """
    try:
        int(s, 16)
        return True
    except Exception:
        return False

def validate_unit(unit: ConversionUnit, default=False) -> int:
    """
    Validates a ConversionUnit prior to conversion.
    :param unit: ConversionUnit to validate.
    :return: Integer error code (0 indicates success).
    """
    if not os.path.exists(unit.output_dir):
        _print_error(f"Output directory does not exist:  `{unit.output_dir}`")
        return 4
    if not os.path.isdir(unit.output_dir):
        _print_error(f"Output directory is not a directory: `{unit.output_dir}`")
        return 5

    if not _is_power_of_two(unit.bpp):
        _print_error(f"Bpp is not power of two: {unit.bpp}")
        return 6

    if unit.output_type not in ACCEPTED_OUTPUT_TYPES:
        _print_error(
            f"Output type is not accepted (acceptable are `both`, `c`, `h`): `{unit.output_type}`"
        )
        return 7

    if unit.transparent != "":
        if not _is_hex(unit.transparent):
            _print_error(f"Transparent RGB15 color is not hex: `{unit.transparent}`")
            return 8
        if int(unit.transparent, 16) > 0x7FFF:
            _print_error(
                f"Transparent RGB15 color is not a valid color (max value is 0x7FFF): `{unit.transparent}`"
            )
            return 9

    img_path = Path(unit.root_dir / unit.name).with_suffix(".png")
    if not img_path.exists() and not default:
        _print_error(f"Input image `{img_path}` does not exist")
        return 1

    if unit.palette_path != "":
        if not Path(unit.palette_path).exists():
            _print_error(f"Palette path does not exist: `{unit.palette_path}`")
            return 2

    if unit.metatile_height < 1 or unit.metatile_width < 1:
        _print_error(
            f"Meta tile height/width must be greater than or equal to 1: "
            f"mh=`{unit.metatile_height}`, mh=`{unit.metatile_width}`"
        )
        return 3

    return 0

def find_unit(build_roots: list[Path], unit_name:str) -> ConversionUnit:
    """
    Finds and returns a ConversionUnit by name.
    :param build_roots: List of directories containing pix2gba.toml files.
    :param unit_name: Name of the unit to locate.
    :return: Matching ConversionUnit instance.
    """
    for build_root in build_roots:
        toml_file = build_root / "pix2gba.toml"
        toml_data = toml.load(toml_file)

        default_unit = build_default(build_root, toml_data)

        for element in toml_data["unit"]:
            if element["name"] == unit_name:
                return convert_unit_dict(element, default_unit)

    _print_error(f"Unit does not exist: `{unit_name}`")
    exit(1)

def read_toml(build_root: Path):
    toml_path = build_root / "pix2gba.toml"

    if toml_path.exists():
        return toml.load(toml_path)

    return None

def build_default(root_dir:Path, data: dict) -> ConversionUnit:
    # Make sure it has a default key
    if data.get("default", None) is None:
        _print_error(f"    Default argument field is missing!")
        _print_error( "    Abandoning.")
        return None
    
    remaining_args = TOML_ARGUMENTS.copy()
    
    # Go through each field in default and make sure
    #   - No duplicate values
    #   - No foreign values
    #   - Default values are valid
    default_data = data["default"]
    for element in default_data:
        # Check if a registered argument
        if element not in TOML_ARGUMENTS:
            print(f"    Unknown default argument: {element}... Discarding.")
            continue
                    
        # Remove the used arg
        if element not in remaining_args:
            print(f"    Duplicate of argument: {element}... Ignoring.")

        remaining_args.remove(element)
        
    if len(remaining_args):
        _print_error(f"    Default arguments missing: {remaining_args}")
        _print_error( "    Abandoning.")
        return None

    default_unit = ConversionUnit(
        name=default_data["name"],
        bpp=default_data["bpp"],
        transparent=default_data["transparent"],
        output_type=default_data["output_type"],
        output_dir=default_data["destination"],
        metatile_width=default_data["metatile_width"],
        metatile_height=default_data["metatile_height"],
        palette_path=default_data["palette"],
        palette_include=default_data["palette_include"],
        generate_palette=default_data["generate_palette"],
        compress=default_data["compress"],
        dedupe=default_data["dedupe"],
        cache=default_data["cache"],
        root_dir=root_dir,
        image_path=Path("")
    )
    
    # Validate values
    if validate_unit(default_unit, True):
        return None

    if data.get("unit", None) is None:
        _print_error(f"    There are no fields under the name `unit`!")
        _print_error("    Abandoning.")
        return None

    return default_unit

def convert_unit_dict(data: dict, default: ConversionUnit) -> ConversionUnit:
    if data.get("name") is None:
        _print_error("    Unit name is missing (can't be defaulted)!")
        return None

    # Create from default if not provided
    new_unit = ConversionUnit(
        name=data.get("name"),
        bpp=data.get("bpp", default.bpp),
        transparent=data.get("transparent", default.transparent),
        output_type=data.get("output_type", default.output_type),
        output_dir=data.get("destination", default.output_dir),
        metatile_width=data.get("metatile_width", default.metatile_width),
        metatile_height=data.get("metatile_height", default.metatile_height),
        palette_path=data.get("palette", default.palette_path),
        palette_include=data.get("palette_include", default.palette_include),
        generate_palette=data.get("generate_palette", default.generate_palette),
        compress=data.get("compress", default.compress),
        dedupe=data.get("dedupe", default.dedupe),
        cache=data.get("cache", default.cache),
        root_dir=default.root_dir,
        image_path=(default.root_dir / data.get("name")).with_suffix(".png")
    )

    # Validate
    if validate_unit(new_unit, False):
        return None

    return new_unit