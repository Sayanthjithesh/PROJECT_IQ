"""
PROJECTIQ - Project Future Simulator Page
"""

import streamlit as st

from config import APP_NAME
from db.database import init_db
from engine.future_simulator import simulate_future
from services.project_data import get_latest_version_dict, get_project_dict
from ui_helpers import inject_global_styles, render_header

st.set_page_config(page_title=f"Future Simulator | {APP_NAME}", page_icon="🚀", layout="wide")
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

render_header(f"Project Future Simulator — {project['name']}")

goal = st.selectbox(
    "Select a project goal",
    ["College Submission", "Portfolio Ready", "Startup MVP", "Production Ready"],
    index=["College Submission", "Portfolio Ready", "Startup MVP", "Production Ready"].index(project["current_goal"])
    if project["current_goal"] in ["College Submission", "Portfolio Ready", "Startup MVP", "Production Ready"] else 1,
)

feature_names = [f["feature"] for f in version["features"]]
roadmap = simulate_future(goal, version["score_total"], feature_names, version["gaps"]["gaps"])

st.markdown('<div class="piq-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.metric(f"{goal} Readiness", f"{roadmap['readiness_percent']}%")
with c2:
    st.metric("Remaining Gap", f"{roadmap['remaining_gap_percent']}%")
st.progress(roadmap["readiness_percent"] / 100)
if roadmap["still_needed"]:
    st.markdown(f"**Still needed for this goal:** {', '.join(roadmap['still_needed'])}")
else:
    st.success("All required capabilities for this goal have been detected.")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.markdown("### Personalized Evolution Roadmap")
for i, stage in enumerate(roadmap["roadmap"]):
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    st.markdown(f"**{stage['version']} — {stage['focus']}**")
    for change in stage["changes"]:
        st.markdown(f"+ {change}" if stage["version"] != "Current" else f"- {change}")
    st.markdown('</div>', unsafe_allow_html=True)
    if i < len(roadmap["roadmap"]) - 1:
        st.markdown('<div style="text-align:center; color:#5B6478; margin:-0.4rem 0;">↓</div>',
                    unsafe_allow_html=True)
