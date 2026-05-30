from __future__ import annotations

import streamlit as st


LEFT_PANEL_WIDTH = 300
RIGHT_PANEL_WIDTH = 320


def inject_three_column_layout_css() -> None:
    """Inject CSS for a professional three-column simulation workstation.

    The markers inserted by `panel_marker` scope the sticky/scrolling behavior to
    the top-level Streamlit columns instead of every nested column used by buttons.
    """
    st.markdown(
        """
        <style>
        :root {
            --hydro-bg: #0E1117;
            --hydro-panel: #121B27;
            --hydro-panel-2: #172335;
            --hydro-border: #26384B;
            --hydro-text: #F5F7FA;
            --hydro-muted: #9FB0C3;
            --hydro-cyan: #00B7FF;
            --hydro-yellow: #FFD166;
            --hydro-green: #57CC99;
            --hydro-pink: #FF4DCA;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background: var(--hydro-bg);
        }

        .block-container {
            max-width: 100% !important;
            padding: 0.65rem 0.85rem 0.85rem 0.85rem !important;
        }

        header[data-testid="stHeader"] {
            background: rgba(14, 17, 23, 0.82);
            backdrop-filter: blur(12px);
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.55rem;
        }

        div[data-testid="column"]:has(.hydrofoil-left-panel) > div:first-child,
        div[data-testid="column"]:has(.hydrofoil-center-panel) > div:first-child,
        div[data-testid="column"]:has(.hydrofoil-right-panel) > div:first-child {
            height: calc(100vh - 5.2rem);
            overflow-y: auto;
            overflow-x: hidden;
            position: sticky;
            top: 3.6rem;
            border: 1px solid var(--hydro-border);
            border-radius: 8px;
            background:
                linear-gradient(180deg, rgba(23, 35, 53, 0.98) 0%, rgba(14, 17, 23, 0.98) 100%);
            padding: 0.85rem 0.85rem 1rem 0.85rem;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
        }

        div[data-testid="column"]:has(.hydrofoil-left-panel) {
            min-width: 300px !important;
            max-width: 330px !important;
        }

        div[data-testid="column"]:has(.hydrofoil-right-panel) {
            min-width: 320px !important;
            max-width: 355px !important;
        }

        div[data-testid="column"]:has(.hydrofoil-center-panel) > div:first-child {
            padding: 0.95rem 1.0rem 1.2rem 1.0rem;
            background:
                linear-gradient(180deg, rgba(15, 25, 38, 0.99) 0%, rgba(10, 15, 22, 0.99) 100%);
        }

        div[data-testid="column"]:has(.hydrofoil-left-panel) > div:first-child::-webkit-scrollbar,
        div[data-testid="column"]:has(.hydrofoil-center-panel) > div:first-child::-webkit-scrollbar,
        div[data-testid="column"]:has(.hydrofoil-right-panel) > div:first-child::-webkit-scrollbar {
            width: 7px;
        }

        div[data-testid="column"]:has(.hydrofoil-left-panel) > div:first-child::-webkit-scrollbar-thumb,
        div[data-testid="column"]:has(.hydrofoil-center-panel) > div:first-child::-webkit-scrollbar-thumb,
        div[data-testid="column"]:has(.hydrofoil-right-panel) > div:first-child::-webkit-scrollbar-thumb {
            background: #32465A;
            border-radius: 8px;
        }

        .hydrofoil-panel-header {
            padding: 0.65rem 0.75rem;
            border: 1px solid rgba(0, 183, 255, 0.28);
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(0, 183, 255, 0.12), rgba(23, 35, 53, 0.72));
            margin-bottom: 0.75rem;
        }

        .hydrofoil-panel-title {
            color: var(--hydro-text);
            font-size: 1.02rem;
            line-height: 1.25;
            font-weight: 750;
            margin: 0;
        }

        .hydrofoil-panel-subtitle {
            color: var(--hydro-muted);
            font-size: 0.78rem;
            margin-top: 0.25rem;
        }

        .hydrofoil-section-title {
            color: var(--hydro-cyan);
            font-size: 0.86rem;
            font-weight: 750;
            letter-spacing: 0.02em;
            margin: 0.7rem 0 0.35rem 0;
            border-bottom: 1px solid rgba(38, 56, 75, 0.85);
            padding-bottom: 0.25rem;
        }

        .hydrofoil-module-title {
            font-size: 1.18rem;
            font-weight: 800;
            color: var(--hydro-text);
            margin-bottom: 0.25rem;
        }

        .hydrofoil-module-caption {
            color: var(--hydro-muted);
            font-size: 0.84rem;
            margin-bottom: 0.75rem;
        }

        .hydrofoil-export-strip {
            border: 1px solid rgba(38, 56, 75, 0.92);
            border-radius: 8px;
            padding: 0.75rem;
            background: rgba(18, 27, 39, 0.82);
            margin-top: 0.65rem;
        }

        .hydrofoil-export-title {
            color: var(--hydro-text);
            font-weight: 750;
            font-size: 0.92rem;
            margin-bottom: 0.45rem;
        }

        .hydrofoil-data-card {
            border: 1px solid rgba(38, 56, 75, 0.92);
            border-radius: 8px;
            padding: 0.58rem 0.65rem;
            background: rgba(18, 27, 39, 0.82);
            margin-bottom: 0.48rem;
        }

        .hydrofoil-data-label {
            color: var(--hydro-muted);
            font-size: 0.73rem;
            margin-bottom: 0.12rem;
        }

        .hydrofoil-data-value {
            color: var(--hydro-text);
            font-size: 0.98rem;
            font-weight: 760;
        }

        div[data-testid="stMetric"] {
            background: rgba(18, 27, 39, 0.82);
            border: 1px solid rgba(38, 56, 75, 0.92);
            border-radius: 8px;
            padding: 0.55rem 0.62rem;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.0rem;
        }

        .stButton > button {
            border-radius: 7px;
            border: 1px solid rgba(0, 183, 255, 0.42);
            background: linear-gradient(180deg, #163047 0%, #102235 100%);
            color: var(--hydro-text);
        }

        .stButton > button:hover {
            border-color: var(--hydro-cyan);
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def panel_marker(name: str) -> None:
    st.markdown(f'<div class="hydrofoil-{name}-panel"></div>', unsafe_allow_html=True)


def panel_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="hydrofoil-panel-header">
            <div class="hydrofoil-panel-title">{title}</div>
            <div class="hydrofoil-panel-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str) -> None:
    st.markdown(f'<div class="hydrofoil-section-title">{title}</div>', unsafe_allow_html=True)


def module_title(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="hydrofoil-module-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="hydrofoil-module-caption">{subtitle}</div>', unsafe_allow_html=True)


def export_strip_title(title: str = "当前模块导出") -> None:
    st.markdown(
        f"""
        <div class="hydrofoil-export-strip">
            <div class="hydrofoil-export-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
