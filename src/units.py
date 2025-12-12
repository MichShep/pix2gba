from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ConversionConfig:
    bpp: int
    transparent: str
    output_type: str
    root_dir: Path
    output_dir: Path
    generate_palette: bool

@dataclass(frozen=True)
class ConversionUnit:
    config: ConversionConfig
    name: str
    metatile_width: int
    metatile_height: int
    palette_path: Path
    palette_include: bool