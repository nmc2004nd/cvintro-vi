---
title: 12. Smoothing
lesson: lesson11_smoothing_pyramids
after:
---
- Tần số : độ biến thiên của các pixel:
    - 0-1 → tần số thấp
    - 0-100 → tần số cao

| Loại bộ lọc | Vai trò |
|---|---|
| Low-Pass Filter | Làm mịn ảnh, giảm nhiễu, làm mờ chi tiết nhỏ |
| High-Pass Filter | Làm nổi bật cạnh, biên và chi tiết tần số cao |

- Tích chập 2D
    - `dst = cv.filter2D(src, ddepth, kernel)`
        - `src `: ảnh đầu vào
        - `ddepth:` độ sâu ảnh đầu ra. Dùng -1 để giữ giống ảnh gốc
        - `kernel:` ma trận lọc để tích chập
        - `dst:` ảnh kết quả sau khi lọc
    - Cơ chế hoạt động
        - Duyệt kernel qua từng vùng ảnh
        - Nhân từng phần tử trong kernel với pixel tương ứng
        - Cộng các kết quả lại
        - Gán kết quả cho pixel trung tâm
        - Lặp lại cho toàn bộ ảnh

        ```python
        kernel = np.ones((5, 5), np.float32) / 25
        dst = cv.filter2D(img, -1, kernel)
        ```

- Các kĩ thuật làm mờ ảnh
    - Giảm nhiễu và làm mịn chi tiết, nhưng cũng có thể làm mềm cạnh vật thể

    | Bộ lọc | Hàm OpenCV | Đặc điểm chính |
    |---|---|---|
    | Averaging/ Box Filter | `cv2.blur(), cv2.boxFilter()` | Lấy trung bình vùng lân cận |
    | Gaussian Blur | `cv2.GaussianBlur()` | Trong số cao với pixel trung tâm,giảm dần ra biên |
    | Median Blur | `cv2.medianBlur()` | Lây trung vị, tốt với nhiễu muối tiêu |
    | Bilateral Filter | `cv2.bilateralFilter()` | Giảm nhiễu, giữ cạnh tốt, nhưng chạy chậm |

- Lọc trung bình
    - Kernel 3x3

        $$M=\frac{1}{9} \begin{bmatrix} 1 & 1 & 1\\ 1 & 1 & 1\\ 1 & 1 & 1 \end{bmatrix}$$

    - Hàm : `blur = cv.blur(img, (5, 5))`
    - Kernel càng lớn ảnh càng mờ
    - `cv2.blur()` : tương đương `cv2.boxFilter(normalize = True)`

    ```python
    dst = cv2.blur(img, (5, 5))
    # dst = cv2.boxFilter(img, -1, (5, 5), normalize = False)

    dst2 = cv2.boxFilter(img, -1, (5, 5), normalize=False)
    # -1 : ddepth
    # không chia trong số nên nếu quá 255 thì sẽ bão hòa ở 255
    ```

- Lọc Gaussian
    - Hàm : `blur_gaussian = cv.GaussianBlur(src, ksize, sigmaX, sigmaY=0)`
        - `src`: ảnh đầu vào
        - `ksize `: kích thước kernel số lẻ
        - `sigmaX`: độ lệch chuẩn theo trục X
        - `sigmaY`: độ lệch chuẩn theo trục Y
        - nếu `sigma `= 0 thì OpenCV sẽ tự tính

        `blur_gaussian = cv2.GaussianBlur(img, (5, 5), 0)`

- Lọc trung vị
    - Thay pixel trung tâm bằng trung vị của các pixel trong vùng kernel
    - Hàm: `median = cv.medianBlur(src, ksize)`
    - Hiệu quả tốt với nhiễu muối tiêu do nhiễu muối tiêu là các pixel có giá trị nhỏ mà lọc trung vị lấy trung vị gắn cho pixel trung tâm lên không làm loang nhiễu
- Lọc song phương
    - Hàm `blur_bilateral = cv.bilateralFilter(src, d, sigmaColor, sigmaSpace)`
        - `src`: ảnh đầu vào
        - `d`: Đường kính vùng lân cận được xét
        - `sigmaColor`: Mức lọc theo khác biệt màu/cường độ
        - `sigmaSpace`: Mức lọc theo khoảng cách không gian
    - Ý tưởng chính
        - Gaussian theo không gian: Pixel gần nhau có độ ảnh hưởng nhiều hơn
        - Gaussian theo cường độ màu: Pixel có màu gần giống nhau có ảnh hưởng nhiều hơn
