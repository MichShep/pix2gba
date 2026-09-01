from pathlib import Path
from PIL import Image
import json
import hashlib
from . import cli_log as log

VERSION = "0.7.0"

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


def _hash_palette(unit: ConversionUnit) -> str:
    """
    Returns a content hash of the unit's palette image, or "" if the
    unit has no palette file to hash (e.g. generate_palette is used instead).
    """
    if not unit.palette_path:
        return ""

    palette_path = Path(unit.palette_path)
    if not palette_path.exists():
        return ""

    return hash_image_pixels(palette_path)


def get_cache_dict(build_path: Path) -> dict:
    cache_path = build_path / "pix2gba_cache.json"

    if not cache_path.exists():
        return {}

    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        log.warn("Cache file unreadable, treating as empty.")
        return {}


def needs_rebuild(unit: ConversionUnit, cache_dict: dict, default_unit: ConversionUnit,) -> bool:
    """
    Returns True if the unit needs rebuilding, False otherwise.
    Assumes cache_dict was already read from pix2gba_cache.json.
    """

    # If the shared defaults changed since last cache, every unit
    # in this build directory needs rebuilding.
    current_default_hash = _hash_unit_dict(default_unit)
    if cache_dict.get("default", "") != current_default_hash:
        return True

    old_hashes = cache_dict.get(unit.name)

    # Unit not cached → rebuild
    if old_hashes is None:
        return True

    unit_hash = _hash_unit_dict(unit)
    image_hash = hash_image_pixels(unit.image_path)
    palette_hash = _hash_palette(unit)

    if (
        old_hashes.get("unit", "") != unit_hash
        or old_hashes.get("image", "") != image_hash
        or old_hashes.get("palette", "") != palette_hash
        or old_hashes.get("version", "") != VERSION
    ):
        return True

    log.cache("no changes compared to cache")
    return False


def create_cache(default_unit: ConversionUnit, passed_units: list[ConversionUnit]):
    """
    Updates cache files after conversion.
    """
    if len(passed_units) == 0:
        return

    cache_file = default_unit.root_dir / "pix2gba_cache.json"

    # Load existing cache so valid units are preserved
    cache_dict = get_cache_dict(default_unit.root_dir)

    # Store default hash once, at the top level — every unit is
    # checked against this same value, not a per-unit copy.
    cache_dict["default"] = _hash_unit_dict(default_unit)

    for unit in passed_units:
        unit_hash = _hash_unit_dict(unit)
        image_hash = hash_image_pixels(unit.image_path)
        palette_hash = _hash_palette(unit)

        cache_dict[unit.name] = {
            "unit": unit_hash,
            "image": image_hash,
            "palette": palette_hash,
            "version": VERSION,
        }

    with open(cache_file, "w") as file:
        json.dump(cache_dict, file, indent=4)