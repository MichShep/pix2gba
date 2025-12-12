import toml
import os
from .units import ConversionConfig, ConversionUnit
from pathlib import Path
from .converter import run_conversion, clean_conversion

ACCEPTED_OUTPUT_TYPES = {
    "both",
    "c",
    "h"
}

def discover_build_roots(root: Path) -> list[Path]:
    root = root.resolve()
    results: list[Path] = []

    toml_file = root / "pix2gba.toml"
    if toml_file.is_file():
        return [root]

    for entry in root.iterdir():
        if entry.is_dir():
            results.extend(discover_build_roots(entry))

    return results

def _build_config(toml_data, root_dir:Path):
    return ConversionConfig(
        bpp=toml_data["graphics"]["bpp"],

        transparent=toml_data["graphics"]["transparent"],

        output_type=toml_data["graphics"]["output_type"],

        root_dir=root_dir,
        output_dir=Path(toml_data["graphics"]["destination"]),

        generate_palette=toml_data["graphics"]["generate_palettes"],
    )

def _build_unit(element_data, config:ConversionConfig):
    return ConversionUnit(
        config=config,
        name=element_data["name"],
        metatile_width=element_data["metatile_width"],
        metatile_height=element_data["metatile_height"],
        palette_path=element_data["palette"],
        palette_include=element_data["palette_include"],
    )

def _is_power_of_two(n):
  return n > 0 and (n & (n - 1) == 0)

def _is_hex(s):
    try:
        int(s, 16)
        return True
    except Exception:
        return False

def _validate_config(config: ConversionConfig):
    if not os.path.exists(config.output_dir):
        print(f"ERROR: Output directory does not exist:  `{config.output_dir}`")
        exit(1)
    if not os.path.isdir(config.output_dir):
        print(f"ERROR: Output directory is not a directory: `{config.output_dir}`")
        exit(1)

    if not _is_power_of_two(config.bpp):
        print(f"ERROR: Bpp is not power of two: {config.bpp}")
        exit(1)

    # Output Type checking
    if config.output_type not in ACCEPTED_OUTPUT_TYPES:
        print(f"ERROR: Output type is not accepted (acceptable are `both`, `c`, `h`): `{config.output_type}`")
        exit(1)

    # Color Checking
    if config.transparent != "": #If provided
        if not _is_hex(config.transparent): # Check if it can be turned into hex
            print(f"ERROR: Transparent RGB15 color is not hex: `{config.transparent}`")
            exit(1)
        if int(config.transparent, 16) > 0x7FFF:
            print(f"ERROR: Transparent RGB15 color is not a valid color (max value is 0x7FFF): `{config.transparent}`")
            exit(1)

def build_units(build_roots: list[Path]) -> list[ConversionUnit]:
    build_units: list[ConversionUnit] = []

    # Go through each root and load in config
    for build_root in build_roots:
        # Load in toml data
        toml_file = build_root / "pix2gba.toml"
        toml_data = toml.load(toml_file)

        # Create and validate the config
        config = _build_config(toml_data, build_root)
        _validate_config(config)

        # Go through each element in toml and build the unit
        for element in toml_data["unit"]:
            unit = _build_unit(element, config)
            build_units.append(unit)

    return build_units

def validate_units(unit: ConversionUnit):
    # File checking
    img_path = Path(unit.config.root_dir / unit.name).with_suffix(".png")
    if not img_path.exists():
        print(f"ERROR: Input image `{img_path}` does not exist")
        exit(1)

    pal_path = Path(unit.config.root_dir / unit.palette_path).with_suffix(".png")
    if unit.palette_path != "":  # Only check palette if one was provided
        if not pal_path.exists():
            print(f"ERROR: Palette path does not exist: `{unit.palette_path}`")
            exit(1)

    # Number checking
    if unit.metatile_height < 1 or unit.metatile_width < 1:
        print(f"ERROR: Meta tile height/width must be greater than or equal to 1: "
              f"mh=`{unit.metatile_height}`, mh=`{unit.metatile_width}`")
        exit(1)

def convert_unit(unit: ConversionUnit):
    input_path = Path(unit.config.root_dir / unit.name).with_suffix(".png")
    palette_path = Path(unit.config.root_dir / unit.palette_path).with_suffix(".png")

    if unit.config.transparent != "": #already been verified
        transparent_int = int(unit.config.transparent, 16)
    else:
        transparent_int = 0x5D53

    if unit.palette_path == "":
        palette_path = None

    args = {
        # Base img
        "image_path": input_path,
        "image_name": unit.name,

        # GBA specs
        "meta_width": unit.metatile_width,
        "meta_height": unit.metatile_height,
        "bpp": unit.config.bpp,
        "transparent": transparent_int,

        # Palette input
        "palette_path": palette_path,

        # Output
        "palette_included": unit.palette_include,
        "generate_palette": unit.config.generate_palette,
        "destination_path": unit.config.output_dir,
        "output_type": unit.config.output_type,
    }

    run_conversion(args)

def clean_unit(unit: ConversionUnit):
    input_path = Path(unit.config.root_dir / unit.name).with_suffix(".png")

    args = {
        # Base img
        "image_path": input_path,
        "image_name": unit.name,

        # GBA specs
        "meta_width": unit.metatile_width,
        "meta_height": unit.metatile_height,
        "bpp": unit.config.bpp,
        "transparent": 0,

        # Palette input
        "palette_path": "",

        # Output
        "palette_included": unit.palette_include,
        "generate_palette": unit.config.generate_palette,
        "destination_path": unit.config.output_dir,
        "output_type": unit.config.output_type,
    }

    clean_conversion(args)