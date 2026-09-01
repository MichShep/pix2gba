import os
import re
from pathlib import Path

from PySide6 import QtWidgets
from PIL import Image as PILImage

from .config import discover_build_roots, find_unit
from .visualizer import OutputWindow
from .converter import run_conversion
from .config import build_default, read_toml, convert_unit_dict
from .units import ConversionStats, VerificationStats
from .template_output import add_template_file
from .cache import create_cache, needs_rebuild, get_cache_dict
from . import cli_log as log

ROOT_DIRECTORY = Path(os.getcwd())
MAX_FAILED_UNITS = 5

def _output_conversion_stats(stats: ConversionStats) -> None:
    """
    Output the final stats (how many failed and which ones)
    :param stats: ConversionStats data struct with final conversion statistics
    :return: None
    """

    log.summary("Conversion Summary...")
    log.indent()

    if stats.total_conversions != 0:
        log.summary(f"New Successful Conversion: {stats.successful_conversions}")
        log.summary(f"Cache hit Conversions: {stats.total_cached}")

        log.summary(f"Failed Conversion: {len(stats.failed_conversion_names)}")
        log.indent()
        for i in range(min(MAX_FAILED_UNITS, len(stats.failed_conversion_names))):
            log.warn(f"{stats.failed_conversion_names[i]}")
    else:
        log.summary("No successful conversions found.")

def build_outputs():
    """
    Handler for finding all units, converting them, and saving the output
    :return: None
    """
    log.info(f"Converting all units in {ROOT_DIRECTORY}")
    log.indent()

    # Fetch all toml files
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Create statistics tracker
    stats = ConversionStats(
        total_conversions=0,
        successful_conversions=0,
        failed_conversion_names =[],
        total_cached=0,
    )

    # Go through all paths and pull units
    # Declare successful units
    successful_units = []
    failed_units = []
    for build_path in build_paths:
        # Build pix2gba.toml file dict
        toml_data = read_toml(build_path)

        if toml_data is None:
            return

        log.info(f"Loading default", build_path.relative_to(ROOT_DIRECTORY))
        default_unit = build_default(build_path, toml_data)

        if default_unit is None:
            continue

        log.ok("Default verified.")
        log.indent()

        # Load in the cache
        cache_dict = get_cache_dict(build_path)
        local_success = []

        # Go through each unit path
        for unit_data in toml_data["unit"]:
            stats.total_conversions += 1
            name = unit_data["name"]

            log.info("Begin", name)
            log.indent()

            # Validate the unit (Paths/TOML/Values)
            log.info(f"Validating...")
            converted_unit = convert_unit_dict(unit_data, default_unit)
            if converted_unit is None:
                log.skip("Abandoning.")
                failed_units.append(unit_data["name"])
                log.dedent()
                continue
            log.ok(f"Validated.")

            # If the same cache then ignore
            if converted_unit.cache and not needs_rebuild(converted_unit, cache_dict, default_unit):
                stats.total_cached += 1
                log.dedent()
                continue

            # Start Conversion
            log.info(f"Converting...")
            run_conversion(converted_unit)
            log.ok(f"Converted.")

            successful_units += [converted_unit]
            local_success += [converted_unit]
            stats.successful_conversions += 1
            log.dedent()

        # Update Cache
        log.dedent()

        log.summary("Updating Cache...")
        create_cache(default_unit, local_success)
        log.ok("Cache Updated.")

        log.ok("Build Directory Finished\n", build_path.relative_to(ROOT_DIRECTORY))

    log.dedent()

    stats.successful_conversions = len(successful_units)
    stats.failed_conversion_names = failed_units.copy()

    _output_conversion_stats(stats)



def clean_outputs() -> None:
    log.summary(f"Cleaning all units in {ROOT_DIRECTORY}")
    log.indent()

    # Find all toml files
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Remove all cache files
    for path in build_paths:
        log.summary(f"Cleaning {path.relative_to(ROOT_DIRECTORY)}")
        log.indent()
        cache_path = path / "pix2gba_cache.json"

        toml_data = read_toml(path)

        if cache_path.exists():
            os.remove(cache_path)
            log.summary(f"Removed {cache_path.relative_to(ROOT_DIRECTORY)}")

        if toml_data.get("unit", None) is None:
            continue

        default_unit = build_default(path, toml_data)

        # Iterate through each unit and delete the files generated from it
        for unit_dict in toml_data["unit"]:
            if unit_dict.get("name", None) is None:
                continue

            converted_unit = convert_unit_dict(unit_dict, default_unit)
            if converted_unit is None:
                log.skip("Could not convert.", unit_dict["name"])
                continue

            name = converted_unit.name
            out_dir = Path(converted_unit.output_dir).absolute()

            paths = [
                out_dir / f"{name}.c",
                out_dir / f"{name}.h",
                out_dir / f"{name}_palette.png",
            ]

            for path in paths:
                if path.exists():
                    path.unlink()
                    log.info(f"Removed {path.relative_to(ROOT_DIRECTORY)}")
        log.dedent()


def view_output(img_name:str):
    """
    Handler for creating a window that shows what a unit will look like on a GBA
    :param img_name: Name of the unit to display
    :return: None
    """
    log.info(f"Viewing {img_name} in {ROOT_DIRECTORY}")
    # Get all reachable toml files
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Find (and validate) the unit from all toml
    found_unit = find_unit(build_paths, img_name)

    if found_unit is None:
        log.error("Problem making unit")
        return

    output = run_conversion(found_unit, True)
    img = PILImage.open(Path(found_unit.image_path))

    # Visualize!
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    output_window = OutputWindow(output.u32_data, output.gba_palette, found_unit.bpp, img.width, img.height, found_unit.metatile_width, found_unit.metatile_height)
    output_window.render()
    output_window.show()
    app.exec()

    log.summary("No longer viewing unit.")

def make_template() -> None:
    """
    Creates a template TOML in the project directory
    :return: None
    """
    log.summary(f"Created Template TOML file in {ROOT_DIRECTORY}")
    add_template_file(ROOT_DIRECTORY)

def _output_verification_stats(stats: VerificationStats) -> None:
    error_code = [
        "Null",
        "Image path does not exist",
        "Palette path does not exist",
        "Metatile width and height must be >= 1"
    ]

    log.summary("Final Statistics.")
    log.indent()
    if stats.total_units != 0:
        log.summary(f" \tVerified Units: {stats.successful_units}")
        log.summary(f" \tFailed Units: {len(stats.failed_unit_names)}")
        log.indent()
        for n in stats.failed_unit_names:
            log.warn(f"{n}")

def verify_inputs() -> None:
    """
    Handler for verifying all units in the TOML files can be converted successfully
    :return:
    """
    log.info(f"Verifying all units in {ROOT_DIRECTORY}")
    log.indent()

    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Create statistics tracker
    stats = VerificationStats(
        total_units=0,
        successful_units=0,
        failed_unit_names=[],
        unit_error_code=[]
    )

    for build_path in build_paths:
        # Build pix2gba.toml file dict
        toml_data = read_toml(build_path)

        if toml_data is None:
            return

        log.info(f"Verifying default...", build_path.relative_to(ROOT_DIRECTORY))
        default_unit = build_default(build_path, toml_data)

        if default_unit is None:
            continue

        log.ok("Default verified.")
        log.indent()

        # Go through each unit path
        for unit_data in toml_data["unit"]:
            log.indent()
            stats.total_units += 1
            name = unit_data["name"]

            # Ignore the cache for verifying
            log.info(f"Verifying unit...", name)
            converted_unit = convert_unit_dict(unit_data, default_unit)

            if converted_unit is None:
                stats.failed_unit_names.append(name)
                log.dedent()
                print()
                continue

            log.ok("Verified.")
            stats.successful_units += 1

            print()
            log.dedent()
        log.dedent()

    log.dedent()
    _output_verification_stats(stats)

def create_byte_data(img_name:str) -> None:
    log.info(f"Creating byte data of {img_name} in {ROOT_DIRECTORY}.")
    # Get all reachable toml files
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Find (and validate) the unit from all toml
    found_unit = find_unit(build_paths, img_name)

    if found_unit is None:
        log.error("Problem making unit.")
        return

    output = run_conversion(found_unit, True)

    # Convert to byte data
    log.info("Converting tile data to bytes.")
    words = re.findall(r'0x[0-9a-fA-F]{8}', str(output.u32_data))

    with open(f"{img_name}_bytes.bin", "wb") as f:
        for w in words:
            v = int(w, 16)
            f.write(v.to_bytes(4, "little"))

    log.ok("Done.")
