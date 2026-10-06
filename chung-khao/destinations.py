"""Nội dung khám phá điểm đến, dùng chung cho trang chủ và trang chi tiết."""

DESTINATIONS = {
    "buon-ma-thuot": {
        "name": "Buôn Ma Thuột", "area": "Buôn Ma Thuột", "category": "CÀ PHÊ · VĂN HÓA",
        "image": "cafe-buon-ma-thuot.jpeg", "image_label": "Không gian văn hóa cà phê ở Buôn Ma Thuột",
        "description": "Nhịp phố cao nguyên, câu chuyện cà phê và những không gian văn hóa.",
        "intro": "Bắt đầu hành trình từ Buôn Ma Thuột để cảm nhận nhịp sống phố núi và văn hóa cà phê. Một buổi khám phá không gian văn hóa, một khoảng nghỉ ở quán cà phê và những món ăn địa phương là gợi ý cho ngày đầu tiên nhẹ nhàng.",
        "interests": ["Cà phê", "Văn hóa", "Ẩm thực"],
        "highlights": [
            ("Câu chuyện cà phê", "Tìm hiểu không gian trưng bày tại Bảo tàng Thế giới Cà phê hoặc thưởng thức cà phê theo khẩu vị của bạn."),
            ("Những điểm dừng văn hóa", "Tham khảo Bảo tàng Đắk Lắk, Buôn Akô Dhông và chùa Sắc Tứ Khải Đoan khi chọn điểm tham quan trong thành phố."),
            ("Nhịp phố và món ngon", "Dành một khoảng nghỉ để thưởng thức cà phê hoặc tìm hiểu các món ăn địa phương như bún đỏ."),
        ],
        "tips": ["Hỏi giá và kiểm tra giờ hoạt động của từng địa điểm trước khi đi.", "Xin phép trước khi chụp ảnh người dân hoặc không gian sinh hoạt.", "Khi tham quan địa điểm tín ngưỡng, chọn trang phục và cách ứng xử phù hợp."],
        "food": "Cà phê và bún đỏ là những gợi ý để bắt đầu tìm hiểu ẩm thực địa phương; chọn quán theo khẩu vị và nhu cầu của nhóm.",
    },
    "dray-nur": {
        "name": "Thác Dray Nur", "area": "Khu vực Krông Ana", "category": "THIÊN NHIÊN · THÁC NƯỚC",
        "image": "dray-nur.jpg", "image_label": "Cảnh quan thác Dray Nur",
        "description": "Dành một ngày gần thiên nhiên, ngắm dòng thác và cảnh quan quanh vùng.",
        "intro": "Thác Dray Nur là một gợi ý cho người muốn dành thời gian giữa thiên nhiên trong chuyến khám phá Đắk Lắk. Bạn có thể ưu tiên ngắm cảnh, chụp ảnh ở khu vực được phép và nghỉ ngơi theo nhịp đi của nhóm.",
        "interests": ["Thiên nhiên"],
        "highlights": [
            ("Ngắm cảnh thác", "Chọn vị trí tham quan được phép để quan sát cảnh quan và dòng nước."),
            ("Một khoảng nghỉ giữa thiên nhiên", "Giữ lịch trình đủ thoáng để ngắm cảnh, nghỉ ngơi và quay về khi điều kiện phù hợp."),
            ("Góc ảnh của riêng bạn", "Tìm góc chụp tại lối đi và điểm dừng được phép, tránh mép nước và bề mặt trơn."),
        ],
        "tips": ["Kiểm tra thời tiết và thông báo của khu tham quan trước khi khởi hành.", "Mang giày có độ bám, tuân thủ biển báo và hướng dẫn tại thác.", "Không xuống nước hoặc đi vào khu vực bị hạn chế; mang rác về đúng nơi quy định."],
        "food": "Chuẩn bị nước uống, hỏi trước về lựa chọn ăn uống trên tuyến và dành thời gian nghỉ phù hợp. Dịch vụ cụ thể cần được xác nhận tại địa phương.",
    },
    "ho-lak": {
        "name": "Hồ Lắk", "area": "Khu vực Lắk", "category": "HỒ · TRẢI NGHIỆM BẢN ĐỊA",
        "image": "ho-lak.jpg", "image_label": "Cảnh quan Hồ Lắk",
        "description": "Không gian mặt hồ và những trải nghiệm gắn với đời sống địa phương.",
        "intro": "Hồ Lắk mang đến một nhịp khám phá chậm hơn: ngắm cảnh mặt hồ, tìm hiểu đời sống địa phương và dành thời gian cho các trải nghiệm văn hóa phù hợp. Đây là gợi ý cho chuyến đi kết hợp cảnh quan và sự kết nối với cộng đồng.",
        "interests": ["Thiên nhiên", "Văn hóa", "Trải nghiệm bản địa"],
        "highlights": [
            ("Không gian mặt hồ", "Dành thời gian ngắm cảnh và chụp ảnh ở những vị trí tham quan được phép."),
            ("Tìm hiểu văn hóa địa phương", "Chọn hoạt động do cộng đồng địa phương giới thiệu, hỏi trước quy tắc ứng xử và điều kiện tham gia."),
            ("Một hành trình chậm", "Kết hợp tham quan với nghỉ ngơi, tránh dồn nhiều hoạt động khi chưa biết thời gian di chuyển thực tế."),
        ],
        "tips": ["Xin phép trước khi chụp ảnh người dân và không gian sinh hoạt.", "Nếu tham gia hoạt động trên mặt nước, xác nhận điều kiện an toàn và tuân thủ hướng dẫn.", "Hỏi rõ chi phí, phạm vi dịch vụ và quy định của cộng đồng trước khi tham gia."],
        "food": "Tìm hiểu món ăn và nguyên liệu địa phương qua người cung cấp dịch vụ; trao đổi trước về dị ứng và yêu cầu ăn uống của nhóm.",
    },
}

SLIDES = [
    {"image": "dray-nur.jpg", "title": "Chạm vào nhịp thở của thiên nhiên", "subtitle": "Thác Dray Nur · Cảm hứng cho một ngày khám phá", "slug": "dray-nur"},
    {"image": "ho-lak.jpg", "title": "Chậm lại bên Hồ Lắk", "subtitle": "Cảnh quan mặt hồ · Những trải nghiệm bản địa", "slug": "ho-lak"},
    {"image": "cafe-buon-ma-thuot.jpeg", "title": "Một thành phố, nhiều câu chuyện cà phê", "subtitle": "Buôn Ma Thuột · Văn hóa và nhịp sống phố núi", "slug": "buon-ma-thuot"},
    {"image": "hero-daklak.jpg", "title": "Đắk Lắk qua những khung hình", "subtitle": "Cao nguyên · Cảm hứng hành trình từ ảnh bạn cung cấp", "slug": None},
]
