from pathlib import Path
from PIL import Image
import json
import hashlib
from . import cli_log as log

VERSION = "0.6.0"

from .units import ConversionUnit


def hash_dict(data):
    serialized_data = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized_data).hexdigest()


def hash_image_pixels(path):
    img = Image.open(path).convert("RGBA")
    h = hashlib.sha256()
    h.update(img.tobytes())
    h.update(str(img.size).encode())
    return h.hexdigest()


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

def get_cache_dict(build_path: Path)-> dict:
    cache_path = build_path / "pix2gba_cache.json"

    if not cache_path.exists():
        return {}

    with open(cache_path, "r") as f:
        return json.load(f)

def needs_rebuild(path: Path, unit: ConversionUnit, cache_dict: dict) -> bool:
    """
    Returns True if the unit needs rebuilding, False otherwise.
    Assumes cache_dict was already read from pix2gba_cache.json.
    """

    unit_hash = _hash_unit_dict(unit)

    old_hashes = cache_dict.get(unit.name)

    # Unit not cached → rebuild
    if old_hashes is None:
        return True

    # Only compute image hash if needed
    image_hash = hash_image_pixels(path / f"{unit.name}.png")

    if (
        old_hashes.get("unit", "") != unit_hash
        or old_hashes.get("image", "") != image_hash
        or old_hashes.get("version", "") != VERSION
    ):
        return True

    log.cache("no changes compared to cache")
    return False


def create_cache(default_unit: ConversionUnit, passed_units: list[ConversionUnit]):
    """
    Updates cache files after conversion.
    """
    cache_file = default_unit.root_dir / "pix2gba_cache.json"

    # Load existing cache so valid units are preserved
    if cache_file.exists():
        with open(cache_file, "r") as file:
            cache_dict = json.load(file)
    else:
        cache_dict = {}

    if len(passed_units) == 0:
        return

    # Create default hash
    default_hash = _hash_unit_dict(default_unit)

    cache_dict["default"] = default_hash

    for unit in passed_units:
        unit_hash = _hash_unit_dict(unit)
        image_hash = hash_image_pixels(unit.image_path)

        cache_dict[unit.name] = {
            "unit": unit_hash,
            "image": image_hash,
            "version": VERSION,
        }

    with open(cache_file, "w") as file:
        json.dump(cache_dict, file, indent=4)