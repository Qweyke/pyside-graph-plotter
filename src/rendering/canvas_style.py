from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QPen,
    QColor,
    QFont,
)


class CanvasStyle:
    background_color = QColor("#FFFFFF")
    plot_area_color = QColor("#FAECC7")

    grid_pen = QPen(QColor("#C5BEBE"), 1, Qt.PenStyle.SolidLine)
    label_font_pen = QPen(QColor("#330505"), 1, Qt.PenStyle.DotLine)
    user_bounds_pen = QPen(QColor("#C5BEBE"), 2, Qt.PenStyle.DotLine)
    naught_axis_pen = QPen(QColor("#000000"), 1)

    label_font = QFont("Segoe UI", 9)
