import toml
import os

from .units import ConversionConfig, ConversionUnit
from pathlib import Path
from .converter import run_conversion, clean_conversion

ACCEPTED_OUTPUT_TYPES = [
    "both",
    "c",
    "h"
]

TOML_CONFIG_ARGUMENTS = [
    "bpp",
    "transparent",
    "output_type",
    "destination"
]

TOML_UNIT_ARGUMENTS = [
    "name",
    "metatile_width",
    "metatile_height",
    "palette",
    "palette_include",
    "generate_palette",
    "compress",
    "dedupe"
]

RED = "\033[31m"
RESET = "\033[0m"

def _print_red(message: str) -> None:
    """
    Prints the string to the terminal as red (usually for error messages).
    :param message: The string to be printed.
    :return: None
    """
    print(RED + message + RESET)


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

def _build_config(toml_data, root_dir:Path) -> ConversionConfig:
    """
    Builds a ConversionConfig object from parsed TOML data.
    :param toml_data: Parsed TOML configuration dictionary.
    :param root_dir: Root directory associated with the configuration.
    :return: A populated ConversionConfig instance.
    """

    missing_settings = []
    for setting in TOML_CONFIG_ARGUMENTS:
        if setting not in toml_data["general"]:
            missing_settings.append(setting)

    if missing_settings:
        _print_red(f"\t TOML in {root_dir} is missing arguments: `{'`, `'.join(missing_settings)}`")
        return None

    return ConversionConfig(
        bpp=toml_data["general"]["bpp"],

        transparent=toml_data["general"]["transparent"],

        output_type=toml_data["general"]["output_type"],

        root_dir=root_dir,
        output_dir=Path(toml_data["general"]["destination"]),
    )

def _build_unit(element_data, config:ConversionConfig) -> ConversionUnit:
    """
    Builds a ConversionUnit from a unit entry in the TOML configuration.
    :param element_data: Dictionary describing a single unit.
    :param config: Shared ConversionConfig for the unit.
    :return: A populated ConversionUnit instance.
    """
    missing_settings = []
    for setting in TOML_UNIT_ARGUMENTS:
        if setting not in element_data:
            missing_settings.append(setting)

    if missing_settings:
        _print_red(f"\t Unit in {config.root_dir} is missing arguments: `{'`, `'.join(missing_settings)}`")
        return None

    return ConversionUnit(
        config=config,
        name=element_data["name"],
        metatile_width=element_data["metatile_width"],
        metatile_height=element_data["metatile_height"],
        palette_path=element_data["palette"],
        palette_include=element_data["palette_include"],
        generate_palette=element_data["generate_palette"],
        compress=element_data["compress"],
        dedupe=element_data["dedupe"]
    )

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

def _validate_config(config: ConversionConfig) -> bool:
    """
    Validates a ConversionConfig for correctness and consistency.
    :param config: ConversionConfig instance to validate.
    :return: True if validation fails, False if validation succeeds.
    """
    if not os.path.exists(config.output_dir):
        _print_red(f" \t ERROR: Output directory does not exist:  `{config.output_dir}`")
        return True
    if not os.path.isdir(config.output_dir):
        _print_red(f" \t ERROR: Output directory is not a directory: `{config.output_dir}`")
        return True

    if not _is_power_of_two(config.bpp):
        _print_red(f" \t ERROR: Bpp is not power of two: {config.bpp}")
        return True

    if config.output_type not in ACCEPTED_OUTPUT_TYPES:
        _print_red(
            f" \t ERROR: Output type is not accepted (acceptable are `both`, `c`, `h`): `{config.output_type}`"
        )
        return True

    if config.transparent != "":
        if not _is_hex(config.transparent):
            _print_red(f" \t ERROR: Transparent RGB15 color is not hex: `{config.transparent}`")
            return True
        if int(config.transparent, 16) > 0x7FFF:
            _print_red(
                f" \t ERROR: Transparent RGB15 color is not a valid color (max value is 0x7FFF): `{config.transparent}`"
            )
            return True

    return False

def build_units(build_roots: list[Path]) -> list[ConversionUnit]:
    """
    Builds ConversionUnit objects from all discovered build roots.
    :param build_roots: List of directories containing pix2gba.toml files.
    :return: A list of ConversionUnit objects.
    """
    build_units: list[ConversionUnit] = []

    for build_root in build_roots:
        toml_file = build_root / "pix2gba.toml"
        toml_data = toml.load(toml_file)
        potential_units = len(toml_data["unit"])

        config = _build_config(toml_data, build_root)

        if config is None or _validate_config(config):
            _print_red(f"\t Config not valid, abandoning {potential_units} potential units")
            continue

        for element in toml_data["unit"]:
            unit = _build_unit(element, config)
            build_units.append(unit)

    return build_units

def validate_unit(unit: ConversionUnit) -> int:
    """
    Validates a ConversionUnit prior to conversion.
    :param unit: ConversionUnit to validate.
    :return: Integer error code (0 indicates success).
    """
    file_name = unit.name
    input_dir = unit.config.root_dir

    img_path = Path(unit.config.root_dir / unit.name).with_suffix(".png")
    if not img_path.exists():
        _print_red(f" \t ERROR: Input image `{img_path}` does not exist\n")
        return 1

    pal_path = Path(unit.config.root_dir / unit.palette_path).with_suffix(".png")
    if unit.palette_path != "":
        if not Path(unit.palette_path).exists():
            _print_red(f" \t ERROR: Palette path does not exist: `{unit.palette_path}`\n")
            return 2

    if unit.metatile_height < 1 or unit.metatile_width < 1:
        _print_red(
            f" \t ERROR: Meta tile height/width must be greater than or equal to 1: "
            f"mh=`{unit.metatile_height}`, mh=`{unit.metatile_width}`\n"
        )
        return 3

    return 0

def create_unit_args(unit: ConversionUnit) -> dict:
    """
    Creates the argument dictionary required for running a conversion.
    :param unit: ConversionUnit to convert.
    :return: Dictionary of conversion arguments.
    """
    input_path = Path(unit.config.root_dir / unit.name).with_suffix(".png")
    palette_path = Path(unit.palette_path)

    if unit.config.transparent != "":
        transparent_int = int(unit.config.transparent, 16)
    else:
        transparent_int = 0x5D53

    if unit.palette_path == "":
        palette_path = None

    args = {
        "image_path": input_path,
        "image_name": unit.name,

        "meta_width": unit.metatile_width,
        "meta_height": unit.metatile_height,
        "bpp": unit.config.bpp,
        "transparent": transparent_int,

        "palette_path": palette_path,

        "palette_included": unit.palette_include,
        "generate_palette": unit.generate_palette,
        "destination_path": unit.config.output_dir,
        "output_type": unit.config.output_type,
        "compress": unit.compress,
        "dedupe": unit.dedupe
    }

    return args

def convert_unit(unit: ConversionUnit):
    """
    Executes the conversion process for a single unit.
    :param unit: ConversionUnit to convert.
    :return: None
    """
    args = create_unit_args(unit)
    run_conversion(args)

def clean_unit(unit: ConversionUnit):
    """
    Cleans generated output files for a conversion unit.
    :param unit: ConversionUnit to clean.
    :return: None
    """
    input_path = Path(unit.config.root_dir / unit.name).with_suffix(".png")

    args = {
        "image_path": input_path,
        "image_name": unit.name,

        "meta_width": unit.metatile_width,
        "meta_height": unit.metatile_height,
        "bpp": unit.config.bpp,
        "transparent": 0,

        "palette_path": "",

        "palette_included": unit.palette_include,
        "generate_palette": unit.generate_palette,
        "destination_path": unit.config.output_dir,
        "output_type": unit.config.output_type,
    }

    clean_conversion(args)

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

        config = _build_config(toml_data, build_root)
        if _validate_config(config):
            exit(1)

        for element in toml_data["unit"]:
            if element["name"] == unit_name:
                return _build_unit(element, config)

    _print_red(f" \t ERROR: Unit does not exist: `{unit_name}`")
    exit(1)
