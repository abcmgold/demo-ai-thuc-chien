"""Điểm vào và điều hướng website Trợ lý Du lịch Đắk Lắk AI."""

from pathlib import Path

import streamlit as st

from ui import apply_theme, sidebar

ROOT = Path(__file__).resolve().parent
logo = str(ROOT / "assets" / "logo-mark.svg")

st.set_page_config(page_title="Trợ lý Du lịch Đắk Lắk AI", page_icon=logo, layout="wide")
st.logo(logo, size="large", icon_image=logo)
apply_theme()

home_page = st.Page("views/home.py", title="Khám phá", icon="🏞️", default=True)
planner_page = st.Page("views/blank.py", title="Lên lịch trình", icon="🧭")
destination_page = st.Page("views/destination.py", title="Điểm đến", icon="📍", url_path="dia-diem")
navigation = st.navigation({"ĐẮK LẮK": [home_page, destination_page, planner_page]})
sidebar()
navigation.run()
