from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ConversionUnit:
    name: str

    bpp: int
    transparent: str
    output_type: str

    image_path: Path
    root_dir: Path
    output_dir: Path

    metatile_width: int
    metatile_height: int

    palette_path: Path
    palette_include: bool
    generate_palette: bool

    compress: bool
    dedupe: bool
    cache: bool

@dataclass(frozen=False)
class UnitOutput:
    u32_data:       list
    num_tiles:      int
    unique_tiles:   int
    tile_mapping:   list
    compress_data:  bytes
    gba_palette:    list

@dataclass(frozen=False)
class ConversionStats:
    """
    Tracks aggregate statistics across multiple conversion runs.

    :param total_conversions: Total number of conversion attempts.
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
