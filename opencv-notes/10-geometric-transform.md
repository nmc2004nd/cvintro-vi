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

    - Hàm dùng: `dst = cv2.warpAffine(img, M, dsize)`
- Rotation - xoay ảnh
    - Ma trận xoay trong toán học : 2x2 → xoay quanh gốc tọa độ (0, 0)

        $$M= \begin{bmatrix} \cos\theta & -\sin\theta\\ \sin\theta & \cos\theta \end{bmatrix}$$

    - Chọn các tham số:
        - Tâm xoay
        - Góc xoay
        - Hệ số scale

        $$\begin{aligned}\alpha &= \text{scale}\cdot\cos\theta\\\beta &= \text{scale}\cdot\sin\theta\end{aligned}$$

        $$M=\begin{bmatrix}\alpha & \beta & (1-\alpha)\,\mathrm{center.x}-\beta\,\mathrm{center.y}\\-\beta & \alpha & \beta\,\mathrm{center.x}+(1-\alpha)\,\mathrm{center.y}\end{bmatrix}$$

        - Dấu của $\beta$ ngược với ma trận toán học ở trên vì trục y của ảnh hướng xuống: góc dương = xoay ngược chiều kim đồng hồ khi nhìn trên ảnh

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
