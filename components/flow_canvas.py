from __future__ import annotations

import html
import json
from pathlib import Path

import streamlit.components.v1 as components

from core.params import ZONE_UI
from core.particle_flow_model import canvas_payload as _core_canvas_payload


TEMPLATE_PATH = Path(__file__).with_name("flow_canvas_template.html")


def _default_zones() -> dict:
    return {
        zone: {
            "enabled": True,
            "angle_deg": spec["default_angle"],
            "response": spec["default_response"],
            "blade_type": spec["blade_type"],
            "drive_type": spec["drive_type"],
        }
        for zone, spec in ZONE_UI.items()
    }


def canvas_payload(
    velocity: float,
    angle: float | None = None,
    animation_speed: float = 1.0,
    particle_count: int = 600,
    trail_length: int = 3,
    emission_rate: float | None = None,
    attachment_strength: float = 0.78,
    wake_strength: float = 0.72,
    vortex_strength: float = 0.45,
    pressure_background: bool | list[list[float]] | None = True,
    show_particles: bool = True,
    **extra: object,
) -> dict:
    """Build a canvas payload while accepting future visual effect keywords."""
    alpha_deg = float(extra.pop("alpha_deg", angle if angle is not None else 0.0))
    emission_strength = float(extra.pop("emission_strength", emission_rate if emission_rate is not None else 0.7))
    rho = float(extra.pop("rho", 1000.0))
    cavitation_threshold_kpa = float(extra.pop("cavitation_threshold_kpa", -30.0))
    grid_density = str(extra.pop("grid_density", "medium"))
    zones = extra.pop("zones", _default_zones())
    show_pressure = bool(extra.pop("show_pressure", True if isinstance(pressure_background, bool) else True))
    show_vortex = bool(extra.pop("show_vortex", extra.get("show_local_vortices", True)))
    show_vanes = bool(extra.pop("show_vanes", extra.get("show_blade_animation", True)))
    playing = bool(extra.pop("playing", True))
    show_zone_labels = bool(extra.pop("show_zone_labels", True))
    separation_strength = float(extra.pop("separation_strength", 0.4))
    cavitation_strength = float(extra.pop("cavitation_strength", 0.3))
    vane_deploy_angle = float(extra.pop("vane_deploy_angle", 24.0))
    quality_mode = str(extra.pop("quality_mode", "流畅"))
    show_separation = bool(extra.pop("show_separation", extra.get("show_separation_zone", False)))
    show_cavitation_bubbles = bool(extra.pop("show_cavitation_bubbles", extra.get("show_cavitation", False)))
    mode_max_particles = int(extra.get("mode_max_particles", 900))
    mode_max_trail = int(extra.get("mode_max_trail", 4))
    particle_count = min(int(particle_count), mode_max_particles)
    trail_length = min(int(trail_length), mode_max_trail)
    pressure_field = pressure_background if isinstance(pressure_background, list) else None

    payload = _core_canvas_payload(
        velocity=velocity,
        alpha_deg=alpha_deg,
        rho=rho,
        cavitation_threshold_kpa=cavitation_threshold_kpa,
        particle_count=particle_count,
        animation_speed=animation_speed,
        grid_density=grid_density,
        zones=zones,
        show_pressure=show_pressure,
        show_particles=show_particles,
        show_vortex=show_vortex,
        show_vanes=show_vanes,
        playing=playing,
        show_zone_labels=show_zone_labels,
        trail_length=trail_length,
        emission_strength=emission_strength,
        attachment_strength=attachment_strength,
        wake_strength=wake_strength,
        vortex_strength=vortex_strength,
        separation_strength=separation_strength,
        cavitation_strength=cavitation_strength,
        vane_deploy_angle=vane_deploy_angle,
        quality_mode=quality_mode,
        show_cavitation_bubbles=show_cavitation_bubbles,
        show_separation=show_separation,
        pressure_background=pressure_field,
        **extra,
    )
    payload.update(
        {
            "angle": alpha_deg,
            "animation_speed": animation_speed,
            "particle_count": int(particle_count),
            "trail_length": int(trail_length),
            "emission_rate": emission_strength,
            "attachment_strength": float(attachment_strength),
            "wake_strength": float(wake_strength),
            "vortex_strength": float(vortex_strength),
            "pressure_background": pressure_background,
            "show_particles": show_particles,
            "show_separation": show_separation,
            "separation_strength": separation_strength,
            "show_cavitation": show_cavitation_bubbles,
            "show_cavitation_bubbles": show_cavitation_bubbles,
            "cavitation_strength": cavitation_strength,
            "visual_style": extra.get("visual_style", "natural_water"),
            "bubble_density": float(extra.get("bubble_density", 0.4)),
            "bubble_size_scale": float(extra.get("bubble_size_scale", 0.8)),
            "vortex_visibility": float(extra.get("vortex_visibility", 0.55)),
            "vortex_core_size": float(extra.get("vortex_core_size", 0.85)),
            "wake_vortex_count": int(extra.get("wake_vortex_count", 2)),
        }
    )
    return payload


def render_flow_canvas(payload: dict, height: int = 660) -> None:
    """Render the enhanced HTML5 Canvas particle-flow viewport."""
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    data = html.escape(json.dumps(payload, ensure_ascii=False), quote=False)
    markup = template.replace("__FLOW_PAYLOAD__", data)
    components.html(markup, height=height, scrolling=False)
