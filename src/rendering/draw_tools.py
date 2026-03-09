from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtGui import QPainter, QPainterPath, Qt, QPen, QPixmap
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


# @staticmethod
# def axis_labels(scene: QPixmap, mapper: CoordinateMapper, theme: CanvasStyle):
#     # Setup painter
#     painter = QPainter(scene)
#     painter.setPen(theme.label_font_pen)
#     painter.setViewport(mapper.viewport)

#     metrics = painter.fontMetrics()
#     label_text = f"{current_x:.2f}"

#     # Labels
#     label_rect = QRectF(
#         bot_point.x() - (mapper.px_for_x * mapper.x_step) / 2,
#         bot_point.y(),
#         mapper.px_for_x * mapper.x_step,
#         mapper.px_for_y,
#     )
#     print(f"X label box size: {label_rect.size()}")
#     painter.drawText(
#         label_rect,
#         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
#         f"{current_x:.2f}",
#     )

#     label_rect = QRectF(
#         left_point.x() - mapper.px_for_x * 1.1,
#         left_point.y() - (mapper.y_step * mapper.px_for_y) / 2,
#         mapper.px_for_x,
#         mapper.y_step * mapper.px_for_y,
#     )

#     print(f"Y label box size: {label_rect.size()}")
#     painter.drawText(
#         label_rect,
#         Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
#         f"{current_y:.2f}",
#     )


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


def function2(scene, mapper, color, x_vals, y_vals, use_cones=False):
    try:
        painter = QPainter(scene)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(color, 2))

        # 1. MASKING: Find where the math actually makes sense
        # We find jumps where the function "flips" across a huge gap
        y_diff = np.abs(np.diff(y_vals))
        y_range = abs(mapper.y_max - mapper.y_min)

        # A 'break' happens if: 1. Value is NaN/Inf OR 2. Massive sign-flip jump
        is_finite = np.isfinite(y_vals)
        # Check for sign flip + huge jump
        is_jump = np.zeros(len(y_vals), dtype=bool)
        is_jump[1:] = (np.sign(y_vals[1:]) != np.sign(y_vals[:-1])) & (
            y_diff > y_range * 2
        )

        # Valid points are finite AND not part of an asymptotic jump
        valid_mask = is_finite & ~is_jump

        # 2. SEGMENTATION: Group indices into continuous chunks
        # This is the "secret sauce" for 1/x
        valid_idxs = np.where(valid_mask)[0]
        if valid_idxs.size == 0:
            return

        # Find where the indices are not consecutive
        breaks = np.where(np.diff(valid_idxs) != 1)[0] + 1
        segments = np.split(valid_idxs, breaks)

        # 3. RENDERING: Draw each chunk as a separate path
        for seg in segments:
            if len(seg) < 2:
                continue

            path = QPainterPath()
            # Move to start of segment
            p0 = mapper.math_to_pixels(QPointF(x_vals[seg[0]], y_vals[seg[0]]))
            path.moveTo(p0)

            # Line to the rest
            for idx in seg[1:]:
                p = mapper.math_to_pixels(QPointF(x_vals[idx], y_vals[idx]))
                path.lineTo(p)

            painter.drawPath(path)

        painter.end()
    except Exception as e:
        print(f"Plot error: {e}")


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
