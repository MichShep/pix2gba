from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ConversionUnit:
    """
    One image to convert, with all TOML settings resolved against the default unit.
    Paths from the TOML (destination, palette) are kept as the strings the user wrote,
    and flags are the 0/1 integers from the TOML.
    """
    name: str

    bpp: int
    transparent: str
    output_type: str

    image_path: Path
    root_dir: Path
    output_dir: str

    metatile_width: int
    metatile_height: int

    palette_path: str
    palette_include: int
    generate_palette: int

    compress: int
    dedupe: int
    cache: int

@dataclass(frozen=False)
class UnitOutput:
    """
    Result of converting a single unit.

    :param u32_data: Packed tile data as "0x%08x" hex strings.
    :param num_tiles: Number of 8x8 tiles before deduping.
    :param unique_tiles: Number of 8x8 tiles after deduping.
    :param tile_mapping: Index into the unique tiles for every original tile (empty if not deduped).
    :param compress_data: LZ77 compressed tile data (empty if not compressed).
    :param gba_palette: GBA RGB15 palette entries.
    """
    u32_data:       list[str]
    num_tiles:      int
    unique_tiles:   int
    tile_mapping:   list[int]
    compress_data:  bytes
    gba_palette:    list[int]

@dataclass(frozen=False)
class ConversionStats:
    """
    Tracks aggregate statistics across multiple conversion runs.

    :param total_conversions: Total number of conversion attempts.
    :param total_cached: Number of units skipped because the cache was unchanged.
    :param successful_conversions: Number of conversions completed successfully.
    :param failed_conversion_names: Names of conversions that failed.
    """
    total_conversions: int
    total_cached: int
    successful_conversions: int
    failed_conversion_names: list[str]


@dataclass(frozen=False)
class VerificationStats:
    """
    Tracks validation results for conversion units prior to execution.

    :param total_units: Total number of units verified.
    :param successful_units: Number of units that passed verification.
    :param failed_unit_names: Names of units that failed verification.
    :param unit_error_code: Error codes corresponding to failed units.
    """
    total_units: int
    successful_units: int
    failed_unit_names: list[str]
    unit_error_code: list[int]
