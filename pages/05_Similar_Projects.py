"""
PROJECTIQ - Similar Project Intelligence Page
"""

import streamlit as st

from config import APP_NAME
from db.database import init_db
from services.project_data import get_latest_version_dict, get_project_dict
from ui_helpers import inject_global_styles, render_header

st.set_page_config(page_title=f"Similar Projects | {APP_NAME}", page_icon="🔍", layout="wide")
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

render_header(f"Similar Project Intelligence — {project['name']}")
st.caption(
    "Similarity is an estimate based on a curated comparison dataset and TF-IDF text "
    "similarity across project descriptions and features. No project is ever claimed to be "
    "completely unique."
)

diff = version["differentiation"]
similar_projects = diff.get("similar_projects", [])

st.markdown("### Differentiation Profile")
d1, d2, d3, d4 = st.columns(4)
with d1:
    st.metric("Common Features", f"{diff['common_features_percent']}%")
with d2:
    st.metric("Differentiating Features", f"{diff['differentiating_features_percent']}%")
with d3:
    st.metric("Technology Combination", f"{diff['technology_combination_percent']}%")
with d4:
    st.metric("Overall Differentiation", f"{diff['overall_differentiation']}/100")
st.markdown(f'<div class="piq-card">{diff["explanation"]}</div>', unsafe_allow_html=True)

st.write("")
st.markdown("### Closest Comparable Project Concepts")

for proj in similar_projects:
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{proj['name']}** — *{proj['domain']}*")
        st.markdown(f'<span class="piq-muted">{proj["description"]}</span>', unsafe_allow_html=True)
    with col2:
        st.progress(proj["similarity_percent"] / 100, text=f"{proj['similarity_percent']}% similar")

    ccol1, ccol2, ccol3 = st.columns(3)
    with ccol1:
        st.markdown("**Common Features**")
        st.markdown(", ".join(proj["common_features"]) or "None")
    with ccol2:
        st.markdown("**Your Differentiators**")
        st.markdown(", ".join(proj["differentiating_features"]) or "None")
    with ccol3:
        st.markdown("**Commonly Missing**")
        st.markdown(", ".join(proj["potentially_missing_features"]) or "None")
    st.markdown('</div>', unsafe_allow_html=True)
