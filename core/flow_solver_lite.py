from __future__ import annotations

import time

import numpy as np

from .hydrofoil_geometry import (
    body_coordinates,
    distance_to_body_surface,
    generate_grid,
    generate_naca0012,
    hydrofoil_mask,
    lower_surface_points,
    naca0012_thickness,
    upper_surface_points,
)
from .pressure_model import bernoulli_relative_pressure_kpa, cavitation_risk_mask, zone_pressure_statistics
from .vortex_model import trailing_edge_vortex_field
from .zone_control import ZONE_RANGES, normalize_zone_settings, recommend_control_strategy, zone_effect_strength


def _smooth_window(x_grid: np.ndarray, x0: float, x1: float, softness: float = 0.018) -> np.ndarray:
    left = 1.0 / (1.0 + np.exp(-(x_grid - x0) / softness))
    right = 1.0 / (1.0 + np.exp((x_grid - x1) / softness))
    return left * right


def _upper_band(chord_x: np.ndarray, body_y: np.ndarray, width: float = 0.070) -> np.ndarray:
    return np.exp(-((body_y - naca0012_thickness(chord_x) - 0.025) / width) ** 2) * (body_y >= 0.0)


def _lower_band(chord_x: np.ndarray, body_y: np.ndarray, width: float = 0.075) -> np.ndarray:
    return np.exp(-((body_y + naca0012_thickness(chord_x) - 0.025) / width) ** 2) * (body_y <= 0.0)


def _sample_field_nearest(x_grid: np.ndarray, y_grid: np.ndarray, field: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    x_axis = x_grid[0, :]
    y_axis = y_grid[:, 0]
    ix = np.clip(np.searchsorted(x_axis, xs), 1, len(x_axis) - 1)
    iy = np.clip(np.searchsorted(y_axis, ys), 1, len(y_axis) - 1)
    ix = np.where(np.abs(xs - x_axis[ix - 1]) <= np.abs(xs - x_axis[ix]), ix - 1, ix)
    iy = np.where(np.abs(ys - y_axis[iy - 1]) <= np.abs(ys - y_axis[iy]), iy - 1, iy)
    return field[iy, ix]


def prepare_static_fields(grid_density: str = "中", alpha_deg: float = 4.0) -> dict:
    x_grid, y_grid = generate_grid(grid_density)
    chord_x, body_y = body_coordinates(x_grid, y_grid, alpha_deg)
    mask = hydrofoil_mask(x_grid, y_grid, alpha_deg)
    surface_distance = distance_to_body_surface(chord_x, body_y)
    return {
        "X": x_grid,
        "Y": y_grid,
        "chord_x": chord_x,
        "body_y": body_y,
        "mask": mask,
        "surface_distance": surface_distance,
        "geometry": generate_naca0012(alpha_deg=alpha_deg),
        "grid_shape": x_grid.shape,
    }


def compute_base_velocity(static: dict, velocity: float, alpha_deg: float) -> tuple[np.ndarray, np.ndarray]:
    chord_x = static["chord_x"]
    body_y = static["body_y"]
    x_grid = static["X"]
    y_grid = static["Y"]
    vx = np.full_like(x_grid, velocity, dtype=float)
    vy = np.zeros_like(y_grid, dtype=float)

    alpha_gain = max(0.0, alpha_deg) / 12.0
    upper = _upper_band(chord_x, body_y)
    lower = _lower_band(chord_x, body_y)
    leading = np.exp(-((chord_x - 0.21) / 0.24) ** 2)
    mid = np.exp(-((chord_x - 0.50) / 0.34) ** 2)
    near_surface = np.exp(-(static["surface_distance"] / 0.055) ** 2) * ((chord_x >= 0.0) & (chord_x <= 1.0))

    vx += velocity * (0.16 + 0.33 * alpha_gain) * leading * upper
    vx += velocity * (0.07 + 0.18 * alpha_gain) * mid * upper
    vx -= velocity * (0.04 + 0.07 * alpha_gain) * mid * lower
    vx += velocity * 0.07 * near_surface
    vy += velocity * 0.06 * alpha_gain * np.exp(-((chord_x - 0.58) / 0.45) ** 2) * np.exp(-(body_y / 0.24) ** 2)

    # 让粒子自然绕开水翼：近表面给法向速度分量，固体内部后续 mask 掉。
    surface_sign = np.sign(body_y)
    vy += velocity * 0.055 * near_surface * surface_sign

    wake = (chord_x > 0.92) * np.exp(-((body_y - 0.025 * alpha_deg / 8.0) / 0.12) ** 2) * np.exp(-np.maximum(0.0, chord_x - 1.0) / 0.42)
    vx -= velocity * (0.08 + 0.13 * alpha_gain) * wake
    return vx, vy


def apply_zone_perturbations(static: dict, vx: np.ndarray, vy: np.ndarray, velocity: float, zones: dict) -> tuple[np.ndarray, np.ndarray]:
    chord_x = static["chord_x"]
    body_y = static["body_y"]
    vx = vx.copy()
    vy = vy.copy()

    a_strength = zone_effect_strength("A", zones["A"])
    if a_strength:
        x0, x1 = ZONE_RANGES["A"]
        window = _smooth_window(chord_x, x0, x1)
        band = _upper_band(chord_x, body_y, width=0.055)
        ripple = np.sin((chord_x - x0) / (x1 - x0) * np.pi * 8.0)
        vx += velocity * 0.050 * a_strength * window * band * ripple
        vy += velocity * 0.080 * a_strength * window * band * np.cos((chord_x - x0) / (x1 - x0) * np.pi * 4.0)

    b_strength = zone_effect_strength("B", zones["B"])
    if b_strength:
        x0, x1 = ZONE_RANGES["B"]
        window = _smooth_window(chord_x, x0, x1)
        band = _upper_band(chord_x, body_y, width=0.090)
        vx -= velocity * 0.185 * b_strength * window * band
        vy += velocity * 0.135 * b_strength * window * band * np.sin((chord_x - x0) / (x1 - x0) * np.pi)

    c_strength = zone_effect_strength("C", zones["C"])
    if c_strength:
        x0, x1 = ZONE_RANGES["C"]
        window = _smooth_window(chord_x, x0, x1)
        upper = _upper_band(chord_x, body_y, width=0.082)
        wake = (chord_x > x0) * np.exp(-((body_y - 0.01) / 0.12) ** 2) * np.exp(-np.maximum(0.0, chord_x - x1) / 0.45)
        vx += velocity * 0.090 * c_strength * window * upper
        vx += velocity * 0.145 * c_strength * wake
        vy -= velocity * 0.060 * c_strength * wake * np.sign(body_y)

    return vx, vy


def simulate_flow(
    velocity: float = 8.0,
    alpha_deg: float = 4.0,
    rho: float = 1000.0,
    cavitation_threshold_kpa: float = -30.0,
    grid_density: str = "中",
    zones: dict | None = None,
    show_vortex: bool = True,
    vortex_phase: float = 0.0,
    static: dict | None = None,
) -> dict:
    start = time.perf_counter()
    zone_settings = normalize_zone_settings(zones)
    if static is None:
        static = prepare_static_fields(grid_density, alpha_deg)
    vx, vy = compute_base_velocity(static, velocity, alpha_deg)
    vx, vy = apply_zone_perturbations(static, vx, vy, velocity, zone_settings)

    c_strength = zone_effect_strength("C", zone_settings["C"])
    if show_vortex:
        vortex_vx, vortex_vy = trailing_edge_vortex_field(static["chord_x"], static["body_y"], velocity, 0.45 + c_strength, vortex_phase)
        vx += vortex_vx
        vy += vortex_vy

    speed = np.sqrt(vx**2 + vy**2)
    pressure_kpa = bernoulli_relative_pressure_kpa(rho, velocity, speed)

    mask = static["mask"]
    vx = np.where(mask, np.nan, vx)
    vy = np.where(mask, np.nan, vy)
    speed = np.where(mask, np.nan, speed)
    pressure_kpa = np.where(mask, np.nan, pressure_kpa)
    cav_mask = cavitation_risk_mask(pressure_kpa, cavitation_threshold_kpa)

    xs = np.linspace(0.02, 0.98, 180)
    xu, yu = upper_surface_points(xs, alpha_deg)
    xl, yl = lower_surface_points(xs, alpha_deg)
    p_upper = _sample_field_nearest(static["X"], static["Y"], pressure_kpa, xu, yu)
    p_lower = _sample_field_nearest(static["X"], static["Y"], pressure_kpa, xl, yl)
    min_index = int(np.nanargmin(p_upper)) if np.isfinite(p_upper).any() else 0

    stats = zone_pressure_statistics(static["chord_x"], static["body_y"], pressure_kpa, cav_mask, rho, velocity)
    stats["recommendation"] = recommend_control_strategy(stats, alpha_deg, cavitation_threshold_kpa)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    return {
        "X": static["X"],
        "Y": static["Y"],
        "chord_x": static["chord_x"],
        "body_y": static["body_y"],
        "Vx": vx,
        "Vy": vy,
        "speed": speed,
        "pressure_kpa": pressure_kpa,
        "mask": mask,
        "cavitation_mask": cav_mask,
        "geometry": static["geometry"],
        "surface_x": xs,
        "surface_upper_xy": (xu, yu),
        "surface_lower_xy": (xl, yl),
        "pressure_upper_kpa": p_upper,
        "pressure_lower_kpa": p_lower,
        "min_upper_pressure_point": (float(xs[min_index]), float(p_upper[min_index])),
        "zone_stats": stats,
        "zone_settings": zone_settings,
        "compute_time_ms": elapsed_ms,
        "grid_shape": static["grid_shape"],
        "inputs": {
            "velocity": velocity,
            "alpha_deg": alpha_deg,
            "rho": rho,
            "cavitation_threshold_kpa": cavitation_threshold_kpa,
            "grid_density": grid_density,
            "show_vortex": show_vortex,
        },
    }
