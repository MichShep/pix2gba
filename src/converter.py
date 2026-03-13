import os
# Helpers
import struct
from .units import ConversionUnit, UnitOutput
from .palette import extract_palette_img, palette_from_img, create_conversion_table
# Actual Converters
from .tile_creator import create_tile_data
from .deduper import dedupe_tiles
from .compressor import gba_lz77_compress_list
# Outputs
from .tile_output import make_output
from . import cli_log as log

def run_conversion(unit: ConversionUnit, simulate=False) -> UnitOutput:
    # Step 1: Create GBA palette
    #print("* Extracting Palette...")
    if unit.palette_path != "":
        gba_palette = extract_palette_img(
            filename=str(unit.palette_path),
            bpp=unit.bpp,
            transparent=int(unit.transparent, 16)
        )
        if gba_palette is None:
            return None
    else:
        gba_palette = palette_from_img(
            filename=str(unit.image_path),
            bpp=unit.bpp,
            transparent=int(unit.transparent, 16)
        )

    # Step 2: Create conversion table
    #print("* Creating Color Conversion Table...")
    conversion_table = create_conversion_table(
        input_img=str(unit.image_path),
        gba_palette=gba_palette,
    )

    # Step 3: Create the base tile with no extras
    #print("* Generating C/Header Output...")
    u32_data = create_tile_data(unit, conversion_table)

    tile_size_bytes = 32 if unit.bpp == 4 else 64

    output_data = UnitOutput(
        u32_data=u32_data,
        num_tiles=(len(u32_data) * 4) // tile_size_bytes,
        tile_mapping=[],
        compress_data = bytes(0),
        gba_palette = gba_palette,
        unique_tiles = (len(u32_data) * 4) // tile_size_bytes
    )

    if not simulate:
        log.indent()

    # Step 4: Attempt deduping
    if unit.dedupe and not simulate:
        log.info("Starting Deduping...")
        dedupe_dict = dedupe_tiles(u32_data, unit.bpp)
        output_data.u32_data = dedupe_dict["final_list"]
        output_data.tile_mapping = dedupe_dict["tile_mapping"]
        output_data.unique_tiles = dedupe_dict["unique_tile_count"]
        log.ok(f"Deduping complete. ({output_data.num_tiles} -> {output_data.unique_tiles})")

    # Step 5: Attempt Compression
    if unit.compress and not simulate:
        log.info("Starting Compressing...")
        output_data.compress_data = gba_lz77_compress_list(output_data.u32_data)
        log.ok(f"Compression Complete. ({len(output_data.u32_data)*4} -> {len(output_data.compress_data)})")

    # Step 6: Create Output OR pass out stuff
    if not simulate:
        log.dedent()
        make_output(unit, output_data)
        return None

    return output_data