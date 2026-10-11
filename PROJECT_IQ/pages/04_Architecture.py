"""
PROJECTIQ - Architecture View Page
"""

import streamlit as st

from config import APP_NAME
from db.database import init_db
from services.project_data import get_latest_version_dict, get_project_dict
from ui_helpers import inject_global_styles, render_header

st.set_page_config(page_title=f"Architecture | {APP_NAME}", page_icon="🏗️", layout="wide")
inject_global_styles()
init_db()

project_id = st.session_state.get("active_project_id")
if not project_id:
    st.warning("No project selected. Choose one from **My Projects** first.", icon="⚠️")
    st.page_link("pages/02_My_Projects.py", label="Go to My Projects →", icon="📁")
    st.stop()

project = get_project_dict(project_id)
version = get_latest_version_dict(project_id)
if project is None or version is None:
    st.error("This project's analysis could not be found.")
    st.stop()

render_header(f"Architecture — {project['name']}")

arch = version["architecture"]


def _diagram(layers, title):
    if not layers:
        st.info("No layers detected for this diagram.")
        return
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    st.markdown(f"**{title}**")
    for i, layer in enumerate(layers):
        st.markdown(
            f'<div style="background-color:#EEF2FB; border-left:4px solid #2F5FDB; '
            f'padding:0.6rem 1rem; margin:0.3rem 0; border-radius:6px;">{layer}</div>',
            unsafe_allow_html=True,
        )
        if i < len(layers) - 1:
            st.markdown('<div style="text-align:center; color:#5B6478;">↓</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


col1, col2 = st.columns(2)
with col1:
    _diagram(arch["detected_layers"], "Current Architecture (Detected)")
with col2:
    _diagram(arch["recommended_diagram"].split(" -> "), "Recommended Architecture")

st.write("")
if arch["gaps"]:
    st.markdown("### Architecture Gaps")
    for gap in arch["gaps"]:
        st.markdown(f"- Missing layer: **{gap}**")
else:
    st.success("No structural architecture gaps were detected against the recommended layered model.")

st.write("")
st.caption(arch["disclaimer"])
