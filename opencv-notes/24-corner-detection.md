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

        :::proof từ E(u, v) tới ma trận M
        **Bước 1 – khai triển Taylor bậc nhất** (dịch nhỏ $u, v$):

        $$I(x + u, y + v) \approx I(x, y) + I_x u + I_y v$$

        nên $I(x + u, y + v) - I(x, y) \approx I_x u + I_y v = [u \;\; v]\begin{bmatrix} I_x \\ I_y \end{bmatrix}$.

        **Bước 2 – bình phương** (dùng $(\mathbf{a}^T\mathbf{d})^2 = \mathbf{d}^T\mathbf{a}\mathbf{a}^T\mathbf{d}$ với $\mathbf{d} = (u, v)$):

        $$(I_x u + I_y v)^2 = I_x^2 u^2 + 2I_xI_y uv + I_y^2 v^2 = [u \;\; v]\begin{bmatrix} I_x^2 & I_xI_y \\ I_xI_y & I_y^2 \end{bmatrix}\begin{bmatrix} u \\ v \end{bmatrix}$$

        **Bước 3 – cộng có trọng số** trên cửa sổ; $(u, v)$ không phụ thuộc $(x, y)$ nên đưa ra ngoài tổng:

        $$E(u, v) \approx [u \;\; v]\Big(\sum_{x,y} w(x,y)\begin{bmatrix} I_x^2 & I_xI_y \\ I_xI_y & I_y^2 \end{bmatrix}\Big)\begin{bmatrix} u \\ v \end{bmatrix} = [u \;\; v]\,M\begin{bmatrix} u \\ v \end{bmatrix} \qquad \blacksquare$$

        **M đối xứng và nửa xác định dương.** $\mathbf{d}^T M \mathbf{d} = \sum w\,(I_x u + I_y v)^2 \ge 0$ với mọi $\mathbf{d}$ (vì $w \ge 0$). Nên $M$ có hai trị riêng thực $\lambda_1 \ge \lambda_2 \ge 0$ và hai vector riêng vuông góc $\mathbf{e}_1, \mathbf{e}_2$.

        **Ý nghĩa của trị riêng (thương Rayleigh).** Viết hướng dịch đơn vị $\mathbf{d} = c_1\mathbf{e}_1 + c_2\mathbf{e}_2$ với $c_1^2 + c_2^2 = 1$:

        $$E(\mathbf{d}) = \lambda_1 c_1^2 + \lambda_2 c_2^2 \in [\lambda_2, \lambda_1]$$

        - $\lambda_1$ = độ thay đổi khi dịch theo hướng **thay đổi nhiều nhất** ($\mathbf{e}_1$).
        - $\lambda_2$ = độ thay đổi khi dịch theo hướng **thay đổi ít nhất** ($\mathbf{e}_2$).

        Ba trường hợp ở đầu ghi chú trở thành chính xác:

        | Vùng | $\lambda_1$ | $\lambda_2$ | Lý do |
        |---|---|---|---|
        | Phẳng | ≈ 0 | ≈ 0 | $I_x \approx I_y \approx 0$ |
        | Cạnh | lớn | ≈ 0 | mọi gradient cùng hướng $\mathbf{g}$ → $M \approx \big(\sum w\lVert\mathbf{g}\rVert^2\big)\hat{\mathbf{g}}\hat{\mathbf{g}}^T$ có hạng 1; dịch dọc cạnh ($\perp \mathbf{g}$) cho $E = 0$ |
        | Góc | lớn | lớn | gradient theo ít nhất hai hướng khác nhau → dịch hướng nào cũng đổi |
        :::

    - Điểm góc: $R = \det(M) - k\,(\operatorname{trace} M)^2 = \lambda_1 \lambda_2 - k(\lambda_1 + \lambda_2)^2$
        - $|R|$ nhỏ ($\lambda_1, \lambda_2$ đều nhỏ) → vùng phẳng
        - $R < 0$ (một $\lambda$ lớn hơn hẳn) → cạnh
        - ==$R$ lớn ($\lambda_1, \lambda_2$ đều lớn và xấp xỉ nhau) → góc==

        :::proof vì sao R = det − k·trace² phân biệt được phẳng / cạnh / góc
        **Không cần tính trị riêng.** Với ma trận $2 \times 2$, đa thức đặc trưng là $\lambda^2 - (\operatorname{tr}M)\lambda + \det M$, nên theo định lý Viète:

        $$\det M = \lambda_1\lambda_2 = AC - B^2, \qquad \operatorname{tr}M = \lambda_1 + \lambda_2 = A + C$$

        với $M = \begin{bmatrix} A & B \\ B & C \end{bmatrix}$. Chỉ cần vài phép nhân, không cần căn bậc hai.

        **Phân tích dấu của $R = \lambda_1\lambda_2 - k(\lambda_1 + \lambda_2)^2$:**

        - **Phẳng** ($\lambda_1, \lambda_2 \approx 0$): cả hai số hạng đều nhỏ → $|R|$ nhỏ.
        - **Cạnh** ($\lambda_1 = \lambda \gg \lambda_2 \approx 0$): $R \approx 0 - k\lambda^2 < 0$.
        - **Góc lý tưởng** ($\lambda_1 = \lambda_2 = \lambda$): $R = \lambda^2 - 4k\lambda^2 = (1 - 4k)\lambda^2 > 0$ khi $k < 1/4$.

        Tổng quát, đặt $\lambda_2 = r\lambda_1$ với $0 \le r \le 1$:

        $$R = \lambda_1^2\big[r - k(1 + r)^2\big] > 0 \iff \frac{r}{(1 + r)^2} > k$$

        Hàm $\frac{r}{(1+r)^2}$ tăng trên $[0, 1]$ (đạo hàm $\frac{1 - r}{(1+r)^3} \ge 0$). Vậy $R > 0$ khi và chỉ khi tỉ số $\lambda_2/\lambda_1$ vượt một ngưỡng phụ thuộc $k$. Với $k = 0.04$: $\frac{r}{(1+r)^2} = 0.04$ cho $r \approx 0.043$. Với $k = 0.06$: $r \approx 0.068$. **$k$ lớn → đòi hỏi hai trị riêng cân bằng hơn → ít góc hơn.** Giá trị 0.04–0.06 là lựa chọn thực nghiệm của Harris & Stephens, không có chứng minh tối ưu. $\blacksquare$

        Đã kiểm tra: tính $\det - k\,\text{tr}^2$ từ Sobel và tổng hộp `blockSize` cho cùng kết quả với `cv.cornerHarris` (sai lệch tương đối $2 \times 10^{-6}$ sau khi chuẩn hóa thang đo).
        :::

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

        :::proof công thức đóng của min(λ1, λ2)
        Giải phương trình đặc trưng $\lambda^2 - (A + C)\lambda + (AC - B^2) = 0$:

        $$\lambda = \frac{(A + C) \pm \sqrt{(A + C)^2 - 4(AC - B^2)}}{2} = \frac{A + C}{2} \pm \sqrt{\Big(\frac{A - C}{2}\Big)^2 + B^2}$$

        (vì $(A+C)^2 - 4AC = (A - C)^2$). Vậy

        $$\lambda_{\min} = \frac{A + C}{2} - \sqrt{\Big(\frac{A - C}{2}\Big)^2 + B^2}$$

        Biểu thức trong căn luôn $\ge 0$, nên trị riêng luôn thực (đúng với ma trận đối xứng).

        **Vì sao Shi–Tomasi "tốt cho tracking".** Tiêu chí $\lambda_{\min} > \tau$ nói rằng *dịch theo hướng tệ nhất* cũng làm cửa sổ thay đổi ít nhất $\tau$. Ma trận $M$ này **chính là ma trận phải nghịch đảo trong Lucas–Kanade** (xem ghi chú Optical Flow): $\lambda_{\min}$ lớn nghĩa là hệ phương trình ổn định, không bị nhiễu khuếch đại. Đó là lý do bài báo gốc tên là *Good Features to Track* và `goodFeaturesToTrack` thường đi cùng `calcOpticalFlowPyrLK`.
        :::

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
