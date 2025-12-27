from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ConversionConfig:
    bpp: int
    transparent: str
    output_type: str
    root_dir: Path
    output_dir: Path

@dataclass(frozen=True)
class ConversionUnit:
    config: ConversionConfig
    name: str
    metatile_width: int
    metatile_height: int
    palette_path: Path
    palette_include: bool
    generate_palette: bool
    compress: bool

@dataclass(frozen=False)
class ConversionStats:
    total_conversions: int
    successful_conversions: int
    failed_conversion_names: list[str]

@dataclass(frozen=False)
class VerificationStats:
    total_units: int
    successful_units: int
    failed_unit_names: list[str]
    unit_error_code: list[int]
