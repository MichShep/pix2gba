import os
from pathlib import Path
from typing import Union
from PIL import Image
import json
import hashlib
import re
from importlib import metadata
from . import cli_log as log
from .units import ConversionUnit

def _read_version() -> str:
    """
    Reads the package version from pyproject.toml, falling back to installed package metadata.
    :return: Version string, or "unknown" if it cannot be found.
    """
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if pyproject.is_file():
        match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject.read_text(), re.MULTILINE)
        if match:
            return match.group(1)

    try:
        return metadata.version("pix2gba")
    except metadata.PackageNotFoundError:
        return "unknown"


VERSION = _read_version()


def hash_dict(data: dict) -> str:
    """
    Returns a stable SHA-256 hash of a JSON-serializable dict.
    :param data: Dict to hash.
    :return: Hex digest of the hash.
    """
    serialized_data = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized_data).hexdigest()


def hash_image_pixels(path: Union[str, Path]) -> str:
    """
    Returns a SHA-256 hash of an image's pixel data and size.
    :param path: Path to the image file.
    :return: Hex digest of the hash.
    """
    img = Image.open(path).convert("RGBA")
    h = hashlib.sha256()
    h.update(img.tobytes())
    h.update(str(img.size).encode())
    return h.hexdigest()


def _relative_to_root(unit: ConversionUnit, path: str) -> str:
    """
    Returns a unit path relative to its TOML directory, so the cache hash doesn't change
    when the project is moved or checked out somewhere else.
    """
    if path == "":
        return ""
    return os.path.relpath(path, unit.root_dir)


def _hash_unit_dict(unit: ConversionUnit) -> str:
    """
    Returns a hash of the unit settings that affect the conversion output.
    :param unit: Unit to hash.
    :return: Hex digest of the hash.
    """
    unit_dict = {
        "bpp": unit.bpp,
        "transparent": unit.transparent,
        "output_type": unit.output_type,
        "destination": _relative_to_root(unit, unit.output_dir),
        "metatile_width": unit.metatile_width,
        "metatile_height": unit.metatile_height,
        "palette": _relative_to_root(unit, unit.palette_path),
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
    """
    Loads pix2gba_cache.json from a build directory.
    :param build_path: Directory that holds the cache file.
    :return: The cache contents, or an empty dict if missing or unreadable.
    """
    cache_path = build_path / "pix2gba_cache.json"

    if not cache_path.exists():
        return {}

    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        log.warn("Cache file unreadable, treating as empty.")
        return {}


def needs_rebuild(unit: ConversionUnit, cache_dict: dict, default_unit: ConversionUnit) -> bool:
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

    # Unit not cached -> rebuild
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


def create_cache(default_unit: ConversionUnit, passed_units: list[ConversionUnit]) -> None:
    """
    Updates cache files after conversion.
    """
    if len(passed_units) == 0:
        return

    cache_file = default_unit.root_dir / "pix2gba_cache.json"

    # Load existing cache so valid units are preserved
    cache_dict = get_cache_dict(default_unit.root_dir)

    # Store default hash once, at the top level; every unit is
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