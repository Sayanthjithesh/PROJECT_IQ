"""
PROJECTIQ - Project Evolution Tracker Page
"""

import pandas as pd
import streamlit as st

from config import APP_NAME
from db.database import init_db
from services.project_data import get_all_versions, get_project_dict
from ui_helpers import inject_global_styles, render_header

st.set_page_config(page_title=f"Evolution Tracker | {APP_NAME}", page_icon="📈", layout="wide")
inject_global_styles()
init_db()

project_id = st.session_state.get("active_project_id")
if not project_id:
    st.warning("No project selected. Choose one from **My Projects** first.", icon="⚠️")
    st.page_link("pages/02_My_Projects.py", label="Go to My Projects →", icon="📁")
    st.stop()

project = get_project_dict(project_id)
versions = get_all_versions(project_id)
if project is None or not versions:
    st.error("No analysis history was found for this project.")
    st.stop()

render_header(f"Evolution Tracker — {project['name']}")

if len(versions) == 1:
    st.info(
        "This project has only one analysis snapshot so far. Re-analyze it after making "
        "changes (from **My Projects**) to start tracking growth over time.",
        icon="ℹ️",
    )

# ------------------------------------------------------------------
# Growth charts
# ------------------------------------------------------------------
chart_df = pd.DataFrame({
    "Version": [f"v{v['version_number']}" for v in versions],
    "Score": [v["score_total"] for v in versions],
    "Feature Count": [len(v["features"]) for v in versions],
})

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Score Growth**")
    st.line_chart(chart_df.set_index("Version")["Score"])
with col2:
    st.markdown("**Feature Growth**")
    st.line_chart(chart_df.set_index("Version")["Feature Count"])

st.write("")
st.markdown("### Version History")

previous_features = set()
for v in versions:
    current_features = {f["feature"] for f in v["features"]}
    added = sorted(current_features - previous_features)
    removed = sorted(previous_features - current_features)
    previous_features = current_features

    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Version {v['version_number']}** — {v['analyzed_at'].strftime('%Y-%m-%d %H:%M')}")
        st.markdown(f"Maturity: **{v['maturity_level']}**")
    with col2:
        st.markdown(f'<div class="piq-metric-value">{v["score_total"]}/100</div>', unsafe_allow_html=True)

    if added:
        st.markdown("**Changes:**")
        for f in added:
            st.markdown(f"+ {f}")
    if removed:
        for f in removed:
            st.markdown(f"- {f} (no longer detected)")
    if not added and not removed and v["version_number"] > 1:
        st.markdown('<span class="piq-muted">No feature-set changes since the previous version.</span>',
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
