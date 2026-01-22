import os, sys
import re
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from PIL import Image as PILImage

from .config import discover_build_roots, build_units, validate_unit, convert_unit, find_unit, create_unit_args
from .visualizer import OutputWindow
from .converter import simulate_conversion
from .config import clean_unit
from .units import ConversionStats, VerificationStats
from .template_output import add_template_file

ROOT_DIRECTORY = Path(os.getcwd())

def _output_conversion_stats(stats: ConversionStats) -> None:
    """
    Output the final stats (how many failed and which ones)
    :param stats: ConversionStats data struct with final conversion statistics
    :return: None
    """

    MAX_FAILED_UNITS = 5

    print("* Final Statistics... ")
    if stats.total_conversions != 0:
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
    else:
        print(" \tNo conversion units were found! Use `pix2gba template` to create a valid TOML file and place in "
              "directory with units")


def build_outputs():
    """
    Handler for finding all units, converting them, and saving the output
    :return: None
    """
    print(f"* Converting all units in {ROOT_DIRECTORY}")

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
        print (f"* \t Starting {unit.name}...")
        # Validate unit
        print (f" \t Validating...")
        if validate_unit(unit):
            # Add failed name to list
            stats.failed_conversion_names.append(unit.name)
            continue

        # Increment success stat
        stats.successful_conversions += 1

        # Send it to be converted
        print(f" \t Converting...")
        convert_unit(unit)

        print(f" \t Done.\n")

    print()
    _output_conversion_stats(stats)

def clean_outputs():
    """
    Handler for removing all generated outputs
    :return: None
    """
    print(f"* Cleaning all units in {ROOT_DIRECTORY}")

    # Find all toml files
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Find all units
    potential_units = build_units(build_paths)

    # Iterate through each unit and delete the files generated from it
    for unit in potential_units:
        clean_unit(unit)

def view_output(img_name:str):
    """
    Handler for creating a window that shows what a unit will look like on a GBA
    :param img_name: Name of the unit to display
    :return: None
    """
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
    """
    Creates a template TOML in the project directory
    :return: None
    """
    print(f"* Created Template TOML file in {ROOT_DIRECTORY}")
    add_template_file(ROOT_DIRECTORY)

def _output_verification_stats(stats: VerificationStats) -> None:
    """
    Output the final stats (how many failed and which ones)
    :param stats: The statistic structure
    :return: None
    """
    error_code = [
        "Null",
        "Image path does not exist",
        "Palette path does not exist",
        "Metatile width and height must be >= 1"
    ]
    """
    Output the final stats of the verification process (how many failed and which ones)
    :param stats: ConversionStats data struct with final verification statistics
    :return: None
    """
    print("* Final Statistics... ")
    if stats.total_units != 0:
        print(f" \tSuccess rate: {(stats.successful_units / stats.total_units)*100}% ({stats.successful_units}/{stats.total_units})")
        print(f" \tFailed Verification: ")
        failed_names = ""
        for i in range(len(stats.failed_unit_names)):
            failed_names += f" \t\t{stats.failed_unit_names[i]} : {error_code[stats.unit_error_code[i]]}, "

        print(failed_names[:-2]) # Remove the last ", "
    else:
        print(" \tNo conversion units were found! Use `pix2gba template` to create a valid TOML file and place in "
              "directory with units")

def verify_inputs():
    """
    Handler for verifying all units in the TOML files can be converted successfully
    :return:
    """
    print(f"* Verifying all units in {ROOT_DIRECTORY}")

    # Fetch all toml files
    print("*\t Verifying default configs...")
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Build units from toml
    potential_units = build_units(build_paths)
    print()

    # Create statistics tracker
    stats = VerificationStats(
        total_units=len(potential_units),
        successful_units=0,
        failed_unit_names=[],
        unit_error_code=[]
    )

    # Process all units
    for unit in potential_units:
        if unit is None:
            continue

        # Validate unit
        print (f"* \t Verifying {unit.name}...")
        error_code = validate_unit(unit)
        if error_code:
            # Add failed name to list
            stats.failed_unit_names.append(unit.name)
            stats.unit_error_code.append(error_code)
            continue
        else:
            print(f" \t Done.")

        stats.successful_units += 1

        print()

    _output_verification_stats(stats)

def create_byte_data(img_name:str):
    """
    Handler for creating the raw byte data of the unit
    :param img_name: Name of the unit to create
    :return: None
    """
    # Get all reachable toml files
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    # Find (and validate) the unit from all toml
    found_unit = find_unit(build_paths, img_name)
    validate_unit(found_unit)

    # Create Vizual Data
    tile_data, pal_data = simulate_conversion(create_unit_args(found_unit))

    # Convert to byte data
    print("* Converting tile data to bytes")
    words = re.findall(r'0x[0-9a-fA-F]{8}', str(tile_data))

    with open(f"{img_name}_bytes.bin", "wb") as f:
        for w in words:
            v = int(w, 16)
            f.write(v.to_bytes(4, "little"))

    print("* Done")
