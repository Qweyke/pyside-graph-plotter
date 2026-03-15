import math

from PySide6.QtCore import QPointF
from PySide6.QtGui import (
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import QWidget

import rendering.draw_tools as draw
from rendering.canvas_style import CanvasStyle
from calculations.coord_mapper import CoordinateMapper
from rendering.function import Function


class PlotBuilder(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Init and build default-scene
        self._cached_scene = QPixmap(self.width(), self.height())
        self._mapper = CoordinateMapper(x_min=-10, x_max=10, y_min=-10, y_max=10)

        self.canvas_style = CanvasStyle()

        self.current_funcs = []

    def resizeEvent(self, event):
        self._cached_scene = QPixmap(self.width(), self.height())
        self._cached_scene.fill(self.canvas_style.background_color)
        self._mapper.remap(new_rect=self._get_plotting_rect(), theme=self.canvas_style)

        self._rebuild_axis_grid()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(QPointF(0, 0), self._cached_scene)

    def _get_plotting_rect(self):
        margin_x = int(self.width() * 0.03)
        margin_y = int(self.height() * 0.02)

        plot_rect = self.contentsRect().adjusted(
            margin_x, margin_y, -margin_x, -margin_y
        )
        return plot_rect

    def _rebuild_axis_grid(self):
        draw.grid(
            mapper=self._mapper,
            scene=self._cached_scene,
            theme=self.canvas_style,
        )
        draw.naught_lines_highlighting(
            mapper=self._mapper,
            scene=self._cached_scene,
            theme=self.canvas_style,
        )

    def clear(self):
        self.current_funcs = []

        self._cached_scene = QPixmap(self.width(), self.height())
        self._cached_scene.fill(self.canvas_style.background_color)
        self._mapper.remap(
            theme=self.canvas_style,
            new_x_min=-10,
            new_x_max=10,
            new_y_min=-10,
            new_y_max=10,
        )

        self._rebuild_axis_grid()
        self.update()

    def _update_x_bounds(self, left_x, right_x, points_qnty):
        if not math.isclose(left_x, self._mapper.x_min) or not math.isclose(
            right_x, self._mapper.x_max
        ):
            self._mapper.remap(
                theme=self.canvas_style,
                new_x_min=left_x,
                new_x_max=right_x,
            )
            for func in self.current_funcs:
                func.recalculate(self._mapper.x_min, self._mapper.x_max, points_qnty)

    def _update_y_bounds(self):
        found_y_min, found_y_max = (
            self.current_funcs[0].y_min,
            self.current_funcs[0].y_max,
        )
        for func in self.current_funcs[1:]:
            found_y_min = min(found_y_min, func.y_min)
            found_y_max = max(found_y_max, func.y_max)

        self._mapper.remap(
            theme=self.canvas_style,
            new_y_min=found_y_min,
            new_y_max=found_y_max,
        )

    def add_function(
        self, symbolic, color, line, left_x, right_x, points_qnty, use_cones
    ):
        self._update_x_bounds(left_x, right_x, points_qnty)

        new_func = Function(symbolic, color, line, left_x, right_x, points_qnty)
        self.current_funcs.append(new_func)

        self._update_y_bounds()
        self._plot_functions(use_cones)

        return id(new_func)

    def remove_function(self, func_id, left_x, right_x, use_cones, points_qnty):
        for i, func in enumerate(self.current_funcs):
            if id(func) == func_id:
                self.current_funcs.pop(i)
                break

        if self.current_funcs:
            self._update_x_bounds(left_x, right_x, points_qnty)
            self._update_y_bounds()
            self._plot_functions(use_cones)
        else:
            self.clear()

    def _plot_functions(self, use_cones):
        self._cached_scene = QPixmap(self.width(), self.height())
        self._cached_scene.fill(self.canvas_style.background_color)
        self._rebuild_axis_grid()

        draw.user_bounds(
            theme=self.canvas_style,
            mapper=self._mapper,
            scene=self._cached_scene,
            left_bound=self._mapper.x_min,
            right_bound=self._mapper.x_max,
            bot_bound=self._mapper.y_min,
            top_bound=self._mapper.y_max,
        )

        for func in self.current_funcs:
            draw.function(
                x_vals=func.x_vals,
                y_vals=func.y_vals,
                mapper=self._mapper,
                scene=self._cached_scene,
                color=func.color,
                use_cones=use_cones,
            )

        self.update()
