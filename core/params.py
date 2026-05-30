from __future__ import annotations

from copy import deepcopy
from typing import Any


MODULES = [
    "动态水流粒子",
    "压力云图",
    "速度场与流线",
    "空化风险",
    "表面压力曲线",
    "参数扫描/动画生成",
    "导出报告",
]

GRID_OPTIONS = ["低", "中", "高"]

ZONE_UI = {
    "A": {
        "label": "A区 前缘调节区",
        "blade_type": "低矮楔形/三角鳍形",
        "drive_type": "柔性铰链 + 微驱动器",
        "max_angle": 15.0,
        "default_angle": 8.0,
        "default_response": 0.55,
    },
    "B": {
        "label": "B区 中弦主控区",
        "blade_type": "宽翻板/小翼型",
        "drive_type": "TSAM + 连杆 + 微弹簧复位",
        "max_angle": 30.0,
        "default_angle": 15.0,
        "default_response": 0.70,
    },
    "C": {
        "label": "C区 后缘整流区",
        "blade_type": "后掠整流鳍/梳齿叶片",
        "drive_type": "微流体腔/膜片 + 推杆",
        "max_angle": 18.0,
        "default_angle": 10.0,
        "default_response": 0.50,
    },
}

VISUAL_DEFAULTS: dict[str, Any] = {
    "particle_count": 600,
    "animation_speed": 1.0,
    "trail_length": 3,
    "emission_strength": 0.80,
    "attachment_strength": 0.78,
    "wake_strength": 0.80,
    "vortex_strength": 0.50,
    "separation_strength": 0.4,
    "cavitation_strength": 0.3,
    "vane_deploy_angle": 24.0,
    "quality_mode": "流畅",
    "pressure_background": True,
    "show_pressure": True,
    "show_particles": True,
    "show_vortex": True,
    "show_vanes": True,
    "show_cavitation_bubbles": False,
    "show_separation": False,
    "show_zone_labels": True,
    "playing": True,
    "wake_highlight_strength": 1.0,
    "speed_colormap_strength": 1.0,
    "vortex_animation_strength": 0.8,
    "blade_animation_strength": 1.0,
    "show_separation_zone": False,
    "show_blade_animation": True,
    "show_wake_highlight": True,
    "show_speed_colormap": True,
    "show_local_vortices": True,
}

DEFAULT_STATE: dict[str, Any] = {
    "active_module": MODULES[0],
    "U": 8.0,
    "alpha": 4.0,
    "rho": 1000.0,
    "cav": -30.0,
    "grid_density": "中",
    "fast_preview": True,
    "show_vortex": True,
    "particle_count": 600,
    "particle_level": "中",
    "animation_speed": 1.0,
    "trail_length": 3,
    "emission_strength": 0.80,
    "attachment_strength": 0.78,
    "wake_strength": 0.80,
    "vortex_strength": 0.50,
    "separation_strength": 0.4,
    "cavitation_strength": 0.3,
    "vane_deploy_angle": 24.0,
    "quality_mode": "流畅",
    "pressure_background": True,
    "show_pressure": True,
    "show_particles": True,
    "show_vanes": True,
    "show_cavitation_bubbles": False,
    "show_separation": False,
    "wake_highlight_strength": 1.0,
    "speed_colormap_strength": 1.0,
    "vortex_animation_strength": 0.8,
    "blade_animation_strength": 1.0,
    "show_separation_zone": False,
    "show_blade_animation": True,
    "show_wake_highlight": True,
    "show_speed_colormap": True,
    "show_local_vortices": True,
    "show_zone_labels": True,
    "playing": True,
    "contour_levels": 34,
    "pressure_auto_range": True,
    "pressure_min": -60.0,
    "pressure_max": 40.0,
    "pressure_show_foil": True,
    "pressure_show_zones": True,
    "pressure_show_cavitation": True,
    "streamline_density": 1.45,
    "streamline_length": 1.0,
    "show_vectors": False,
    "vector_stride": 10,
    "wake_display_strength": 0.70,
    "velocity_show_foil": True,
    "velocity_show_zones": True,
    "risk_alpha": 0.45,
    "risk_contour": True,
    "risk_lowlight": True,
    "risk_show_stats": True,
    "curve_smoothing": 1,
    "curve_show_upper": True,
    "curve_show_lower": True,
    "curve_annotate_min": True,
    "curve_mark_zones": True,
    "curve_x_axis": "x/c",
    "curve_y_unit": "kPa",
    "scan_target": "流速",
    "scan_start": 2.0,
    "scan_end": 20.0,
    "scan_frames": 16,
    "gif_fps": 10,
    "scan_resolution": "中",
    "scan_show_pressure": True,
    "scan_show_particles": True,
    "scan_show_vortex": True,
    "report_title": "仿生分区主动水翼简化仿真报告",
    "report_include_pressure": True,
    "report_include_velocity": True,
    "report_include_particle": True,
    "report_include_curve": True,
    "report_include_json": True,
    "report_include_principle": True,
    "report_include_disclaimer": True,
    "last_gif_path": "",
    "recent_exports": [],
}

PRESETS = {
    "低速巡航": {
        "U": 5.0,
        "alpha": 2.0,
        "particle_count": 650,
        "zones": {"A": (True, 4.0, 0.35), "B": (False, 0.0, 0.25), "C": (True, 6.0, 0.45)},
    },
    "高攻角防失速": {
        "U": 8.0,
        "alpha": 10.0,
        "particle_count": 900,
        "zones": {"A": (True, 12.0, 0.80), "B": (True, 28.0, 0.90), "C": (True, 12.0, 0.60)},
    },
    "空化抑制": {
        "U": 14.0,
        "alpha": 6.0,
        "particle_count": 900,
        "zones": {"A": (True, 8.0, 0.60), "B": (True, 24.0, 1.00), "C": (True, 10.0, 0.55)},
    },
    "后缘整流": {
        "U": 11.0,
        "alpha": 3.0,
        "particle_count": 850,
        "zones": {"A": (False, 0.0, 0.30), "B": (True, 8.0, 0.35), "C": (True, 16.0, 0.95)},
    },
    "三分区协同控制": {
        "U": 10.0,
        "alpha": 7.0,
        "particle_count": 1000,
        "zones": {"A": (True, 10.0, 0.75), "B": (True, 22.0, 0.85), "C": (True, 14.0, 0.75)},
    },
    "全部收起": {
        "U": 8.0,
        "alpha": 4.0,
        "particle_count": 650,
        "zones": {"A": (False, 0.0, 0.0), "B": (False, 0.0, 0.0), "C": (False, 0.0, 0.0)},
    },
    "全部展开演示": {
        "U": 12.0,
        "alpha": 7.0,
        "particle_count": 1100,
        "zones": {"A": (True, 15.0, 1.0), "B": (True, 30.0, 1.0), "C": (True, 18.0, 1.0)},
    },
}


QUALITY_MODE_LIMITS: dict[str, dict[str, Any]] = {
    "流畅": {
        "max_particles": 900,
        "max_trail": 4,
        "target_fps": 60,
        "bubble_cap": 0,
        "vortex_marks": 2,
        "shadow_level": 0,
        "dpr": 1.0,
    },
    "平衡": {
        "max_particles": 1400,
        "max_trail": 7,
        "target_fps": 50,
        "bubble_cap": 40,
        "vortex_marks": 4,
        "shadow_level": 1,
        "dpr": 1.25,
    },
    "炸裂": {
        "max_particles": 2500,
        "max_trail": 12,
        "target_fps": 45,
        "bubble_cap": 120,
        "vortex_marks": 6,
        "shadow_level": 2,
        "dpr": 1.5,
    },
}

VISUAL_PRESETS: dict[str, dict[str, Any]] = {
    "流畅演示": {
        "quality_mode": "流畅",
        "particle_count": 600,
        "trail_length": 3,
        "emission_strength": 0.8,
        "wake_strength": 0.8,
        "vortex_strength": 0.5,
        "separation_strength": 0.4,
        "cavitation_strength": 0.3,
        "show_cavitation_bubbles": False,
        "show_separation": False,
        "show_separation_zone": False,
        "show_wake_highlight": True,
        "show_speed_colormap": True,
        "show_blade_animation": True,
        "show_local_vortices": True,
        "fast_preview": True,
    },
    "平衡展示": {
        "quality_mode": "平衡",
        "particle_count": 1000,
        "trail_length": 5,
        "emission_strength": 0.9,
        "wake_strength": 0.9,
        "vortex_strength": 0.7,
        "separation_strength": 0.55,
        "cavitation_strength": 0.45,
        "show_cavitation_bubbles": True,
        "show_separation": True,
        "show_separation_zone": True,
        "show_wake_highlight": True,
        "show_speed_colormap": True,
        "show_blade_animation": True,
        "show_local_vortices": True,
        "fast_preview": True,
    },
    "炸裂截图": {
        "quality_mode": "炸裂",
        "particle_count": 1800,
        "trail_length": 10,
        "emission_strength": 1.15,
        "wake_strength": 1.25,
        "vortex_strength": 1.0,
        "separation_strength": 0.9,
        "cavitation_strength": 0.8,
        "show_cavitation_bubbles": True,
        "show_separation": True,
        "show_separation_zone": True,
        "show_wake_highlight": True,
        "show_speed_colormap": True,
        "show_blade_animation": True,
        "show_local_vortices": True,
        "fast_preview": False,
    },
    "低配电脑模式": {
        "quality_mode": "流畅",
        "particle_count": 400,
        "trail_length": 2,
        "emission_strength": 0.65,
        "wake_strength": 0.55,
        "vortex_strength": 0.3,
        "separation_strength": 0.2,
        "cavitation_strength": 0.15,
        "show_cavitation_bubbles": False,
        "show_separation": False,
        "show_separation_zone": False,
        "show_wake_highlight": True,
        "show_speed_colormap": True,
        "show_blade_animation": True,
        "show_local_vortices": True,
        "fast_preview": True,
    },
}


def init_session_state(st_module) -> None:
    for key, value in DEFAULT_STATE.items():
        st_module.session_state.setdefault(key, deepcopy(value))
    for zone, spec in ZONE_UI.items():
        st_module.session_state.setdefault(f"{zone}_enabled", True)
        st_module.session_state.setdefault(f"{zone}_angle", spec["default_angle"])
        st_module.session_state.setdefault(f"{zone}_response", spec["default_response"])


def apply_preset_to_state(st_module, preset_name: str) -> None:
    preset = PRESETS[preset_name]
    st_module.session_state["U"] = preset["U"]
    st_module.session_state["alpha"] = preset["alpha"]
    st_module.session_state["particle_count"] = preset["particle_count"]
    for zone, values in preset["zones"].items():
        enabled, angle, response = values
        st_module.session_state[f"{zone}_enabled"] = enabled
        st_module.session_state[f"{zone}_angle"] = angle
        st_module.session_state[f"{zone}_response"] = response


def apply_visual_preset_to_state(st_module, preset_name: str) -> None:
    preset = VISUAL_PRESETS[preset_name]
    for key, value in preset.items():
        st_module.session_state[key] = deepcopy(value)


def normalize_quality_mode(mode: str | None) -> str:
    aliases = {
        "Performance": "流畅",
        "High Performance": "流畅",
        "高性能": "流畅",
        "流畅模式": "流畅",
        "Balanced": "平衡",
        "平衡模式": "平衡",
        "Cinematic": "炸裂",
        "高画质": "炸裂",
        "炸裂模式": "炸裂",
    }
    value = str(mode or "流畅")
    return aliases.get(value, value if value in QUALITY_MODE_LIMITS else "流畅")


def apply_quality_limits(visual: dict[str, Any], fast_preview: bool = False) -> dict[str, Any]:
    merged = merge_visual_defaults(visual)
    mode = normalize_quality_mode(merged.get("quality_mode"))
    if fast_preview and mode == "炸裂":
        mode = "平衡"
    limits = QUALITY_MODE_LIMITS[mode]

    merged["quality_mode"] = mode
    merged["quality_label"] = mode
    merged["target_fps"] = limits["target_fps"]
    merged["auto_degrade_enabled"] = True
    merged["mode_max_particles"] = limits["max_particles"]
    merged["mode_max_trail"] = limits["max_trail"]
    merged["bubble_cap"] = 0 if fast_preview and mode == "流畅" else limits["bubble_cap"]
    merged["vortex_mark_count"] = limits["vortex_marks"]
    merged["shadow_level"] = limits["shadow_level"]
    merged["max_dpr"] = limits["dpr"]

    merged["particle_count"] = min(int(merged.get("particle_count", 600)), limits["max_particles"])
    merged["trail_length"] = min(int(merged.get("trail_length", 3)), limits["max_trail"])
    if mode == "流畅" or fast_preview:
        merged["trail_length"] = min(int(merged["trail_length"]), 4)
        merged["show_cavitation_bubbles"] = False
        merged["show_separation"] = bool(merged.get("show_separation", False)) and float(merged.get("separation_strength", 0.0)) > 0.65
        merged["show_separation_zone"] = merged["show_separation"]
        merged["cavitation_strength"] = min(float(merged.get("cavitation_strength", 0.3)), 0.35)
        merged["separation_strength"] = min(float(merged.get("separation_strength", 0.4)), 0.45)
        merged["vortex_strength"] = min(float(merged.get("vortex_strength", 0.5)), 0.55)
    elif mode == "平衡":
        merged["cavitation_strength"] = min(float(merged.get("cavitation_strength", 0.45)), 0.65)
        merged["separation_strength"] = min(float(merged.get("separation_strength", 0.55)), 0.75)
    return merged


def current_zone_settings(st_module) -> dict[str, dict[str, Any]]:
    return {
        zone: {
            "enabled": bool(st_module.session_state[f"{zone}_enabled"]),
            "angle_deg": float(st_module.session_state[f"{zone}_angle"]),
            "response": float(st_module.session_state[f"{zone}_response"]),
            "blade_type": spec["blade_type"],
            "drive_type": spec["drive_type"],
        }
        for zone, spec in ZONE_UI.items()
    }


def zones_to_tuple(zones: dict[str, dict[str, Any]]) -> tuple:
    return tuple(
        (
            zone,
            bool(setting["enabled"]),
            round(float(setting["angle_deg"]), 4),
            round(float(setting["response"]), 4),
            str(setting["blade_type"]),
            str(setting["drive_type"]),
        )
        for zone, setting in sorted(zones.items())
    )


def tuple_to_zones(zones_tuple: tuple) -> dict[str, dict[str, Any]]:
    return {
        zone: {
            "enabled": enabled,
            "angle_deg": angle,
            "response": response,
            "blade_type": blade_type,
            "drive_type": drive_type,
        }
        for zone, enabled, angle, response, blade_type, drive_type in zones_tuple
    }


def merge_visual_defaults(visual: dict[str, Any] | None) -> dict[str, Any]:
    merged = deepcopy(VISUAL_DEFAULTS)
    provided = dict(visual or {})
    merged.update(provided)

    if "wake_highlight_strength" not in provided:
        merged["wake_highlight_strength"] = merged.get("wake_strength", VISUAL_DEFAULTS["wake_highlight_strength"])
    if "vortex_animation_strength" not in provided:
        merged["vortex_animation_strength"] = merged.get("vortex_strength", VISUAL_DEFAULTS["vortex_animation_strength"])
    if "blade_animation_strength" not in provided:
        merged["blade_animation_strength"] = 1.0 if merged.get("show_vanes", True) else 0.0
    if "show_separation_zone" not in provided:
        merged["show_separation_zone"] = merged.get("show_separation", VISUAL_DEFAULTS["show_separation_zone"])
    if "show_blade_animation" not in provided:
        merged["show_blade_animation"] = merged.get("show_vanes", VISUAL_DEFAULTS["show_blade_animation"])
    if "show_local_vortices" not in provided:
        merged["show_local_vortices"] = merged.get("show_vortex", VISUAL_DEFAULTS["show_local_vortices"])
    return merged


def _state_value(st_module, key: str) -> Any:
    if key not in st_module.session_state:
        fallback = DEFAULT_STATE.get(key, VISUAL_DEFAULTS.get(key))
        st_module.session_state[key] = deepcopy(fallback)
    return st_module.session_state[key]


def build_current_params(st_module) -> dict[str, Any]:
    zones = current_zone_settings(st_module)
    return {
        "module": st_module.session_state["active_module"],
        "flow": {
            "velocity": float(st_module.session_state["U"]),
            "alpha_deg": float(st_module.session_state["alpha"]),
            "rho": float(st_module.session_state["rho"]),
            "cavitation_threshold_kpa": float(st_module.session_state["cav"]),
            "grid_density": str(st_module.session_state["grid_density"]),
            "fast_preview": bool(st_module.session_state["fast_preview"]),
        },
        "zones": zones,
        "visual": apply_quality_limits({
            "particle_count": int(_state_value(st_module, "particle_count")),
            "animation_speed": float(_state_value(st_module, "animation_speed")),
            "trail_length": int(_state_value(st_module, "trail_length")),
            "emission_strength": float(_state_value(st_module, "emission_strength")),
            "attachment_strength": float(_state_value(st_module, "attachment_strength")),
            "wake_strength": float(_state_value(st_module, "wake_strength")),
            "vortex_strength": float(_state_value(st_module, "vortex_strength")),
            "separation_strength": float(_state_value(st_module, "separation_strength")),
            "cavitation_strength": float(_state_value(st_module, "cavitation_strength")),
            "vane_deploy_angle": float(_state_value(st_module, "vane_deploy_angle")),
            "quality_mode": str(_state_value(st_module, "quality_mode")),
            "pressure_background": bool(_state_value(st_module, "pressure_background")),
            "show_pressure": bool(_state_value(st_module, "show_pressure")),
            "show_particles": bool(_state_value(st_module, "show_particles")),
            "show_vortex": bool(_state_value(st_module, "show_vortex")),
            "show_vanes": bool(_state_value(st_module, "show_vanes")),
            "show_cavitation_bubbles": bool(_state_value(st_module, "show_cavitation_bubbles")),
            "show_separation": bool(_state_value(st_module, "show_separation")),
            "show_zone_labels": bool(_state_value(st_module, "show_zone_labels")),
            "playing": bool(_state_value(st_module, "playing")),
            "wake_highlight_strength": float(_state_value(st_module, "wake_highlight_strength")),
            "speed_colormap_strength": float(_state_value(st_module, "speed_colormap_strength")),
            "vortex_animation_strength": float(_state_value(st_module, "vortex_animation_strength")),
            "blade_animation_strength": float(_state_value(st_module, "blade_animation_strength")),
            "show_separation_zone": bool(_state_value(st_module, "show_separation_zone")),
            "show_blade_animation": bool(_state_value(st_module, "show_blade_animation")),
            "show_wake_highlight": bool(_state_value(st_module, "show_wake_highlight")),
            "show_speed_colormap": bool(_state_value(st_module, "show_speed_colormap")),
            "show_local_vortices": bool(_state_value(st_module, "show_local_vortices")),
            "contour_levels": int(st_module.session_state["contour_levels"]),
            "pressure_auto_range": bool(st_module.session_state["pressure_auto_range"]),
            "pressure_min": float(st_module.session_state["pressure_min"]),
            "pressure_max": float(st_module.session_state["pressure_max"]),
            "pressure_show_foil": bool(st_module.session_state["pressure_show_foil"]),
            "pressure_show_zones": bool(st_module.session_state["pressure_show_zones"]),
            "pressure_show_cavitation": bool(st_module.session_state["pressure_show_cavitation"]),
            "streamline_density": float(st_module.session_state["streamline_density"]),
            "streamline_length": float(st_module.session_state["streamline_length"]),
            "show_vectors": bool(st_module.session_state["show_vectors"]),
            "vector_stride": int(st_module.session_state["vector_stride"]),
            "wake_display_strength": float(st_module.session_state["wake_display_strength"]),
            "risk_alpha": float(st_module.session_state["risk_alpha"]),
            "risk_contour": bool(st_module.session_state["risk_contour"]),
            "risk_lowlight": bool(st_module.session_state["risk_lowlight"]),
            "curve_smoothing": int(st_module.session_state["curve_smoothing"]),
            "curve_show_upper": bool(st_module.session_state["curve_show_upper"]),
            "curve_show_lower": bool(st_module.session_state["curve_show_lower"]),
            "curve_annotate_min": bool(st_module.session_state["curve_annotate_min"]),
            "curve_mark_zones": bool(st_module.session_state["curve_mark_zones"]),
            "curve_x_axis": str(st_module.session_state["curve_x_axis"]),
            "curve_y_unit": str(st_module.session_state["curve_y_unit"]),
        }, bool(st_module.session_state["fast_preview"])),
        "export": {
            "scan_target": str(st_module.session_state["scan_target"]),
            "scan_start": float(st_module.session_state["scan_start"]),
            "scan_end": float(st_module.session_state["scan_end"]),
            "scan_frames": int(st_module.session_state["scan_frames"]),
            "gif_fps": int(st_module.session_state["gif_fps"]),
            "scan_resolution": str(st_module.session_state["scan_resolution"]),
            "scan_show_pressure": bool(st_module.session_state["scan_show_pressure"]),
            "scan_show_particles": bool(st_module.session_state["scan_show_particles"]),
            "scan_show_vortex": bool(st_module.session_state["scan_show_vortex"]),
            "report_title": str(st_module.session_state["report_title"]),
            "report_include_pressure": bool(st_module.session_state["report_include_pressure"]),
            "report_include_velocity": bool(st_module.session_state["report_include_velocity"]),
            "report_include_particle": bool(st_module.session_state["report_include_particle"]),
            "report_include_curve": bool(st_module.session_state["report_include_curve"]),
            "report_include_json": bool(st_module.session_state["report_include_json"]),
            "report_include_principle": bool(st_module.session_state["report_include_principle"]),
            "report_include_disclaimer": bool(st_module.session_state["report_include_disclaimer"]),
        },
    }


def solver_kwargs(params: dict[str, Any], density_override: str | None = None) -> dict[str, Any]:
    flow = params["flow"]
    visual = apply_quality_limits(params.get("visual"), bool(params.get("flow", {}).get("fast_preview", False)))
    return {
        "velocity": flow["velocity"],
        "alpha_deg": flow["alpha_deg"],
        "rho": flow["rho"],
        "cavitation_threshold_kpa": flow["cavitation_threshold_kpa"],
        "grid_density": density_override or flow["grid_density"],
        "zones": params["zones"],
        "show_vortex": visual.get("show_vortex", True),
    }


def exportable_extra(params: dict[str, Any]) -> dict[str, Any]:
    visual = apply_quality_limits(params.get("visual"), bool(params.get("flow", {}).get("fast_preview", False)))
    return {
        "module": params["module"],
        "particle_count": visual.get("particle_count", 600),
        "animation_speed": visual.get("animation_speed", 1.0),
        "trail_length": visual.get("trail_length", 3),
        "emission_strength": visual.get("emission_strength", 0.80),
        "attachment_strength": visual.get("attachment_strength", 0.78),
        "wake_strength": visual.get("wake_strength", 0.80),
        "vortex_strength": visual.get("vortex_strength", 0.50),
        "separation_strength": visual.get("separation_strength", 0.4),
        "cavitation_strength": visual.get("cavitation_strength", 0.3),
        "vane_deploy_angle": visual.get("vane_deploy_angle", 24.0),
        "quality_mode": visual.get("quality_mode", "流畅"),
        "pressure_background": visual.get("pressure_background", True),
        "wake_highlight_strength": visual.get("wake_highlight_strength", 1.0),
        "speed_colormap_strength": visual.get("speed_colormap_strength", 1.0),
        "vortex_animation_strength": visual.get("vortex_animation_strength", 0.8),
        "blade_animation_strength": visual.get("blade_animation_strength", 1.0),
    }
