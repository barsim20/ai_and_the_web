import streamlit as st

from navigation import show_navigation


st.set_page_config(page_title="Football Guessing Game", page_icon="⚽")

page = show_navigation()
page.run()
