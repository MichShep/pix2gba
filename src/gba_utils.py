import numpy as np

def rgb24_to_rgb15(color: tuple[int, int, int]) -> int:
    """
    :param color: tuple[int, int, int]
    :return: int
    """
    r8, g8, b8 = color
    r = int(r8 / 8)
    g = int(g8 / 8)
    b = int(b8 / 8)

    gba_val = (b << 10) + (g << 5) + r
    return gba_val


def rgb24_to_hex(color: tuple[int, int, int]) -> str:
    """
    :param color: tuple[int, int, int]
    :return: str
    """
    r8, g8, b8 = color

    rh = (r8 << 16)
    gh = (r8 << 8)
    bh = b8

    return hex(rh + gh + bh)


def rgb888_to_rgb24(rgb: tuple[int, int, int]) -> int:
    """
    :param rgb: tuple[int, int, int]
    :return: int
    """
    color = 0
    for c in rgb[::-1]:
        color = (color << 8) + c
    return color


def rgb24_to_rgb888(color: int) -> tuple[int, int, int]:
    """
    :param color: int
    :return: tuple[int, int, int]
    """
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF

    return r, g, b


def rgb15_to_rgb888(color15: int) -> tuple[int, int, int]:
    """
    :param color15: int
    :return: tuple[int, int, int]
    """
    r5 = color15 & 0x1F
    g5 = (color15 >> 5) & 0x1F
    b5 = (color15 >> 10) & 0x1F

    r8 = (r5 * 255) // 31
    g8 = (g5 * 255) // 31
    b8 = (b5 * 255) // 31

    return r8, g8, b8


def unpack_gba_color(c: int) -> np.ndarray:
    """
    :param c: int
    :return: numpy.ndarray
    """
    r = c & 0x1F
    g = (c >> 5) & 0x1F
    b = (c >> 10) & 0x1F
    return np.array([r, g, b], dtype=np.int16)
