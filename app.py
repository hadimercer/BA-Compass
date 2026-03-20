"""Entry point and router for the BA Compass Streamlit application."""

from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="BA Compass",
    layout="wide",
    initial_sidebar_state="expanded",
)

if st.session_state.get("session_token"):
    st.switch_page("pages/dashboard.py")
    st.stop()

st.switch_page("pages/login.py")
