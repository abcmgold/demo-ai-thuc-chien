"""Trang chi tiết địa điểm, mở từ thẻ hoặc ảnh trên trang chủ."""

from html import escape

import streamlit as st

from destinations import DESTINATIONS
from ui import destination_card, footer, page_header, photo_uri, section_title


slug = st.query_params.get("destination", st.session_state.get("selected_destination", "buon-ma-thuot"))
if slug not in DESTINATIONS:
    st.info("Địa điểm này chưa có nội dung. Bạn có thể chọn một địa điểm bên dưới.")
    slug = "buon-ma-thuot"
st.session_state.selected_destination = slug

back, selector = st.columns([1, 2], vertical_alignment="center")
with back:
    st.page_link("views/home.py", label="← Về trang khám phá")
with selector:
    selected = st.selectbox("Khám phá địa điểm", list(DESTINATIONS), index=list(DESTINATIONS).index(slug),
                            format_func=lambda value: DESTINATIONS[value]["name"])
    if selected != slug:
        st.session_state.selected_destination = selected
        st.query_params["destination"] = selected
        st.rerun()

destination = DESTINATIONS[slug]
page_header(destination["category"], destination["name"], destination["description"])
uri = photo_uri(destination["image"])
if uri:
    st.markdown(f'<figure class="dl-detail-hero"><img src="{uri}" alt="{escape(destination["image_label"], quote=True)}"><figcaption>{escape(destination["image_label"])}</figcaption></figure>', unsafe_allow_html=True)

main, aside = st.columns([1.65, 0.85], gap="large")
with main:
    section_title("Câu chuyện điểm đến", f"Khám phá {destination['name']}")
    st.write(destination["intro"])
    st.markdown("### Trải nghiệm gợi ý")
    for index, (title, description) in enumerate(destination["highlights"], start=1):
        st.markdown(f'<div class="dl-experience"><span>{index:02d}</span><div><h3>{escape(title)}</h3><p>{escape(description)}</p></div></div>', unsafe_allow_html=True)
    st.markdown("### Ăn gì và nghỉ ở đâu?")
    st.write(destination["food"])
    st.write("Nơi lưu trú nên được chọn theo tuyến đi, số người và ngân sách. Bạn có thể xem dự toán ăn uống và lưu trú khi lập lịch trình.")
    st.markdown("### Trước khi khởi hành")
    for tip in destination["tips"]:
        st.write("• " + tip)
with aside:
    with st.container(border=True, key="destination-practical"):
        st.markdown("### Chuyến đi theo cách của bạn")
        st.caption("KHU VỰC")
        st.write(destination["area"])
        st.caption("SỞ THÍCH PHÙ HỢP")
        st.write(" · ".join(destination["interests"]))
        st.markdown("---")
        st.write("Chuyển các sở thích này sang form để tạo hành trình phù hợp với số ngày và ngân sách của bạn.")
        if st.button("Lên lịch trình với sở thích này", type="primary", width="stretch"):
            draft = dict(st.session_state.get("trip_draft", {}))
            draft["interests"] = destination["interests"].copy()
            st.session_state.trip_draft = draft
            for key in list(st.session_state):
                if key.startswith("planner-") or key.startswith("adjust-"):
                    del st.session_state[key]
            st.session_state.show_trip_preview = False
            st.switch_page("views/blank.py")
        st.caption("Giá, giờ mở cửa và dịch vụ cần được xác nhận trước khi đi. Trang lập lịch trình hiện dùng giá và lưu trú giả lập để dự toán.")

st.markdown("<div class='dl-spacer'></div>", unsafe_allow_html=True)
section_title("Tiếp tục khám phá", "Một góc khác của Đắk Lắk")
related = [(key, item) for key, item in DESTINATIONS.items() if key != slug]
for column, (key, item) in zip(st.columns(len(related), gap="large"), related):
    with column:
        destination_card(item["name"], item["category"], item["description"], item["image"], item["image_label"], slug=key)
footer()
