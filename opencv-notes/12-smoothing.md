---
title: 12. Smoothing
lesson: lesson11_smoothing_pyramids
after:
---
- Tần số: tốc độ thay đổi giá trị pixel theo không gian
    - Pixel kề nhau thay đổi ít (ví dụ 0 → 1) → tần số thấp: vùng phẳng, mảng màu
    - Pixel kề nhau thay đổi đột ngột (ví dụ 0 → 100) → tần số cao: cạnh, chi tiết nhỏ, nhiễu

| Loại bộ lọc | Vai trò |
|---|---|
| Low-Pass Filter | Làm mịn ảnh, giảm nhiễu, làm mờ chi tiết nhỏ |
| High-Pass Filter | Làm nổi bật cạnh, biên và chi tiết tần số cao |

- Tích chập 2D
    - `dst = cv.filter2D(src, ddepth, kernel)`
        - `src`: ảnh đầu vào
        - `ddepth:` độ sâu ảnh đầu ra. Dùng -1 để giữ giống ảnh gốc
        - `kernel:` ma trận lọc để tích chập
        - `dst:` ảnh kết quả sau khi lọc
    - Cơ chế hoạt động
        - Duyệt kernel qua từng vùng ảnh
        - Nhân từng phần tử trong kernel với pixel tương ứng
        - Cộng các kết quả lại
        - Gán kết quả cho pixel trung tâm
        - Lặp lại cho toàn bộ ảnh
        - Lưu ý: `filter2D` thực chất tính **tương quan** (correlation), không lật kernel; với kernel đối xứng thì kết quả giống tích chập

        ```python
        kernel = np.ones((5, 5), np.float32) / 25
        dst = cv.filter2D(img, -1, kernel)
        ```

- Các kĩ thuật làm mờ ảnh
    - Giảm nhiễu và làm mịn chi tiết, nhưng cũng có thể làm mềm cạnh vật thể

    | Bộ lọc | Hàm OpenCV | Đặc điểm chính |
    |---|---|---|
    | Averaging/ Box Filter | `cv2.blur(), cv2.boxFilter()` | Lấy trung bình vùng lân cận |
    | Gaussian Blur | `cv2.GaussianBlur()` | Trọng số cao với pixel trung tâm, giảm dần ra biên |
    | Median Blur | `cv2.medianBlur()` | Lấy trung vị, tốt với nhiễu muối tiêu |
    | Bilateral Filter | `cv2.bilateralFilter()` | Giảm nhiễu, giữ cạnh tốt, nhưng chạy chậm |

- Lọc trung bình
    - Kernel 3x3

        $$M=\frac{1}{9} \begin{bmatrix} 1 & 1 & 1\\ 1 & 1 & 1\\ 1 & 1 & 1 \end{bmatrix}$$

    - Hàm : `blur = cv.blur(img, (5, 5))`
    - Kernel càng lớn ảnh càng mờ
    - `cv2.blur()` : tương đương `cv2.boxFilter(normalize = True)`

    ```python
    dst = cv2.blur(img, (5, 5))
    # tương đương: dst = cv2.boxFilter(img, -1, (5, 5), normalize=True)

    dst2 = cv2.boxFilter(img, -1, (5, 5), normalize=False)
    # -1 : ddepth
    # không chia trọng số (chỉ cộng) nên nếu quá 255 thì sẽ bão hòa ở 255
    ```

- Lọc Gaussian
    - Hàm : `blur_gaussian = cv.GaussianBlur(src, ksize, sigmaX, sigmaY=0)`
        - `src`: ảnh đầu vào
        - `ksize`: kích thước kernel, số lẻ
        - `sigmaX`: độ lệch chuẩn theo trục X
        - `sigmaY`: độ lệch chuẩn theo trục Y
        - nếu `sigmaX = 0` thì OpenCV tự tính từ `ksize`; nếu` sigmaY = 0` thì lấy bằng `sigmaX`

        `blur_gaussian = cv2.GaussianBlur(img, (5, 5), 0)`

- Lọc trung vị
    - Thay pixel trung tâm bằng trung vị của các pixel trong vùng kernel
    - Hàm: `median = cv.medianBlur(src, ksize)`
    - Hiệu quả tốt với nhiễu muối tiêu vì nhiễu muối tiêu là các pixel lẻ có giá trị cực trị (0 hoặc 255); trung vị bỏ qua các giá trị ngoại lai này nên không làm loang nhiễu như lọc trung bình
    - `ksize` là số lẻ lớn hơn 1
- Lọc song phương
    - Hàm `blur_bilateral = cv.bilateralFilter(src, d, sigmaColor, sigmaSpace)`
        - `src`: ảnh đầu vào
        - `d`: Đường kính vùng lân cận được xét
        - `sigmaColor`: Mức lọc theo khác biệt màu/cường độ
        - `sigmaSpace`: Mức lọc theo khoảng cách không gian
    - Ý tưởng chính
        - Gaussian theo không gian: Pixel gần nhau có độ ảnh hưởng nhiều hơn
        - Gaussian theo cường độ màu: Pixel có màu gần giống nhau có ảnh hưởng nhiều hơn
