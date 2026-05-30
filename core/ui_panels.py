from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import streamlit as st

from .layout import panel_header, section_title
from .params import GRID_OPTIONS, MODULES, PRESETS, VISUAL_PRESETS, ZONE_UI, apply_preset_to_state, apply_visual_preset_to_state


def rerun_streamlit() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def render_zone_controls(zone: str, response_label: str = "响应强度") -> None:
    spec = ZONE_UI[zone]
    st.checkbox(f"{zone}区 开启", key=f"{zone}_enabled")
    st.slider(f"{zone}区 叶片角度 (deg)", 0.0, float(spec["max_angle"]), key=f"{zone}_angle", step=0.5)
    st.slider(f"{zone}区 {response_label}", 0.0, 1.0, key=f"{zone}_response", step=0.05)
    st.caption(f"叶片：{spec['blade_type']}")
    st.caption(f"驱动：{spec['drive_type']}")


def render_presets() -> None:
    section_title("预设工况")
    for name in PRESETS:
        if st.button(name, key=f"preset_{name}", use_container_width=True):
            apply_preset_to_state(st, name)
            rerun_streamlit()


def render_particle_parameters() -> None:
    section_title("基础流动")
    if st.session_state.get("quality_mode") not in ("流畅", "平衡", "炸裂"):
        st.session_state["quality_mode"] = "流畅"
    st.session_state["particle_count"] = min(2500, max(300, int(st.session_state.get("particle_count", 600))))
    st.session_state["trail_length"] = min(12, max(2, int(st.session_state.get("trail_length", 3))))

    st.radio("画质模式", ["流畅", "平衡", "炸裂"], key="quality_mode", horizontal=True)
    st.caption("流畅模式适合云端默认运行；炸裂模式保留全部高级效果，适合截图展示，可能较卡。")
    c1, c2 = st.columns(2)
    for idx, name in enumerate(VISUAL_PRESETS):
        target = c1 if idx % 2 == 0 else c2
        if target.button(name, key=f"visual_preset_{name}", use_container_width=True):
            apply_visual_preset_to_state(st, name)
            rerun_streamlit()
    if st.button("应用高画质参数", key="apply_cinematic_visuals", use_container_width=True):
        apply_visual_preset_to_state(st, "炸裂截图")
        rerun_streamlit()

    st.slider("流速 U (m/s)", 2.0, 20.0, key="U", step=0.2)
    st.slider("攻角 alpha (deg)", -2.0, 12.0, key="alpha", step=0.2)
    st.slider("动画速度", 0.2, 3.0, key="animation_speed", step=0.1)
    st.slider("粒子数量", 300, 2500, key="particle_count", step=100)
    st.slider("粒子拖尾长度", 2, 12, key="trail_length", step=1)
    st.slider("粒子发射强度", 0.2, 1.4, key="emission_strength", step=0.05)
    st.slider("流线贴附强度", 0.1, 1.3, key="attachment_strength", step=0.05)
    st.slider("尾迹强度", 0.0, 1.6, key="wake_strength", step=0.05)
    st.slider("涡旋强度", 0.0, 1.6, key="vortex_strength", step=0.05)
    st.slider("分离区强度", 0.0, 1.6, key="separation_strength", step=0.05)
    st.slider("空化强度", 0.0, 1.6, key="cavitation_strength", step=0.05)
    st.slider("叶片展开角 (deg)", 0.0, 35.0, key="vane_deploy_angle", step=0.5)
    st.checkbox("压力背景", key="show_pressure")
    st.checkbox("显示粒子", key="show_particles")
    st.checkbox("叶片示意", key="show_vanes")
    st.checkbox("显示空化气泡", key="show_cavitation_bubbles")
    st.checkbox("显示分离区", key="show_separation")
    st.checkbox("涡旋显示", key="show_vortex")
    st.checkbox("A/B/C 标识", key="show_zone_labels")
    st.toggle("暂停/播放", key="playing")
    section_title("A/B/C 分区")
    render_zone_controls("A", "扰动强度")
    render_zone_controls("B", "扰动强度")
    render_zone_controls("C", "整流强度")


def render_pressure_parameters() -> None:
    section_title("压力场参数")
    st.slider("流速 U (m/s)", 2.0, 20.0, key="U", step=0.2)
    st.slider("攻角 alpha (deg)", -2.0, 12.0, key="alpha", step=0.2)
    st.number_input("水密度 rho (kg/m^3)", min_value=900.0, max_value=1100.0, key="rho", step=5.0)
    st.number_input("空化压力阈值 (kPa)", min_value=-100.0, max_value=0.0, key="cav", step=2.0)
    st.selectbox("网格密度", GRID_OPTIONS, key="grid_density")
    st.slider("等值线层数", 12, 60, key="contour_levels", step=2)
    st.checkbox("色图范围自动", key="pressure_auto_range")
    if not st.session_state["pressure_auto_range"]:
        st.slider("手动最小压力 (kPa)", -120.0, 0.0, key="pressure_min", step=2.0)
        st.slider("手动最大压力 (kPa)", 0.0, 100.0, key="pressure_max", step=2.0)
    st.checkbox("显示水翼轮廓", key="pressure_show_foil")
    st.checkbox("显示 A/B/C 分区", key="pressure_show_zones")
    st.checkbox("显示空化风险等值线", key="pressure_show_cavitation")
    section_title("分区控制")
    render_zone_controls("A")
    render_zone_controls("B")
    render_zone_controls("C")


def render_velocity_parameters() -> None:
    section_title("速度与流线")
    st.slider("流速 U (m/s)", 2.0, 20.0, key="U", step=0.2)
    st.slider("攻角 alpha (deg)", -2.0, 12.0, key="alpha", step=0.2)
    st.selectbox("网格密度", GRID_OPTIONS, key="grid_density")
    st.slider("流线密度", 0.4, 2.6, key="streamline_density", step=0.05)
    st.slider("流线长度", 0.5, 2.0, key="streamline_length", step=0.05)
    st.checkbox("显示速度矢量", key="show_vectors")
    st.slider("矢量采样间隔", 6, 22, key="vector_stride", step=1)
    st.slider("尾迹显示强度", 0.0, 1.6, key="wake_display_strength", step=0.05)
    st.slider("C区整流强度", 0.0, 1.0, key="C_response", step=0.05)
    st.checkbox("叠加水翼轮廓", key="velocity_show_foil")
    st.checkbox("显示 A/B/C 分区", key="velocity_show_zones")


def render_cavitation_parameters() -> None:
    section_title("空化分析")
    st.slider("流速 U (m/s)", 2.0, 20.0, key="U", step=0.2)
    st.slider("攻角 alpha (deg)", -2.0, 12.0, key="alpha", step=0.2)
    st.number_input("水密度 rho (kg/m^3)", min_value=900.0, max_value=1100.0, key="rho", step=5.0)
    st.number_input("空化压力阈值 (kPa)", min_value=-100.0, max_value=0.0, key="cav", step=2.0)
    st.slider("风险透明度", 0.1, 0.9, key="risk_alpha", step=0.05)
    st.checkbox("风险等值线", key="risk_contour")
    st.checkbox("低压区域高亮", key="risk_lowlight")
    st.checkbox("显示风险统计", key="risk_show_stats")
    section_title("主控分区")
    st.checkbox("A区 开启", key="A_enabled")
    st.checkbox("B区 开启", key="B_enabled")
    st.slider("B区 叶片角度 (deg)", 0.0, 30.0, key="B_angle", step=0.5)
    st.slider("B区 响应强度", 0.0, 1.0, key="B_response", step=0.05)
    st.checkbox("C区 开启", key="C_enabled")


def render_surface_curve_parameters() -> None:
    section_title("曲线分析")
    st.slider("流速 U (m/s)", 2.0, 20.0, key="U", step=0.2)
    st.slider("攻角 alpha (deg)", -2.0, 12.0, key="alpha", step=0.2)
    st.number_input("水密度 rho (kg/m^3)", min_value=900.0, max_value=1100.0, key="rho", step=5.0)
    st.slider("曲线平滑系数", 1, 9, key="curve_smoothing", step=1)
    st.checkbox("显示上表面", key="curve_show_upper")
    st.checkbox("显示下表面", key="curve_show_lower")
    st.checkbox("标注最低压力点", key="curve_annotate_min")
    st.checkbox("标注 A/B/C 分区范围", key="curve_mark_zones")
    st.radio("横坐标类型", ["x/c", "mm"], key="curve_x_axis", horizontal=True)
    st.radio("纵坐标单位", ["kPa", "Pa"], key="curve_y_unit", horizontal=True)


def render_scan_parameters() -> None:
    section_title("扫描与动画")
    st.selectbox("扫描对象", ["流速", "攻角", "A区叶片角", "B区叶片角", "C区叶片角"], key="scan_target")
    st.number_input("起始值", key="scan_start", step=1.0)
    st.number_input("终止值", key="scan_end", step=1.0)
    st.slider("帧数", 6, 48, key="scan_frames", step=1)
    st.slider("GIF 帧率", 4, 20, key="gif_fps", step=1)
    st.selectbox("图像分辨率", ["低", "中", "高"], key="scan_resolution")
    st.checkbox("显示压力背景", key="scan_show_pressure")
    st.checkbox("显示粒子", key="scan_show_particles")
    st.checkbox("显示涡旋", key="scan_show_vortex")


def render_report_parameters() -> None:
    section_title("报告内容")
    st.text_input("报告标题", key="report_title")
    st.checkbox("包含压力云图", key="report_include_pressure")
    st.checkbox("包含速度场", key="report_include_velocity")
    st.checkbox("包含动态粒子截图", key="report_include_particle")
    st.checkbox("包含表面压力曲线", key="report_include_curve")
    st.checkbox("包含参数 JSON", key="report_include_json")
    st.checkbox("包含模型说明", key="report_include_principle")
    st.checkbox("包含非高精度 CFD 声明", key="report_include_disclaimer")


MODULE_PARAMETER_RENDERERS = {
    "动态水流粒子": render_particle_parameters,
    "压力云图": render_pressure_parameters,
    "速度场与流线": render_velocity_parameters,
    "空化风险": render_cavitation_parameters,
    "表面压力曲线": render_surface_curve_parameters,
    "参数扫描/动画生成": render_scan_parameters,
    "导出报告": render_report_parameters,
}


def render_left_panel() -> None:
    panel_header("模块专属参数", "切换模块后左侧参数会自动更新")
    st.radio("当前仿真模块", MODULES, key="active_module")
    st.checkbox("快速预览模式", key="fast_preview")
    renderer = MODULE_PARAMETER_RENDERERS[st.session_state["active_module"]]
    renderer()
    render_presets()


def _format_float(value: float, suffix: str = "") -> str:
    if not np.isfinite(value):
        return "N/A"
    return f"{value:.2f}{suffix}"


def _data_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="hydrofoil-data-card">
            <div class="hydrofoil-data-label">{label}</div>
            <div class="hydrofoil-data-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _risk_level(percent: float) -> str:
    if percent < 2.0:
        return "低"
    if percent < 8.0:
        return "中"
    return "高"


def render_right_panel(result: dict, params: dict[str, Any], display_density: str) -> None:
    stats = result["zone_stats"]
    visual = params["visual"]
    module = params["module"]
    panel_header("精密参数与诊断", "实时数据、风险判断、当前参数")
    _data_card("当前模块", module)
    _data_card("当前流速", _format_float(result["inputs"]["velocity"], " m/s"))
    _data_card("当前攻角", _format_float(result["inputs"]["alpha_deg"], " deg"))
    _data_card("动压 q", _format_float(stats["overall"]["dynamic_pressure_kpa"], " kPa"))
    _data_card("最小压力", _format_float(stats["overall"]["min_pressure_kpa"], " kPa"))
    _data_card("最大压力", _format_float(stats["overall"]["max_pressure_kpa"], " kPa"))
    _data_card("A区平均压力", _format_float(stats["A"]["avg_pressure_kpa"], " kPa"))
    _data_card("B区平均压力", _format_float(stats["B"]["avg_pressure_kpa"], " kPa"))
    _data_card("C区平均压力", _format_float(stats["C"]["avg_pressure_kpa"], " kPa"))
    _data_card("空化风险面积占比", _format_float(stats["overall"]["cavitation_percent"], "%"))
    _data_card("计算耗时", _format_float(result["compute_time_ms"], " ms"))
    _data_card("网格规模", f"{result['grid_shape'][1]} x {result['grid_shape'][0]} ({display_density})")

    section_title("模块附加指标")
    if module == "动态水流粒子":
        _data_card("当前粒子数", str(visual.get("particle_count", 600)))
        _data_card("粒子速度倍率", _format_float(visual.get("animation_speed", 1.0)))
        _data_card("尾迹强度", _format_float(visual.get("wake_strength", 0.8)))
        _data_card("涡旋强度", _format_float(visual.get("vortex_strength", 0.5)))
        _data_card("分离区强度", _format_float(visual.get("separation_strength", 0.4)))
        _data_card("空化强度", _format_float(visual.get("cavitation_strength", 0.3)))
        _data_card("渲染模式", visual.get("quality_mode", "流畅"))
        _data_card("目标帧率", f"{visual.get('target_fps', 60)} fps")
        _data_card("实际粒子上限", str(visual.get("mode_max_particles", 900)))
        _data_card("自动降级", "Canvas 内部启用" if visual.get("auto_degrade_enabled", True) else "关闭")
    elif module == "压力云图":
        p = result["pressure_kpa"]
        min_idx = np.nanargmin(p)
        max_idx = np.nanargmax(p)
        min_rc = np.unravel_index(min_idx, p.shape)
        max_rc = np.unravel_index(max_idx, p.shape)
        _data_card("压力范围", f"{np.nanmin(p):.2f} / {np.nanmax(p):.2f} kPa")
        _data_card("最低压力位置", f"x={result['X'][min_rc]:.3f}, y={result['Y'][min_rc]:.3f}")
        _data_card("最高压力位置", f"x={result['X'][max_rc]:.3f}, y={result['Y'][max_rc]:.3f}")
        _data_card("空化阈值", _format_float(result["inputs"]["cavitation_threshold_kpa"], " kPa"))
    elif module == "速度场与流线":
        speed = result["speed"]
        wake = speed[(result["chord_x"] > 0.82) & np.isfinite(speed)]
        _data_card("最大速度", _format_float(float(np.nanmax(speed)), " m/s"))
        _data_card("平均速度", _format_float(float(np.nanmean(speed)), " m/s"))
        _data_card("尾迹区域平均速度", _format_float(float(np.nanmean(wake)) if wake.size else float("nan"), " m/s"))
    elif module == "空化风险":
        cav_mask = result["cavitation_mask"]
        _data_card("风险面积占比", _format_float(stats["overall"]["cavitation_percent"], "%"))
        _data_card("低压区域数量", str(int(np.nansum(cav_mask))))
        _data_card("风险等级", _risk_level(stats["overall"]["cavitation_percent"]))
    elif module == "表面压力曲线":
        upper = result["pressure_upper_kpa"]
        lower = result["pressure_lower_kpa"]
        _data_card("上表面最低压力", _format_float(float(np.nanmin(upper)), " kPa"))
        _data_card("下表面最高压力", _format_float(float(np.nanmax(lower)), " kPa"))
        _data_card("压力差峰值", _format_float(float(np.nanmax(lower - upper)), " kPa"))

    section_title("控制建议")
    st.info(stats["recommendation"])

    section_title("当前参数 JSON")
    st.json(params, expanded=False)

    recent = st.session_state.get("recent_exports", [])
    if recent:
        section_title("最近导出")
        for item in recent[-6:][::-1]:
            st.caption(str(item))


def record_export(path: Path) -> None:
    entries = list(st.session_state.get("recent_exports", []))
    entries.append(path.name)
    st.session_state["recent_exports"] = entries[-12:]


def params_json_preview(params: dict[str, Any]) -> str:
    return json.dumps(params, ensure_ascii=False, indent=2)
