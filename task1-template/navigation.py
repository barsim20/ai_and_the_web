import streamlit as st


def show_navigation():
    """the two pages used by the app."""
    return st.navigation(
        [
            st.Page("play.py", title="Play", icon="⚽"),
            st.Page("stats.py", title="Stats", icon="📊"),
        ]
    )