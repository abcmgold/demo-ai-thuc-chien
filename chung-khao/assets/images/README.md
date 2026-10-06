# Ảnh giao diện

| Tệp | Vị trí sử dụng |
|---|---|
| `hero-daklak.jpg` | Ảnh mở đầu trang Khám phá; dùng lại ở thẻ cảm hứng trang Lên lịch trình |
| `cafe-buon-ma-thuot.jpeg` | Thẻ điểm đến Buôn Ma Thuột |
| `dray-nur.jpg` | Thẻ điểm đến thác Dray Nur |
| `ho-lak.jpg` | Thẻ điểm đến Hồ Lắk |

Ảnh mới cho giao diện đặt trong thư mục này. Hàm `image_slot()` nhận tên tệp tương đối với thư mục `images/`.

Trang chủ dùng cả 4 ảnh trong slideshow tự động và dải ảnh khám phá. Ba địa điểm Buôn Ma Thuột, thác Dray Nur, Hồ Lắk có trang chi tiết riêng. Nội dung và ánh xạ ảnh được khai báo ở `chung-khao/destinations.py`; ảnh mới cần được thêm vào danh sách `SLIDES` để xuất hiện trong slideshow và dải ảnh.
