from __future__ import annotations

import html
import json
from pathlib import Path

import streamlit.components.v1 as components


TEMPLATE_PATH = Path(__file__).with_name("flow_canvas_template.html")


def render_flow_canvas(payload: dict, height: int = 660) -> None:
    """Render the enhanced HTML5 Canvas particle-flow viewport."""
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    data = html.escape(json.dumps(payload, ensure_ascii=False), quote=False)
    markup = template.replace("__FLOW_PAYLOAD__", data)
    components.html(markup, height=height, scrolling=False)
