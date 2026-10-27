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

        :::proof dạng pháp tuyến của đường thẳng và vì sao mỗi điểm thành một đường sin
        **1. Dạng pháp tuyến.** Gọi $\mathbf{n} = (\cos\theta, \sin\theta)$ là vector đơn vị vuông góc với đường thẳng, $P_0 = \rho\,\mathbf{n}$ là chân đường vuông góc hạ từ gốc (cách gốc đúng $\rho$). Điểm $X = (x, y)$ nằm trên đường thẳng khi và chỉ khi $X - P_0$ song song với đường, tức vuông góc với $\mathbf{n}$:

        $$(X - \rho\,\mathbf{n}) \cdot \mathbf{n} = 0 \iff X \cdot \mathbf{n} = \rho\,(\mathbf{n} \cdot \mathbf{n}) = \rho \iff x\cos\theta + y\sin\theta = \rho \qquad \blacksquare$$

        Mọi đường thẳng (kể cả thẳng đứng: $\theta = 0$, $x = \rho$) đều có dạng này, với $\theta \in [0, \pi)$ và $\rho$ có dấu.

        **2. Miền giá trị hữu hạn.** Với ảnh $W \times H$, theo Cauchy–Schwarz $|\rho| = |X \cdot \mathbf{n}| \le |X|\,|\mathbf{n}| = |X| \le \sqrt{W^2 + H^2}$. Cả $\rho$ và $\theta$ đều bị chặn, nên mảng tích lũy có kích thước cố định: khoảng $2\sqrt{W^2+H^2}/\text{rho} \times \pi/\text{theta}$ ô. Dạng $y = mx + c$ có $m \in (-\infty, \infty)$ nên không thể chia ô hữu hạn.

        **3. Mỗi điểm biên vẽ một đường sin trong không gian $(\theta, \rho)$.** Cố định điểm $(x_0, y_0)$, viết $x_0 = R\cos\varphi$, $y_0 = R\sin\varphi$ với $R = \sqrt{x_0^2 + y_0^2}$:

        $$\rho(\theta) = R\cos\varphi\cos\theta + R\sin\varphi\sin\theta = R\cos(\theta - \varphi)$$

        Đây là tập mọi đường thẳng đi qua $(x_0, y_0)$.

        **4. Hai điểm → các đường sin cắt nhau đúng một lần, tại đường thẳng nối chúng.** Hai đường cong của $(x_1, y_1)$ và $(x_2, y_2)$ cắt nhau khi

        $$x_1\cos\theta + y_1\sin\theta = x_2\cos\theta + y_2\sin\theta \iff (x_1 - x_2)\cos\theta + (y_1 - y_2)\sin\theta = 0$$

        tức $\mathbf{n} \perp (P_1 - P_2)$: pháp tuyến vuông góc với đoạn nối hai điểm. Trong $[0, \pi)$ chỉ có đúng một hướng như vậy, và nó xác định đúng đường thẳng qua $P_1$, $P_2$. Tổng quát: $k$ điểm thẳng hàng cho $k$ đường sin **cùng đi qua một ô** → ô đó nhận $k$ phiếu. $\blacksquare$ Đó là lý do "ô nhiều phiếu = nhiều điểm thẳng hàng", kể cả khi đường bị đứt đoạn hay lẫn nhiễu (điểm nhiễu chỉ rải phiếu đều ra nhiều ô).

        **5. Vì sao Hough Gradient cho đường tròn rẻ hơn.** Không gian $(x_c, y_c, r)$ có 3 chiều. Nhưng tại một điểm biên của đường tròn, gradient hướng theo **bán kính** (gradient vuông góc với biên – xem ghi chú Gradient), nên tâm phải nằm trên đường thẳng qua điểm đó theo hướng gradient. Mỗi điểm biên chỉ cần bỏ phiếu dọc một đoạn thẳng trong mặt phẳng $(x_c, y_c)$ (2D). Tìm được tâm rồi mới chọn $r$ bằng histogram khoảng cách từ tâm tới các điểm biên (1D).
        :::

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
