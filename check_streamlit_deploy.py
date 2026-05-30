from __future__ import annotations

import importlib.util
import py_compile
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

TEXT_SUFFIXES = {".py", ".md", ".txt", ".toml", ".html", ".css", ".js", ".json", ".csv"}
REQUIRED_FILES = [
    APP_ROOT / "app.py",
    APP_ROOT / "requirements.txt",
    APP_ROOT / "README.md",
    APP_ROOT / ".streamlit" / "config.toml",
    APP_ROOT / "components" / "flow_canvas.py",
    APP_ROOT / "components" / "flow_canvas_template.html",
    APP_ROOT / "core" / "hydrofoil_geometry.py",
    APP_ROOT / "core" / "pressure_model.py",
    APP_ROOT / "core" / "flow_solver_lite.py",
    APP_ROOT / "core" / "particle_flow_model.py",
    APP_ROOT / "core" / "vortex_model.py",
    APP_ROOT / "core" / "zone_control.py",
    APP_ROOT / "core" / "params.py",
    APP_ROOT / "core" / "layout.py",
    APP_ROOT / "core" / "ui_panels.py",
    APP_ROOT / "core" / "export_utils.py",
    APP_ROOT / "docs" / "simulation_principle.md",
    APP_ROOT / "docs" / "deploy_guide.md",
]
REQUIRED_DIRS = [
    APP_ROOT / "core",
    APP_ROOT / "components",
    APP_ROOT / "assets",
    APP_ROOT / "assets" / "outputs",
    APP_ROOT / "docs",
]
REQUIRED_PACKAGES = {"streamlit", "numpy", "matplotlib", "pillow", "plotly"}
DISALLOWED_REQUIREMENTS = [
    "cad" + "query",
    "o" + "cp",
    "solid" + "works",
    "py" + "win32",
    "open" + "foam",
    "flu" + "ent",
    "ju" + "pyter",
    "note" + "book",
]
FORBIDDEN_TEXT_PATTERNS = [
    re.compile(r"\b[A-Za-z]:[\\/][^\s\"'<>`]+"),
    re.compile("/" + "Users" + r"/[^/\s\"'<>`]+/"),
    re.compile("/" + "home" + r"/[^/\s\"'<>`]+/"),
    re.compile(r"\\" + "Users" + r"\\[^\\\s\"'<>`]+\\"),
    re.compile("hydrofoil" + "_cq", re.IGNORECASE),
]
GEOMETRY_SUFFIXES = {"." + "step", "." + "stp", "." + "stl"}
BATCH_SUFFIX = "." + "bat"


def rel(path: Path) -> str:
    try:
        return path.relative_to(APP_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def add_result(report: list[str], ok: bool, message: str) -> bool:
    report.append(f"- {'OK' if ok else 'ERROR'} {message}")
    return ok


def check_required_paths(report: list[str]) -> bool:
    report.append("## Required Structure")
    ok = True
    for path in REQUIRED_FILES:
        ok = add_result(report, path.is_file() and path.stat().st_size > 0, f"`{rel(path)}` exists") and ok
    for path in REQUIRED_DIRS:
        ok = add_result(report, path.is_dir(), f"`{rel(path)}` directory exists") and ok
    report.append("")
    return ok


def check_requirements(report: list[str]) -> bool:
    report.append("## Requirements")
    path = APP_ROOT / "requirements.txt"
    if not path.exists():
        report.append("- ERROR `requirements.txt` missing")
        report.append("")
        return False
    lines = [
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    normalized = {line.split("==")[0].split(">=")[0].split("<=")[0].strip() for line in lines}
    missing = sorted(REQUIRED_PACKAGES - normalized)
    bad = [item for item in lines for blocked in DISALLOWED_REQUIREMENTS if blocked in item]
    ok = True
    ok = add_result(report, not missing, "all required cloud packages are declared") and ok
    if missing:
        report.append(f"  Missing: {', '.join(missing)}")
    ok = add_result(report, not bad, "no blocked local/CAD packages are declared") and ok
    if bad:
        report.append(f"  Blocked lines: {', '.join(bad)}")
    report.append("")
    return ok


def check_forbidden_content(report: list[str]) -> bool:
    report.append("## Forbidden Content")
    ok = True
    batch_files = [path for path in APP_ROOT.rglob("*") if path.is_file() and path.suffix.lower() == BATCH_SUFFIX]
    geometry_files = [path for path in APP_ROOT.rglob("*") if path.is_file() and path.suffix.lower() in GEOMETRY_SUFFIXES]
    cache_dirs = [path for path in APP_ROOT.rglob("__pycache__") if path.is_dir()]
    pyc_files = [path for path in APP_ROOT.rglob("*.pyc") if path.is_file()]

    ok = add_result(report, not batch_files, "no batch launcher files exist") and ok
    for path in batch_files:
        report.append(f"  Found: `{rel(path)}`")
    ok = add_result(report, not geometry_files, "no CAD exchange geometry files exist") and ok
    for path in geometry_files:
        report.append(f"  Found: `{rel(path)}`")
    ok = add_result(report, not cache_dirs, "no Python cache directories exist") and ok
    for path in cache_dirs:
        report.append(f"  Found: `{rel(path)}`")
    ok = add_result(report, not pyc_files, "no bytecode files exist") and ok
    for path in pyc_files:
        report.append(f"  Found: `{rel(path)}`")

    forbidden_hits: list[str] = []
    for path in APP_ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(text):
                forbidden_hits.append(f"`{rel(path)}` contains forbidden local path token")
                break
    ok = add_result(report, not forbidden_hits, "no forbidden local path tokens in text files") and ok
    report.extend(f"  {hit}" for hit in forbidden_hits)
    report.append("")
    return ok


def check_py_compile(report: list[str]) -> bool:
    report.append("## Python Compile")
    ok = True
    py_files = sorted(path for path in APP_ROOT.rglob("*.py") if "__pycache__" not in path.parts)
    with tempfile.TemporaryDirectory(prefix="streamlit_deploy_compile_") as tmp:
        tmp_dir = Path(tmp)
        for index, path in enumerate(py_files):
            try:
                py_compile.compile(str(path), cfile=str(tmp_dir / f"{index}.pyc"), doraise=True)
                report.append(f"- OK `{rel(path)}`")
            except py_compile.PyCompileError as exc:
                ok = False
                report.append(f"- ERROR `{rel(path)}`: {exc.msg}")
    report.append("")
    return ok


def check_installed_dependencies(report: list[str]) -> bool:
    report.append("## Import Availability")
    import_names = {
        "streamlit": "streamlit",
        "numpy": "numpy",
        "matplotlib": "matplotlib",
        "pillow": "PIL",
        "plotly": "plotly",
    }
    for package, import_name in import_names.items():
        installed = importlib.util.find_spec(import_name) is not None
        level = "OK" if installed else "WARNING"
        note = "available" if installed else "not installed in current local environment; cloud installs from requirements.txt"
        report.append(f"- {level} `{package}` import is {note}")
    report.append("")
    return True


def check_core_smoke(report: list[str]) -> bool:
    report.append("## Core Simulation And Export")
    try:
        from core.export_utils import (
            create_pressure_figure,
            generate_particle_animation_gif,
            generate_particle_snapshot_png,
            save_figure,
        )
        from core.flow_solver_lite import simulate_flow
        from core.params import ZONE_UI
        from core.pressure_model import bernoulli_relative_pressure_kpa, dynamic_pressure_kpa

        pressure = bernoulli_relative_pressure_kpa(1000.0, 8.0, np.array([6.0, 8.0, 10.0]))
        dynamic = dynamic_pressure_kpa(1000.0, 8.0)
        if not np.all(np.isfinite(pressure)) or dynamic <= 0:
            raise RuntimeError("pressure calculation returned invalid values")

        zones = {
            zone: {
                "enabled": True,
                "angle_deg": spec["default_angle"],
                "response": spec["default_response"],
                "blade_type": spec["blade_type"],
                "drive_type": spec["drive_type"],
            }
            for zone, spec in ZONE_UI.items()
        }
        result = simulate_flow(
            velocity=8.0,
            alpha_deg=4.0,
            rho=1000.0,
            cavitation_threshold_kpa=-30.0,
            grid_density="低",
            zones=zones,
            show_vortex=True,
        )
        output_dir = APP_ROOT / "assets" / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        png_path = output_dir / "test_deploy_pressure_field.png"
        gif_path = output_dir / "test_deploy_particle_flow.gif"
        snapshot_path = output_dir / "test_deploy_canvas_snapshot.png"

        fig = create_pressure_figure(result)
        save_figure(fig, png_path)
        plt.close(fig)
        params = {
            "velocity": 8.0,
            "alpha_deg": 4.0,
            "rho": 1000.0,
            "cavitation_threshold_kpa": -30.0,
            "grid_density": "低",
            "zones": zones,
            "show_vortex": True,
            "particle_count": 220,
        }
        generate_particle_snapshot_png(params, snapshot_path)
        generate_particle_animation_gif(params, gif_path, frames=8)

        paths = [png_path, snapshot_path, gif_path]
        for path in paths:
            add_result(report, path.exists() and path.stat().st_size > 0, f"generated `{rel(path)}`")
        report.append(f"- OK pressure sample `{pressure.tolist()}`")
        report.append(f"- OK grid `{result['grid_shape'][1]} x {result['grid_shape'][0]}`")
        report.append("")
        return all(path.exists() and path.stat().st_size > 0 for path in paths)
    except Exception as exc:  # noqa: BLE001
        report.append(f"- ERROR core smoke test failed: {exc}")
        report.append("")
        return False


def write_report(report: list[str], passed: bool) -> Path:
    docs_dir = APP_ROOT / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    path = docs_dir / "app_check_report.md"
    header = [
        "# Streamlit Deploy Check Report",
        "",
        f"- Version: `v01`",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Result: `{'PASS' if passed else 'FAIL'}`",
        "",
    ]
    path.write_text("\n".join(header + report) + "\n", encoding="utf-8")
    return path


def print_tree() -> None:
    print("")
    print("streamlit_deploy tree")
    for path in sorted(APP_ROOT.rglob("*")):
        if "__pycache__" in path.parts:
            continue
        depth = len(path.relative_to(APP_ROOT).parts)
        prefix = "  " * (depth - 1)
        name = path.name + ("/" if path.is_dir() else "")
        print(f"{prefix}{name}")


def main() -> int:
    report: list[str] = []
    checks = [
        check_required_paths,
        check_requirements,
        check_forbidden_content,
        check_py_compile,
        check_installed_dependencies,
        check_core_smoke,
    ]
    results = [check(report) for check in checks]
    passed = all(results)
    report_path = write_report(report, passed)
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Report: {rel(report_path)}")
    print_tree()
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
