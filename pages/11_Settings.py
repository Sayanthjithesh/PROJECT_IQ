"""
PROJECTIQ - Settings Page
"""

import streamlit as st

from config import (
    APP_NAME, DATABASE_URL, MAX_UPLOAD_MB, gemini_configured, github_configured,
)
from db.database import init_db
from ui_helpers import inject_global_styles, render_header

st.set_page_config(page_title=f"Settings | {APP_NAME}", page_icon="⚙️", layout="wide")
inject_global_styles()
init_db()

render_header("Application configuration and environment status.")

st.markdown('<div class="piq-card">', unsafe_allow_html=True)
st.markdown("### AI / API Configuration")
st.markdown(
    ("✅ **Gemini API key detected.** The AI Chatbot and RAG explanations are enabled."
     if gemini_configured() else
     "⚠️ **No Gemini API key detected.** Add `GEMINI_API_KEY` to your `.env` file "
     "(see `.env.example`) and restart the app to enable the AI Chatbot.")
)
st.markdown(
    ("✅ **GitHub token detected.** GitHub metadata lookups are enabled."
     if github_configured() else
     "ℹ️ **No GitHub token configured (optional).** Add `GITHUB_TOKEN` to your `.env` file "
     "to enable direct GitHub repository metadata lookups.")
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="piq-card">', unsafe_allow_html=True)
st.markdown("### Storage")
st.markdown(f"**Database:** `{DATABASE_URL}`")
st.markdown(f"**Maximum upload size:** {MAX_UPLOAD_MB} MB")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="piq-card">', unsafe_allow_html=True)
st.markdown("### About")
st.markdown(
    f"**{APP_NAME}** is an AI-powered Project Intelligence and Evolution Platform. "
    "All scoring and feature detection is performed with deterministic, rule-based static "
    "analysis; the Gemini API is used only for conversational explanations in the AI Chatbot. "
    "No uploaded code is ever executed."
)
st.markdown('</div>', unsafe_allow_html=True)

st.info(
    "To change environment variables, edit the `.env` file in the project root and restart "
    "the Streamlit application (`Ctrl+C` then `streamlit run Home.py`).",
    icon="ℹ️",
)
