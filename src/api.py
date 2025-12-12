import os
from .config import discover_build_roots, build_units, validate_units, convert_unit
from pathlib import Path

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
        validate_units(unit)

        # Send it to be converted
        convert_unit(unit)

def clean_outputs():
    print(f"Cleaning all units in {ROOT_DIRECTORY}")
    build_paths = discover_build_roots(ROOT_DIRECTORY)

    potential_units = build_units(build_paths)

    for unit in potential_units:
        clean_unit(unit)

def make_template():
    pass