---
title: 21. Hough Transform
lesson: lesson12_differentiation_edges
after: Hough
draft: true
---
| Hàm | Kết quả | Ứng dụng |
|---|---|---|
| `cv.HoughLines()` | Danh sách $(\rho, \theta)$ của các đường thẳng vô hạn | Tìm hướng chính, đường chân trời |
| `cv.HoughLinesP()` | Danh sách đoạn thẳng $(x_1, y_1, x_2, y_2)$ | Phát hiện làn đường, cạnh vật thể |
| `cv.HoughCircles()` | Danh sách $(x, y, r)$ | Đếm đồng xu, phát hiện con ngươi, biển báo tròn |

- Hough Transform tìm các hình dạng có thể ==biểu diễn bằng công thức toán học== (đường thẳng, đường tròn), kể cả khi hình bị đứt đoạn hoặc có nhiễu
- ==Đầu vào là ảnh nhị phân==: thường là kết quả của Canny hoặc threshold
- ==**Hough Lines**==
    - Đường thẳng viết dạng tham số: $\rho = x\cos\theta + y\sin\theta$
        - $\rho$: khoảng cách vuông góc từ gốc tọa độ (góc trên trái) tới đường thẳng
        - $\theta$: góc giữa đường vuông góc đó và trục ngang, tính theo radian
        - Dạng $y = mx + c$ không biểu diễn được đường thẳng đứng ($m = \infty$) nên không dùng
    - Cơ chế bỏ phiếu (voting):
        - Tạo mảng tích lũy (accumulator) 2D: hàng là $\rho$, cột là $\theta$, ban đầu bằng 0
        - Với mỗi điểm biên (x, y), thử mọi $\theta$, tính $\rho$ tương ứng rồi cộng 1 vào ô $(\rho, \theta)$
        - ==Ô nào có nhiều phiếu → có nhiều điểm cùng nằm trên một đường thẳng==
    - Hàm: `lines = cv.HoughLines(edges, rho, theta, threshold)`
        - `rho`: độ phân giải của $\rho$ (pixel), thường 1
        - `theta`: độ phân giải của $\theta$ (radian), thường `np.pi / 180`
        - `threshold`: số phiếu tối thiểu để coi là một đường thẳng
        - Trả về mảng shape (N, 1, 2) gồm các cặp $(\rho, \theta)$

    ```python
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray, 50, 150, apertureSize=3)
    lines = cv.HoughLines(edges, 1, np.pi / 180, 150)

    for rho, theta in lines[:, 0]:
        a, b = np.cos(theta), np.sin(theta)
        x0, y0 = a * rho, b * rho                          # chân đường vuông góc
        # đi 1000 pixel về hai phía để vẽ đường "vô hạn"
        pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * a))
        pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * a))
        cv.line(img, pt1, pt2, (0, 0, 255), 2)
    ```

- ==**Probabilistic Hough (HoughLinesP)**==
    - Chỉ bỏ phiếu bằng một tập con điểm ngẫu nhiên → ==nhanh hơn==
    - ==Trả về trực tiếp hai đầu mút của đoạn thẳng== → dễ dùng hơn
    - Thêm hai tham số:
        - `minLineLength`: đoạn ngắn hơn giá trị này bị loại
        - `maxLineGap`: khoảng hở tối đa giữa hai đoạn để vẫn gộp thành một đường

    ```python
    lines = cv.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=80, maxLineGap=5)
    for x1, y1, x2, y2 in lines[:, 0]:
        cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    ```

    ![](img/opencv-notes/21-hough-transform-1.png)

- ==**Hough Circles**==
    - Đường tròn: $(x - x_c)^2 + (y - y_c)^2 = r^2$ → 3 tham số, bỏ phiếu 3D rất tốn bộ nhớ
    - OpenCV dùng **Hough Gradient Method**: dùng hướng gradient tại điểm biên để bỏ phiếu cho tâm, sau đó mới tìm bán kính
    - ==Đầu vào là ảnh xám 8-bit, không phải ảnh Canny== (hàm tự gọi Canny bên trong)
    - Hàm: `circles = cv.HoughCircles(img, method, dp, minDist, param1, param2, minRadius, maxRadius)`

    | Tham số | Ý nghĩa |
    |---|---|
    | `method` | `cv.HOUGH_GRADIENT` (hoặc `cv.HOUGH_GRADIENT_ALT` từ OpenCV 4.3, chính xác hơn) |
    | `dp` | Tỷ lệ nghịch độ phân giải accumulator; 1 = cùng độ phân giải ảnh |
    | `minDist` | Khoảng cách tối thiểu giữa hai tâm; nhỏ quá → nhiều vòng trùng, lớn quá → sót |
    | `param1` | Ngưỡng cao của Canny bên trong (ngưỡng thấp = một nửa) |
    | `param2` | Ngưỡng phiếu cho tâm; ==nhỏ hơn → nhiều vòng hơn, kể cả vòng giả== |
    | `minRadius`, `maxRadius` | Giới hạn bán kính; 0 = không giới hạn |

    ```python
    img = cv.medianBlur(img, 5)                          # giảm nhiễu trước
    circles = cv.HoughCircles(img, cv.HOUGH_GRADIENT, 1, 20,
                              param1=100, param2=25, minRadius=15, maxRadius=50)
    circles = np.uint16(np.around(circles))
    for x, y, r in circles[0]:
        cv.circle(cimg, (int(x), int(y)), int(r), (0, 255, 0), 2)   # đường tròn
        cv.circle(cimg, (int(x), int(y)), 2, (0, 0, 255), 3)        # tâm
    ```

    ![](img/opencv-notes/21-hough-transform-2.png)

    - Kết quả rất nhạy với `param2`: trong hình trên `param2=30` chỉ tìm được 4/6 đồng xu, `param2=25` tìm đủ 6
    - Hàm trả về `None` nếu không tìm thấy → ==kiểm tra `if circles is not None` trước khi dùng==
