# GBA Image Converter

## Introduction

**GBA Image Converter** is a command-line tool designed to convert standard PNG images into GBA (Game Boy Advance)-compatible tile and palette data in C format. Allowing developers working on GBA homebrew games or emulation tools to easily generate optimized graphics data, including metatiles and palettes, with optional C header and source files.

---

## Features

- Converts PNG images to GBA-compatible `.c` and `.h` files.
- Supports both 4bpp and 8bpp color modes.
- Automatic or manual palette extraction.
- Optional palette PNG generation.
- Supports configurable metatile dimensions.
- Includes detailed comments in generated output for better maintainability.

---

## Installation

```bash
pip install .
```

Alternatively, if you are running the tool directly:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python pix2gba.py -i <input_image.png> -mw <meta_width> -mh <meta_height> -bpp <4|8> -o <h|c|both> [options]
```

---

## Command Line Arguments

| Argument              | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `-i`, `--input`       | **(Required)** Path to the input PNG image.                                 |
| `-mw`, `--meta_width` | **(Required)** Meta-tile width in tiles (1 tile = 8px).                     |
| `-mh`, `--meta_height` | **(Required)** Meta-tile height in tiles.                                   |
| `-bpp`                | **(Required)** Bits per pixel. Must be a power of 2 (4 or 8).                |
| `-o`, `--output`      | **(Required)** Output type: `h`, `c`, or `both`.                             |
| `-p`, `--palette`     | Optional external palette PNG file.                                          |
| `-ip`                 | Include palette array in the output files.                                  |
| `-gp`                 | Generate and save a PNG version of the GBA palette.                         |
| `-d`, `--destination` | Destination directory for the output files (default: current directory).    |
| `--help` | Display information on each possible command |

---

## Examples

**Basic conversion with generated palette (both `.c` and `.h`):**

```bash
python pix2gba.py -i assets/sprite.png -mw 2 -mh 2 -bpp 4 -o both
```

**Using external palette and saving generated palette image:**

```bash
python pix2gba.py -i assets/bg.png -p assets/palette.png -mw 4 -mh 4 -bpp 8 -o both -ip -gp -d output/
```

---

## Dependencies

- [Pillow](https://python-pillow.org/) (Image processing)
- [NumPy](https://numpy.org/) (Color distance calculations)

These are automatically installed via `setup.py`.

---

## Configuration

There is no external configuration file. All configuration is passed via command-line arguments.

---

## Troubleshooting

| Issue                            | Solution                                                                 |
|----------------------------------|--------------------------------------------------------------------------|
| "Input PNG file not found"       | Check the file path provided to `-i`.                                    |
| "Destination folder not found"   | Make sure the `-d` folder exists or create it before running.            |
| "Input files must be PNG"        | Only PNG files are supported for both images and palettes.               |
| "BPP must be a power of 2"       | Only `4` and `8` are valid values for `--bpp`.                           |
| "Too many pixels!"               | Make sure your palette image has ≤ `2^bpp` colors.                       |

---

## Contributors

- **Main Developer**: MichShep
- Feel free to contribute by submitting pull requests or reporting issues.

