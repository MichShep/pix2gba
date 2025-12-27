import os, sys
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from PIL import Image as PILImage

from .config import discover_build_roots, build_units, validate_unit, convert_unit, find_unit, create_unit_args
from .visualizer import OutputWindow
from .converter import simulate_conversion
from .config import clean_unit
from .units import ConversionStats

ROOT_DIRECTORY = Path(os.getcwd())

def _output_conversion_stats(stats: ConversionStats) -> None:
    """
    Output the final stats (how many failed and which ones)
    :param stats: ConversionStats data struct with final conversion statistics
    :return: None
    """

    MAX_FAILED_UNITS = 5

    print("* Final Statistics... ")
    print(f" \tSuccess rate: {(stats.successful_conversions / stats.total_conversions)*100}% ({stats.successful_conversions}/{stats.total_conversions})")
    print(f" \tFailed Unit Conversions: ", end="")
    failed_names = ""
    for i in range(min(MAX_FAILED_UNITS, len(stats.failed_conversion_names))):
        failed_names += f"{stats.failed_conversion_names[i]}, "

    print(failed_names[:-2]) # Remove the last ", "
    if len(stats.failed_conversion_names) > MAX_FAILED_UNITS:
        print(", ect...")
    else:
        print()


def build_outputs():
    print(f"Converting all units in {ROOT_DIRECTORY}")

    # Fetch all toml files
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Build units from toml
    potential_units = build_units(build_paths)

    # Create statistics tracker
    stats = ConversionStats(
        total_conversions=len(potential_units),
        successful_conversions=0,
        failed_conversion_names =[]
    )

    # Process all units
    for unit in potential_units:
        # Validate unit
        if validate_unit(unit):
            # Add failed name to list
            stats.failed_conversion_names.append(unit.name)
            continue

        # Increment success stat
        stats.successful_conversions += 1

        # Send it to be converted
        convert_unit(unit)


    _output_conversion_stats(stats)

def clean_outputs():
    print(f"Cleaning all units in {ROOT_DIRECTORY}")
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    potential_units = build_units(build_paths)

    for unit in potential_units:
        clean_unit(unit)

def view_output(img_name:str):
    # Get all reachable toml files
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Find (and validate) the unit from all toml
    found_unit = find_unit(build_paths, img_name)
    validate_unit(found_unit)

    # Create Vizual Data
    tile_data, pal_data = simulate_conversion(create_unit_args(found_unit))
    img = PILImage.open(Path(found_unit.config.root_dir / found_unit.name).with_suffix(".png"))

    # Visualize!
    app = QtWidgets.QApplication()
    output_window = OutputWindow(tile_data, pal_data, found_unit.config.bpp, img.width, img.height, found_unit.metatile_width, found_unit.metatile_height)
    output_window.render()
    output_window.show()
    app.exec()

def make_template():
    pass