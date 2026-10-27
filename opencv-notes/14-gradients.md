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
        - $\frac{\partial I}{\partial x} \approx \frac{I(x+1, y) - I(x-1, y)}{2}$ → $dx = [-1, 0, 1]$ (OpenCV bỏ hệ số $\frac12$)
        - $\frac{\partial I}{\partial y} \approx \frac{I(x, y+1) - I(x, y-1)}{2}$ → $dy = [-1, 0, 1]^T$
        - Đạo hàm theo x (dx) thì làm mượt Gaussian theo y → $Ga_y = [1, 2, 1]^T$
        - Đạo hàm theo y (dy) thì làm mượt Gaussian theo x → $Ga_x = [1, 2, 1]$
        - Với Scharr thì $Ga_y = [3, 10, 3]^T$ và $Ga_x = [3, 10, 3]$

            :::proof đạo hàm sai phân, kernel Sobel tách được và hệ số Scharr
            **1. Vì sao dùng sai phân trung tâm.** Khai triển Taylor theo $x$ (bước $h = 1$ pixel):

            $$I(x+1) = I(x) + I'(x) + \tfrac{1}{2}I''(x) + \tfrac{1}{6}I'''(x) + \dots$$

            $$I(x-1) = I(x) - I'(x) + \tfrac{1}{2}I''(x) - \tfrac{1}{6}I'''(x) + \dots$$

            Trừ hai dòng, các số hạng bậc chẵn triệt tiêu:

            $$I(x+1) - I(x-1) = 2I'(x) + \tfrac{1}{3}I'''(x) + \dots \;\Rightarrow\; I'(x) = \frac{I(x+1) - I(x-1)}{2} + O(h^2)$$

            Sai phân tiến $I(x+1) - I(x)$ chỉ có sai số $O(h)$ (còn sót $\tfrac12 I''$) và lệch nửa pixel. Kernel $[-1, 0, 1]$ chính là sai phân trung tâm **chưa chia 2**; OpenCV bỏ hệ số này, nên giá trị Sobel lớn hơn đạo hàm thật (xem mục 3).

            **2. Kernel 3x3 = tích ngoài của hai vector 1D (tách được).**

            $$\begin{bmatrix} 1 \\ 2 \\ 1 \end{bmatrix}\begin{bmatrix} -1 & 0 & 1 \end{bmatrix} = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}$$

            Vì $K(i, j) = a_i b_j$ nên $\sum_{i,j} a_i b_j f(x+j, y+i) = \sum_i a_i \big(\sum_j b_j f(x+j, y+i)\big)$: lọc theo hàng bằng $b$ rồi theo cột bằng $a$ cho cùng kết quả, tốn $3 + 3 = 6$ phép nhân thay vì 9 (kernel $k \times k$: $2k$ thay vì $k^2$). $[1, 2, 1] = [1, 1] * [1, 1]$ là hệ số nhị thức, xấp xỉ Gauss rời rạc; nó làm mượt theo hướng *vuông góc* với hướng đạo hàm để giảm nhiễu mà không làm mờ cạnh theo hướng đang đo.

            **3. Sobel trả về 8 lần đạo hàm thật.** Trên ảnh dốc đều $I = ax$: hàng giữa cho $a(x+1) - a(x-1) = 2a$, và ba hàng có trọng số $1 + 2 + 1 = 4$, tổng cộng $8a$. Mình đã kiểm tra: ảnh dốc với $a = 3$ cho Sobel = 24. Với Scharr hệ số là $2 \cdot (3 + 10 + 3) = 32$. Hướng gradient không đổi vì $G_x, G_y$ cùng bị nhân một hằng số.

            **4. Vì sao Scharr chính xác hơn về hướng.** Đưa vào một sóng phẳng tần số $\omega$ theo hướng $\varphi$: $I = \cos(\omega_x x + \omega_y y)$ với $\omega_x = \omega\cos\varphi$, $\omega_y = \omega\sin\varphi$. Kernel tách được $[a, b, a]^T \otimes [-1, 0, 1]$ cho

            $$G_x \propto \sin\omega_x\,(b + 2a\cos\omega_y), \qquad G_y \propto \sin\omega_y\,(b + 2a\cos\omega_x)$$

            Khai triển $\sin u \approx u - u^3/6$, $\cos u \approx 1 - u^2/2$ khi $\omega$ nhỏ:

            $$\frac{G_y}{G_x} \approx \frac{\omega_y}{\omega_x}\Big[1 + (\omega_y^2 - \omega_x^2)\Big(\frac{a}{b + 2a} - \frac{1}{6}\Big)\Big]$$

            Hướng ước lượng đúng ($G_y/G_x = \tan\varphi$) với mọi $\varphi$ khi $\frac{a}{b+2a} = \frac16$, tức $b = 4a$. Sobel có $\frac{1}{1+2+1} = \frac14 \ne \frac16$ nên lệch hướng; số hạng sai bằng 0 khi $\omega_x = \omega_y$ (45°) hoặc khi một trong hai bằng 0 (0°, 90°). Scharr $[3, 10, 3]$ có $\frac{3}{16} \approx 0.19$, gần $\frac16 \approx 0.17$ hơn nhiều; hệ số này được Scharr tối ưu số trên *mọi* tần số chứ không chỉ tần số thấp, nên không đúng bằng $[1,4,1]$.

            Tính số trên sóng có $\omega = \pi/2$ (chi tiết cỡ 4 pixel): Sobel lệch tối đa **3.2°** (ở 22.5° và 67.5°), Scharr chỉ **0.3°**. Ở 0°, 45°, 90° cả hai đều đúng tuyệt đối.
            :::

        - Sobel xấp xỉ:
            - ==Hướng gradient đúng ở 0°, 45°, 90°; lệch nhiều nhất quanh 22.5° và 67.5° (tới khoảng 3° với chi tiết nhỏ)==
            - ==Hay phát hiện cạnh giả do nhiễu==
            - ==Cạnh dày==
            - $K_x = Ga_y * dx = \begin{bmatrix}-1 & 0 & 1 \\-2 & 0 & 2 \\-1 & 0 & 1\end{bmatrix}$: đạo hàm theo x (theo cột) → tìm cạnh dọc
            - $K_y = dy *Ga_x = \begin{bmatrix}-1 & -2 & -1 \\0 & 0 & 0 \\1 & 2 & 1\end{bmatrix}$: đạo hàm theo y (theo hàng) → tìm cạnh ngang
        - Scharr (cùng quy ước dấu với Sobel ở trên, giống kernel của OpenCV):
            - ==Sai số góc nhỏ hơn nhiều, chính xác ở mọi hướng==
            - $$K_x = Ga_y * dx = \begin{bmatrix}-3 & 0 & 3 \\-10 & 0 & 10 \\-3 & 0 & 3\end{bmatrix}$$
            - $$K_y = dy *Ga_x = \begin{bmatrix}-3 & -10 & -3 \\0 & 0 & 0 \\3 & 10 & 3\end{bmatrix}$$
    - $G = \sqrt{G_x^2 + G_y^2}$ hoặc có thể tăng tốc độ bằng $G \approx |G_x| + |G_y|$

        :::proof độ lớn, hướng gradient và xấp xỉ |Gx| + |Gy|
        **1. Gradient chỉ hướng tăng nhanh nhất, độ lớn là tốc độ tăng đó.** Đạo hàm theo hướng vector đơn vị $\mathbf{u} = (\cos\psi, \sin\psi)$ là

        $$D_{\mathbf{u}}I = \nabla I \cdot \mathbf{u} = G_x\cos\psi + G_y\sin\psi = |\nabla I|\cos(\psi - \theta)$$

        với $\theta$ là góc của $\nabla I = (G_x, G_y)$. Biểu thức lớn nhất khi $\psi = \theta$ và có giá trị $|\nabla I| = \sqrt{G_x^2 + G_y^2}$. Theo hướng $\psi = \theta \pm 90°$ thì $D_{\mathbf{u}} I = 0$: cường độ không đổi → đó là **hướng chạy dọc theo cạnh**. Vậy gradient luôn vuông góc với cạnh. $\blacksquare$

        **2. Vì sao dùng `atan2` chứ không dùng `atan(Gy/Gx)`.** `atan` chỉ cho góc trong $(-90°, 90°)$ và lỗi khi $G_x = 0$; $(G_x, G_y)$ và $(-G_x, -G_y)$ cho cùng tỉ số nên không phân biệt được "tối → sáng" với "sáng → tối". `atan2` dùng dấu của cả hai thành phần để trả về góc đầy đủ $(-180°, 180°]$.

        **3. Sai số của $|G_x| + |G_y|$.** Với $a = G_x$, $b = G_y$:

        - $(|a| + |b|)^2 = a^2 + b^2 + 2|ab| \ge a^2 + b^2$ → $|a| + |b| \ge G$
        - $2|ab| \le a^2 + b^2$ (vì $(|a| - |b|)^2 \ge 0$) → $(|a| + |b|)^2 \le 2(a^2 + b^2)$ → $|a| + |b| \le \sqrt{2}\,G$

        $$G \le |G_x| + |G_y| \le \sqrt{2}\,G$$

        Đúng tuyệt đối với cạnh ngang/dọc (một thành phần bằng 0), lớn hơn thật tối đa $\sqrt2 \approx 1.41$ lần ở cạnh chéo 45°. Nghĩa là với cùng một ngưỡng, cạnh chéo dễ được giữ hơn cạnh ngang/dọc. Đó là lý do Canny có tùy chọn `L2gradient`.
        :::

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

            :::proof kernel Laplace 3x3 và vì sao nó bất biến với phép xoay
            **1. Đạo hàm bậc hai bằng sai phân.** Cộng hai khai triển Taylor ở mục trước (lần này các số hạng bậc lẻ triệt tiêu):

            $$I(x+1) + I(x-1) = 2I(x) + I''(x) + O(h^4) \;\Rightarrow\; \frac{\partial^2 I}{\partial x^2} \approx I(x+1) - 2I(x) + I(x-1)$$

            tức kernel $[1, -2, 1]$, sai số $O(h^2)$. Làm tương tự theo $y$ rồi cộng lại:

            $$\begin{bmatrix} 0 & 0 & 0 \\ 1 & -2 & 1 \\ 0 & 0 & 0 \end{bmatrix} + \begin{bmatrix} 0 & 1 & 0 \\ 0 & -2 & 0 \\ 0 & 1 & 0 \end{bmatrix} = \begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix}$$

            Đã kiểm tra: `cv.Laplacian(img, cv.CV_32F)` (mặc định `ksize=1`) trùng với `filter2D` bằng kernel này.

            **2. Kernel có tổng bằng 0** → kết quả bằng 0 trên vùng phẳng *và* trên vùng dốc đều $I = ax + by + c$ (đạo hàm bậc hai của hàm tuyến tính bằng 0). Laplace chỉ phản ứng với chỗ độ dốc *thay đổi*: hai bên của một cạnh cho dấu ngược nhau, và cạnh nằm ở **điểm cắt không** (zero-crossing).

            **3. Bất biến với phép xoay (bản liên tục).** $\Delta I$ là vết (trace) của ma trận Hessian $H = \begin{bmatrix} I_{xx} & I_{xy} \\ I_{xy} & I_{yy} \end{bmatrix}$. Khi xoay hệ trục bằng $R$, Hessian thành $R^T H R$, và

            $$\operatorname{tr}(R^T H R) = \operatorname{tr}(H R R^T) = \operatorname{tr}(H)$$

            (dùng $\operatorname{tr}(AB) = \operatorname{tr}(BA)$ và $RR^T = I$). Vậy Laplace phát hiện biên **theo mọi hướng bằng một phép lọc**, không cần tách $x$, $y$ như Sobel. Đổi lại nó là đạo hàm bậc hai nên khuếch đại nhiễu mạnh hơn (nhiễu tần số $\omega$ bị nhân khoảng $\omega^2$ thay vì $\omega$) – đó là lý do thường làm mờ Gauss trước (LoG).
            :::


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
