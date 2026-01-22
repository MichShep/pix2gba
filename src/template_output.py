from pathlib import Path

def add_template_file(project_root: Path):
    """
    Simple function that creates a template pix2gba.toml file in the project root
    :param project_root:
    :return:
    """
    template = """# Template pix2gba TOML (move into directory and remove `_output` from toml name
[general]
bpp = 4
transparent = "0x5D53"
output_type = "both"
destination = "./destination"

[[unit]]
name = "unit name"
metatile_width = 1
metatile_height = 1
palette = "./palette.png"
palette_include = 1
generate_palette = 1
compress = 1
"""
    template_path = (project_root / "pix2gba_template").with_suffix(".toml")

    with open(str(template_path), 'w') as file:
        file.write(template)
        file.close()