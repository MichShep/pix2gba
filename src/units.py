from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConversionConfig:
    """
    Immutable configuration shared across one or more conversion units.

    :param bpp: Bits per pixel used for tile and palette generation.
    :param transparent: Color value (string form) treated as transparent.
    :param output_type: Output format selector (e.g., 'c', 'h', or 'both').
    :param root_dir: Root directory used for resolving relative paths.
    :param output_dir: Directory where generated files will be written.
    """
    bpp: int
    transparent: str
    output_type: str
    root_dir: Path
    output_dir: Path


@dataclass(frozen=True)
class ConversionUnit:
    """
    Represents a single image conversion job and its associated settings.

    :param config: Shared conversion configuration.
    :param name: Logical name of the conversion unit (used for output files).
    :param metatile_width: Width of a metatile in tiles.
    :param metatile_height: Height of a metatile in tiles.
    :param palette_path: Path to the palette file used for conversion.
    :param palette_include: Whether the palette should be emitted in output.
    :param generate_palette: Whether to generate a PNG palette preview.
    :param compress: Whether to apply compression to generated output.
    """
    config: ConversionConfig
    name: str
    metatile_width: int
    metatile_height: int
    palette_path: Path
    palette_include: bool
    generate_palette: bool
    compress: bool
    dedupe: bool


@dataclass(frozen=False)
class ConversionStats:
    """
    Tracks aggregate statistics across multiple conversion runs.

    :param total_conversions: Total number of conversion attempts.
    :param successful_conversions: Number of conversions completed successfully.
    :param failed_conversion_names: Names of conversions that failed.
    """
    total_conversions: int
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
