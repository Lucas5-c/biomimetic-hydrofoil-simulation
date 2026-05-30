from __future__ import annotations

from dataclasses import dataclass


ZONE_RANGES = {
    "A": (0.18, 0.35),
    "B": (0.35, 0.65),
    "C": (0.65, 0.82),
}

ZONE_LABELS = {
    "A": "A区 前缘调节区",
    "B": "B区 中弦主控区",
    "C": "C区 后缘整流区",
}

ZONE_COLORS = {
    "A": "#00B7FF",
    "B": "#FFD166",
    "C": "#57CC99",
}

ZONE_BLADE_TYPES = {
    "A": "低矮楔形/三角鳍形",
    "B": "宽翻板/小翼型",
    "C": "后掠整流鳍/梳齿叶片",
}

ZONE_DRIVE_TYPES = {
    "A": "柔性铰链 + 微驱动器",
    "B": "TSAM + 连杆 + 微弹簧复位",
    "C": "微流体腔/膜片 + 推杆",
}


@dataclass(frozen=True)
class ZoneSetting:
    enabled: bool
    angle_deg: float
    response: float
    blade_type: str
    drive_type: str


def default_zone_settings() -> dict[str, ZoneSetting]:
    return {
        "A": ZoneSetting(True, 8.0, 0.55, ZONE_BLADE_TYPES["A"], ZONE_DRIVE_TYPES["A"]),
        "B": ZoneSetting(True, 15.0, 0.70, ZONE_BLADE_TYPES["B"], ZONE_DRIVE_TYPES["B"]),
        "C": ZoneSetting(True, 10.0, 0.50, ZONE_BLADE_TYPES["C"], ZONE_DRIVE_TYPES["C"]),
    }


def normalize_zone_settings(raw: dict | None) -> dict[str, ZoneSetting]:
    defaults = default_zone_settings()
    if not raw:
        return defaults
    normalized: dict[str, ZoneSetting] = {}
    for zone, fallback in defaults.items():
        value = raw.get(zone, fallback)
        if isinstance(value, ZoneSetting):
            normalized[zone] = value
        else:
            normalized[zone] = ZoneSetting(
                enabled=bool(value.get("enabled", fallback.enabled)),
                angle_deg=float(value.get("angle_deg", fallback.angle_deg)),
                response=float(value.get("response", fallback.response)),
                blade_type=str(value.get("blade_type", fallback.blade_type)),
                drive_type=str(value.get("drive_type", fallback.drive_type)),
            )
    return normalized


def zone_effect_strength(zone: str, setting: ZoneSetting) -> float:
    if not setting.enabled:
        return 0.0
    max_angle = {"A": 15.0, "B": 30.0, "C": 18.0}[zone]
    return max(0.0, min(1.25, setting.angle_deg / max_angle * setting.response))


def preset_conditions() -> dict[str, dict]:
    return {
        "低速巡航": {
            "U": 5.0,
            "alpha": 2.0,
            "particles": 650,
            "zones": {
                "A": ZoneSetting(True, 4.0, 0.35, ZONE_BLADE_TYPES["A"], ZONE_DRIVE_TYPES["A"]),
                "B": ZoneSetting(False, 0.0, 0.25, ZONE_BLADE_TYPES["B"], ZONE_DRIVE_TYPES["B"]),
                "C": ZoneSetting(True, 6.0, 0.45, ZONE_BLADE_TYPES["C"], ZONE_DRIVE_TYPES["C"]),
            },
        },
        "高攻角防失速": {
            "U": 8.0,
            "alpha": 10.0,
            "particles": 900,
            "zones": {
                "A": ZoneSetting(True, 12.0, 0.80, ZONE_BLADE_TYPES["A"], ZONE_DRIVE_TYPES["A"]),
                "B": ZoneSetting(True, 28.0, 0.90, ZONE_BLADE_TYPES["B"], ZONE_DRIVE_TYPES["B"]),
                "C": ZoneSetting(True, 12.0, 0.60, ZONE_BLADE_TYPES["C"], ZONE_DRIVE_TYPES["C"]),
            },
        },
        "空化抑制": {
            "U": 14.0,
            "alpha": 6.0,
            "particles": 900,
            "zones": {
                "A": ZoneSetting(True, 8.0, 0.60, ZONE_BLADE_TYPES["A"], ZONE_DRIVE_TYPES["A"]),
                "B": ZoneSetting(True, 24.0, 1.00, ZONE_BLADE_TYPES["B"], ZONE_DRIVE_TYPES["B"]),
                "C": ZoneSetting(True, 10.0, 0.55, ZONE_BLADE_TYPES["C"], ZONE_DRIVE_TYPES["C"]),
            },
        },
        "后缘整流": {
            "U": 11.0,
            "alpha": 3.0,
            "particles": 850,
            "zones": {
                "A": ZoneSetting(False, 0.0, 0.30, ZONE_BLADE_TYPES["A"], ZONE_DRIVE_TYPES["A"]),
                "B": ZoneSetting(True, 8.0, 0.35, ZONE_BLADE_TYPES["B"], ZONE_DRIVE_TYPES["B"]),
                "C": ZoneSetting(True, 16.0, 0.95, ZONE_BLADE_TYPES["C"], ZONE_DRIVE_TYPES["C"]),
            },
        },
        "三分区协同控制": {
            "U": 10.0,
            "alpha": 7.0,
            "particles": 1000,
            "zones": {
                "A": ZoneSetting(True, 10.0, 0.75, ZONE_BLADE_TYPES["A"], ZONE_DRIVE_TYPES["A"]),
                "B": ZoneSetting(True, 22.0, 0.85, ZONE_BLADE_TYPES["B"], ZONE_DRIVE_TYPES["B"]),
                "C": ZoneSetting(True, 14.0, 0.75, ZONE_BLADE_TYPES["C"], ZONE_DRIVE_TYPES["C"]),
            },
        },
        "全部收起": {
            "U": 8.0,
            "alpha": 4.0,
            "particles": 700,
            "zones": {
                "A": ZoneSetting(False, 0.0, 0.0, ZONE_BLADE_TYPES["A"], ZONE_DRIVE_TYPES["A"]),
                "B": ZoneSetting(False, 0.0, 0.0, ZONE_BLADE_TYPES["B"], ZONE_DRIVE_TYPES["B"]),
                "C": ZoneSetting(False, 0.0, 0.0, ZONE_BLADE_TYPES["C"], ZONE_DRIVE_TYPES["C"]),
            },
        },
        "全部展开演示": {
            "U": 12.0,
            "alpha": 7.0,
            "particles": 1100,
            "zones": {
                "A": ZoneSetting(True, 15.0, 1.00, ZONE_BLADE_TYPES["A"], ZONE_DRIVE_TYPES["A"]),
                "B": ZoneSetting(True, 30.0, 1.00, ZONE_BLADE_TYPES["B"], ZONE_DRIVE_TYPES["B"]),
                "C": ZoneSetting(True, 18.0, 1.00, ZONE_BLADE_TYPES["C"], ZONE_DRIVE_TYPES["C"]),
            },
        },
    }


def recommend_control_strategy(stats: dict, alpha_deg: float, cav_threshold_kpa: float) -> str:
    cav_pct = float(stats.get("overall", {}).get("cavitation_percent", 0.0))
    min_pressure = float(stats.get("overall", {}).get("min_pressure_kpa", 0.0))
    c_avg = float(stats.get("C", {}).get("avg_pressure_kpa", 0.0))
    b_avg = float(stats.get("B", {}).get("avg_pressure_kpa", 0.0))
    if cav_pct > 8.0 or min_pressure < cav_threshold_kpa:
        return "建议增强 B区主控叶片，并配合 A区预扰动，抬升上表面极端低压区。"
    if alpha_deg >= 8.0:
        return "建议提高 A区快速预扰动和 B区主控角度，降低高攻角分离趋势。"
    if c_avg < b_avg - 3.0:
        return "建议提高 C区整流强度，稳定后缘尾迹并改善压力恢复。"
    return "当前流场较平稳，可维持轻度 A/C 控制并降低 B区能耗。"
