"""
PROJECTIQ - Feature Impact Predictor Page
"""

import streamlit as st

from config import APP_NAME
from db.database import init_db
from engine.feature_impact import predict_feature_impact
from ui_helpers import inject_global_styles, render_header

st.set_page_config(page_title=f"Feature Impact Predictor | {APP_NAME}", page_icon="⚡", layout="wide")
inject_global_styles()
init_db()

render_header("Estimate the impact of a proposed feature before you build it.")

description = st.text_area(
    "Describe the feature you're considering",
    placeholder="e.g. I want to add a chatbot that answers customer questions.",
    height=100,
)

if st.button("⚡ Predict Impact", type="primary", disabled=not description.strip()):
    result = predict_feature_impact(description.strip())

    st.markdown('<div class="piq-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Portfolio Value", result["portfolio_value"])
    with c2:
        st.metric("Technical Complexity", result["technical_complexity"])
    with c3:
        st.metric("User Value", result["user_value"])

    st.markdown(f"**Recommendation:** {result['recommendation']}")
    st.markdown("**Prerequisites:**")
    for p in result["prerequisites"]:
        st.markdown(f"- {p}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption(result["disclaimer"])
