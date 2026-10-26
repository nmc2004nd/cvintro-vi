---
title: 24. Corner Detection - Harris, Shi-Tomasi
lesson: lesson20_feature_detection_matching
after: Shi-Tomasi
draft: true
---
| Hàm | Thuật toán | Kết quả |
|---|---|---|
| `cv.cornerHarris()` | Harris (1988) | Ảnh "điểm góc" R, cùng kích thước ảnh |
| `cv.goodFeaturesToTrack()` | Shi-Tomasi (1994) | N góc mạnh nhất, tọa độ (x, y) |
| `cv.cornerSubPix()` | Tinh chỉnh | Tọa độ góc chính xác tới mức sub-pixel |

- Đặc trưng tốt là vùng mà ==dịch cửa sổ theo mọi hướng đều làm thay đổi lớn cường độ==:
    - Vùng phẳng: dịch hướng nào cũng không đổi → không dùng được
    - Cạnh: chỉ đổi khi dịch vuông góc với cạnh, dịch dọc cạnh thì không đổi
    - ==Góc==: dịch hướng nào cũng đổi → đặc trưng tốt nhất
- ==**Harris Corner Detector**==
    - Độ thay đổi cường độ khi dịch cửa sổ một đoạn $(u, v)$:

        $$E(u, v) = \sum_{x, y} w(x, y)\,[I(x + u, y + v) - I(x, y)]^2 \approx [u \;\; v]\, M \begin{bmatrix} u \\ v \end{bmatrix}$$

        $$M = \sum_{x, y} w(x, y) \begin{bmatrix} I_x^2 & I_x I_y \\ I_x I_y & I_y^2 \end{bmatrix}$$

        - $I_x, I_y$: đạo hàm theo x, y (tính bằng Sobel)
        - $w(x, y)$: cửa sổ (hình chữ nhật hoặc Gauss)
    - Điểm góc: $R = \det(M) - k\,(\operatorname{trace} M)^2 = \lambda_1 \lambda_2 - k(\lambda_1 + \lambda_2)^2$
        - $|R|$ nhỏ ($\lambda_1, \lambda_2$ đều nhỏ) → vùng phẳng
        - $R < 0$ (một $\lambda$ lớn hơn hẳn) → cạnh
        - ==$R$ lớn ($\lambda_1, \lambda_2$ đều lớn và xấp xỉ nhau) → góc==
    - Hàm: `dst = cv.cornerHarris(img, blockSize, ksize, k)`
        - `img`: ảnh xám, ==kiểu `float32`==
        - `blockSize`: kích thước vùng lân cận
        - `ksize`: kích thước kernel Sobel
        - `k`: hệ số tự do, thường 0.04-0.06

    ```python
    gray = np.float32(cv.cvtColor(img, cv.COLOR_BGR2GRAY))
    dst = cv.cornerHarris(gray, 2, 3, 0.04)
    dst = cv.dilate(dst, None)                     # chỉ để chấm góc to hơn khi vẽ
    img[dst > 0.01 * dst.max()] = [0, 0, 255]      # ngưỡng tùy ảnh
    ```

- **Góc chính xác tới sub-pixel**: `cv.cornerSubPix()`
    - Lấy tâm các cụm góc Harris bằng `connectedComponentsWithStats`, rồi tinh chỉnh

    ```python
    ret, dst = cv.threshold(dst, 0.01 * dst.max(), 255, 0)
    ret, labels, stats, centroids = cv.connectedComponentsWithStats(np.uint8(dst))

    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv.cornerSubPix(gray, np.float32(centroids), (5, 5), (-1, -1), criteria)
    ```

    - `criteria`: điều kiện dừng = đủ số vòng lặp **hoặc** độ dịch chuyển nhỏ hơn epsilon
- ==**Shi-Tomasi Corner Detector**==
    - Thay hàm điểm của Harris bằng: $R = \min(\lambda_1, \lambda_2)$
    - ==Chỉ khi cả hai $\lambda$ đều lớn hơn một ngưỡng mới là góc== → ổn định hơn Harris
    - Hàm: `corners = cv.goodFeaturesToTrack(gray, maxCorners, qualityLevel, minDistance)`
        - `maxCorners`: số góc tối đa (lấy N góc mạnh nhất)
        - `qualityLevel`: 0-1, loại góc có điểm < `qualityLevel` x điểm cao nhất
        - `minDistance`: khoảng cách Euclid tối thiểu giữa hai góc
        - Có thể đặt `useHarrisDetector=True` để dùng hàm điểm Harris
        - Trả về `float32` shape (N, 1, 2)

    ```python
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    corners = cv.goodFeaturesToTrack(gray, 25, 0.01, 10)
    corners = np.intp(corners)                     # tài liệu dùng np.int0 nhưng NumPy 2 đã xóa
    for c in corners:
        x, y = c.ravel()
        cv.circle(img, (int(x), int(y)), 3, 255, -1)
    ```

    ![](img/opencv-notes/24-corner-detection-1.png)

- ==Lưu ý: góc Harris/Shi-Tomasi bất biến với xoay nhưng **không** bất biến với tỷ lệ==: một góc khi phóng to nhìn qua cửa sổ nhỏ có thể chỉ còn là cạnh cong → cần SIFT
- ==Ứng dụng:==
    - ==Chọn điểm để theo dõi bằng optical flow (Lucas-Kanade)==
    - ==Tìm góc bàn cờ khi hiệu chỉnh camera==
