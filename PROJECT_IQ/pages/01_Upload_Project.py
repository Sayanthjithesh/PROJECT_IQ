"""
PROJECTIQ - Upload Project Page
"""

import streamlit as st

from config import APP_NAME, MAX_UPLOAD_MB
from db.database import get_session, init_db
from db.models import Project
from services.analysis_service import persist_analysis, run_full_analysis
from ui_helpers import inject_global_styles, render_header
from utils.project_loader import UploadValidationError, extract_project_zip

st.set_page_config(page_title=f"Upload Project | {APP_NAME}", page_icon="📤", layout="wide")
inject_global_styles()
init_db()
render_header("Upload a project for ProjectIQ to understand, evaluate, and evolve.")

source_tab, github_tab = st.tabs(["📦 Upload ZIP / Files", "🔗 GitHub Repository URL"])

with source_tab:
    st.markdown(
        f'<div class="piq-card">Upload a ZIP archive of your project. Files up to '
        f"{MAX_UPLOAD_MB} MB are accepted. `node_modules`, `.git`, `venv`, `__pycache__`, "
        f"`dist`, and `build` directories are automatically ignored. Uploaded code is "
        f"never executed — only read for static analysis.</div>",
        unsafe_allow_html=True,
    )

    project_name = st.text_input("Project name", placeholder="e.g. Fraud Detection System")
    goal = st.selectbox(
        "What is this project's current goal?",
        ["College Submission", "Portfolio Ready", "Startup MVP", "Production Ready"],
        index=1,
    )
    uploaded_file = st.file_uploader("Project ZIP file", type=["zip"])

    if st.button("🚀 Analyze Project", type="primary", disabled=not (uploaded_file and project_name.strip())):
        with st.spinner("Extracting archive and running static analysis..."):
            try:
                data = uploaded_file.read()
                storage_path = extract_project_zip(data, project_name.strip())

                with get_session() as session:
                    project = Project(
                        name=project_name.strip(),
                        source_type="zip",
                        storage_path=str(storage_path),
                        current_goal=goal,
                    )
                    session.add(project)
                    session.flush()
                    project_id = project.id

                analysis = run_full_analysis(project_name.strip(), str(storage_path), goal=goal)
                persist_analysis(project_id, analysis)

                st.session_state["active_project_id"] = project_id
                st.success(f"Analysis complete. ProjectIQ Score: **{analysis['score']['total']}/100** "
                           f"({analysis['score']['maturity']}).")
                st.balloons()
                st.page_link("pages/03_Project_Workspace.py", label="Open Project Workspace →", icon="🧬")

            except UploadValidationError as exc:
                st.error(f"Upload rejected: {exc}")
            except Exception as exc:  # pragma: no cover - defensive UI guard
                st.error(f"Analysis could not be completed: {exc}")

with github_tab:
    st.markdown(
        '<div class="piq-card">GitHub repository analysis requires downloading the repository '
        "as a ZIP archive. Paste a public repository URL below, download its ZIP from GitHub "
        "(Code → Download ZIP), and upload it using the tab on the left. A direct GitHub API "
        "integration for metadata (stars, topics, primary language) is available once a "
        "<b>GITHUB_TOKEN</b> is configured in Settings.</div>",
        unsafe_allow_html=True,
    )
    repo_url = st.text_input("GitHub repository URL", placeholder="https://github.com/owner/repository")
    if repo_url:
        st.info(
            "Reference saved. Download the repository ZIP from GitHub and use the "
            "**Upload ZIP / Files** tab to run the full ProjectIQ analysis.",
            icon="ℹ️",
        )
