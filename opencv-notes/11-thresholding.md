---
title: 11. Thresholding
lesson: lesson03_thresholding_morphology
after: Otsu
---
- ==**Thường áp dụng với ảnh xám**==
- Ứng dụng thông thường là ==**tạo mask**==
- Nhị phân hóa cố định - **Simple thresholding**
    - Dùng một ngưỡng thresh cho toàn bộ ảnh - ==**Global thresh**==
    - Hàm:
        - `ret, dst = cv.threshold(src, thresh, maxval, type)`
    - Type thresholding:
        - `cv2.THRESH_BINARY:` ghim về Max nếu lớn hơn ngưỡng và ngược lại

            $$g(p)=\begin{cases}M, & p > T\\0, & p \le T\end{cases}$$

        - `cv2.THRESH_BINARY_INV:` ghim về 0 nếu lớn hơn ngưỡng và ngược lại

            $$g(p)=\begin{cases}0, & p > T\\M, & p \le T\end{cases}$$

        - `cv2.THRESH_TRUNC:` ghim về ngưỡng nếu lớn hơn ngưỡng, còn giữ giá trị nếu nhỏ hơn

            $$g(p)=\begin{cases}T, & p > T\\p, & p \le T\end{cases}$$

        - `cv2.THRESH_TOZERO:` Giữ giá trị nếu lớn hơn ngưỡng, ngược lại ghim về 0

            $$g(p)=\begin{cases}p, & p > T\\0, & p \le T\end{cases}$$

        - `cv2.THRESH_TOZERO_INV:` Giữ giá trị nếu nhỏ hơn ngưỡng, ngược lại ghim về 0

            $$g(p)=\begin{cases}0, & p > T\\p, & p \le T\end{cases}$$

        ```python
        ret, thresh1 = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
        ret, thresh2 = cv.threshold(img, 127, 255, cv.THRESH_BINARY_INV)
        ret, thresh3 = cv.threshold(img, 127, 255, cv.THRESH_TRUNC)
        ret, thresh4 = cv.threshold(img, 127, 255, cv.THRESH_TOZERO)
        ret, thresh5 = cv.threshold(img, 127, 255, cv.THRESH_TOZERO_INV)
        ```

- Adaptive thresholding
    - Với Simple thresholding nếu ánh sáng không đều - vùng sáng mạnh, vùng tối hoặc bị đổ bóng khi dùng 1 ngưỡng duy nhất cho toàn bộ bức ảnh sẽ cho kết quả không tốt
    - Adaptive : ==**tính ngưỡng riêng lẻ cho từng vùng lân cận mỗi pixel**==

    ```python
    dst = cv.adaptiveThreshold(
        src,
        maxValue,
        adaptiveMethod,
        thresholdType,
        blockSize,
        C,
    )
    ```

    | Tham số | Ý nghĩa |
    |---|---|
    | `src` | Ảnh xám đầu vào |
    | `maxValue` | Gán giá trị cho pixel thỏa mãn điều kiện |
    | `adaptiveMethod` | Cách tính ngưỡng cục bộ - Local |
    | `thresholdType` | Thường dùng `cv2.THRESH_BINARY` or `cv2.THRESH_BINARY_INV` |
    | `blockSize` | Kích thước vùng lân cận - số lẻ lớn hơn 1 |
    | `C` | Hằng số trừ đi khỏi giá trị trung bình cục bộ |

    - Adaptive Mean - trọng số đều nhau với các pixel
        - `cv2.ADAPTIVE_THRESH_MEAN_C`

        $$T(x,y)=\left(\frac{1}{N}\sum_{(i,j)\in\Omega(x,y)} I(i,j)\right)-C$$

    - Adaptive Gaussian - ưu tiên trọng số với các pixel trung tâm
        - `cv2.ADAPTIVE_THRESH_GAUSSIAN_C`

        $$T(x,y)=\left(\sum_{(i,j)\in\Omega(x,y)} w(i,j)\,I(i,j)\right)-C, \quad \sum w(i,j) = 1$$

        - Trọng số Gaussian $w$ đã chuẩn hóa tổng bằng 1 nên không chia thêm cho $N$

        ```python
        th2 = cv.adaptiveThreshold(
            img,
            255,
            cv.ADAPTIVE_THRESH_MEAN_C,
            cv.THRESH_BINARY,
            11,
            2,
        )

        th3 = cv.adaptiveThreshold(
            img,
            255,
            cv.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv.THRESH_BINARY,
            11,
            2,
        )
        ```

- Threshold Otsu
    - ==**Thường lọc nhiễu trước khi áp dụng Otsu**==
    - Tự động phân tích histogram ảnh để tìm ngưỡng tối ưu
    - Otsu hoạt động tốt nhất với ảnh lưỡng đỉnh - Histogram hai đỉnh
        - Một cụm cho nền
        - Một cụm cho vật thể
    - Ngưỡng tối ưu thường nằm ở vùng thung lũng giữa hai cụm này

        ```python
        blur = cv.GaussianBlur(img, (5, 5), 0)
        ret3, th3 = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        ```

        - Tham số ngưỡng (0) bị bỏ qua, ngưỡng Otsu tìm được trả về ở `ret3`

- Công thức Otsu
    - Với một ngưỡng t, Histogram của ảnh chia làm hai lớp
        - $C_1$ : các mức xám từ 0 đến $t-1$
        - $C_2$ : các mức xám từ $t$ đến $L-1$
        - Với ảnh `uint8` $L = 256$
    - Ngưỡng t được tìm bằng cách tìm Min của phương trình sau:
        - $\sigma_w^2(t)=q_1(t)\sigma_1^2(t)+q_2(t)\sigma_2^2(t)$
    - Xác suất tích lũy của hai lớp
        - $q_1(t)=\sum_{i=0}^{t-1} P(i)$
        - $q_2(t)=\sum_{i=t}^{L-1} P(i)$
    - Giá trị trung bình của hai lớp
        - Chia cho $q_i(t)$ để xác suất trong mỗi lớp có tổng bằng 1 (xác suất có điều kiện)
        - $$\mu_1(t)=\sum_{i=0}^{t-1}\frac{i \cdot P(i)}{q_1(t)}$$
        - $$\mu_2(t)=\sum_{i=t}^{L-1}\frac{i \cdot P(i)}{q_2(t)}$$
    - Phương sai của hai lớp
        - Chia cho $q_i(t)$ với cùng lý do như trên
        - $$\sigma_1^2(t)=\sum_{i=0}^{t-1}\frac{(i - \mu_1(t))^2 \cdot P(i)}{q_1(t)}$$
        - $$\sigma_2^2(t)=\sum_{i=t}^{L-1}\frac{(i - \mu_2(t))^2 \cdot P(i)}{q_2(t)}$$
