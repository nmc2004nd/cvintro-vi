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

        :::proof vì sao triệt tiêu phi cực đại tìm đúng tâm cạnh
        **1. Cạnh nằm ở đỉnh của độ lớn gradient theo hướng gradient.** Cắt ảnh dọc theo hướng gradient $\mathbf{n}$ qua một điểm biên, ta được hồ sơ cường độ 1D $f(s)$: một bậc thang đã bị làm mờ, có dạng chữ S. Độ lớn gradient trên lát cắt là $|f'(s)|$. Tâm cạnh là nơi cường độ đổi nhanh nhất, tức $|f'|$ cực đại, tức

        $$\frac{d}{ds}f'(s) = f''(s) = 0 \quad \text{và } f' \ne 0$$

        (chính là *điểm uốn* của chữ S, cũng là điểm cắt không của Laplace theo hướng $\mathbf{n}$). Sau khi làm mờ, $|f'|$ là một "quả đồi" rộng vài pixel, nên ngưỡng trực tiếp sẽ cho cạnh dày. Giữ lại *chỉ đỉnh đồi* thì cạnh dày đúng 1 pixel.

        **2. Vì sao chỉ so với 2 hàng xóm dọc theo gradient.** Dọc theo cạnh (vuông góc với gradient), $|\nabla I|$ gần như không đổi – mọi điểm trên cạnh đều cao như nhau, so theo hướng đó sẽ xóa nhầm cạnh. Chỉ theo hướng gradient thì tâm cạnh mới là cực đại địa phương.

        **3. Làm tròn góc về 4 hướng.** Lưới pixel chỉ có 8 hàng xóm, tức 4 trục: 0°, 45°, 90°, 135° (hướng và hướng ngược lại dùng chung một trục, nên xét $\theta \bmod 180°$). Mỗi góc được gán về trục gần nhất, tức các khoảng rộng 45° có tâm tại trục:

        | $\theta \bmod 180°$ | Trục | So với hai pixel |
        |---|---|---|
        | $[0°, 22.5°) \cup [157.5°, 180°)$ | 0° | trái, phải |
        | $[22.5°, 67.5°)$ | 45° | hai pixel chéo theo hướng đó |
        | $[67.5°, 112.5°)$ | 90° | trên, dưới |
        | $[112.5°, 157.5°)$ | 135° | hai pixel chéo còn lại |

        (Với trục $y$ hướng xuống, "45°" nối pixel dưới-phải với trên-trái.) Sai số hướng tối đa là 22.5°, đủ tốt vì ta chỉ cần biết hai hàng xóm nào nằm "phía trước" và "phía sau" của cạnh.

        **4. Hai ngưỡng (hysteresis) không có chứng minh tối ưu** – đây là lựa chọn thiết kế. Canny đề xuất tỉ lệ `maxVal : minVal` khoảng 2:1 đến 3:1 dựa trên thực nghiệm: ngưỡng cao để chắc chắn bắt đầu từ cạnh thật, ngưỡng thấp để nối tiếp cạnh đó qua những đoạn yếu đi (bóng, độ tương phản giảm) mà không bị đứt. Nhiễu cô lập hiếm khi nối liền được tới một cạnh mạnh nên bị loại.

        **Về "tối ưu" của Canny:** Canny (1986) đặt ra ba tiêu chí – phát hiện tốt, định vị chính xác, mỗi cạnh chỉ một phản hồi – rồi giải bài toán biến phân, được một bộ lọc gần giống **đạo hàm của Gauss** (sai khác khoảng 20%). Phép chứng minh này dài và nằm ngoài phạm vi ghi chú; trong thực hành nó là lý do pipeline Canny là "Gauss rồi lấy đạo hàm".
        :::

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
