from __future__ import annotations

import numpy as np

from .hydrofoil_geometry import body_coordinates, naca0012_thickness, rotate_points
from .zone_control import ZONE_LABELS, ZONE_RANGES, normalize_zone_settings, zone_effect_strength


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
    show_particles: bool,
    show_vortex: bool,
    show_vanes: bool,
    playing: bool,
    show_zone_labels: bool = True,
    trail_length: int = 3,
    emission_strength: float = 0.8,
    attachment_strength: float = 0.78,
    wake_strength: float = 0.8,
    vortex_strength: float = 0.5,
    separation_strength: float = 0.4,
    cavitation_strength: float = 0.3,
    vane_deploy_angle: float = 24.0,
    quality_mode: str = "流畅",
    show_cavitation_bubbles: bool = False,
    show_separation: bool = False,
    pressure_background: list[list[float]] | None = None,
    **extra: object,
) -> dict:
    if "show_separation_zone" in extra:
        show_separation = bool(extra["show_separation_zone"])
    if "show_cavitation" in extra:
        show_cavitation_bubbles = bool(extra["show_cavitation"])

    wake_highlight_strength = float(extra.get("wake_highlight_strength", wake_strength))
    speed_colormap_strength = float(extra.get("speed_colormap_strength", 1.0))
    vortex_animation_strength = float(extra.get("vortex_animation_strength", vortex_strength))
    blade_animation_strength = float(extra.get("blade_animation_strength", 1.0 if show_vanes else 0.0))
    show_wake_highlight = bool(extra.get("show_wake_highlight", True))
    show_speed_colormap = bool(extra.get("show_speed_colormap", True))
    show_local_vortices = bool(extra.get("show_local_vortices", show_vortex))
    show_blade_animation = bool(extra.get("show_blade_animation", show_vanes))
    target_fps = int(extra.get("target_fps", 60))
    mode_max_particles = int(extra.get("mode_max_particles", 900))
    mode_max_trail = int(extra.get("mode_max_trail", 4))
    bubble_cap = int(extra.get("bubble_cap", 0))
    vortex_mark_count = int(extra.get("vortex_mark_count", 2))
    shadow_level = int(extra.get("shadow_level", 0))
    max_dpr = float(extra.get("max_dpr", 1.0))
    auto_degrade_enabled = bool(extra.get("auto_degrade_enabled", True))
    visual_style = str(extra.get("visual_style", "natural_water"))
    bubble_density = float(extra.get("bubble_density", 0.4))
    bubble_size_scale = float(extra.get("bubble_size_scale", 0.8))
    vortex_visibility = float(extra.get("vortex_visibility", 0.55))
    vortex_core_size = float(extra.get("vortex_core_size", 0.85))
    wake_vortex_count = int(extra.get("wake_vortex_count", 2))

    zone_settings = normalize_zone_settings(zones)
    zone_payload = {
        zone: {
            "enabled": setting.enabled,
            "angle": setting.angle_deg,
            "response": setting.response,
            "strength": zone_effect_strength(zone, setting),
            "range": ZONE_RANGES[zone],
            "label": ZONE_LABELS[zone],
            "bladeType": setting.blade_type,
            "driveType": setting.drive_type,
        }
        for zone, setting in zone_settings.items()
    }
    foil_x = np.linspace(0.0, 1.0, 220)
    foil_t = naca0012_thickness(foil_x)
    xu, yu = rotate_points(foil_x, foil_t, alpha_deg)
    xl, yl = rotate_points(foil_x, -foil_t, alpha_deg)
    outline = [
        {"x": float(x), "y": float(y)}
        for x, y in zip(
            np.concatenate([xu, xl[::-1]]),
            np.concatenate([yu, yl[::-1]]),
        )
    ]
    payload = {
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
        "showParticles": show_particles,
        "showVortex": show_vortex,
        "showVanes": show_vanes,
        "showZoneLabels": show_zone_labels,
        "playing": playing,
        "trailLength": int(trail_length),
        "emissionStrength": float(emission_strength),
        "attachmentStrength": float(attachment_strength),
        "wakeStrength": float(wake_strength),
        "vortexStrength": float(vortex_strength),
        "separationStrength": float(separation_strength),
        "cavitationStrength": float(cavitation_strength),
        "vaneDeployAngle": float(vane_deploy_angle),
        "qualityMode": quality_mode,
        "showCavitationBubbles": show_cavitation_bubbles,
        "showSeparation": show_separation,
        "showCavitation": show_cavitation_bubbles,
        "wakeHighlightStrength": wake_highlight_strength,
        "speedColormapStrength": speed_colormap_strength,
        "vortexAnimationStrength": vortex_animation_strength,
        "bladeAnimationStrength": blade_animation_strength,
        "showWakeHighlight": show_wake_highlight,
        "showSpeedColormap": show_speed_colormap,
        "showLocalVortices": show_local_vortices,
        "showBladeAnimation": show_blade_animation,
        "showSeparationZone": show_separation,
        "targetFps": target_fps,
        "modeMaxParticles": mode_max_particles,
        "modeMaxTrail": mode_max_trail,
        "bubbleCap": bubble_cap,
        "vortexMarkCount": vortex_mark_count,
        "shadowLevel": shadow_level,
        "maxDpr": max_dpr,
        "autoDegradeEnabled": auto_degrade_enabled,
        "visualStyle": visual_style,
        "bubbleDensity": bubble_density,
        "bubbleSizeScale": bubble_size_scale,
        "vortexVisibility": vortex_visibility,
        "vortexCoreSize": vortex_core_size,
        "wakeVortexCount": wake_vortex_count,
        "foilOutline": outline,
        "pressureBackground": pressure_background or [],
    }
    payload.update(extra)
    return payload


def particle_trace_samples(
    velocity: float,
    alpha_deg: float,
    zones: dict,
    particle_count: int = 300,
    steps: int = 80,
    wake_strength: float = 0.72,
    vortex_strength: float = 0.70,
    separation_strength: float = 0.70,
    attachment_strength: float = 0.78,
) -> np.ndarray:
    """Generate lightweight concept-flow particle traces for export previews."""
    rng = np.random.default_rng(42)
    y0 = rng.uniform(-0.30, 0.30, particle_count)
    x = np.full(particle_count, -0.12)
    y = y0.copy()
    traces = np.zeros((steps, particle_count, 2), dtype=float)
    zone_settings = normalize_zone_settings(zones)
    alpha_gain = max(0.0, alpha_deg) / 12.0
    relief = 0.52 * zone_effect_strength("B", zone_settings["B"]) + 0.30 * zone_effect_strength("C", zone_settings["C"])
    separation = max(0.0, min(1.35, ((max(0.0, alpha_deg - 5.2) / 8.5) * separation_strength * (1.0 - 0.55 * relief))))

    for step in range(steps):
        xb, yb = body_coordinates(x, y, alpha_deg)
        thickness = naca0012_thickness(xb)
        in_chord = (xb >= 0.0) & (xb <= 1.0)
        near = np.exp(-((np.abs(yb) - thickness) / (0.070 + 0.015 * attachment_strength)) ** 2) * in_chord
        upper = np.exp(-((yb - thickness - 0.025) / 0.078) ** 2) * (yb > 0.0)

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

        aft = xb > 0.78
        wake = aft * np.exp(-np.maximum(0.0, xb - 0.84) / (0.44 + 0.10 * velocity / 8.0))
        vx += 0.006 * wake_strength * wake * np.cos(step * 0.28 + xb * 18.0)
        vy += 0.010 * wake_strength * wake * np.sin(step * 0.30 + xb * 20.0)

        if vortex_strength:
            for cx, cy, spin, radius in ((0.84, 0.07, 1.0, 0.09), (1.02, -0.03, -0.9, 0.13), (0.65, 0.06, 0.7, 0.08)):
                dx = xb - cx
                dy = yb - cy
                rr = dx * dx + dy * dy + 0.003
                env = np.exp(-rr / (radius * radius))
                swirl = vortex_strength * (0.35 + alpha_gain) * env / (0.18 + 10.0 * rr)
                vx += -dy * swirl * spin * 0.010
                vy += dx * swirl * spin * 0.014

        if separation:
            sep_start = 0.72 - 0.20 * min(1.0, separation)
            sep_window = np.clip((xb - sep_start) / max(0.10, 1.0 - sep_start), 0.0, 1.0)
            sep_band = upper * sep_window
            vx -= 0.006 * separation * sep_band
            vy += 0.012 * separation * sep_band * np.sin(step * 0.42 + xb * 34.0)

        x += vx
        y += vy
        reset = (x > 1.32) | (y > 0.42) | (y < -0.42)
        x[reset] = -0.12
        y[reset] = rng.uniform(-0.30, 0.30, np.count_nonzero(reset))
        traces[step, :, 0] = x
        traces[step, :, 1] = y
    return traces
