from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

try:
    import streamlit as st
except ModuleNotFoundError:
    print("缺少 streamlit。请先运行 python -m pip install -r requirements.txt")
    raise SystemExit(1)

import matplotlib.pyplot as plt
import numpy as np

from components.flow_canvas import render_flow_canvas
from core.export_utils import (
    OUTPUT_DIR,
    create_pressure_figure,
    create_streamline_figure,
    create_surface_pressure_figure,
    create_velocity_figure,
    export_params_json,
    export_simulation_report,
    export_surface_pressure_csv,
    export_zone_pressure_csv,
    generate_particle_animation_gif,
    generate_particle_snapshot_png,
    generate_speed_sweep_gif,
    generate_zone_deployment_gif,
    result_to_exportable_params,
    save_figure,
    timestamped_name,
)
from core.flow_solver_lite import prepare_static_fields, simulate_flow
from core.layout import inject_three_column_layout_css, module_title, panel_marker, section_title
from core.params import (
    build_current_params,
    exportable_extra,
    init_session_state,
    solver_kwargs,
    tuple_to_zones,
    zones_to_tuple,
)
from core.particle_flow_model import canvas_payload
from core.ui_panels import record_export, render_left_panel, render_right_panel
from core.zone_control import ZONE_COLORS, ZONE_RANGES


PLOTLY_AVAILABLE = importlib.util.find_spec("plotly") is not None
if PLOTLY_AVAILABLE:
    import plotly.graph_objects as go


def rerun_streamlit() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


@st.cache_data(show_spinner=False)
def cached_static_fields(grid_density: str, alpha_deg: float) -> dict:
    return prepare_static_fields(grid_density, alpha_deg)


@st.cache_data(show_spinner=False)
def cached_simulation(
    velocity: float,
    alpha_deg: float,
    rho: float,
    cavitation_threshold_kpa: float,
    grid_density: str,
    zones_tuple: tuple,
    show_vortex: bool,
) -> dict:
    static = cached_static_fields(grid_density, alpha_deg)
    return simulate_flow(
        velocity=velocity,
        alpha_deg=alpha_deg,
        rho=rho,
        cavitation_threshold_kpa=cavitation_threshold_kpa,
        grid_density=grid_density,
        zones=tuple_to_zones(zones_tuple),
        show_vortex=show_vortex,
        static=static,
    )


def compute_result(params: dict[str, Any]) -> tuple[dict, str]:
    density = "低" if params["flow"]["fast_preview"] else params["flow"]["grid_density"]
    kwargs = solver_kwargs(params, density)
    result = cached_simulation(
        kwargs["velocity"],
        kwargs["alpha_deg"],
        kwargs["rho"],
        kwargs["cavitation_threshold_kpa"],
        kwargs["grid_density"],
        zones_to_tuple(kwargs["zones"]),
        kwargs["show_vortex"],
    )
    return result, density


def export_params(result: dict, params: dict[str, Any]) -> dict[str, Any]:
    payload = result_to_exportable_params(result, exportable_extra(params))
    payload["ui_params"] = params
    return payload


def canvas_export_params(result: dict, params: dict[str, Any]) -> dict[str, Any]:
    payload = export_params(result, params)
    payload["particle_count"] = params["visual"]["particle_count"]
    return payload


def open_output_folder() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    st.info("云端版本不会打开服务器文件夹。导出文件保存在当前会话目录中，建议生成后立即下载。")


def notify_export(path: Path) -> None:
    record_export(path)
    st.success(f"已生成：{path.name}。云端导出文件不保证长期保存，请及时下载。")


def render_download(path: Path, label: str | None = None) -> None:
    if not path.exists():
        return
    st.download_button(
        label=label or f"下载 {path.name}",
        data=path.read_bytes(),
        file_name=path.name,
        mime=download_mime(path),
        use_container_width=True,
    )


def download_mime(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".png": "image/png",
        ".gif": "image/gif",
        ".csv": "text/csv",
        ".json": "application/json",
        ".md": "text/markdown",
        ".txt": "text/plain",
    }.get(suffix, "application/octet-stream")


def export_field_csv(result: dict, field_name: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x", "y", field_name])
        field = result[field_name]
        for x, y, value in zip(result["X"].ravel(), result["Y"].ravel(), field.ravel()):
            if np.isfinite(value):
                writer.writerow([float(x), float(y), float(value)])
    return path


def export_risk_json(result: dict, path: Path) -> Path:
    stats = result["zone_stats"]
    risk = {
        "threshold_kpa": result["inputs"]["cavitation_threshold_kpa"],
        "overall_cavitation_percent": stats["overall"]["cavitation_percent"],
        "overall_min_pressure_kpa": stats["overall"]["min_pressure_kpa"],
        "zones": {zone: stats[zone] for zone in ("A", "B", "C")},
    }
    path.write_text(json.dumps(risk, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_minimum_pressure_json(result: dict, path: Path) -> Path:
    min_x, min_p = result["min_upper_pressure_point"]
    payload = {
        "surface": "upper",
        "x_over_c": min_x,
        "pressure_kpa": min_p,
        "note": "The value is produced by a lightweight visualization model, not high-fidelity CFD.",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def plotly_heatmap(result: dict, field: str, title: str, colorscale: str, colorbar_title: str):
    if not PLOTLY_AVAILABLE:
        return None
    fig = go.Figure()
    fig.add_trace(
        go.Heatmap(
            x=result["X"][0, :],
            y=result["Y"][:, 0],
            z=result[field],
            colorscale=colorscale,
            colorbar={"title": colorbar_title},
            zsmooth="best",
        )
    )
    geom = result["geometry"]
    fig.add_trace(
        go.Scatter(
            x=geom.outline_x,
            y=geom.outline_y,
            mode="lines",
            line={"color": "white", "width": 2},
            name="水翼轮廓",
        )
    )
    for zone, (x0, x1) in ZONE_RANGES.items():
        fig.add_vrect(x0=x0, x1=x1, fillcolor=ZONE_COLORS[zone], opacity=0.12, line_width=0)
        fig.add_annotation(x=(x0 + x1) / 2, y=0.30, text=zone, showarrow=False, font={"color": "white", "size": 13})
    fig.update_layout(
        title=title,
        height=610,
        margin={"l": 10, "r": 10, "t": 48, "b": 10},
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font={"color": "#F5F7FA"},
        xaxis={"range": [-0.15, 1.24], "title": "x/c", "gridcolor": "#26384B"},
        yaxis={"range": [-0.34, 0.34], "title": "y/c", "scaleanchor": "x", "scaleratio": 1, "gridcolor": "#26384B"},
    )
    return fig


def create_cavitation_figure(result: dict, alpha: float = 0.45) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10.4, 5.8), dpi=140)
    fig.patch.set_facecolor("#0E1117")
    ax.set_facecolor("#0E1117")
    pressure = result["pressure_kpa"]
    vmin, vmax = np.nanpercentile(pressure, [3, 97])
    ax.contourf(result["X"], result["Y"], pressure, levels=34, cmap="turbo", vmin=vmin, vmax=vmax, alpha=0.72)
    cav = result["cavitation_mask"].astype(float)
    if np.nanmax(cav) > 0:
        ax.contourf(result["X"], result["Y"], cav, levels=[0.5, 1.0], colors=["#FF4DCA"], alpha=alpha)
        ax.contour(result["X"], result["Y"], cav, levels=[0.5], colors="#FFFFFF", linewidths=0.9)
    geom = result["geometry"]
    ax.plot(geom.outline_x, geom.outline_y, color="#F5F7FA", linewidth=1.8)
    for zone, (x0, x1) in ZONE_RANGES.items():
        ax.axvspan(x0, x1, color=ZONE_COLORS[zone], alpha=0.08)
        ax.text((x0 + x1) / 2, 0.31, zone, ha="center", va="top", color=ZONE_COLORS[zone], weight="bold")
    ax.set_title("空化风险高亮图", color="#F5F7FA")
    ax.set_xlabel("x/c", color="#D6DEE8")
    ax.set_ylabel("y/c", color="#D6DEE8")
    ax.set_xlim(-0.14, 1.24)
    ax.set_ylim(-0.34, 0.34)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color="#32465A", alpha=0.35)
    ax.tick_params(colors="#D6DEE8")
    fig.tight_layout()
    return fig


def create_cavitation_stats_figure(result: dict) -> plt.Figure:
    stats = result["zone_stats"]
    fig, ax = plt.subplots(figsize=(8.8, 3.6), dpi=135)
    fig.patch.set_facecolor("#0E1117")
    ax.set_facecolor("#0E1117")
    zones = ["A", "B", "C"]
    values = [stats[z]["cavitation_percent"] for z in zones]
    ax.bar(zones, values, color=[ZONE_COLORS[z] for z in zones], alpha=0.82)
    ax.set_title("A/B/C 分区空化风险占比", color="#F5F7FA")
    ax.set_ylabel("风险面积占比 (%)", color="#D6DEE8")
    ax.tick_params(colors="#D6DEE8")
    ax.grid(axis="y", color="#32465A", alpha=0.35)
    fig.tight_layout()
    return fig


def smooth_curve(values: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return values
    kernel = np.ones(window) / window
    return np.convolve(values, kernel, mode="same")


def create_module_surface_curve_figure(result: dict, params: dict[str, Any]) -> plt.Figure:
    visual = params["visual"]
    fig, ax = plt.subplots(figsize=(10.2, 4.8), dpi=140)
    fig.patch.set_facecolor("#0E1117")
    ax.set_facecolor("#0E1117")
    x = result["surface_x"].copy()
    upper = smooth_curve(result["pressure_upper_kpa"], visual["curve_smoothing"])
    lower = smooth_curve(result["pressure_lower_kpa"], visual["curve_smoothing"])
    if visual["curve_x_axis"] == "mm":
        x = x * 1000.0
        x_label = "弦向位置 (mm，假定弦长 1000 mm)"
    else:
        x_label = "弦向位置 x/c"
    scale = 1000.0 if visual["curve_y_unit"] == "Pa" else 1.0
    y_label = f"相对压力 ({visual['curve_y_unit']})"
    if visual["curve_show_upper"]:
        ax.plot(x, upper * scale, color="#00B7FF", linewidth=2.1, label="上表面")
    if visual["curve_show_lower"]:
        ax.plot(x, lower * scale, color="#FF6B6B", linewidth=2.1, label="下表面")
    if visual["curve_mark_zones"]:
        for zone, (x0, x1) in ZONE_RANGES.items():
            z0, z1 = (x0 * 1000.0, x1 * 1000.0) if visual["curve_x_axis"] == "mm" else (x0, x1)
            ax.axvspan(z0, z1, color=ZONE_COLORS[zone], alpha=0.11)
    if visual["curve_annotate_min"]:
        idx = int(np.nanargmin(upper))
        ax.scatter([x[idx]], [upper[idx] * scale], color="#FF4DCA", zorder=4)
        ax.annotate(
            f"最低 {upper[idx] * scale:.1f}",
            xy=(x[idx], upper[idx] * scale),
            xytext=(x[idx] + (28 if visual["curve_x_axis"] == "mm" else 0.04), upper[idx] * scale + 6 * scale),
            color="#F5F7FA",
            arrowprops={"arrowstyle": "->", "color": "#FF4DCA"},
        )
    ax.set_title("上下表面压力曲线", color="#F5F7FA")
    ax.set_xlabel(x_label, color="#D6DEE8")
    ax.set_ylabel(y_label, color="#D6DEE8")
    ax.grid(True, color="#32465A", alpha=0.35)
    ax.tick_params(colors="#D6DEE8")
    legend = ax.legend(loc="best")
    for text in legend.get_texts():
        text.set_color("#111827")
    fig.tight_layout()
    return fig


def render_canvas_module(result: dict, params: dict[str, Any]) -> None:
    visual = params["visual"]
    module_title("动态水流粒子", "Canvas 实时渲染尾迹辉光、速度色带、局部涡旋、叶片展开、分离区与空化气泡")
    payload = canvas_payload(
        velocity=params["flow"]["velocity"],
        alpha_deg=params["flow"]["alpha_deg"],
        rho=params["flow"]["rho"],
        cavitation_threshold_kpa=params["flow"]["cavitation_threshold_kpa"],
        particle_count=visual["particle_count"] if visual["show_particles"] else 0,
        animation_speed=visual["animation_speed"],
        grid_density=params["flow"]["grid_density"],
        zones=params["zones"],
        show_pressure=visual["show_pressure"],
        show_particles=visual["show_particles"],
        show_vortex=visual["show_vortex"],
        show_vanes=visual["show_vanes"],
        playing=visual["playing"],
        show_zone_labels=visual["show_zone_labels"],
        trail_length=visual["trail_length"],
        emission_strength=visual["emission_strength"],
        attachment_strength=visual["attachment_strength"],
        wake_strength=visual["wake_strength"],
        vortex_strength=visual["vortex_strength"],
        separation_strength=visual["separation_strength"],
        cavitation_strength=visual["cavitation_strength"],
        vane_deploy_angle=visual["vane_deploy_angle"],
        quality_mode=visual["quality_mode"],
        show_cavitation_bubbles=visual["show_cavitation_bubbles"],
        show_separation=visual["show_separation"],
    )
    render_flow_canvas(payload, height=660)
    render_canvas_exports(result, params)
    if st.session_state.get("last_gif_path"):
        gif_path = Path(st.session_state["last_gif_path"])
        if gif_path.exists():
            st.image(str(gif_path), caption=gif_path.name, use_container_width=True)


def render_canvas_exports(result: dict, params: dict[str, Any]) -> None:
    st.markdown('<div class="hydrofoil-export-strip"><div class="hydrofoil-export-title">动态粒子导出</div></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    export_payload = canvas_export_params(result, params)
    if c1.button("导出当前截图 PNG", use_container_width=True):
        path = generate_particle_snapshot_png(export_payload, timestamped_name("canvas_snapshot", "png"))
        notify_export(path)
        render_download(path)
    if c2.button("生成水流粒子 GIF", use_container_width=True):
        with st.spinner("正在生成水流粒子 GIF..."):
            path = generate_particle_animation_gif(export_payload, timestamped_name("particle_flow", "gif"), frames=42)
        st.session_state["last_gif_path"] = str(path)
        notify_export(path)
        render_download(path)
    if c3.button("导出当前参数 JSON", use_container_width=True):
        path = export_params_json(export_payload, timestamped_name("particle_params", "json"))
        notify_export(path)
        render_download(path)
    if c4.button("云端导出说明", use_container_width=True):
        open_output_folder()


def render_pressure_module(result: dict, params: dict[str, Any]) -> None:
    module_title("压力云图", "简化势流扰动 + 伯努利相对压力估算，用于趋势展示")
    fig = plotly_heatmap(result, "pressure_kpa", "压力云图（相对压力 kPa）", "Turbo", "kPa")
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    else:
        mpl_fig = create_pressure_figure(result)
        st.pyplot(mpl_fig, clear_figure=True, use_container_width=True)
        plt.close(mpl_fig)
    st.markdown('<div class="hydrofoil-export-strip"><div class="hydrofoil-export-title">压力云图导出</div></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("导出压力云图 PNG", use_container_width=True):
        fig = create_pressure_figure(result)
        path = save_figure(fig, timestamped_name("pressure_field", "png"))
        plt.close(fig)
        notify_export(path)
        render_download(path)
    if c2.button("导出压力场数据 CSV", use_container_width=True):
        path = export_field_csv(result, "pressure_kpa", timestamped_name("pressure_field", "csv"))
        notify_export(path)
        render_download(path)
    if c3.button("导出当前参数 JSON", use_container_width=True):
        path = export_params_json(export_params(result, params), timestamped_name("pressure_params", "json"))
        notify_export(path)
        render_download(path)
    if c4.button("生成压力图报告片段", use_container_width=True):
        path = export_simulation_report(result, timestamped_name("pressure_report_fragment", "md"))
        notify_export(path)
        render_download(path)


def render_velocity_module(result: dict, params: dict[str, Any]) -> None:
    module_title("速度场与流线", "速度大小背景、流线以及尾迹趋势用于观察整流效果")
    fig1 = create_velocity_figure(result)
    st.pyplot(fig1, clear_figure=True, use_container_width=True)
    plt.close(fig1)
    fig2 = create_streamline_figure(result)
    st.pyplot(fig2, clear_figure=True, use_container_width=True)
    plt.close(fig2)
    st.markdown('<div class="hydrofoil-export-strip"><div class="hydrofoil-export-title">速度与流线导出</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("导出速度场 PNG", use_container_width=True):
        fig = create_velocity_figure(result)
        path = save_figure(fig, timestamped_name("velocity_field", "png"))
        plt.close(fig)
        notify_export(path)
        render_download(path)
    if c2.button("导出流线图 PNG", use_container_width=True):
        fig = create_streamline_figure(result)
        path = save_figure(fig, timestamped_name("streamlines", "png"))
        plt.close(fig)
        notify_export(path)
        render_download(path)
    if c3.button("导出速度场数据 CSV", use_container_width=True):
        path = export_field_csv(result, "speed", timestamped_name("velocity_field", "csv"))
        notify_export(path)
        render_download(path)


def render_cavitation_module(result: dict, params: dict[str, Any]) -> None:
    module_title("空化风险", "用压力阈值标出潜在低压风险区，结果用于趋势提示")
    fig1 = create_cavitation_figure(result, params["visual"]["risk_alpha"])
    st.pyplot(fig1, clear_figure=True, use_container_width=True)
    plt.close(fig1)
    fig2 = create_cavitation_stats_figure(result)
    st.pyplot(fig2, clear_figure=True, use_container_width=True)
    plt.close(fig2)
    st.markdown('<div class="hydrofoil-export-strip"><div class="hydrofoil-export-title">空化风险导出</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("导出空化风险 PNG", use_container_width=True):
        fig = create_cavitation_figure(result, params["visual"]["risk_alpha"])
        path = save_figure(fig, timestamped_name("cavitation_risk", "png"))
        plt.close(fig)
        notify_export(path)
        render_download(path)
    if c2.button("导出风险统计 CSV", use_container_width=True):
        path = export_zone_pressure_csv(result, timestamped_name("cavitation_zone_stats", "csv"))
        notify_export(path)
        render_download(path)
    if c3.button("导出风险分析 JSON", use_container_width=True):
        path = export_risk_json(result, timestamped_name("cavitation_risk", "json"))
        notify_export(path)
        render_download(path)


def render_curve_module(result: dict, params: dict[str, Any]) -> None:
    module_title("表面压力曲线", "沿弦向比较上下表面压力，并标注分区范围和最低压力点")
    fig = create_module_surface_curve_figure(result, params)
    st.pyplot(fig, clear_figure=True, use_container_width=True)
    plt.close(fig)
    st.markdown('<div class="hydrofoil-export-strip"><div class="hydrofoil-export-title">表面压力曲线导出</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("导出压力曲线 PNG", use_container_width=True):
        fig = create_module_surface_curve_figure(result, params)
        path = save_figure(fig, timestamped_name("surface_pressure_curve", "png"))
        plt.close(fig)
        notify_export(path)
        render_download(path)
    if c2.button("导出曲线数据 CSV", use_container_width=True):
        path = export_surface_pressure_csv(result, timestamped_name("surface_pressure", "csv"))
        notify_export(path)
        render_download(path)
    if c3.button("导出最低压力点 JSON", use_container_width=True):
        path = export_minimum_pressure_json(result, timestamped_name("minimum_pressure_point", "json"))
        notify_export(path)
        render_download(path)


def render_scan_module(result: dict, params: dict[str, Any]) -> None:
    module_title("参数扫描/动画生成", "用当前参数生成压力场、流速扫描或分区展开动画")
    fig = create_pressure_figure(result)
    st.pyplot(fig, clear_figure=True, use_container_width=True)
    plt.close(fig)
    st.markdown('<div class="hydrofoil-export-strip"><div class="hydrofoil-export-title">扫描与动画导出</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    export_payload = canvas_export_params(result, params)
    if c1.button("导出 GIF", use_container_width=True):
        target = params["export"]["scan_target"]
        with st.spinner(f"正在生成 {target} 扫描 GIF..."):
            if target == "流速":
                speeds = list(np.linspace(params["export"]["scan_start"], params["export"]["scan_end"], params["export"]["scan_frames"]))
                path = generate_speed_sweep_gif(export_payload, timestamped_name("speed_sweep", "gif"), speeds=speeds)
            else:
                path = generate_zone_deployment_gif(export_payload, timestamped_name("zone_deployment", "gif"), steps=params["export"]["scan_frames"])
        st.session_state["last_gif_path"] = str(path)
        notify_export(path)
        render_download(path)
    if c2.button("云端导出说明", use_container_width=True):
        open_output_folder()
    if c3.button("导出扫描参数 JSON", use_container_width=True):
        path = export_params_json(params, timestamped_name("scan_params", "json"))
        notify_export(path)
        render_download(path)
    if st.session_state.get("last_gif_path"):
        gif_path = Path(st.session_state["last_gif_path"])
        if gif_path.exists():
            st.image(str(gif_path), caption=gif_path.name, use_container_width=True)


def render_report_module(result: dict, params: dict[str, Any]) -> None:
    module_title("导出报告", "报告按钮仍在当前模块下方，右侧只保留最近导出记录")
    preview = [
        f"# {params['export']['report_title']}",
        "",
        "- 本报告用于专利展示、汇报演示和概念验证。",
        "- 模型为简化流场/粒子可视化，不是高精度 CFD。",
        f"- 当前流速：{params['flow']['velocity']:.2f} m/s",
        f"- 当前攻角：{params['flow']['alpha_deg']:.2f} deg",
        f"- 空化风险占比：{result['zone_stats']['overall']['cavitation_percent']:.2f}%",
        f"- 控制建议：{result['zone_stats']['recommendation']}",
    ]
    st.markdown("\n".join(preview))
    recent = st.session_state.get("recent_exports", [])
    if recent:
        section_title("已生成文件列表")
        for item in recent[-10:][::-1]:
            st.code(item)
    st.markdown('<div class="hydrofoil-export-strip"><div class="hydrofoil-export-title">报告导出</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("生成 Markdown 报告", use_container_width=True):
        path = export_simulation_report(result, timestamped_name("simulation_report", "md"))
        notify_export(path)
        render_download(path)
    if c2.button("云端导出说明", use_container_width=True):
        open_output_folder()
    if c3.button("导出参数 JSON", use_container_width=True):
        path = export_params_json(export_params(result, params), timestamped_name("report_params", "json"))
        notify_export(path)
        render_download(path)


MODULE_RENDERERS = {
    "动态水流粒子": render_canvas_module,
    "压力云图": render_pressure_module,
    "速度场与流线": render_velocity_module,
    "空化风险": render_cavitation_module,
    "表面压力曲线": render_curve_module,
    "参数扫描/动画生成": render_scan_module,
    "导出报告": render_report_module,
}


def render_center_panel(result: dict, params: dict[str, Any]) -> None:
    renderer = MODULE_RENDERERS[params["module"]]
    renderer(result, params)


def main() -> None:
    st.set_page_config(
        page_title="仿生分区主动水翼综合仿真平台",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_three_column_layout_css()
    init_session_state(st)
    st.markdown("### 仿生分区主动水翼综合仿真平台")
    st.caption("三栏独立滚动工作台：左侧模块参数，中间仿真与导出，右侧精密诊断。该平台不是高精度 CFD。")
    st.caption("云端部署版：导出文件只保存在当前服务器会话中，生成后请立即下载。")
    params = build_current_params(st)
    result, display_density = compute_result(params)

    left, center, right = st.columns([0.22, 0.55, 0.23], gap="medium")
    with left:
        panel_marker("left")
        render_left_panel()
    with center:
        panel_marker("center")
        render_center_panel(result, params)
    with right:
        panel_marker("right")
        render_right_panel(result, params, display_density)


if __name__ == "__main__":
    if "streamlit" not in sys.modules:
        print("请使用 python -m streamlit run app.py 运行本应用。")
    main()
