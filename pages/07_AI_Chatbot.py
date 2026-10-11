"""
PROJECTIQ - AI Chatbot Page
Two modes: Project-Aware Assistant (RAG over the active project) and
Project Mentor (general guidance, optionally informed by the project).
"""

import streamlit as st

from ai.gemini_client import gemini_status_message
from ai.rag import answer_project_question, build_knowledge_base
from config import APP_NAME
from db.database import get_session, init_db
from db.models import ChatMessage
from services.project_data import get_latest_version_dict, get_project_dict
from ui_helpers import inject_global_styles, render_header

st.set_page_config(page_title=f"AI Chatbot | {APP_NAME}", page_icon="💬", layout="wide")
inject_global_styles()
init_db()

render_header("Ask ProjectIQ about your project, or get general project mentorship.")
st.caption(gemini_status_message())

project_id = st.session_state.get("active_project_id")
project = get_project_dict(project_id) if project_id else None
version = get_latest_version_dict(project_id) if project_id else None

mode_label = st.radio(
    "Chatbot Mode",
    ["🧠 Project-Aware Assistant", "🎓 Project Mentor"],
    horizontal=True,
)
mode = "project_assistant" if "Project-Aware" in mode_label else "mentor"

if mode == "project_assistant" and not project:
    st.warning(
        "The Project-Aware Assistant needs an active project. Select one from **My Projects**, "
        "or switch to **Project Mentor** mode for general guidance.",
        icon="⚠️",
    )
    st.page_link("pages/02_My_Projects.py", label="Go to My Projects →", icon="📁")
    st.stop()

if project:
    st.markdown(f'<div class="piq-card">Active project: <b>{project["name"]}</b></div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Build / cache the knowledge base for RAG (project mode only)
# ------------------------------------------------------------------
knowledge_base = []
if mode == "project_assistant" and version:
    dna = version["project_dna"]
    analysis_summary = (
        f"Project: {dna['project_name']}. Domain: {dna['domain']}. Type: {dna['project_type']}. "
        f"Complexity: {dna['complexity']}. Score: {version['score_total']}/100 "
        f"({version['maturity_level']}). Detected features: {', '.join(dna['detected_features'])}. "
        f"Frameworks: {', '.join(dna['frameworks'])}. Libraries: {', '.join(dna['libraries'])}. "
        f"Architecture layers: {', '.join(version['architecture']['detected_layers'])}. "
        f"High priority gaps: {', '.join(version['gaps']['gaps']['high_priority'])}. "
        f"Professional gaps: {', '.join(version['gaps']['gaps']['professional'])}."
    )
    recs_text = "\n".join(
        f"{r['recommendation']} (Priority: {r['priority']}) - {r['why']} Impact: {r['expected_impact']}"
        for r in version["recommendations"]
    )
    knowledge_base = build_knowledge_base(
        readme_text=dna.get("main_purpose", ""),
        analysis_summary=analysis_summary,
        extra_documents=[("Recommendations", recs_text)],
    )

# ------------------------------------------------------------------
# Chat history (persisted per project; session-only in mentor mode
# without an active project)
# ------------------------------------------------------------------
history_key = f"chat_history_{project_id}_{mode}" if project_id else f"chat_history_none_{mode}"
if history_key not in st.session_state:
    if project_id:
        with get_session() as session:
            existing = (
                session.query(ChatMessage)
                .filter_by(project_id=project_id, mode=mode)
                .order_by(ChatMessage.created_at)
                .all()
            )
            st.session_state[history_key] = [{"role": m.role, "content": m.content} for m in existing]
    else:
        st.session_state[history_key] = []

for message in st.session_state[history_key]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

example_questions = (
    ["Explain my architecture.", "What is missing from my project?",
     "How can I make this portfolio ready?", "Which part should I improve first?"]
    if mode == "project_assistant" else
    ["What technology stack fits a real-time chat app?", "How do I structure a microservices project?",
     "What should I learn next as a backend developer?"]
)
st.markdown('<span class="piq-muted">Try asking:</span>', unsafe_allow_html=True)
st.markdown(" · ".join(f"*{q}*" for q in example_questions))

user_question = st.chat_input("Ask ProjectIQ...")
if user_question:
    st.session_state[history_key].append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = answer_project_question(user_question, knowledge_base, mode=mode)
        st.markdown(answer)

    st.session_state[history_key].append({"role": "assistant", "content": answer})

    if project_id:
        with get_session() as session:
            session.add(ChatMessage(project_id=project_id, mode=mode, role="user", content=user_question))
            session.add(ChatMessage(project_id=project_id, mode=mode, role="assistant", content=answer))
