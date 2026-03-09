from typing import Callable, Tuple
import numpy as np
import sympy as sp


class Function:
    def __init__(
        self, symbolic, color, line, left_x: float, right_x: float, points_qnty: int
    ) -> None:

        self.symbolic = symbolic
        self.color = color
        self.line = line
        self.points_qnty = points_qnty

        self._x_min = left_x
        self._x_max = right_x
        self._x_vals = None

        self._y_min = None
        self._y_max = None
        self._y_vals = None

        self._compute_vals()

    @property
    def y_min(self):
        return self._y_min

    @property
    def y_max(self):
        return self._y_max

    @property
    def y_vals(self):
        return self._y_vals

    @property
    def x_vals(self):
        return self._x_vals

    def recalculate(self, left_x: float, right_x: float, points_qnty):
        self._x_min = left_x
        self._x_max = right_x
        self.points_qnty = points_qnty
        self._compute_vals()

    def _compute_vals(
        self,
    ):
        # Convert to numpy function
        x_sym = sp.symbols("x")
        expr_sym = sp.parse_expr(self.symbolic.replace("^", "**"))
        func = sp.lambdify(x_sym, expr_sym, "numpy")

        # 1. Generate Raw Data
        with np.errstate(divide="ignore", invalid="ignore"):
            x_vals = np.linspace(self._x_min, self._x_max, self.points_qnty)
            y_vals = func(x_vals)

            # Handle constant functions
            if not isinstance(y_vals, np.ndarray):
                y_vals = np.full_like(x_vals, y_vals)

        # 2. Extract Finite Data
        finite_mask = np.isfinite(y_vals)
        y_finite = y_vals[finite_mask]

        if y_finite.size > 0:
            y_min, y_max = float(y_finite.min()), float(y_finite.max())
            # Fix typo: check if range is not zero
            if y_max != y_min:
                margin = (y_max - y_min) * 0.1
            else:
                margin = 1.0
            pos_inf_limit = y_max + margin
            neg_inf_limit = y_min - margin
        else:
            y_min, y_max = -1.0, 1.0
            pos_inf_limit, neg_inf_limit = 100.0, -100.0

        # 3. Vectorized Cleaning
        # Fill NaNs with a neutral value or interpolate (Simplified here to clip)
        # We use np.nan_to_num to handle Inf and NaN in one go
        y_clean_vals = np.nan_to_num(
            y_vals,
            nan=np.nan,  # Keep NaNs for the renderer to "break" the line
            posinf=pos_inf_limit,
            neginf=neg_inf_limit,
        )

        self._x_vals = x_vals

        self._y_min = y_min
        self._y_max = y_max

        self._y_vals = y_clean_vals
