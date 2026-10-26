---
title: 15. Canny edge
lesson: lesson12_differentiation_edges
after: Canny
---
| Đặc tính hình học | Toán tử Sobel | Thuật toán Canny |
|---|---|---|
| Bản chất kiến trúc | Phép toán lọc đạo hàm bậc một, gồm 1 bước chính. | Quy trình xử lý đa giai đoạn: lọc nhiễu, khử cực đại và ngưỡng trễ. |
| Độ dày đường biên | Dày và nhòe, thường có nhiều pixel chồng lấn. | Mỏng tuyệt đối, rộng đúng 1 pixel nhờ bước NMS. |
| Khả năng chống nhiễu | Trung bình, dễ bị sót các hạt nhiễu sáng rải rác. | Tốt, lọc bỏ nhiễu cô lập nhờ bước hysteresis. |
| Kết quả đầu ra | Ảnh xám chứa biên độ dốc thực tế. | Ảnh nhị phân thuần túy, cạnh trắng trên nền đen. |

- Quy trình của thuật toán Canny
    - GD1: Giảm nhiễu
        - Cho ảnh grayscale đầu vào qua bộ lọc Gaussian 5x5
        - Lưu ý: `cv2.Canny` **không** tự làm mờ, bước này phải tự gọi `GaussianBlur` trước
    - GD2: Tìm gradient cường độ ảnh
        - $G = \sqrt{G_x^2 + G_y^2}$ or $G \approx |G_x| + |G_y|$
        - $\theta = \text{atan2}(G_y, G_x)$
        - Hướng của gradient luôn vuông góc với đường biên của cạnh
        - Giá trị góc này sẽ được làm tròn về 1 trong 4 hướng: 0°, 45°, 90°, 135°
    - GD3: Triệt tiêu phi cực đại - Loại trừ cạnh dày
        - Tại mỗi pixel A kiểm tra xem $G_A$ có max trong vùng lân cận dọc theo Gradient không
        - Nếu $G_A$ max thì sẽ giữ lại
        - Nếu $G_A$ không phải là max thì là cạnh giả đặt về 0 ( nền đen)
    - GD4: Ngưỡng trễ:
        - Chọn hai ngưỡng `minVal` và `maxVal`
        - Cạnh chắc chắn (Sure-edge): $G_A$ > `maxVal`
        - Không phải cạnh (Non-edge): $G_A$ < `minVal`
        - Cạnh yếu (Weak-edge): `minVal` < $G_A$ < `maxVal`
            - Nếu A kết nối với một cạnh chắc chắn thì nó được thăng cấp thành cạnh
            - Nếu A bị cô lập với cạnh chắc chắn thì xóa bỏ nó
        - Hệ quả:
            - Loại bỏ các đốm nhỏ nhiễu pixel, cạnh giả

        ![](img/opencv-notes/15-canny-edge-1.png)

- Hàm `cv2.Canny(image, threshold1, threshold2, apertureSize=3, L2gradient=False)`
- Nhớ áp dụng bộ lọc `blur = cv2.GaussianBlur(img, (5, 5), 0)`

    | Tham số | Ý nghĩa |
    |---|---|
    | `image` | Ảnh đầu vào, thường là ảnh xám 8-bit. |
    | `threshold1` | Giá trị ngưỡng thấp (`minVal`). |
    | `threshold2` | Giá trị ngưỡng cao (`maxVal`). |
    | `apertureSize` | Kích thước của mặt nạ Sobel dùng để tính gradient ở giai đoạn 2. Mặc định bằng `3`. |
    | `L2gradient` | Quyết định công thức tính độ lớn gradient $G$. Mặc định là `False`. |

    - $G = \sqrt{G_x^2 + G_y^2}$ nếu `L2gradient = True`
    - $G \approx |G_x| + |G_y|$ nếu `L2gradient = False`
