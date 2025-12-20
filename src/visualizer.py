import os
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from .gba_utils import rgb15_to_rgb888, rgb888_to_hex

class OutputWindow(QtWidgets.QMainWindow):
    def __init__(self,
                 tile_data:list,
                 pal_data:list,
                 bpp: int,
                 pxl_width:int,
                 pxl_height:int,
                 meta_width:int,
                 meta_height:int,
    ) -> None:
        super().__init__()

        self.label = QtWidgets.QLabel()
        self.canvas = QtGui.QPixmap(pxl_width, pxl_height)
        self.canvas.fill(Qt.white)
        self.label.setPixmap(self.canvas)
        self.setCentralWidget(self.label)
        self.setWindowTitle("Visualizer")

        self.tile_data = tile_data
        self.pal_data = pal_data
        self.bpp = bpp
        self.pxl_width = pxl_width
        self.pxl_height = pxl_height
        self.meta_width = meta_width
        self.meta_height = meta_height

    def render(self) -> None:
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        pen = QtGui.QPen()
        pen.setWidth(1)

        # Size definitions
        num_metatiles_width = self.pxl_width // (self.meta_width * 8)
        meta_total_width = self.meta_width * 8
        meta_total_height = self.meta_height * 8

        # Position Trackers
        y = 0
        x_offset = y_offset = 0
        pxl_row_count = meta_row_count = meta_col_count = 0
        metatile_row_count = metatile_col_count = 0
        total_meta_tiles = 0

        pxl_per_u32 = 32 // self.bpp
        pxl_mask = (1 << self.bpp) - 1

        for u32_hex in self.tile_data: # go through each uint in the tile data
            u32 = int(u32_hex, 16)
            for pxl in range(pxl_per_u32):
                pal_index = (u32 >> (pxl*self.bpp)) & pxl_mask
                r, g, b = rgb15_to_rgb888(self.pal_data[pal_index])

                pen.setColor(QtGui.QColor(r, g, b))
                painter.setPen(pen)
                painter.fillRect(x_offset + pxl, y + y_offset, 1, 1, QtGui.QColor(r, g, b))

            y += 1
            pxl_row_count += 1

            if pxl_row_count % 8 == 0:
                y = 0
                meta_col_count += 1

            if meta_col_count % self.meta_width == 0 and meta_col_count != 0:
                meta_row_count += 1
                meta_col_count = 0

            if meta_row_count % self.meta_height == 0 and meta_row_count != 0:
                total_meta_tiles += 1
                metatile_col_count += 1
                meta_row_count = 0

            if metatile_col_count % num_metatiles_width == 0 and metatile_col_count != 0:
                metatile_row_count += 1
                metatile_col_count = 0

            x_offset = meta_col_count * 8 + metatile_col_count * meta_total_width
            y_offset = meta_row_count * 8 + metatile_row_count * meta_total_height

        painter.end()
        scale = 8

        scaled = canvas.scaled(
            self.pxl_width * scale,
            self.pxl_height * scale,
            Qt.IgnoreAspectRatio,
            Qt.FastTransformation
        )

        self.label.setPixmap(scaled)