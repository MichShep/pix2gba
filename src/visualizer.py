import os
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from .gba_utils import rgb15_to_rgb888, rgb888_to_hex


class OutputWindow(QtWidgets.QMainWindow):
    """
    Visualization window for rendered GBA tile and palette data.

    This window reconstructs pixel output from packed tile data and a GBA
    palette, displaying the result using Qt drawing primitives. It is intended
    as a debugging and verification tool for tile conversion output.

    The renderer respects metatile layout and bit-depth when reconstructing
    pixel positions.
    """

    def __init__(
        self,
        tile_data: list,
        pal_data: list,
        bpp: int,
        pxl_width: int,
        pxl_height: int,
        meta_width: int,
        meta_height: int,
    ) -> None:
        """
        Initializes the output visualization window.

        :param tile_data: List of packed tile data (uint32 hex strings).
        :param pal_data: List of GBA palette entries (rgb15 values).
        :param bpp: Bits per pixel used in the tile data.
        :param pxl_width: Width of the rendered image in pixels.
        :param pxl_height: Height of the rendered image in pixels.
        :param meta_width: Width of a metatile in tiles.
        :param meta_height: Height of a metatile in tiles.
        """
        super().__init__()

        # Qt display setup
        self.label = QtWidgets.QLabel()
        self.canvas = QtGui.QPixmap(pxl_width, pxl_height)
        self.canvas.fill(Qt.white)
        self.label.setPixmap(self.canvas)
        self.setCentralWidget(self.label)
        self.setWindowTitle("Visualizer")

        # Store rendering data
        self.tile_data = tile_data
        self.pal_data = pal_data
        self.bpp = bpp
        self.pxl_width = pxl_width
        self.pxl_height = pxl_height
        self.meta_width = meta_width
        self.meta_height = meta_height

    def render(self) -> None:
        """
        Renders the tile data to the canvas using the provided palette.

        Tile data is unpacked according to the configured bit depth and drawn
        pixel-by-pixel while respecting tile, metatile, and image layout.
        The final output is scaled up for easier viewing.
        """
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)

        pen = QtGui.QPen()
        pen.setWidth(1)

        # Metatile layout calculations
        num_metatiles_width = self.pxl_width // (self.meta_width * 8)
        meta_total_width = self.meta_width * 8
        meta_total_height = self.meta_height * 8

        # Position tracking
        y = 0
        x_offset = y_offset = 0
        pxl_row_count = meta_row_count = meta_col_count = 0
        metatile_row_count = metatile_col_count = 0
        total_meta_tiles = 0

        # Bit unpacking helpers
        pxl_per_u32 = 32 // self.bpp
        pxl_mask = (1 << self.bpp) - 1

        # Iterate over each packed 32-bit word
        for u32_hex in self.tile_data:
            u32 = int(u32_hex, 16)

            # Extract pixels from the packed word
            for pxl in range(pxl_per_u32):
                pal_index = (u32 >> (pxl * self.bpp)) & pxl_mask
                r, g, b = rgb15_to_rgb888(self.pal_data[pal_index])

                pen.setColor(QtGui.QColor(r, g, b))
                painter.setPen(pen)
                painter.fillRect(
                    x_offset + pxl,
                    y + y_offset,
                    1,
                    1,
                    QtGui.QColor(r, g, b),
                )

            # Advance within tile rows
            y += 1
            pxl_row_count += 1

            # Move to next tile column after 8 rows
            if pxl_row_count % 8 == 0:
                y = 0
                meta_col_count += 1

            # Move to next metatile row
            if meta_col_count % self.meta_width == 0 and meta_col_count != 0:
                meta_row_count += 1
                meta_col_count = 0

            # Move to next metatile
            if meta_row_count % self.meta_height == 0 and meta_row_count != 0:
                total_meta_tiles += 1
                metatile_col_count += 1
                meta_row_count = 0

            # Wrap to next metatile row
            if metatile_col_count % num_metatiles_width == 0 and metatile_col_count != 0:
                metatile_row_count += 1
                metatile_col_count = 0

            # Update pixel offsets
            x_offset = meta_col_count * 8 + metatile_col_count * meta_total_width
            y_offset = meta_row_count * 8 + metatile_row_count * meta_total_height

        painter.end()

        # Scale up the final image for visibility
        scale = 8
        scaled = canvas.scaled(
            self.pxl_width * scale,
            self.pxl_height * scale,
            Qt.IgnoreAspectRatio,
            Qt.FastTransformation,
        )

        self.label.setPixmap(scaled)
