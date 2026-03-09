from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QPolygonF,
    QRadialGradient,
    Qt,
    QPen,
    QPixmap,
    QLinearGradient,
)
from PySide6.QtCore import QPointF, QRectF
import numpy as np


if TYPE_CHECKING:
    from calculations.coord_mapper import CoordinateMapper
    from rendering.plot_builder import CanvasStyle


def grid(scene: QPixmap, mapper: CoordinateMapper, theme: CanvasStyle):
    # Setup painter
    painter = QPainter(scene)
    painter.setPen(theme.grid_pen)
    painter.setViewport(mapper.viewport)

    # Draw frame
    painter.setBrush(theme.plot_area_color)
    painter.drawRect(mapper.viewport)
    font_metrics = painter.fontMetrics()

    # Draw vertical grid lines
    left_line_x = mapper.x_min
    right_line_x = mapper.x_max
    while left_line_x <= right_line_x + (mapper.x_step / 2):
        bot_point = mapper.math_to_pixels(QPointF(left_line_x, mapper.y_min))
        top_point = mapper.math_to_pixels(QPointF(left_line_x, mapper.y_max))

        painter.setPen(theme.grid_pen)
        painter.drawLine(bot_point, top_point)

        # Label for x-lines
        label_text = f"{left_line_x:.5g}"
        text_width = font_metrics.horizontalAdvance(label_text)
        label_text_rect = QRectF(
            bot_point.x() - (text_width / 2),
            bot_point.y(),
            text_width,
            font_metrics.height(),
        )

        painter.setPen(theme.label_font_pen)
        painter.drawText(
            label_text_rect,
            Qt.AlignmentFlag.AlignHCenter,
            label_text,
        )

        left_line_x += mapper.x_step

    # Draw horizontal grid lines
    bottom_line_y = mapper.y_min
    top_line_y = mapper.y_max
    while bottom_line_y <= top_line_y + (mapper.y_step / 2):
        left_point = mapper.math_to_pixels(QPointF(mapper.x_min, bottom_line_y))
        right_point = mapper.math_to_pixels(QPointF(mapper.x_max, bottom_line_y))
        painter.setPen(theme.grid_pen)
        painter.drawLine(left_point, right_point)

        # Label for y-lines
        label_text = f"{bottom_line_y:.5g}"
        text_width = font_metrics.horizontalAdvance(label_text)
        text_height = font_metrics.height()
        label_text_rect = QRectF(
            left_point.x() - text_width - 5,
            left_point.y() - text_height / 2,
            text_width,
            text_height,
        )

        painter.setPen(theme.label_font_pen)
        painter.drawText(
            label_text_rect,
            Qt.AlignmentFlag.AlignRight,
            label_text,
        )

        bottom_line_y += mapper.y_step

    # Release painter
    painter.end()


def naught_lines_highlighting(
    scene: QPixmap, mapper: CoordinateMapper, theme: CanvasStyle
):
    painter = QPainter(scene)
    painter.setPen(theme.naught_axis_pen)
    painter.setViewport(mapper.viewport)

    if mapper.x_min <= 0 <= mapper.x_max:
        top_zero = mapper.math_to_pixels(QPointF(0, mapper.y_max))
        bot_zero = mapper.math_to_pixels(QPointF(0, mapper.y_min))
        painter.drawLine(top_zero, bot_zero)

    if mapper.y_min <= 0 <= mapper.y_max:
        left_zero = mapper.math_to_pixels(QPointF(mapper.x_min, 0))
        right_zero = mapper.math_to_pixels(QPointF(mapper.x_max, 0))
        painter.drawLine(left_zero, right_zero)

    # Release painter
    painter.end()


def user_bounds(
    scene: QPixmap,
    mapper: CoordinateMapper,
    theme: CanvasStyle,
    left_bound: float,
    right_bound: float,
    top_bound: float,
    bot_bound: float,
):
    painter = QPainter(scene)
    painter.setViewport(mapper.viewport)
    painter.setPen(theme.user_bounds_pen)
    # font = painter.font()
    # font.setBold(True)
    # painter.setFont(font)
    # font_metrics = painter.fontMetrics()

    for val in [left_bound, right_bound]:
        bot_point = mapper.math_to_pixels(QPointF(val, bot_bound))
        top_point = mapper.math_to_pixels(QPointF(val, top_bound))

        painter.drawLine(bot_point, top_point)

        # label_text = f"{val:.5g}"
        # text_width = font_metrics.horizontalAdvance(label_text)
        # label_text_rect = QRectF(
        #     bot_point.x() - (text_width / 2),
        #     bot_point.y(),
        #     text_width,
        #     font_metrics.height(),
        # )

        # painter.setPen(theme.label_font_pen)
        # painter.drawText(
        #     label_text_rect,
        #     Qt.AlignmentFlag.AlignHCenter,
        #     label_text,
        # )

    painter.end()


def pseudo_cones_3d_style(
    painter: QPainter,
    mapper: CoordinateMapper,
    x_vals,
    y_vals,
    color,
):
    if len(x_vals) < 2:
        return

    # вычисляем ширину конуса из шага по X
    p1 = mapper.math_to_pixels(QPointF(x_vals[0], 0))
    p2 = mapper.math_to_pixels(QPointF(x_vals[1], 0))
    cone_width = abs(p2.x() - p1.x()) * 0.8

    y_zero_px = mapper.math_to_pixels(QPointF(0, 0)).y()

    for x, y in zip(x_vals, y_vals):

        if not np.isfinite(y) or abs(y) < 1e-6:
            continue

        # вершина
        tip_px = mapper.math_to_pixels(QPointF(x, y))

        # центр основания
        base_center_px = mapper.math_to_pixels(QPointF(x, 0))

        left_x = base_center_px.x() - cone_width / 2
        right_x = base_center_px.x() + cone_width / 2

        # градиент освещения
        grad = QLinearGradient(left_x, 0, right_x, 0)
        grad.setColorAt(0.0, color.lighter(150))
        grad.setColorAt(0.3, color)
        grad.setColorAt(1.0, color.darker(150))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)

        # тело конуса
        cone_poly = QPolygonF(
            [
                tip_px,
                QPointF(left_x, y_zero_px),
                QPointF(right_x, y_zero_px),
            ]
        )

        painter.drawPolygon(cone_poly)

        # основание (эллипс)
        ellipse_h = cone_width * 0.3

        ellipse_rect = QRectF(
            left_x,
            y_zero_px - ellipse_h / 2,
            cone_width,
            ellipse_h,
        )

        painter.setBrush(color.darker(180))
        painter.drawEllipse(ellipse_rect)


def function(
    scene: QPixmap,
    mapper: CoordinateMapper,
    color,
    x_vals,
    y_vals,
    use_cones=False,
):
    try:
        # Prepare for plotting
        painter = QPainter(scene)
        painter.setViewport(mapper.viewport)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Cut outside-values
        painter.setClipRect(mapper.viewport)

        # Plotting cycle
        if use_cones:
            pseudo_cones_3d_style(
                painter=painter,
                mapper=mapper,
                x_vals=x_vals,
                y_vals=y_vals,
                color=color,
            )
            # self._pseudo_cones(painter, x_vals, y_vals, color)
            pass
        else:
            painter.setPen(QPen(color, 2))
            last_point = None

            for i in range(len(x_vals)):
                curr_point = mapper.math_to_pixels(QPointF(x_vals[i], y_vals[i]))

                if last_point is not None:
                    painter.drawLine(last_point, curr_point)

                last_point = curr_point

        # Release and paint
        painter.end()

    except Exception as e:
        print(f"Plot error: {e}")
