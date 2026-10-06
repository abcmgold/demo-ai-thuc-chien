# Dữ liệu lịch trình Đắk Lắk

`synthetic_travel_samples.json` là 50 mẫu do người dùng cung cấp: 10 điểm đến × 5 hồ sơ nhóm. Tên điểm đến là nhãn tham khảo; toàn bộ giá, tên lưu trú và phương án vận chuyển đều giả lập, chưa xác minh.

Khi gửi biểu mẫu lịch trình, ứng dụng dùng các tiêu chí chuyến đi để tìm một mẫu mới trên web, trích xuất dữ liệu có nguồn URL và nối vào tệp trước khi tạo lịch trình. Trường chưa tìm được giữ giá trị `null`; mẫu chưa đủ giá hoặc thông tin bắt buộc vẫn được lưu nhưng không dùng để tính lịch trình. Mẫu mới có `source_urls` và `price_status=web_sourced_unverified`; dữ liệu tìm trên web vẫn cần người dùng kiểm tra lại trước khi đặt dịch vụ. Cấu hình `TRAVEL_SEARCH_MODEL` và `TRAVEL_EXTRACTION_MODEL` trong `chung-khao/.env` theo `.env.example`.

Mỗi mẫu web mới lưu `collected_at` theo UTC. Khi tìm lại cùng hồ sơ, quy mô nhóm, số đêm, điểm tham quan, khách sạn, món ăn và phương tiện (không phân biệt chữ hoa, dấu, khoảng trắng), ứng dụng cập nhật mẫu web cũ và giữ nguyên ID thay vì thêm dòng trùng. Mẫu giả lập gốc không bị thay thế. Planner bỏ qua mẫu web quá `TRAVEL_FRESHNESS_DAYS` ngày (mặc định 30) hoặc không có thời điểm thu thập hợp lệ; mẫu cũ vẫn nằm trong JSON để truy vết. `collected_at` chỉ đo tuổi của lần tìm kiếm, không xác nhận ngày cập nhật giá trên website. Giá web vẫn cần kiểm tra lại với nguồn trước khi đặt dịch vụ.

Agent `gpt-6-luna` chọn mã mẫu và giải thích. Python lọc tiêu chí, kiểm tra mã, số ngày, điểm trùng và tính chênh lệch ngân sách; tối đa một lần yêu cầu model sửa kết quả khi cấu trúc hoặc lựa chọn không hợp lệ. Ngân sách là mục tiêu: kể cả khi thấp hơn mốc chi phí tối thiểu hoặc bằng 0, vẫn gọi agent để gợi ý. Kế hoạch và chỉnh sửa vượt ngân sách được chấp nhận, kèm cảnh báo số tiền vượt cho cả nhóm. Mức ngân sách mỗi người được nhân với số người trước khi so sánh.

## Công thức dự toán

- Vé/ngày = số người × giá vé/người.
- Ăn/ngày = số người × số bữa/ngày × đơn giá bữa trong mẫu. Món ăn chỉ minh họa, không đại diện thực đơn của toàn bộ bữa.
- Di chuyển/ngày = `ceil(số người / số người nhóm mẫu)` × giá khứ hồi của nhóm mẫu. Ưu tiên mẫu đúng số người khi có. Nhân gói mẫu là giả định dự toán, không xác nhận sức chứa xe hay dịch vụ có sẵn.
- Lưu trú/chuyến = `ceil(số người / sức chứa phòng)` × số đêm × đơn giá phòng/đêm. Chỉ chọn một nơi lưu trú tại Buôn Ma Thuột cho cả chuyến vì các hành trình khứ hồi đều xuất phát từ đây.
- Tổng = tổng vé + ăn + di chuyển của mọi ngày + lưu trú một lần. Không cộng trực tiếp `sample_total_vnd` của các mẫu.

Mỗi ngày có một điểm tham quan chính; chưa có tọa độ, giờ mở cửa, thời gian di chuyển hoặc tuyến nhiều điểm. Nếu số ngày lớn hơn số điểm, có thể lặp sau khi đã chọn đủ điểm khác nhau. Chi phí đến/rời Đắk Lắk, hoạt động bổ sung và dự phòng không nằm trong dự toán. Số đêm mặc định bằng số ngày trừ một, cho phép người dùng thay đổi.
