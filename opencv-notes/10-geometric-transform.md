---
title: 10. Geometric Transform
lesson: lesson08_geometric_transformations
after:
---
- Các phép biến đổi hình ảnh:
    - Resize, tịnh tiến, xoay, biến đổi affine,
    - Phối cảnh (PerspectiveTransform)
- Tổng quan:

    | Hàm | Matrix | Ứng dụng |
    |---|---|---|
    | `cv2.warpAffine()` | 2x3 | Scaling, translation, rotation, affine transform |
    | `cv2.warpPerspective()` | 3x3 | Perspective transform, nắn thẳng ảnh bị nghiêng phối cảnh |

- Hàm chung
    - `dst = cv2.warpAffine(src, M, dsize)`
    - `dst = cv2.warpPerspective(src, M, dsize)`
    - Lưu ý: `dsize : (WxH)` khác với `shape (HxWxD)`
- Resize
    - `resized = cv.resize(src, dsize, fx=0, fy=0, interpolation=cv.INTER_LINEAR)`
    - có thể scale theo kích thước `dsize = (WxH)` và `fx =0, fy = 0`
    - có thể scale theo tỷ số tỷ lệ : `fx, fy` và `dsize = None`
    - Các phương pháp nội suy:

        | Interpolation | Khi nên dùng |
        |---|---|
        | `cv2.INTER_AREA` | Thu nhỏ ảnh |
        | `cv2.INTER_LINEAR` | Phóng to ảnh, mặc định trong OpenCV |
        | `cv2.INTER_CUBIC` | Phóng to ảnh chất lượng cao hơn nhưng chậm hơn |

- Translation - tịnh tiến ảnh
    - Tịnh tiến ảnh theo trục x và y
    - Ma trận tịnh tiến

        $$M= \begin{bmatrix} 1 & 0 & dx\\ 0 & 1 & dy \end{bmatrix}$$

        :::proof vì sao ma trận tịnh tiến có kích thước 2x3
        Phép tịnh tiến $x' = x + d_x,\ y' = y + d_y$ **không tuyến tính**: nó đưa gốc $(0, 0)$ tới $(d_x, d_y) \ne (0, 0)$, trong khi mọi ma trận $2 \times 2$ đều giữ nguyên gốc ($A \cdot \mathbf{0} = \mathbf{0}$). Vì vậy không có ma trận $2 \times 2$ nào biểu diễn được phép tịnh tiến.

        **Cách giải: tọa độ đồng nhất.** Thêm thành phần thứ ba bằng 1 vào điểm, $(x, y) \to (x, y, 1)$:

        $$\begin{bmatrix} 1 & 0 & d_x \\ 0 & 1 & d_y \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix} = \begin{bmatrix} 1\cdot x + 0\cdot y + d_x \cdot 1 \\ 0 \cdot x + 1 \cdot y + d_y \cdot 1 \end{bmatrix} = \begin{bmatrix} x + d_x \\ y + d_y \end{bmatrix}$$

        Cột thứ ba nhân với số 1 nên được *cộng thẳng* vào kết quả. Tổng quát, mọi phép affine $\mathbf{x}' = A\mathbf{x} + \mathbf{t}$ đều viết được thành một ma trận $2 \times 3$ là $[A \mid \mathbf{t}]$; đó chính là dạng mà `cv2.warpAffine` nhận vào.
        :::


    - Hàm dùng: `dst = cv2.warpAffine(img, M, dsize)`
- Rotation - xoay ảnh
    - Ma trận xoay trong toán học : 2x2 → xoay quanh gốc tọa độ (0, 0)

        $$M= \begin{bmatrix} \cos\theta & -\sin\theta\\ \sin\theta & \cos\theta \end{bmatrix}$$

        :::proof công thức ma trận xoay
        **Bước 1 – viết điểm theo tọa độ cực.** Một điểm cách gốc $r$, hợp với trục $x$ góc $\varphi$:

        $$x = r\cos\varphi, \qquad y = r\sin\varphi$$

        **Bước 2 – xoay thêm góc $\theta$** (ngược chiều kim đồng hồ trong hệ trục toán học, $y$ hướng lên): khoảng cách $r$ giữ nguyên, góc thành $\varphi + \theta$:

        $$x' = r\cos(\varphi + \theta), \qquad y' = r\sin(\varphi + \theta)$$

        **Bước 3 – khai triển bằng công thức cộng góc:**

        $$x' = r\cos\varphi\cos\theta - r\sin\varphi\sin\theta = x\cos\theta - y\sin\theta$$

        $$y' = r\sin\varphi\cos\theta + r\cos\varphi\sin\theta = x\sin\theta + y\cos\theta$$

        Viết dạng ma trận ra đúng $R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}$. $\blacksquare$

        **Tính chất (kiểm tra trực tiếp):**

        - $R^T R = I$ vì $\cos^2\theta + \sin^2\theta = 1$ và hai cột vuông góc → phép xoay **giữ nguyên độ dài và góc**.
        - $\det R = \cos^2\theta + \sin^2\theta = 1$ → giữ nguyên diện tích, không lật ảnh.
        - $R(\theta)^{-1} = R(-\theta) = R(\theta)^T$: xoay ngược lại chỉ cần chuyển vị.
        :::


    - Chọn các tham số:
        - Tâm xoay
        - Góc xoay
        - Hệ số scale

        $$\begin{aligned}\alpha &= \text{scale}\cdot\cos\theta\\\beta &= \text{scale}\cdot\sin\theta\end{aligned}$$

        $$M=\begin{bmatrix}\alpha & \beta & (1-\alpha)\,\mathrm{center.x}-\beta\,\mathrm{center.y}\\-\beta & \alpha & \beta\,\mathrm{center.x}+(1-\alpha)\,\mathrm{center.y}\end{bmatrix}$$

        - Dấu của $\beta$ ngược với ma trận toán học ở trên vì trục y của ảnh hướng xuống: góc dương = xoay ngược chiều kim đồng hồ khi nhìn trên ảnh

            :::proof ma trận của getRotationMatrix2D
            Xoay quanh tâm $c = (c_x, c_y)$ (không phải gốc) kèm co giãn $s$ = ghép 3 bước:

            1. Tịnh tiến để tâm về gốc: $\mathbf{x} \mapsto \mathbf{x} - c$
            2. Xoay và co giãn quanh gốc: nhân với $A$
            3. Tịnh tiến trả tâm về chỗ cũ: cộng $c$

            $$\mathbf{x}' = A(\mathbf{x} - c) + c = A\mathbf{x} + (I - A)\,c$$

            **Ma trận $A$ trong hệ trục ảnh.** Trục $y$ của ảnh hướng *xuống*, tức là hệ trục toán học bị lật bởi $F = \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}$. Một phép xoay "ngược chiều kim đồng hồ khi nhìn trên màn hình" góc $\theta$ trong hệ ảnh tương ứng với: lật sang hệ toán học, xoay $\theta$, lật lại:

            $$F\,R(\theta)\,F = \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}\begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}\begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix} = \begin{bmatrix} \cos\theta & \sin\theta \\ -\sin\theta & \cos\theta \end{bmatrix} = R(-\theta)$$

            Nhân thêm hệ số $s$: $A = sR(-\theta) = \begin{bmatrix} \alpha & \beta \\ -\beta & \alpha \end{bmatrix}$ với $\alpha = s\cos\theta$, $\beta = s\sin\theta$. Đây là lý do dấu của $\beta$ bị đảo.

            **Cột tịnh tiến** $(I - A)c$:

            $$\begin{bmatrix} 1 - \alpha & -\beta \\ \beta & 1 - \alpha \end{bmatrix}\begin{bmatrix} c_x \\ c_y \end{bmatrix} = \begin{bmatrix} (1-\alpha)c_x - \beta c_y \\ \beta c_x + (1-\alpha)c_y \end{bmatrix}$$

            Ghép $[A \mid (I-A)c]$ ra đúng ma trận ở trên. $\blacksquare$

            Kiểm chứng: tâm $c$ là điểm bất động vì $A c + (I - A)c = c$. Mình đã so ma trận ghép $T(c)\,sR(-\theta)\,T(-c)$ với `cv.getRotationMatrix2D((40, 25), 30, 1.5)`: trùng khớp đến sai số làm tròn.
            :::


    - Hàm để tính M
        - `M = cv.getRotationMatrix2D(center, angle, scale)`
- Biến đổi Affine:
    - ==Giữ tính chất song song của đường thẳng== (đường thẳng vẫn là đường thẳng)
        - Ví dụ: A//B thì A’//B’
    - Các bước biến đổi Affine: ==2x3==
        - Chọn 3 điểm (không thẳng hàng) trên ảnh gốc
        - Chọn 3 điểm tương ứng trên ảnh đích
        - Dùng `cv2.getAffineTransform()`
        - Áp dụng `cv2.warpAffine()`

        ```python
        height, width = img.shape[:2]

        pts1 = np.float32([
            [50, 50],
            [200, 50],
            [50, 200],
        ])

        pts2 = np.float32([
            [10, 100],
            [200, 50],
            [100, 250],
        ])

        M = cv.getAffineTransform(pts1, pts2)
        dst = cv.warpAffine(img, M, (width, height))
        ```

- Biến đổi phối cảnh (Perspective Transform)
    - Không giữ tính chất song song nhưng đường thẳng vẫn là đường thẳng
    - Ứng dụng:
        - Nắn thẳng giấy tờ bị chụp nghiêng
        - Nắn tem nhãn, mã vạch, QR code
        - Căn chỉnh bảng mạch PCB trên băng truyền
        - Trích vùng biển báo, mặt phẳng, bảng số hoặc lưới Sudoku
    - Các bước biến đổi phối cảnh:
        - Chọn 4 điểm trên ảnh gốc
        - Chọn 4 điểm tương ứng trên ảnh mới
        - Đảm bảo không có 3 điểm nào trong 4 điểm bị thẳng hàng
        - Dùng `cv2.getPerspectiveTransform()`
        - Áp dụng bằng `cv2.warpPerspective()`

        ```python
        pts1 = np.float32([
            [56, 65],
            [368, 52],
            [28, 387],
            [389, 390],
        ])

        pts2 = np.float32([
            [0, 0],
            [300, 0],
            [0, 300],
            [300, 300],
        ])

        M = cv.getPerspectiveTransform(pts1, pts2)
        dst = cv.warpPerspective(img, M, (300, 300))
        ```
