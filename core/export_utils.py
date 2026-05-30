from __future__ import annotations

import csv
import json
from datetime import datetime
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

from .flow_solver_lite import simulate_flow
from .hydrofoil_geometry import generate_naca0012
from .particle_flow_model import particle_trace_samples
from .zone_control import ZONE_COLORS, ZONE_LABELS, ZONE_RANGES


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "outputs"
SOLVER_KEYS = {
    "velocity",
    "alpha_deg",
    "rho",
    "cavitation_threshold_kpa",
    "grid_density",
    "zones",
    "show_vortex",
}

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def timestamped_name(prefix: str, suffix: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return ensure_output_dir() / f"{prefix}_{stamp}.{suffix}"


def _solver_only_params(params: dict) -> dict:
    return {key: value for key, value in params.items() if key in SOLVER_KEYS}


def _field_range(field: np.ndarray, low: float = 2.0, high: float = 98.0) -> tuple[float, float]:
    finite = field[np.isfinite(field)]
    if finite.size == 0:
        return -1.0, 1.0
    return float(np.nanpercentile(finite, low)), float(np.nanpercentile(finite, high))


def _dark_figure(figsize: tuple[float, float] = (9.8, 5.2)) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize, dpi=135)
    fig.patch.set_facecolor("#0E1117")
    ax.set_facecolor("#0E1117")
    return fig, ax


def _style_axes(ax, result: dict, title: str) -> None:
    geom = result["geometry"]
    ax.plot(geom.outline_x, geom.outline_y, color="#F5F7FA", linewidth=1.8)
    for zone, (x0, x1) in ZONE_RANGES.items():
        ax.axvspan(x0, x1, color=ZONE_COLORS[zone], alpha=0.10)
        ax.text((x0 + x1) / 2, 0.31, zone, color=ZONE_COLORS[zone], ha="center", va="top", fontsize=11, weight="bold")
    ax.set_title(title, color="#F5F7FA")
    ax.set_xlabel("x/c", color="#D6DEE8")
    ax.set_ylabel("y/c", color="#D6DEE8")
    ax.set_xlim(-0.14, 1.24)
    ax.set_ylim(-0.34, 0.34)
    ax.set_aspect("equal", adjustable="box")
    ax.tick_params(colors="#D6DEE8")
    ax.grid(True, color="#32465A", alpha=0.35, linewidth=0.6)


def _add_cavitation(ax, result: dict) -> None:
    cav = result["cavitation_mask"].astype(float)
    if np.nanmax(cav) > 0:
        ax.contour(result["X"], result["Y"], cav, levels=[0.5], colors="#FF4DCA", linewidths=1.2)
        ax.text(0.01, 0.255, "潜在空化风险区", color="#FF4DCA", fontsize=9, weight="bold")


def create_pressure_figure(result: dict) -> plt.Figure:
    fig, ax = _dark_figure()
    vmin, vmax = _field_range(result["pressure_kpa"], 3.0, 97.0)
    cf = ax.contourf(result["X"], result["Y"], result["pressure_kpa"], levels=np.linspace(vmin, vmax, 32), cmap="turbo", extend="both")
    _add_cavitation(ax, result)
    _style_axes(ax, result, "压力云图（相对压力 kPa）")
    cbar = fig.colorbar(cf, ax=ax, label="kPa", shrink=0.84)
    cbar.ax.yaxis.label.set_color("#D6DEE8")
    cbar.ax.tick_params(colors="#D6DEE8")
    fig.tight_layout()
    return fig


def create_velocity_figure(result: dict) -> plt.Figure:
    fig, ax = _dark_figure()
    _, vmax = _field_range(result["speed"], 1.0, 98.0)
    cf = ax.contourf(result["X"], result["Y"], result["speed"], levels=30, cmap="viridis", vmin=0.0, vmax=vmax)
    _style_axes(ax, result, "速度场（m/s）")
    cbar = fig.colorbar(cf, ax=ax, label="m/s", shrink=0.84)
    cbar.ax.yaxis.label.set_color("#D6DEE8")
    cbar.ax.tick_params(colors="#D6DEE8")
    fig.tight_layout()
    return fig


def create_streamline_figure(result: dict) -> plt.Figure:
    fig, ax = _dark_figure()
    _, vmax = _field_range(result["speed"], 1.0, 98.0)
    ax.contourf(result["X"], result["Y"], result["speed"], levels=24, cmap="magma", vmin=0.0, vmax=vmax, alpha=0.72)
    ax.streamplot(
        result["X"][0, :],
        result["Y"][:, 0],
        np.nan_to_num(result["Vx"], nan=0.0),
        np.nan_to_num(result["Vy"], nan=0.0),
        density=1.45,
        color="#EAF6FF",
        linewidth=0.62,
        arrowsize=0.70,
    )
    _style_axes(ax, result, "速度场与流线")
    fig.tight_layout()
    return fig


def create_pressure_streamline_figure(result: dict) -> plt.Figure:
    fig, ax = _dark_figure()
    vmin, vmax = _field_range(result["pressure_kpa"], 3.0, 97.0)
    cf = ax.contourf(result["X"], result["Y"], result["pressure_kpa"], levels=np.linspace(vmin, vmax, 30), cmap="turbo", alpha=0.88)
    ax.streamplot(
        result["X"][0, :],
        result["Y"][:, 0],
        np.nan_to_num(result["Vx"], nan=0.0),
        np.nan_to_num(result["Vy"], nan=0.0),
        density=1.10,
        color="white",
        linewidth=0.45,
        arrowsize=0.55,
    )
    _add_cavitation(ax, result)
    _style_axes(ax, result, "压力 + 流线叠加")
    cbar = fig.colorbar(cf, ax=ax, label="kPa", shrink=0.84)
    cbar.ax.yaxis.label.set_color("#D6DEE8")
    cbar.ax.tick_params(colors="#D6DEE8")
    fig.tight_layout()
    return fig


def create_surface_pressure_figure(result: dict) -> plt.Figure:
    fig, ax = _dark_figure(figsize=(9.6, 4.6))
    ax.plot(result["surface_x"], result["pressure_upper_kpa"], label="上表面压力", color="#00B7FF", linewidth=2.1)
    ax.plot(result["surface_x"], result["pressure_lower_kpa"], label="下表面压力", color="#FF6B6B", linewidth=2.1)
    ymin, ymax = ax.get_ylim()
    for zone, (x0, x1) in ZONE_RANGES.items():
        ax.axvspan(x0, x1, color=ZONE_COLORS[zone], alpha=0.11)
        ax.text((x0 + x1) / 2, ymax, zone, ha="center", va="top", color=ZONE_COLORS[zone], weight="bold")
    min_x, min_p = result["min_upper_pressure_point"]
    ax.scatter([min_x], [min_p], color="#FF4DCA", zorder=4)
    ax.annotate(f"最低点 {min_p:.1f} kPa", xy=(min_x, min_p), xytext=(min_x + 0.04, min_p + 6.0), color="#F5F7FA", arrowprops={"arrowstyle": "->", "color": "#FF4DCA"})
    ax.set_title("上下表面压力分布", color="#F5F7FA")
    ax.set_xlabel("弦向位置 x/c", color="#D6DEE8")
    ax.set_ylabel("相对压力 kPa", color="#D6DEE8")
    ax.grid(True, color="#32465A", alpha=0.35)
    ax.tick_params(colors="#D6DEE8")
    legend = ax.legend(loc="best")
    for text in legend.get_texts():
        text.set_color("#111827")
    fig.tight_layout()
    return fig


def save_figure(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190, bbox_inches="tight", facecolor=fig.get_facecolor())
    return path


def export_surface_pressure_csv(result: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x_over_c", "upper_pressure_kpa", "lower_pressure_kpa"])
        for x_value, upper, lower in zip(result["surface_x"], result["pressure_upper_kpa"], result["pressure_lower_kpa"]):
            writer.writerow([float(x_value), float(upper), float(lower)])
    return path


def export_zone_pressure_csv(result: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["zone", "label", "avg_pressure_kpa", "min_pressure_kpa", "max_pressure_kpa", "cavitation_percent"])
        for zone in ("A", "B", "C"):
            stats = result["zone_stats"][zone]
            writer.writerow([zone, ZONE_LABELS[zone], stats["avg_pressure_kpa"], stats["min_pressure_kpa"], stats["max_pressure_kpa"], stats["cavitation_percent"]])
    return path


def result_to_exportable_params(result: dict, extra: dict | None = None) -> dict:
    zones = {
        zone: {
            "enabled": setting.enabled,
            "angle_deg": setting.angle_deg,
            "response": setting.response,
            "blade_type": setting.blade_type,
            "drive_type": setting.drive_type,
        }
        for zone, setting in result["zone_settings"].items()
    }
    payload = {**result["inputs"], "zones": zones, "zone_labels": ZONE_LABELS}
    if extra:
        payload.update(extra)
    return payload


def export_params_json(params: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(params, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_simulation_report(result: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    stats = result["zone_stats"]
    params = result_to_exportable_params(result)
    lines = [
        "# 仿生分区主动水翼综合仿真报告",
        "",
        f"- 生成时间：`{datetime.now().isoformat(timespec='seconds')}`",
        "- 模型定位：轻量化粒子动画 + 简化压力/速度场，不是高精度 CFD。",
        "",
        "## 当前参数",
        "",
        f"- 流速：`{params['velocity']:.2f} m/s`",
        f"- 攻角：`{params['alpha_deg']:.2f} deg`",
        f"- 水密度：`{params['rho']:.1f} kg/m^3`",
        f"- 空化阈值：`{params['cavitation_threshold_kpa']:.1f} kPa`",
        f"- 网格密度：`{params['grid_density']}`",
        "",
        "## 分区统计",
        "",
        "| 分区 | 平均压力 kPa | 最低压力 kPa | 空化占比 % |",
        "|---|---:|---:|---:|",
    ]
    for zone in ("A", "B", "C"):
        zone_stats = stats[zone]
        lines.append(f"| {ZONE_LABELS[zone]} | {zone_stats['avg_pressure_kpa']:.2f} | {zone_stats['min_pressure_kpa']:.2f} | {zone_stats['cavitation_percent']:.2f} |")
    lines.extend(
        [
            "",
            "## 总体结果",
            "",
            f"- 动压 q：`{stats['overall']['dynamic_pressure_kpa']:.2f} kPa`",
            f"- 最小压力：`{stats['overall']['min_pressure_kpa']:.2f} kPa`",
            f"- 最大压力：`{stats['overall']['max_pressure_kpa']:.2f} kPa`",
            f"- 空化风险面积占比：`{stats['overall']['cavitation_percent']:.2f}%`",
            f"- 控制建议：{stats['recommendation']}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _world_to_px(x: float, y: float, width: int, height: int) -> tuple[int, int]:
    return int((x + 0.18) / 1.50 * width), int((0.40 - y) / 0.80 * height)


def _draw_particle_frame(traces: np.ndarray, frame_index: int, width: int, height: int, alpha_deg: float) -> Image.Image:
    image = Image.new("RGB", (width, height), "#0E1117")
    draw = ImageDraw.Draw(image, "RGBA")
    for zone, (x0, x1) in ZONE_RANGES.items():
        p0 = _world_to_px(x0, 0.36, width, height)
        p1 = _world_to_px(x1, -0.36, width, height)
        color = ZONE_COLORS[zone].lstrip("#")
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        draw.rectangle([p0, p1], fill=(*rgb, 28))
    geom = generate_naca0012(alpha_deg=alpha_deg)
    foil = [_world_to_px(float(x), float(y), width, height) for x, y in zip(geom.outline_x, geom.outline_y)]
    draw.polygon(foil, fill=(245, 247, 250, 225), outline=(20, 28, 38, 255))
    start = max(0, frame_index - 8)
    for particle_index in range(traces.shape[1]):
        tail = traces[start : frame_index + 1, particle_index, :]
        for idx in range(1, len(tail)):
            fade = int(30 + 180 * idx / max(1, len(tail)))
            p0 = _world_to_px(float(tail[idx - 1, 0]), float(tail[idx - 1, 1]), width, height)
            p1 = _world_to_px(float(tail[idx, 0]), float(tail[idx, 1]), width, height)
            draw.line([p0, p1], fill=(0, 183, 255, fade), width=2)
    return image


def generate_particle_snapshot_png(params: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    traces = particle_trace_samples(
        velocity=float(params["velocity"]),
        alpha_deg=float(params["alpha_deg"]),
        zones=params["zones"],
        particle_count=min(int(params.get("particle_count", 700)), 420),
        steps=24,
    )
    image = _draw_particle_frame(traces, traces.shape[0] - 1, 900, 500, float(params["alpha_deg"]))
    image.save(path)
    return path


def generate_particle_animation_gif(params: dict, path: Path, frames: int = 36) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    traces = particle_trace_samples(
        velocity=float(params["velocity"]),
        alpha_deg=float(params["alpha_deg"]),
        zones=params["zones"],
        particle_count=min(int(params.get("particle_count", 700)), 420),
        steps=frames,
    )
    images = [_draw_particle_frame(traces, i, 900, 500, float(params["alpha_deg"])) for i in range(frames)]
    images[0].save(path, save_all=True, append_images=images[1:], duration=70, loop=0)
    return path


def fig_to_frame(fig: plt.Figure) -> Image.Image:
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=115, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer).convert("P", palette=Image.Palette.ADAPTIVE)


def generate_speed_sweep_gif(base_params: dict, path: Path, speeds: list[float] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if speeds is None:
        speeds = list(np.linspace(2.0, 20.0, 14))
    frames: list[Image.Image] = []
    for speed in speeds:
        params = dict(base_params)
        params["velocity"] = float(speed)
        result = simulate_flow(**_solver_only_params(params))
        fig = create_pressure_streamline_figure(result)
        fig.axes[0].set_title(f"流速扫描：U = {speed:.1f} m/s", color="#F5F7FA")
        frames.append(fig_to_frame(fig))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=320, loop=0)
    return path


def generate_zone_deployment_gif(base_params: dict, path: Path, steps: int = 14) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    target_zones = base_params["zones"]
    frames: list[Image.Image] = []
    for ratio in np.linspace(0.0, 1.0, steps):
        zones = {}
        for zone, setting in target_zones.items():
            zones[zone] = {**setting, "angle_deg": float(setting.get("angle_deg", 0.0)) * float(ratio)}
        params = dict(base_params)
        params["zones"] = zones
        result = simulate_flow(**_solver_only_params(params))
        fig = create_pressure_figure(result)
        fig.axes[0].set_title(f"分区展开：{ratio * 100:.0f}%", color="#F5F7FA")
        frames.append(fig_to_frame(fig))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=320, loop=0)
    return path
