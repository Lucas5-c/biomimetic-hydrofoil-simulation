from __future__ import annotations

import numpy as np

from .zone_control import ZONE_RANGES


def dynamic_pressure_kpa(rho: float, velocity: float) -> float:
    return 0.5 * rho * velocity**2 / 1000.0


def bernoulli_relative_pressure_kpa(rho: float, reference_velocity: float, speed: np.ndarray) -> np.ndarray:
    return 0.5 * rho * (reference_velocity**2 - speed**2) / 1000.0


def cavitation_risk_mask(pressure_kpa: np.ndarray, threshold_kpa: float) -> np.ndarray:
    return np.isfinite(pressure_kpa) & (pressure_kpa <= threshold_kpa)


def zone_pressure_statistics(
    chord_x: np.ndarray,
    body_y: np.ndarray,
    pressure_kpa: np.ndarray,
    cavitation_mask: np.ndarray,
    rho: float,
    velocity: float,
) -> dict:
    valid = np.isfinite(pressure_kpa)
    stats: dict[str, dict] = {}
    for zone, (x0, x1) in ZONE_RANGES.items():
        zone_mask = (chord_x >= x0) & (chord_x <= x1) & (body_y >= 0.0) & (body_y <= 0.18) & valid
        values = pressure_kpa[zone_mask]
        if values.size == 0:
            stats[zone] = {
                "avg_pressure_kpa": float("nan"),
                "min_pressure_kpa": float("nan"),
                "max_pressure_kpa": float("nan"),
                "cavitation_percent": 0.0,
            }
            continue
        stats[zone] = {
            "avg_pressure_kpa": float(np.nanmean(values)),
            "min_pressure_kpa": float(np.nanmin(values)),
            "max_pressure_kpa": float(np.nanmax(values)),
            "cavitation_percent": float(np.count_nonzero(cavitation_mask[zone_mask]) / values.size * 100.0),
        }
    finite = pressure_kpa[valid]
    stats["overall"] = {
        "min_pressure_kpa": float(np.nanmin(finite)) if finite.size else float("nan"),
        "max_pressure_kpa": float(np.nanmax(finite)) if finite.size else float("nan"),
        "cavitation_percent": float(np.count_nonzero(cavitation_mask) / max(1, np.count_nonzero(valid)) * 100.0),
        "dynamic_pressure_kpa": dynamic_pressure_kpa(rho, velocity),
    }
    return stats
