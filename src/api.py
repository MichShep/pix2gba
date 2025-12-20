import os, sys
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from PIL import Image as PILImage

from .config import discover_build_roots, build_units, validate_unit, convert_unit, find_unit, create_unit_args
from .visualizer import OutputWindow
from .converter import simulate_conversion
from .config import clean_unit

ROOT_DIRECTORY = Path(os.getcwd())

def build_outputs():
    print(f"Converting all units in {ROOT_DIRECTORY}")

    # Fetch all toml files
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Build units from toml
    potential_units = build_units(build_paths)

    # Process all units
    for unit in potential_units:
        # Validate unit
        if validate_unit(unit):
            continue

        # Send it to be converted
        convert_unit(unit)

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