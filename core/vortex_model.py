from __future__ import annotations

import numpy as np


def trailing_edge_vortex_field(
    chord_x: np.ndarray,
    body_y: np.ndarray,
    velocity: float,
    strength: float,
    phase: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Lightweight trailing-edge wake/vortex term for visualization only."""
    velocity_gain = np.clip(velocity / 8.0, 0.35, 2.6)
    wake_length = 0.36 + 0.10 * velocity_gain
    wake = (chord_x > 0.76) * np.exp(-np.maximum(0.0, chord_x - 0.82) / wake_length)
    core_y = (0.030 + 0.018 * velocity_gain) * np.sin((chord_x - 0.80) * 18.0 + phase)
    dy = body_y - core_y
    envelope = wake * np.exp(-(dy / (0.10 + 0.012 * velocity_gain)) ** 2)
    swirl = strength * velocity * envelope
    vx = 0.11 * swirl * np.cos((chord_x - 0.82) * 21.0 + phase)
    vy = 0.20 * swirl * np.sin((chord_x - 0.82) * 21.0 + phase) - 0.06 * swirl * np.sign(body_y)
    return vx, vy


def canvas_vortex_descriptors(enabled: bool, strength: float) -> list[dict]:
    if not enabled:
        return []
    return [
        {"x": 0.92, "y": 0.045, "radius": 0.080, "strength": 0.55 * strength},
        {"x": 1.08, "y": -0.030, "radius": 0.105, "strength": -0.42 * strength},
        {"x": 1.22, "y": 0.018, "radius": 0.125, "strength": 0.30 * strength},
    ]
