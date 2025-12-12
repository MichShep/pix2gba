from PIL import Image as PILImage
import gba_functions as gf
import numpy as np

MAGENTA = 0x5d53

def extract_palette_img(filename, bpp):
    # Load the image palette
    img = PILImage.open(filename).convert("RGB")
    width, height = img.size

    if (width * height) > (1 << bpp):
        print("Too many pixels!")
        exit(1)

    gba_palette = []
    for j in range(height):
        for i in range(width):
            pxl = img.getpixel((i, j))
            gba_palette.append(
                gf.rgb24_to_rgb15(pxl)
            )

    # Hard code Magenta
    gba_palette[0] = 0x5d53

    return gba_palette

def palette_from_img(filename, bpp):
    img = PILImage.open(filename).convert("RGB")
    width, height = img.size

    # Load and sort colors by usage
    colors = img.getcolors()
    colors.sort(key=lambda c: c[0], reverse=True)

    #Take top 2^bpp
    top_col = [color for count, color in colors[:2**bpp]]
    gba_palette = [gf.rgb24_to_rgb15(color) for color in top_col]

    # Remove duplicates
    gba_palette = list(set(gba_palette))

    # Save old first color
    old_first = gba_palette[0] if len(gba_palette) > 0 else None

    # Remove magenta if it exists anywhere
    if MAGENTA in gba_palette:
        gba_palette.remove(MAGENTA)

    # Insert magenta at the front
    gba_palette.insert(0, MAGENTA)



    # Put displaced first color at the end (but only if it existed and isn't magenta)
    if old_first is not None and old_first != MAGENTA:
        gba_palette.append(old_first)

    # Enforce palette limit
    gba_palette = gba_palette[:2**bpp]

    return gba_palette


def closest_gba_color(color, gba_palette):
    target = gf.unpack_gba_color(color)
    colors = np.array([gf.unpack_gba_color(c) for c in gba_palette], dtype=np.int16)

    distances = np.sqrt(np.sum((colors - target) ** 2, axis=1))
    return int(np.argmin(distances))  # index of closest color


def create_conversion_table(input_img, gba_palette, bpp):
    img = PILImage.open(input_img).convert("RGB")
    img_palette = img.getcolors()

    img24_to_gba15 = {}

    # Go through each color and assign it to the closest GBA color
    for junk, color in img_palette:
        gba_col = gf.rgb24_to_rgb15(color)
        rgb88_col = gf.rgb888_to_rgb24(color)

        #print(color, rgb88_col, hex(rgb88_col), gba_col)

        closest_idx = closest_gba_color(gba_col, gba_palette)
        img24_to_gba15[gba_col] = closest_idx

    return img24_to_gba15