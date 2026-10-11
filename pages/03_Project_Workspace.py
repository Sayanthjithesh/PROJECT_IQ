"""
PROJECTIQ - Project Workspace Page
Central analysis results view: Project DNA, technologies, features,
ProjectIQ Score, feature gaps, and explainable recommendations.
"""

import streamlit as st

from config import APP_NAME
from db.database import init_db
from services.project_data import get_latest_version_dict, get_project_dict
from ui_helpers import (
    inject_global_styles, render_header, render_maturity_badge, render_priority_badge,
)

st.set_page_config(page_title=f"Project Workspace | {APP_NAME}", page_icon="🧬", layout="wide")
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
    st.error("This project's analysis could not be found. It may have been deleted.")
    st.stop()

render_header(f"Workspace — {project['name']} (v{version['version_number']})")

dna = version["project_dna"]
tech = version["technologies"]
features = version["features"]
score = {"total": version["score_total"], "breakdown": version["score_breakdown"], "maturity": version["maturity_level"]}
gaps = version["gaps"]
recommendations = version["recommendations"]
outlook = version["outlook"]

# ------------------------------------------------------------------
# Top summary row
# ------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    st.markdown('<div class="piq-muted">ProjectIQ Score</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="piq-metric-value">{score["total"]}/100</div>', unsafe_allow_html=True)
    render_maturity_badge(score["maturity"])
    st.markdown('</div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    st.markdown('<div class="piq-muted">Detected Features</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="piq-metric-value">{len(features)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    st.markdown('<div class="piq-muted">Complexity</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="piq-metric-value" style="font-size:1.5rem;">{dna["complexity"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    st.markdown('<div class="piq-muted">Open Recommendations</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="piq-metric-value">{len(recommendations)}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")
tab_dna, tab_tech, tab_features, tab_score, tab_gaps, tab_outlook = st.tabs(
    ["🧬 Project DNA", "🛠️ Technologies", "✅ Features", "📊 ProjectIQ Score", "🧩 Gaps & Recommendations", "🔭 Outlook"]
)

# ------------------------------------------------------------------
# Project DNA
# ------------------------------------------------------------------
with tab_dna:
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    st.markdown(f"**Project:** {dna['project_name']}")
    st.markdown(f"**Domain:** {dna['domain']}")
    st.markdown(f"**Project Type:** {dna['project_type']}")
    st.markdown(f"**Languages:** {', '.join(dna['languages']) or 'Not detected'}")
    st.markdown(f"**Frameworks:** {', '.join(dna['frameworks']) or 'Not detected'}")
    st.markdown(f"**Libraries:** {', '.join(dna['libraries']) or 'Not detected'}")
    st.markdown(f"**Database:** {', '.join(dna['databases']) or 'Not detected'}")
    st.markdown(f"**Complexity:** {dna['complexity']}")
    st.markdown(f"**Main Purpose:** {dna['main_purpose']}")
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Technologies
# ------------------------------------------------------------------
with tab_tech:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Languages Detected**")
        if tech["languages"]:
            st.bar_chart(tech["languages"])
        else:
            st.info("No source languages were detected.")
    with col2:
        st.markdown("**Frameworks & Libraries**")
        combined = tech["frameworks"] + tech["libraries"]
        if combined:
            for item in combined:
                st.markdown(f"- {item}")
        else:
            st.info("No frameworks or libraries were detected.")

    st.markdown("**Declared Dependencies**")
    deps = tech["dependencies"]
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.caption("Python packages")
        st.code("\n".join(deps["python_packages"]) or "None found", language="text")
    with dcol2:
        st.caption("Node dependencies")
        st.code("\n".join(deps["node_dependencies"]) or "None found", language="text")

# ------------------------------------------------------------------
# Features
# ------------------------------------------------------------------
with tab_features:
    if not features:
        st.info("No application-level features were confidently detected.")
    for f in features:
        st.markdown('<div class="piq-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{f['feature']}**")
            st.markdown(f'<span class="piq-muted">{f["evidence"]}</span>', unsafe_allow_html=True)
            if f["files"]:
                st.markdown(f'<span class="piq-muted">Files: {", ".join(f["files"])}</span>', unsafe_allow_html=True)
        with col2:
            st.progress(f["confidence"] / 100, text=f"{f['confidence']}% confidence")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# ProjectIQ Score
# ------------------------------------------------------------------
with tab_score:
    st.markdown(f"### Total Score: {score['total']} / 100")
    render_maturity_badge(score["maturity"])
    st.write("")
    for category, data in score["breakdown"].items():
        st.markdown('<div class="piq-card">', unsafe_allow_html=True)
        st.markdown(f"**{category}** — {data['score']}/{data['max']}")
        st.progress(min(data["score"] / data["max"], 1.0) if data["max"] else 0)
        for reason in data["reasons"]:
            st.markdown(f'<span class="piq-muted">• {reason}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Gaps & Recommendations
# ------------------------------------------------------------------
with tab_gaps:
    st.markdown(f"**Feature completeness for a {gaps['project_type_used']}:** "
                f"{gaps['completeness_percent']}%")
    st.progress(gaps["completeness_percent"] / 100)

    gcol1, gcol2, gcol3 = st.columns(3)
    with gcol1:
        st.markdown("**High Priority Gaps**")
        for item in gaps["gaps"]["high_priority"]:
            st.markdown(f"- {item}")
        if not gaps["gaps"]["high_priority"]:
            st.markdown('<span class="piq-muted">None detected.</span>', unsafe_allow_html=True)
    with gcol2:
        st.markdown("**Professional-Level Gaps**")
        for item in gaps["gaps"]["professional"]:
            st.markdown(f"- {item}")
        if not gaps["gaps"]["professional"]:
            st.markdown('<span class="piq-muted">None detected.</span>', unsafe_allow_html=True)
    with gcol3:
        st.markdown("**Advanced Gaps**")
        for item in gaps["gaps"]["advanced"]:
            st.markdown(f"- {item}")
        if not gaps["gaps"]["advanced"]:
            st.markdown('<span class="piq-muted">None detected.</span>', unsafe_allow_html=True)

    st.write("")
    st.markdown("### Explainable Recommendations")
    if not recommendations:
        st.success("No further recommendations — detected features cover the expected profile well.")
    for rec in recommendations:
        st.markdown('<div class="piq-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{rec['recommendation']}**")
        with col2:
            render_priority_badge(rec["priority"])
        st.markdown(f"*Why:* {rec['why']}")
        st.markdown(f"*Evidence:* {rec['evidence']}")
        st.markdown(f"*Expected Impact:* {rec['expected_impact']}")
        st.markdown(f"*Skills Required:* {', '.join(rec['skills_required'])}")
        st.markdown(f"*Difficulty:* {rec['difficulty']}")
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Outlook
# ------------------------------------------------------------------
with tab_outlook:
    st.markdown("### Analyze My Project Outlook")
    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    st.markdown(f"**Detected pages/modules:** {', '.join(outlook['detected_pages_or_modules']) or 'None detected'}")
    st.markdown(f"**User-facing features:** {', '.join(outlook['detected_user_facing_features']) or 'None detected'}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### What Might Users Expect Next?")
    if outlook["recommended_next_features"]:
        for item in outlook["recommended_next_features"]:
            st.markdown(f"- {item}")
    else:
        st.info("No further natural extensions were identified from the current feature set.")

st.write("")
nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.page_link("pages/04_Architecture.py", label="View Architecture →", icon="🏗️")
with nav2:
    st.page_link("pages/05_Similar_Projects.py", label="Similar Project Intelligence →", icon="🔍")
with nav3:
    st.page_link("pages/10_Future_Simulator.py", label="Project Future Simulator →", icon="🚀")
