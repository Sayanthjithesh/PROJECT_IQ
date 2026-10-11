import streamlit as st
from pathlib import Path

def inject_css():
    css=Path(__file__).resolve().parents[2]/'assets'/'styles.css'
    st.markdown(f'<style>{css.read_text()}</style>',unsafe_allow_html=True)
def hero_card(title,text):
    st.markdown(f"<div class='card'><h3>{title}</h3><p>{text}</p></div>",unsafe_allow_html=True)
def insight(title,text):
    st.markdown(f"<div class='insight'><b>{title}</b><br>{text}</div>",unsafe_allow_html=True)
