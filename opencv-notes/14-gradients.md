---
title: 14. Gradients
lesson: lesson12_differentiation_edges
after: Sobel
---
- Trích xuất gradients của ảnh, để tìm đường biên (outline - có độ biến thiên giá trị pixel cao) đặc trưng bằng các bộ lọc thông cao (High-pass filters)

| Cú pháp hàm | Tham số cốt lõi cần nhớ | Đặc trưng thuật toán |
|---|---|---|
| `cv.Sobel()` | `src`,` ddepth`,` dx`,` dy`,` ksize` | Tính đạo hàm bậc một. Cho phép tách biệt rõ rệt hướng cạnh ngang hoặc cạnh dọc. Chống nhiễu tốt nhờ tích hợp Gaussian. |
| `cv.Scharr()` | `src`,` ddepth`,` dx`,` dy` | Phiên bản tối ưu hơn của Sobel với kernel 3×3. Thường cho kết quả đạo hàm chính xác hơn Sobel 3×3. |
| `cv.Laplacian()` | `src`,` ddepth`,` ksize` | Tính đạo hàm bậc hai tổng hợp. Phát hiện nhanh toàn bộ đường biên theo mọi hướng cùng lúc, nhưng nhạy cảm với nhiễu hơn Sobel. |

- ==**Gradient bằng Sobel và Scharr**==
    - Kết hợp giữa:
        - Làm mịn Gaussian
        - Phép đạo hàm sai biệt
        - `Derivative×Gaussian`
        - $\frac{\partial I}{\partial x} = I(x+1, y) - I(x-1, y)$ → $dx = [-1, 0, 1]$
        - $\frac{\partial I}{\partial y} = I(x, y+1) - I(x, y-1)$ → $dy = [-1, 0, 1]^T$
        - Đạo hàm theo x (dx) thì làm mượt Gaussian theo y → $Ga_y = [1, 2, 1]^T$
        - Đạo hàm theo y (dy) thì làm mượt Gaussian theo x → $Ga_x = [1, 2, 1]$
        - Với Scharr thì $Ga_y = [3, 10, 3]^T$ và $Ga_x = [3, 10, 3]$
        - Sobel xấp xỉ:
            - ==Chính xác nhất với cạnh ngang/dọc (0°, 90°), sai số góc lớn hơn ở các hướng chéo==
            - ==Hay phát hiện cạnh giả do nhiễu==
            - ==Cạnh dày==
            - $K_x = Ga_y * dx = \begin{bmatrix}-1 & 0 & 1 \\-2 & 0 & 2 \\-1 & 0 & 1\end{bmatrix}$: đạo hàm theo x (theo cột) → tìm cạnh dọc
            - $K_y = dy *Ga_x = \begin{bmatrix}-1 & -2 & -1 \\0 & 0 & 0 \\1 & 2 & 1\end{bmatrix}$: đạo hàm theo y (theo hàng) → tìm cạnh ngang
        - Scharr (cùng quy ước dấu với Sobel ở trên, giống kernel của OpenCV):
            - ==Sai số góc nhỏ hơn nhiều, chính xác ở mọi hướng==
            - $$K_x = Ga_y * dx = \begin{bmatrix}-3 & 0 & 3 \\-10 & 0 & 10 \\-3 & 0 & 3\end{bmatrix}$$
            - $$K_y = dy *Ga_x = \begin{bmatrix}-3 & -10 & -3 \\0 & 0 & 0 \\3 & 10 & 3\end{bmatrix}$$
    - $G = \sqrt{G_x^2 + G_y^2}$ hoặc có thể tăng tốc độ bằng $G \approx |G_x| + |G_y|$
    - $$\theta = \operatorname{atan2}(G_y, G_x)\times\frac{180}{\pi}$$
    - ==Có khả năng chống nhiễu hạt tốt==

    ```python
    # Lưu ý: Sử dụng kiểu dữ liệu cv.CV_64F để giữ lại các giá trị âm (tránh mất biên)
    # ksize = -1, OpenCV sẽ kích hoạt bộ lọc Scharr kích thước 3×3
    sobelx = cv.Sobel(img, cv.CV_64F, 1, 0, ksize=5)  # xorder=1, yorder=0 -> Chỉ tìm cạnh dọc
    sobely = cv.Sobel(img, cv.CV_64F, 0, 1, ksize=5)  # xorder=0, yorder=1 -> Chỉ tìm cạnh ngang
    ```

- ==**Gradient bằng Laplacian**==
    - Tính toán đạo hàm bậc hai của ảnh dựa trên phương trình:
        - $$\Delta img = \frac{\partial^2 img}{\partial x^2} + \frac{\partial^2 img}{\partial y^2}$$
        - Mỗi thành phần đều được xấp xỉ bằng cách tính dựa trên các toán tử Sobel
        - Với `ksize = 1`

            $$\begin{bmatrix}0 & 1 & 0 \\1 & -4 & 1 \\0 & 1 & 0\end{bmatrix}$$

    - `laplacian = cv.Laplacian(img, cv.CV_64F)`
- ==**Vấn đề: Mất cạnh hoặc tràn số**==
    - Kiểu dữ liệu đầu ra của đạo hàm
    - Gradient có thể mang dấu âm dương tùy vào dx, dy:
        - Đen→Trắng : +
        - Trắng→Đen: -
    - Do đó nếu ép kiểu `np.uint8` hoặc `cv2.CV_8U`
        - Mọi số âm sẽ bị ép cứng về 0 → điều này sẽ làm mất cạnh thuộc vùng dịch chuyển Trắng → Đen
    - ==Giải pháp 1:==
        - `ddepth = cv2.CV_64F` hoặc `cv2.CV_16S`
        - Lấy giá trị tuyệt đối bằng hàm `np.absolute`
        - Sau đó ép kiểu ma trận ngược lại về dạng `np.uint8`
        - Cẩn thận: giá trị tuyệt đối có thể lớn hơn 255, `np.uint8()` sẽ **tràn số** (quay vòng) thay vì bão hòa → nên `np.clip(..., 0, 255)` hoặc `cv2.normalize` trước, hoặc dùng giải pháp 2

        ```python
        sobelx64f = cv.Sobel(img, cv.CV_64F, 1, 0, ksize=5)
        abs_sobel64f = np.absolute(sobelx64f)
        sobel_8u = np.uint8(abs_sobel64f)
        ```

    - ==Giải pháp 2:==
        - Dùng thẳng hàm `cv2.convertScaleAbs` (lấy trị tuyệt đối rồi bão hòa về `uint8`)
        - Sau đó tính `G = cv2.addWeighted`

        ```python
        # Sobel operator and converting the result to uint8
        sobelx = cv2.Sobel(img1, cv2.CV_64F, 1, 0, ksize = 5)
        sobely = cv2.Sobel(img1, cv2.CV_64F, 0, 1, ksize = 5)

        sobelx_1 = cv2.convertScaleAbs(sobelx)
        sobely_1 = cv2.convertScaleAbs(sobely)

        # Combining the two gradients
        sobel_combined_1 = cv2.addWeighted(sobelx_1, 0.5, sobely_1, 0.5, 0)
        ```

        - Cũng có thể dùng L2 norm sau đó normalize :

        ```python
        # Using the L2 norm to combine the gradients
        sobel_combined_2 = cv2.magnitude(sobelx, sobely)
        sobel_combined_2_normalized = cv2.normalize(sobel_combined_2, None, 0, 255, cv2.NORM_MINMAX)
        ```

        ![](img/opencv-notes/14-gradients-1.png)

        ![](img/opencv-notes/14-gradients-2.png)

        ![](img/opencv-notes/14-gradients-3.png)
