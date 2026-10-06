"""Trang khám phá điểm đến và bắt đầu tạo hành trình."""

import streamlit as st

from html import escape

from destinations import DESTINATIONS, SLIDES
from ui import destination_card, footer, photo_slideshow, photo_uri, section_title


with st.container(key="home-hero"):
    copy, photo = st.columns([1.08, 0.92], gap="large", vertical_alignment="center")
    with copy:
        st.markdown('<div class="dl-eyebrow">Cao nguyên · Rừng · Văn hóa</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="dl-hero-title">Đắk Lắk<br><span>theo cách của bạn.</span></h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="dl-hero-description">Một hành trình vừa vặn với quỹ thời gian, sở thích và ngân sách của bạn — '
            'từ phố cà phê Buôn Ma Thuột đến hồ, thác và những trải nghiệm bản địa.</p>',
            unsafe_allow_html=True,
        )
        st.page_link("views/blank.py", label="Lên lịch trình của tôi", icon="🧭")
        st.markdown('<div class="dl-trust-line">Đi dễ hơn · Dự toán rõ hơn · Khám phá sâu hơn</div>', unsafe_allow_html=True)
    with photo:
        photo_slideshow(SLIDES, height=430)

st.markdown("<div class='dl-spacer'></div>", unsafe_allow_html=True)
with st.container(key="home-quickstart"):
    section_title("Bắt đầu trong vài bước", "Bạn muốn chuyến đi như thế nào?", "Nhập thông tin cơ bản, phần còn lại có thể tùy chỉnh sau.")
    with st.form("quick-trip-form", border=False):
        c_people, c_days, c_budget, c_basis = st.columns([0.9, 0.9, 1.2, 1.0], gap="medium")
        with c_people:
            people = st.number_input("Số người", min_value=1, max_value=30, value=2, step=1)
        with c_days:
            days = st.number_input("Số ngày", min_value=1, max_value=14, value=3, step=1)
        with c_budget:
            budget = st.number_input("Ngân sách (VNĐ)", min_value=0, value=6000000, step=500000, format="%d")
        with c_basis:
            budget_basis = st.selectbox("Tính ngân sách", ["Cả nhóm", "Mỗi người"])
        interests = st.multiselect(
            "Bạn quan tâm điều gì?",
            ["Thiên nhiên", "Cà phê", "Văn hóa", "Ẩm thực", "Nghỉ dưỡng", "Trải nghiệm bản địa"],
            default=["Thiên nhiên", "Cà phê"],
            placeholder="Chọn một hoặc vài sở thích",
        )
        submitted = st.form_submit_button("Tiếp tục lên lịch trình", type="primary", width="stretch")
    if submitted:
        st.session_state.trip_draft = {
            "people": int(people), "days": int(days), "budget": int(budget),
            "budget_basis": budget_basis, "interests": interests,
        }
        for key in list(st.session_state):
            if key.startswith("planner-") or key.startswith("adjust-"):
                del st.session_state[key]
        st.session_state.show_trip_preview = False
        st.switch_page("views/blank.py")

st.markdown("<div class='dl-spacer'></div>", unsafe_allow_html=True)
section_title("Đắk Lắk qua ống kính", "Những khung hình gọi mời một chuyến đi", "Từ phố cà phê đến mặt hồ và dòng thác — chọn khung hình bạn muốn khám phá.")
gallery = st.columns(4, gap="medium")
for column, slide in zip(gallery, SLIDES):
    with column:
        uri = photo_uri(slide["image"])
        if uri:
            content = f'<img src="{uri}" alt="{escape(slide["subtitle"], quote=True)}" loading="lazy">'
            if slide["slug"]:
                content = f'<a href="dia-diem?destination={slide["slug"]}" target="_self">{content}</a>'
            st.markdown(f'<figure class="dl-gallery-photo">{content}<figcaption>{escape(slide["subtitle"])}</figcaption></figure>', unsafe_allow_html=True)

st.markdown("<div class='dl-spacer'></div>", unsafe_allow_html=True)
section_title("Một vùng đất, nhiều nhịp đi", "Bắt đầu từ điều bạn muốn khám phá", "Chọn một cảm hứng — hành trình vẫn do bạn quyết định.")
cards = st.columns(3, gap="large")
for column, (slug, destination) in zip(cards, DESTINATIONS.items()):
    with column:
        destination_card(destination["name"], destination["category"], destination["description"],
                         destination["image"], destination["image_label"], slug=slug)

st.markdown("<div class='dl-spacer'></div>", unsafe_allow_html=True)
with st.container(key="home-note"):
    note, action = st.columns([1.5, 1], vertical_alignment="center")
    with note:
        st.markdown('<div class="dl-note-kicker">Hành trình có trách nhiệm</div>', unsafe_allow_html=True)
        st.markdown("### Khám phá có hiểu biết, trải nghiệm có tôn trọng")
        st.markdown("Ưu tiên trải nghiệm địa phương, dành thời gian vừa đủ và tìm hiểu quy tắc ứng xử tại mỗi điểm đến.")
    with action:
        st.page_link("views/blank.py", label="Thiết kế chuyến đi", icon="🧭")

footer()
