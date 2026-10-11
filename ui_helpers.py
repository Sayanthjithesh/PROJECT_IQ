"""
PROJECTIQ - Shared UI Helpers

Reusable Streamlit rendering helpers and the application's CSS design
system (60/30/10 color rule: 60% deep charcoal-navy background,
30% panel surfaces, 10% signal-blue accent).
"""

import streamlit as st

from config import APP_NAME, APP_TAGLINE

COLOR_DOMINANT = "#F5EDEC"  # 60%
COLOR_SECONDARY = "#FFFFFF"   # 30%
COLOR_ACCENT =  "#ab230e"    # 10%
COLOR_SUCCESS = "#1F9D6C"
COLOR_WARNING = "#C77E00"
COLOR_DANGER = "#D93A46"
COLOR_TEXT = "#000000" 
COLOR_MUTED = "#5B6478"

MATURITY_COLORS = {
    "Beginner": COLOR_DANGER,
    "Developing": COLOR_WARNING,
    "Intermediate": COLOR_ACCENT,
    "Advanced": "#8B7CF6",
    "Professional": COLOR_SUCCESS,
}

RISK_COLORS = {
    "Low Risk": COLOR_SUCCESS,
    "Medium Risk": COLOR_WARNING,
    "High Risk": COLOR_DANGER,
}

PRIORITY_COLORS = {"High": COLOR_DANGER, "Professional": COLOR_ACCENT, "Advanced": COLOR_MUTED}


def inject_global_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {COLOR_DOMINANT};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {COLOR_SECONDARY};
        }}
        .piq-card {{
            background-color: {COLOR_SECONDARY};
            border: 1px solid rgba(26,34,51,0.08);
            border-radius: 12px;
            padding: 1.1rem 1.3rem;
            margin-bottom: 0.9rem;
        }}
        .piq-badge {{
            display: inline-block;
            padding: 0.15rem 0.65rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            color: white;
            margin-right: 0.35rem;
        }}
        .piq-muted {{
            color: {COLOR_MUTED};
            font-size: 0.88rem;
        }}
        .piq-metric-value {{
            font-size: 2.1rem;
            font-weight: 700;
            color: {COLOR_TEXT};
        }}
        .piq-accent-text {{
            color: {COLOR_ACCENT};
            font-weight: 600;
        }}
        h1, h2, h3, h4 {{
            color: {COLOR_TEXT} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div style="display:flex; align-items:baseline; gap:0.6rem; margin-bottom:0.1rem;">
            <span style="font-size:1.9rem; font-weight:800; color:{COLOR_TEXT};">{APP_NAME}</span>
            <span style="font-size:0.95rem; color:{COLOR_ACCENT}; font-weight:600;">{APP_TAGLINE}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(f'<div class="piq-muted">{subtitle}</div>', unsafe_allow_html=True)
    st.write("")


def badge(text: str, color: str) -> str:
    return f'<span class="piq-badge" style="background-color:{color};">{text}</span>'


def render_maturity_badge(maturity: str) -> None:
    color = MATURITY_COLORS.get(maturity, COLOR_ACCENT)
    st.markdown(badge(maturity, color), unsafe_allow_html=True)


def render_risk_badge(level: str) -> None:
    color = RISK_COLORS.get(level, COLOR_MUTED)
    st.markdown(badge(level, color), unsafe_allow_html=True)


def render_priority_badge(priority: str) -> None:
    color = PRIORITY_COLORS.get(priority, COLOR_MUTED)
    st.markdown(badge(priority, color), unsafe_allow_html=True)


def score_gauge_dataframe(score_total: float):
    import pandas as pd
    return pd.DataFrame({"Category": ["Score", "Remaining"], "Value": [score_total, max(0, 100 - score_total)]})


def empty_state(message: str, icon: str = "info") -> None:
    st.info(message, icon="ℹ️" if icon == "info" else "⚠️")


def require_active_project():
    """Guard clause used at the top of workspace-dependent pages."""
    project_id = st.session_state.get("active_project_id")
    if not project_id:
        st.warning(
            "No project is currently selected. Upload a new project or choose one "
            "from **My Projects** to continue.",
            icon="⚠️",
        )
        st.stop()
    return project_id
