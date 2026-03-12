from pathlib import Path
from PIL import Image
import json
import hashlib

VERSION = "0.5.0"

from .units import ConversionUnit, ConversionConfig


def hash_dict(data):
    serialized_data = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized_data).hexdigest()


def hash_image_pixels(path):
    img = Image.open(path).convert("RGBA")
    h = hashlib.sha256()
    h.update(img.tobytes())
    h.update(str(img.size).encode())
    return h.hexdigest()


def _hash_unit_config(config: ConversionConfig):
    config_dict = {
        "bpp": config.bpp,
        "root": str(config.root_dir),
        "output": str(config.output_dir),
        "transparent": config.transparent,
        "type": config.output_type,
    }

    return hash_dict(config_dict)


def _hash_unit_dict(unit: ConversionUnit):
    unit_dict = {
        "metatile_width": unit.metatile_width,
        "metatile_height": unit.metatile_height,
        "palette": unit.palette_path,
        "palette_include": unit.palette_include,
        "generate_palette": unit.generate_palette,
        "compress": unit.compress,
        "dedupe": unit.dedupe,
    }

    return hash_dict(unit_dict)


def read_caches(potential_units: dict[Path, list[ConversionUnit]]):
    """
    Removes units from potential_units that do not need rebuilding.
    """

    for path in potential_units.keys():

        cache_path = path / "pix2gba_cache.json"

        if not cache_path.exists():
            continue

        with open(cache_path, "r") as f:
            cache_dict = json.load(f)

        if len(potential_units[path]) == 0:
            continue

        config_hash = _hash_unit_config(potential_units[path][0].config)

        # If config changed rebuild everything
        if cache_dict.get("configuration") != config_hash:
            continue

        rebuild_units = []

        for unit in potential_units[path]:

            unit_hash = _hash_unit_dict(unit)
            image_hash = hash_image_pixels(path / f"{unit.name}.png")

            old_hashes = cache_dict.get(unit.name)

            # Unit not cached then rebuild
            if old_hashes is None:
                rebuild_units.append(unit)
                continue

            if (
                old_hashes.get("unit") != unit_hash
                or old_hashes.get("image") != image_hash
                or old_hashes.get("version") != VERSION
            ):
                rebuild_units.append(unit)
            else:
                print(" \t Skip rebuilding unit " + unit.name)

        potential_units[path] = rebuild_units


def create_caches(unit_paths: dict[Path, list[ConversionUnit]], failed_units: list[ConversionUnit]):
    """
    Updates cache files after conversion.
    """
    for path in unit_paths:
        cache_file = path / "pix2gba_cache.json"

        # Load existing cache so valid units are preserved
        if cache_file.exists():
            with open(cache_file, "r") as file:
                cache_dict = json.load(file)
        else:
            cache_dict = {}

        if len(unit_paths[path]) == 0:
            continue

        config = unit_paths[path][0].config
        cache_dict["configuration"] = _hash_unit_config(config)

        for unit in unit_paths[path]:

            if unit in failed_units:
                continue

            unit_hash = _hash_unit_dict(unit)
            image_hash = hash_image_pixels(path / f"{unit.name}.png")

            cache_dict[unit.name] = {
                "unit": unit_hash,
                "image": image_hash,
                "version": VERSION,
            }

        with open(cache_file, "w") as file:
            json.dump(cache_dict, file, indent=4)