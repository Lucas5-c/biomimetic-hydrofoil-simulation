# Streamlit Deploy Check Report

- Version: `v01`
- Generated: `2026-05-30T16:05:39`
- Result: `PASS`

## Required Structure
- OK `app.py` exists
- OK `requirements.txt` exists
- OK `README.md` exists
- OK `.streamlit/config.toml` exists
- OK `components/flow_canvas.py` exists
- OK `components/flow_canvas_template.html` exists
- OK `core/hydrofoil_geometry.py` exists
- OK `core/pressure_model.py` exists
- OK `core/flow_solver_lite.py` exists
- OK `core/particle_flow_model.py` exists
- OK `core/vortex_model.py` exists
- OK `core/zone_control.py` exists
- OK `core/params.py` exists
- OK `core/layout.py` exists
- OK `core/ui_panels.py` exists
- OK `core/export_utils.py` exists
- OK `docs/simulation_principle.md` exists
- OK `docs/deploy_guide.md` exists
- OK `core` directory exists
- OK `components` directory exists
- OK `assets` directory exists
- OK `assets/outputs` directory exists
- OK `docs` directory exists

## Requirements
- OK all required cloud packages are declared
- OK no blocked local/CAD packages are declared

## Forbidden Content
- OK no batch launcher files exist
- OK no CAD exchange geometry files exist
- OK no Python cache directories exist
- OK no bytecode files exist
- OK no forbidden local path tokens in text files

## Python Compile
- OK `app.py`
- OK `check_streamlit_deploy.py`
- OK `components/flow_canvas.py`
- OK `core/__init__.py`
- OK `core/export_utils.py`
- OK `core/flow_solver_lite.py`
- OK `core/hydrofoil_geometry.py`
- OK `core/layout.py`
- OK `core/params.py`
- OK `core/particle_flow_model.py`
- OK `core/pressure_model.py`
- OK `core/ui_panels.py`
- OK `core/vortex_model.py`
- OK `core/zone_control.py`

## Import Availability
- OK `streamlit` import is available
- OK `numpy` import is available
- OK `matplotlib` import is available
- OK `pillow` import is available
- OK `plotly` import is available

## Canvas Payload Visual Parameters
- OK canvas payload accepts advanced visual parameters

## Core Simulation And Export
- OK generated `assets/outputs/test_deploy_pressure_field.png`
- OK generated `assets/outputs/test_deploy_canvas_snapshot.png`
- OK generated `assets/outputs/test_deploy_particle_flow.gif`
- OK pressure sample `[14.0, 0.0, -18.0]`
- OK grid `120 x 80`

