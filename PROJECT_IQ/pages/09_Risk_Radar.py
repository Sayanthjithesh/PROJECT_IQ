"""
PROJECTIQ - Project Risk Radar Page
"""

import streamlit as st

from config import APP_NAME
from db.database import init_db
from services.project_data import get_latest_version_dict, get_project_dict
from ui_helpers import inject_global_styles, render_header, render_risk_badge

st.set_page_config(page_title=f"Risk Radar | {APP_NAME}", page_icon="⚠️", layout="wide")
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

render_header(f"Project Risk Radar — {project['name']}")

risk_data = version["risk_radar"]
st.warning(risk_data["disclaimer"], icon="⚠️")

for category, entry in risk_data["risks"].items():
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{category}**")
        st.markdown(f'<span class="piq-muted">{entry["reason"]}</span>', unsafe_allow_html=True)
    with col2:
        render_risk_badge(entry["level"])
    st.markdown('</div>', unsafe_allow_html=True)
