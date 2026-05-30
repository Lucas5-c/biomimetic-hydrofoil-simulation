from __future__ import annotations

from dataclasses import dataclass

import numpy as np


GRID_SIZES = {
    "低": (120, 80),
    "中": (180, 120),
    "高": (260, 160),
}


@dataclass(frozen=True)
class HydrofoilGeometry:
    x_upper: np.ndarray
    y_upper: np.ndarray
    x_lower: np.ndarray
    y_lower: np.ndarray
    outline_x: np.ndarray
    outline_y: np.ndarray
    alpha_deg: float


def naca0012_thickness(x: np.ndarray | float, thickness: float = 0.12) -> np.ndarray:
    x_arr = np.clip(np.asarray(x, dtype=float), 0.0, 1.0)
    return 5.0 * thickness * (
        0.2969 * np.sqrt(x_arr)
        - 0.1260 * x_arr
        - 0.3516 * x_arr**2
        + 0.2843 * x_arr**3
        - 0.1015 * x_arr**4
    )


def rotate_points(
    x: np.ndarray | float,
    y: np.ndarray | float,
    alpha_deg: float,
    pivot: tuple[float, float] = (0.25, 0.0),
) -> tuple[np.ndarray, np.ndarray]:
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    alpha = np.deg2rad(alpha_deg)
    xp = x_arr - pivot[0]
    yp = y_arr - pivot[1]
    xr = xp * np.cos(alpha) - yp * np.sin(alpha) + pivot[0]
    yr = xp * np.sin(alpha) + yp * np.cos(alpha) + pivot[1]
    return xr, yr


def inverse_rotate_points(
    x: np.ndarray | float,
    y: np.ndarray | float,
    alpha_deg: float,
    pivot: tuple[float, float] = (0.25, 0.0),
) -> tuple[np.ndarray, np.ndarray]:
    return rotate_points(x, y, -alpha_deg, pivot=pivot)


def generate_naca0012(n_points: int = 280, alpha_deg: float = 0.0) -> HydrofoilGeometry:
    x = np.linspace(0.0, 1.0, n_points)
    yt = naca0012_thickness(x)
    xu, yu = rotate_points(x, yt, alpha_deg)
    xl, yl = rotate_points(x, -yt, alpha_deg)
    outline_x = np.concatenate([xu, xl[::-1], [xu[0]]])
    outline_y = np.concatenate([yu, yl[::-1], [yu[0]]])
    return HydrofoilGeometry(xu, yu, xl, yl, outline_x, outline_y, alpha_deg)


def generate_grid(density: str = "中") -> tuple[np.ndarray, np.ndarray]:
    nx, ny = GRID_SIZES.get(density, GRID_SIZES["中"])
    x = np.linspace(-0.18, 1.32, nx)
    y = np.linspace(-0.40, 0.40, ny)
    return np.meshgrid(x, y)


def body_coordinates(x_grid: np.ndarray, y_grid: np.ndarray, alpha_deg: float) -> tuple[np.ndarray, np.ndarray]:
    return inverse_rotate_points(x_grid, y_grid, alpha_deg)


def hydrofoil_mask(x_grid: np.ndarray, y_grid: np.ndarray, alpha_deg: float = 0.0) -> np.ndarray:
    xb, yb = body_coordinates(x_grid, y_grid, alpha_deg)
    in_chord = (xb >= 0.0) & (xb <= 1.0)
    return in_chord & (np.abs(yb) <= naca0012_thickness(xb))


def upper_surface_points(xs: np.ndarray, alpha_deg: float, offset: float = 0.012) -> tuple[np.ndarray, np.ndarray]:
    return rotate_points(xs, naca0012_thickness(xs) + offset, alpha_deg)


def lower_surface_points(xs: np.ndarray, alpha_deg: float, offset: float = 0.012) -> tuple[np.ndarray, np.ndarray]:
    return rotate_points(xs, -naca0012_thickness(xs) - offset, alpha_deg)


def distance_to_body_surface(chord_x: np.ndarray, body_y: np.ndarray) -> np.ndarray:
    """用于粒子贴附/避让的近似表面距离。"""
    thickness = naca0012_thickness(chord_x)
    return np.abs(np.abs(body_y) - thickness)
