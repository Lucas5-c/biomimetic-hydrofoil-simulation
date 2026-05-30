from __future__ import annotations

import numpy as np

from .hydrofoil_geometry import body_coordinates, naca0012_thickness, rotate_points
from .zone_control import ZONE_RANGES, normalize_zone_settings, zone_effect_strength


def canvas_payload(
    velocity: float,
    alpha_deg: float,
    rho: float,
    cavitation_threshold_kpa: float,
    particle_count: int,
    animation_speed: float,
    grid_density: str,
    zones: dict,
    show_pressure: bool,
    show_vortex: bool,
    show_vanes: bool,
    playing: bool,
    show_zone_labels: bool = True,
    trail_length: int = 20,
    emission_strength: float = 0.7,
    attachment_strength: float = 0.78,
    wake_strength: float = 0.72,
    vortex_strength: float = 0.7,
    pressure_background: list[list[float]] | None = None,
) -> dict:
    zone_settings = normalize_zone_settings(zones)
    zone_payload = {
        zone: {
            "enabled": setting.enabled,
            "angle": setting.angle_deg,
            "response": setting.response,
            "strength": zone_effect_strength(zone, setting),
            "range": ZONE_RANGES[zone],
        }
        for zone, setting in zone_settings.items()
    }
    foil_x = np.linspace(0.0, 1.0, 220)
    foil_t = naca0012_thickness(foil_x)
    xu, yu = rotate_points(foil_x, foil_t, alpha_deg)
    xl, yl = rotate_points(foil_x, -foil_t, alpha_deg)
    outline = [{"x": float(x), "y": float(y)} for x, y in zip(np.concatenate([xu, xl[::-1]]), np.concatenate([yu, yl[::-1]]))]
    return {
        "velocity": velocity,
        "alphaDeg": alpha_deg,
        "rho": rho,
        "cavitationThresholdKpa": cavitation_threshold_kpa,
        "particleCount": int(particle_count),
        "animationSpeed": animation_speed,
        "gridDensity": grid_density,
        "zones": zone_payload,
        "zoneRanges": ZONE_RANGES,
        "showPressure": show_pressure,
        "showVortex": show_vortex,
        "showVanes": show_vanes,
        "showZoneLabels": show_zone_labels,
        "playing": playing,
        "trailLength": int(trail_length),
        "emissionStrength": float(emission_strength),
        "attachmentStrength": float(attachment_strength),
        "wakeStrength": float(wake_strength),
        "vortexStrength": float(vortex_strength),
        "foilOutline": outline,
        "pressureBackground": pressure_background or [],
    }


def particle_trace_samples(
    velocity: float,
    alpha_deg: float,
    zones: dict,
    particle_count: int = 300,
    steps: int = 80,
) -> np.ndarray:
    """生成轻量粒子轨迹样本，供导出或测试使用。"""
    rng = np.random.default_rng(42)
    y0 = rng.uniform(-0.30, 0.30, particle_count)
    x = np.full(particle_count, -0.12)
    y = y0.copy()
    traces = np.zeros((steps, particle_count, 2), dtype=float)
    zone_settings = normalize_zone_settings(zones)
    for step in range(steps):
        xb, yb = body_coordinates(x, y, alpha_deg)
        thickness = naca0012_thickness(xb)
        near = np.exp(-((np.abs(yb) - thickness) / 0.07) ** 2) * ((xb >= 0.0) & (xb <= 1.0))
        vx = 0.010 + 0.0015 * velocity + 0.006 * near
        vy = 0.0005 * alpha_deg * np.exp(-((xb - 0.5) / 0.45) ** 2)
        vy += 0.006 * near * np.sign(yb)
        for zone, (x0, x1) in ZONE_RANGES.items():
            strength = zone_effect_strength(zone, zone_settings[zone])
            if not strength:
                continue
            window = ((xb >= x0) & (xb <= x1)).astype(float)
            if zone == "A":
                vy += 0.007 * strength * window * np.sin(step * 0.35 + xb * 30.0)
            elif zone == "B":
                vy += 0.012 * strength * window * np.sin((xb - x0) / (x1 - x0) * np.pi)
                vx -= 0.004 * strength * window * (yb > 0)
            else:
                vx += 0.007 * strength * (xb > x0)
                vy *= 1.0 - 0.25 * strength * (xb > x0)
        x += vx
        y += vy
        reset = x > 1.32
        x[reset] = -0.12
        y[reset] = rng.uniform(-0.30, 0.30, np.count_nonzero(reset))
        traces[step, :, 0] = x
        traces[step, :, 1] = y
    return traces
