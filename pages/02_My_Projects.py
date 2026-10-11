"""
PROJECTIQ - My Projects Page
"""

import streamlit as st

from config import APP_NAME
from db.database import get_session, init_db
from db.models import Project
from services.analysis_service import persist_analysis, run_full_analysis
from ui_helpers import inject_global_styles, render_header, render_maturity_badge
from utils.project_loader import delete_project_storage

st.set_page_config(page_title=f"My Projects | {APP_NAME}", page_icon="📁", layout="wide")
inject_global_styles()
init_db()
render_header("Every project you've analyzed, saved locally and ready to revisit.")

with get_session() as session:
    projects = session.query(Project).order_by(Project.last_analyzed_date.desc()).all()
    project_rows = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "score": p.current_score,
            "maturity": p.current_maturity,
            "goal": p.current_goal,
            "uploaded": p.upload_date.strftime("%Y-%m-%d %H:%M"),
            "last_analyzed": p.last_analyzed_date.strftime("%Y-%m-%d %H:%M"),
            "versions": len(p.versions),
            "storage_path": p.storage_path,
        }
        for p in projects
    ]

if not project_rows:
    st.info(
        "No projects yet. Head to **Upload Project** to analyze your first one.",
        icon="ℹ️",
    )
    st.page_link("pages/01_Upload_Project.py", label="Upload a Project →", icon="📤")
    st.stop()

for row in project_rows:
    with st.container():
        st.markdown('<div class="piq-card">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([3, 1.2, 1.2, 2])

        with col1:
            st.markdown(f"### {row['name']}")
            st.markdown(f'<span class="piq-muted">{row["description"] or "No description available."}</span>',
                        unsafe_allow_html=True)
            st.markdown(f'<span class="piq-muted">Uploaded {row["uploaded"]} · '
                        f'Last analyzed {row["last_analyzed"]} · {row["versions"]} version(s) · '
                        f'Goal: {row["goal"]}</span>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="piq-metric-value">' + f'{row["score"]}/100' + '</div>', unsafe_allow_html=True)
            render_maturity_badge(row["maturity"])

        with col3:
            if st.button("Open", key=f"open_{row['id']}", use_container_width=True):
                st.session_state["active_project_id"] = row["id"]
                st.switch_page("pages/03_Project_Workspace.py")
            if st.button("Re-analyze", key=f"reanalyze_{row['id']}", use_container_width=True):
                with st.spinner("Re-analyzing project..."):
                    analysis = run_full_analysis(row["name"], row["storage_path"], goal=row["goal"])
                    persist_analysis(row["id"], analysis)
                st.success(f"New version saved. Updated score: {analysis['score']['total']}/100.")
                st.rerun()

        with col4:
            confirm_key = f"confirm_delete_{row['id']}"
            if st.session_state.get(confirm_key):
                st.warning("Delete this project and all its analysis history?")
                dcol1, dcol2 = st.columns(2)
                with dcol1:
                    if st.button("Yes, delete", key=f"yes_{row['id']}", use_container_width=True):
                        with get_session() as session:
                            proj = session.get(Project, row["id"])
                            if proj:
                                delete_project_storage(proj.storage_path)
                                session.delete(proj)
                        if st.session_state.get("active_project_id") == row["id"]:
                            st.session_state.pop("active_project_id", None)
                        st.rerun()
                with dcol2:
                    if st.button("Cancel", key=f"no_{row['id']}", use_container_width=True):
                        st.session_state[confirm_key] = False
                        st.rerun()
            else:
                if st.button("🗑️ Delete", key=f"delete_{row['id']}", use_container_width=True):
                    st.session_state[confirm_key] = True
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
