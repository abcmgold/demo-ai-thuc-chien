"""Nhập nhu cầu, tạo và điều chỉnh lịch trình từ dữ liệu mẫu."""

from copy import deepcopy
from html import escape

import streamlit as st

from nexus import get_settings
from nexus.travel import (
    COMFORTS, DISCLOSURE, INTERESTS, TRANSPORTS, PlanningError,
    daily_cost, eligible_samples, generate_plan, hotel_cost, hotel_samples, revise_plan,
)
from travel_search import SearchDataError, search_and_append
from ui import footer, image_slot, page_header
from travel_export import export_plan_excel


def money(value: int) -> str:
    return f"{value:,}".replace(",", ".") + " VNĐ"


def render_request_form() -> None:
    draft = st.session_state.get("trip_draft", {})
    page_header("THIẾT KẾ CHUYẾN ĐI", "Lên lịch trình Đắk Lắk", "Chọn nhu cầu của bạn để nhận kế hoạch và dự toán rõ ràng.")
    st.markdown('<div class="dl-stepper"><span class="is-active"><b>1</b> Nhu cầu của bạn</span><i></i><span><b>2</b> Xem lịch trình</span></div>', unsafe_allow_html=True)
    form_col, side_col = st.columns([1.45, 0.75], gap="large")
    with form_col:
        with st.container(border=True, key="planner-form-card"):
            st.markdown('<div class="dl-form-heading">Chuyến đi của bạn</div>', unsafe_allow_html=True)
            with st.form("trip-details-form", border=False):
                people_col, days_col = st.columns(2)
                with people_col:
                    people = st.number_input("Số người", min_value=1, max_value=30, value=draft.get("people", 2), step=1, key="planner-people")
                with days_col:
                    days = st.number_input("Số ngày", min_value=1, max_value=14, value=draft.get("days", 3), step=1, key="planner-days")
                budget_col, basis_col = st.columns([1.25, 0.75])
                with budget_col:
                    budget = st.number_input("Ngân sách dự kiến (VNĐ)", min_value=0, value=draft.get("budget", 6000000), step=500000, format="%d", key="planner-budget")
                with basis_col:
                    basis_options = ["Cả nhóm", "Mỗi người"]
                    budget_basis = st.selectbox("Ngân sách tính cho", basis_options, index=basis_options.index(draft.get("budget_basis", "Cả nhóm")), key="planner-budget-basis")
                interests = st.multiselect("Sở thích của bạn", INTERESTS, default=draft.get("interests", ["Thiên nhiên", "Cà phê"]), key="planner-interests")
                with st.expander("Tùy chỉnh thêm", expanded=False):
                    start_area = st.selectbox("Điểm bắt đầu", ["Buôn Ma Thuột", "Đến từ nơi khác", "Chưa xác định"], key="planner-start")
                    transport = st.selectbox("Phương tiện chính", list(TRANSPORTS), key="planner-transport")
                    comfort = st.selectbox("Mức tiện nghi", list(COMFORTS), key="planner-comfort")
                    pace = st.select_slider("Nhịp độ chuyến đi", options=["Thư thả", "Cân bằng", "Khám phá nhiều"], value="Cân bằng", key="planner-pace")
                    meals = st.number_input("Số bữa dự trù mỗi ngày", min_value=1, max_value=3, value=draft.get("meals_per_day", 3), key="planner-meals")
                    custom_nights = st.checkbox("Tự chọn số đêm lưu trú", value=draft.get("custom_nights", False), key="planner-custom-nights")
                    nights = st.number_input("Số đêm khi tự chọn", min_value=0, max_value=14, value=draft.get("nights", max(0, int(days) - 1)), key="planner-nights")
                    st.caption("Mặc định lưu trú bằng số ngày trừ 1. Khi tự chọn, số đêm không được vượt số ngày.")
                submitted = st.form_submit_button("Tạo lịch trình của tôi", type="primary", width="stretch")
            if submitted:
                request = {"people": int(people), "days": int(days), "budget": int(budget),
                           "budget_basis": budget_basis, "interests": interests, "start_area": start_area,
                           "transport": transport, "comfort": comfort, "pace": pace,
                           "nights": int(nights) if custom_nights else int(days) - 1,
                           "meals_per_day": int(meals), "custom_nights": custom_nights}
                st.session_state.trip_draft = request
                try:
                    with st.spinner("Đang chọn điểm đến và kiểm tra dự toán cho chuyến đi…"):
                        search_and_append(request)
                        plan = generate_plan(request)
                except (PlanningError, SearchDataError) as error:
                    st.error(str(error))
                except Exception as error:
                    if not get_settings().api_key:
                        st.error("Chưa cấu hình THUCCHIEN_API_KEY để tạo lịch trình.")
                    else:
                        status = getattr(error, "status_code", None)
                        message = {401: "Không xác thực được kết nối AI. Kiểm tra cấu hình API key.",
                                   429: "Dịch vụ AI đang giới hạn yêu cầu hoặc đã hết hạn mức. Vui lòng thử lại sau."}.get(status)
                        st.error(message or "Chưa tìm được dữ liệu du lịch đầy đủ hoặc chưa kết nối được dịch vụ AI. Vui lòng thử lại với tiêu chí khác.")
                else:
                    for key in list(st.session_state):
                        if key.startswith("adjust-"):
                            del st.session_state[key]
                    st.session_state.travel_plan = plan
                    st.session_state.show_trip_preview = True
                    st.rerun()
    with side_col:
        with st.container(border=True, key="planner-aside"):
            image_slot("hero-daklak.jpg", "Cảm hứng hành trình cao nguyên", height=175)
            st.markdown('<div class="dl-aside-title">Một kế hoạch vừa vặn</div>', unsafe_allow_html=True)
            st.write("Chọn điểm đến theo sở thích, dự trù ăn uống, di chuyển và lưu trú theo ngân sách.")
            st.markdown('<div class="dl-aside-points"><span>01</span> Nhập nhu cầu chuyến đi<span>02</span> Nhận hành trình và dự toán<span>03</span> Điều chỉnh trước khi khởi hành</div>', unsafe_allow_html=True)
            st.info(DISCLOSURE)
            st.caption("Phạm vi dữ liệu: 10 điểm đến. Mỗi ngày một điểm chính, xuất phát và quay về Buôn Ma Thuột. Chi phí đến/rời Đắk Lắk chưa được tính.")


def render_adjustments(plan: dict) -> None:
    request = plan["request"]
    samples = {sample["id"]: sample for sample in eligible_samples(request)}
    hotels = {sample["id"]: sample for sample in hotel_samples(request)}
    def sample_label(sample_id: str) -> str:
        sample = samples[sample_id]
        return f"{sample['travel_location']['name']} · {sample['profile_label']} · {money(daily_cost(sample, request)['total'])}/ngày"
    def lodging_label(sample_id: str) -> str:
        sample = hotels[sample_id]
        return f"{sample['hotel']['name']} · {money(hotel_cost(sample, request)['total'])}/chuyến"
    with st.expander("Đổi điểm đến hoặc nơi lưu trú"):
        st.caption("Dự toán được tính lại theo lựa chọn. Nếu vượt ngân sách, bạn vẫn có thể áp dụng và xem số tiền vượt; điểm đến trùng cần được điều chỉnh.")
        with st.form("adjust-plan"):
            selected = []
            ids = list(samples)
            for day in plan["days"]:
                selected.append(st.selectbox(f"Điểm đến ngày {day['day']}", ids,
                                            index=ids.index(day["sample_id"]), format_func=sample_label,
                                            key=f"adjust-day-{day['day']}"))
            hotel_id = None
            if plan["lodging"]:
                hotel_ids = list(hotels)
                hotel_id = st.selectbox("Lưu trú toàn chuyến", hotel_ids, index=hotel_ids.index(plan["lodging"]["sample_id"]),
                                        format_func=lodging_label, key="adjust-hotel")
            submitted = st.form_submit_button("Áp dụng và tính lại dự toán", type="primary")
        if submitted:
            selection = deepcopy(plan["selection"])
            selection["hotel_sample_id"] = hotel_id
            changed = False
            for day, sample_id in zip(selection["days"], selected):
                if day["sample_id"] != sample_id:
                    changed = True
                    day.update(sample_id=sample_id, reason="Điểm đến do bạn lựa chọn khi điều chỉnh lịch trình.")
            if changed:
                selection["summary"] = "Hành trình Đắk Lắk đã được điều chỉnh theo lựa chọn của bạn."
            try:
                updated = revise_plan(plan, selection)
            except PlanningError as error:
                st.error(str(error))
            else:
                st.session_state.travel_plan = updated
                st.rerun()


def render_preview() -> None:
    plan = st.session_state.travel_plan
    request = plan["request"]
    page_header("HÀNH TRÌNH CỦA BẠN", "Đắk Lắk · Khám phá theo cách của bạn", f"{request['people']} người · {request['days']} ngày · {request['nights']} đêm")
    st.info(DISCLOSURE)
    st.write(plan["summary"])
    if plan.get("manually_adjusted"):
        st.caption("Bạn đã điều chỉnh kế hoạch sau khi nhận gợi ý.")
    if st.button("Sửa tiêu chí", icon="✏️"):
        st.session_state.show_trip_preview = False
        for key in list(st.session_state):
            if key.startswith("adjust-"):
                del st.session_state[key]
        st.rerun()
    over_budget = max(0, plan["total_vnd"] - request["group_budget_vnd"])
    if over_budget:
        st.warning(f"Dự toán {money(plan['total_vnd'])} vượt ngân sách cả nhóm {money(request['group_budget_vnd'])} là {money(over_budget)}. Bạn vẫn có thể xem và điều chỉnh lịch trình bên dưới.")
    with st.container(key="trip-budget-metrics"):
        totals = st.columns(4)
    budget_label = "Vượt ngân sách" if over_budget else "Còn lại trong ngân sách"
    budget_difference = over_budget if over_budget else plan["remaining_vnd"]
    for column, label, value in zip(totals, ["Dự toán cả nhóm", "Bình quân/người", "Ngân sách cả nhóm", budget_label],
                                    [plan["total_vnd"], plan["per_person_vnd"], request["group_budget_vnd"], budget_difference]):
        column.metric(label, money(value))
    st.caption("Dự toán chưa gồm chi phí ngoài phạm vi và dự phòng. Bình quân/người làm tròn lên đến 1 VNĐ.")
    tabs = st.tabs([f"Ngày {day['day']}" for day in plan["days"]])
    for tab, day in zip(tabs, plan["days"]):
        with tab:
            location, food, transport, costs = day["location"], day["food"], day["transport"], day["costs"]
            route_col, timeline_col = st.columns([0.75, 1.25], gap="large")
            with route_col:
                st.markdown(f'<div class="dl-route-heading">Tuyến ngày {day["day"]}</div><div class="dl-route-name">{escape(location["name"])}</div>', unsafe_allow_html=True)
                image_name = {"Thác Dray Nur": "dray-nur.jpg", "Hồ Lắk": "ho-lak.jpg"}.get(location["name"], "cafe-buon-ma-thuot.jpeg" if location["area"] == "Buôn Ma Thuột" else "hero-daklak.jpg")
                image_slot(image_name, "Ảnh gợi cảm hứng khu vực", height=190)
                with st.container(border=True):
                    st.write("Trung tâm Buôn Ma Thuột")
                    st.write(f"↓ {location['name']} · {location['area']}")
                    st.write("↓ Trở về Buôn Ma Thuột")
                    st.caption("Thứ tự định hướng; chưa có thời gian di chuyển và giờ hoạt động xác minh.")
                st.caption(f"Nguồn mẫu: {day['sample_id']}")
            with timeline_col:
                with st.container(border=True):
                    st.markdown(f"### {location['name']}")
                    st.write(day["reason"])
                    st.write(f"Vé: {request['people']} người × {money(location['entrance_cost_vnd_per_person'])} = {money(costs['tickets'])}")
                with st.container(border=True):
                    st.markdown("### Ăn uống và nghỉ ngơi")
                    st.write(f"Món tham khảo: {food['item']}")
                    st.write(f"{request['people']} người × {request['meals_per_day']} bữa × {money(food['cost_vnd_per_person_per_meal'])} = {money(costs['food'])}")
                    st.caption("Các bữa dùng chung đơn giá để dự trù; chưa có thực đơn và quán ăn xác minh.")
                with st.container(border=True):
                    st.markdown("### Di chuyển khứ hồi")
                    st.write(f"Phương tiện mẫu: {transport['mode']}")
                    st.write(f"{costs['transport_packages']} gói mẫu × {money(transport['cost_vnd_per_group_round_trip'])} = {money(costs['transport'])}")
                    st.caption(f"Mỗi gói tham chiếu cho {transport['reference_party_size']} người. Đây là giả định chi phí, chưa xác nhận số xe và sức chứa.")
                st.markdown(f"**Tổng ngày {day['day']}: {money(costs['total'])}** · chưa gồm lưu trú")
    st.markdown("### Lưu trú toàn chuyến")
    lodging = plan["lodging"]
    if lodging:
        st.write(f"{lodging['name']} · {lodging['area']}")
        st.write(f"{lodging['rooms']} phòng × {lodging['nights']} đêm × {money(lodging['cost_vnd_per_room_per_night'])} = {money(lodging['total'])}")
        st.caption(f"Sức chứa mẫu: {lodging['room_capacity_persons']} người/phòng · Mã nguồn {lodging['sample_id']}. Tên lưu trú giả lập, chưa có địa chỉ hay khả năng đặt phòng.")
    else:
        st.write("Bạn chọn không tính lưu trú.")
    st.markdown("### Chi phí theo hạng mục")
    cols = st.columns(4)
    for col, key, label in zip(cols, ["tickets", "food", "transport", "lodging"], ["Vé tham quan", "Ăn uống", "Di chuyển", "Lưu trú"]):
        with col:
            st.markdown(f'<div class="dl-budget-item"><span>{label}</span><b>{money(plan["costs"][key])}</b></div>', unsafe_allow_html=True)
    render_adjustments(plan)
    with st.expander("Phạm vi dự toán và điều cần xác nhận", expanded=True):
        for warning in plan["warnings"][1:]:
            st.write("• " + warning)
        st.write("Tôn trọng quy định tại điểm tham quan và cộng đồng địa phương; xác nhận thông tin dịch vụ trước khi khởi hành.")
    st.download_button("Tải lịch trình Excel", data=export_plan_excel(plan),
                       file_name="lich-trinh-dak-lak.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if st.session_state.get("show_trip_preview") and st.session_state.get("travel_plan"):
    render_preview()
else:
    render_request_form()
footer()
