# <img alt="logo.png" height="48" src="logo.png" width="48"/> pix2gba 

A Python-based tool for converting standard image formats (PNG, JPEG) into GBA-compatible tile data, palettes, and headers for use in GBA homebrew development.

## Introduction

`pix2gba` is a command-line utility that transforms raster images into assets usable on the Game Boy Advance (GBA). It generates `.c` and `.h` files containing tile and palettes data in formats compatible with GBA development tools. It supports configurable bit depths, metatile dimensions, and both custom and auto-generated palettes. It can also output a visual preview of the generated palette.

## Project Structure

```
pix2gba/
├── Readme.md
├── assets/
│   └── test.png                  # Sample input image
├── examples/
│   ├── test.c                    # Example output C file
│   ├── test.h                    # Example output header
│   └── test_palette.png          # Preview of the generated palette
├── requirements.txt              # Python dependencies
└── src/
    ├── cli.py                    # CLI definition and argument parsing
    ├── converter.py              # Conversion workflow
    ├── gba_utils.py              # Color utilities (RGB<->GBA format)
    ├── palette.py                # Palette generation and mapping
    ├── tile_creator.py           # Tile and metatile conversion logic
    └── tile_output.py            # Output .c/.h file generation
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pix2gba.git
cd pix2gba
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 src/cli.py -i assets/test.png -mw 2 -mh 2 -bpp 4 -o both -d examples/ -ip -gp
```

### CLI Arguments

| Argument              | Type    | Description | Required |
|------------------------|---------|-------------| ---|
| `-i, --input`          | Path    | Path to the input image (PNG, JPG)                                            | `True`
| `-mw, --meta_width`    | Integer | Width of each metatile in number of 8×8 tiles                               | `True`
| `-mh, --meta_height`   | Integer | Height of each metatile in number of 8×8 tiles                              | `True`
| `-bpp, --bpp`          | Integer | Bits per pixel (e.g., 4 or 8). Must be a power of two                       | `True`
| `-p, --palette`        | Path    | Optional custom palette image                                               | `False`
| `-d, --destination`    | Path    | Directory to save output files                                              | `False`
| `-o, --output`         | Path    | Output format: `h`, `c`, or `both`                                          | `True`
| `-ip, --include_palette` | Flag    | Include palette in header and source output                                 | `False`
| `-gp, --generate_palette` | Flag    | Save a PNG visualization of the palette                                     | `False`
| `-t, --transparent`    | RGB15   | RGB15 Color to use as the transparent color (must be in index 0 of palette) | `False`

## Features

- Converts standard images to GBA-compatible tile data
- Supports 4bpp and 8bpp modes
- Automatic or user-specified palettes
- Palette visualization as PNG
- Configurable metatile sizes
- Outputs `.h` and `.c` files for easy inclusion in GBA projects

## Technical Concepts

### Bits Per Pixel (BPP)

BPP defines how many bits are used to represent each pixel:

- 4 BPP = 16 colors per tile (uses 4 bits per pixel)
- 8 BPP = 256 colors per tile (uses 8 bits per pixel)

Higher BPP allows more colors per tile but consumes more memory.

### Palettes

A palette is a lookup table of colors. In the GBA:

- Colors are stored in 15-bit RGB format (5 bits per channel)
- A tile references its color by index into the palette
- `pix2gba` can auto-generate a palette from the image or use a provided one
- Index 0 is reserved for transparency and is forced to magenta (0x5D53) if not specified by `--transparent`

### Tiles

- A tile is an 8x8 pixel block, the base unit for GBA graphics.
- Each pixel in a tile refers to a color index in the palette.
- Tiles are used in backgrounds, sprites, and UI elements.

### Metatiles

A metatile is a larger logical structure made up of multiple tiles.

For example, a 2x2 metatile consists of 4 tiles (each 8×8), forming a 16×16 graphic unit.

#### Benefits:

- Helps reuse patterns more efficiently (tilemaps reference metatiles instead of raw tiles)
- Simplifies level design or sprite grouping

#### Use Cases:

- Backgrounds: Metatiles can map entire tilemaps, making scrolling and map editing more manageable.
- Sprites: Large or composite sprites can be built from multiple tiles as metatiles.

## Examples

Sample conversion command:

```bash
python3 src/cli.py -i assets/test.png -mw 2 -mh 2 -bpp 4 -o both -d examples/ -ip -gp
```

This will:
- Convert `test.png` into 4bpp tile data
- Use 2x2 metatiles
- Generate both `.h` and `.c` files
- Include the palette
- Output the results to the `examples/` directory
- Save a preview of the palette as `test_palette.png`

## Dependencies

- Pillow - Image handling and manipulation
- NumPy - Efficient color distance calculations

Install them with:

```bash
pip install -r requirements.txt
```

## Troubleshooting

Here are some general issues you might encounter and how to resolve them:

- **Input image does not exist**: Double-check the file path and ensure the image file is in the specified location.
- **Input image type is not accepted**: Only PNG and JPG/JPEG formats are supported.
- **Meta tile dimensions must be >= 1**: Make sure you use postive integers for `--meta_width` and `--meta_height`.
- **Invalid BPP value**: Valid values are powers of two (e.g., 1, 2, 4, or 8). The most common are 4 and 8.
- **Output directory errors**: The destination directory must exist and be a valid directory.
- **Palette file errors**: If a custom palette is used, it must be a valid image file and follow the format requirements (1 pixel per color, with total count matching `2^bpp`).
- **Out-of-bounds errors**: Ensure the image dimensions are compatible with the chosen metatile sizes. The tool pads the image to align with 8×8 tiles if needed.
- **File permissions**: Make sure you have write access to the destination directory.
- **Invalid transparent Color:** Make sure the value is RGB15, not RGB24
