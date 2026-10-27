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

        :::proof vì sao ngưỡng cục bộ chịu được ánh sáng không đều
        **Mô hình ánh sáng.** Giả sử ảnh = nội dung + độ sáng nền: $I(x, y) = S(x, y) + L(x, y)$, trong đó $L$ (ánh sáng, bóng đổ) thay đổi *chậm*, gần như hằng số trong một cửa sổ $\Omega$ kích thước `blockSize`.

        **Bước 1.** Với trọng số $w$ có tổng bằng 1 (trung bình đều $w = 1/N$, hoặc Gauss đã chuẩn hóa), và $L \approx L_0$ trong $\Omega$:

        $$\sum_{\Omega} w\,I = \sum_{\Omega} w\,S + \sum_{\Omega} w\,L \approx \overline{S} + L_0 \sum_\Omega w = \overline{S} + L_0$$

        **Bước 2.** Điều kiện giữ pixel ở `THRESH_BINARY` là $I(x, y) > T(x, y) = \sum w I - C$, tương đương

        $$S(x, y) + L_0 > \overline{S} + L_0 - C \iff S(x, y) - \overline{S} > -C$$

        $L_0$ **bị triệt tiêu**: quyết định chỉ còn phụ thuộc vào việc pixel sáng hơn hay tối hơn trung bình *xung quanh nó*, không phụ thuộc vùng đó đang sáng hay đang bị bóng. Ngưỡng toàn cục không làm được điều này vì $L$ khác nhau giữa các vùng. $\blacksquare$

        **Vì sao trọng số phải có tổng bằng 1.** Nếu $\sum w = k \ne 1$ thì ở vùng phẳng $I \equiv c$, ngưỡng thành $kc - C$, lệch theo độ sáng $c$, và $L_0$ không còn triệt tiêu. Với tổng bằng 1, vùng phẳng cho $T = c - C$ đúng như mong muốn.

        **Ý nghĩa của C.** Ở vùng phẳng, $S - \overline{S} \approx$ nhiễu nhỏ. Với $C > 0$, điều kiện $S - \overline{S} > -C$ đúng cho cả các pixel tối hơn trung bình một chút, nên vùng phẳng thành trắng hết thay vì lốm đốm nhiễu. Chỉ những nét tối hơn hẳn nền (chữ, đường kẻ) mới thành đen.

        **Thực tế OpenCV làm gì:** $T$ chính là ảnh đã làm mờ (`boxFilter` hoặc `GaussianBlur` với cửa sổ `blockSize`) trừ $C$, nên chi phí chỉ bằng một lần lọc. `blockSize` phải lẻ để cửa sổ có pixel tâm, và nên lớn hơn kích thước nét cần giữ (nếu cửa sổ nằm gọn trong một nét chữ dày thì trung bình chính là nét chữ, pixel không còn tối hơn trung bình).
        :::


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

    :::proof Otsu – từ phương sai trong lớp tới công thức tính nhanh
    Ký hiệu: $P(i) = n_i / N$ là xác suất mức xám $i$, lớp $C_1 = \{0, \dots, t-1\}$, $C_2 = \{t, \dots, L-1\}$, các đại lượng $q_k, \mu_k, \sigma_k^2$ như trên, và

    $$\mu_T = \sum_{i=0}^{L-1} i\,P(i), \qquad \sigma_T^2 = \sum_{i=0}^{L-1} (i - \mu_T)^2 P(i)$$

    là trung bình và phương sai của *toàn ảnh*, **không phụ thuộc $t$**.

    **Bước 0 – trung bình toàn ảnh là trung bình có trọng số của hai lớp.** Tách tổng làm hai phần:

    $$\mu_T = \sum_{C_1} iP(i) + \sum_{C_2} iP(i) = q_1\mu_1 + q_2\mu_2, \qquad q_1 + q_2 = 1$$

    **Bước 1 – phân rã phương sai: $\sigma_T^2 = \sigma_w^2 + \sigma_b^2$.** Xét phần tổng trên $C_1$, chèn $\mu_1$ vào:

    $$\sum_{C_1} (i - \mu_T)^2 P(i) = \sum_{C_1} \big[(i - \mu_1) + (\mu_1 - \mu_T)\big]^2 P(i)$$

    $$= \underbrace{\sum_{C_1} (i - \mu_1)^2 P(i)}_{= q_1\sigma_1^2} + 2(\mu_1 - \mu_T)\underbrace{\sum_{C_1} (i - \mu_1) P(i)}_{= q_1\mu_1 - \mu_1 q_1 = 0} + (\mu_1 - \mu_T)^2 \underbrace{\sum_{C_1} P(i)}_{= q_1}$$

    Số hạng giữa bằng 0 vì $\sum_{C_1} iP(i) = q_1\mu_1$ (định nghĩa của $\mu_1$). Làm y hệt cho $C_2$ rồi cộng lại:

    $$\sigma_T^2 = \underbrace{q_1\sigma_1^2 + q_2\sigma_2^2}_{\sigma_w^2 \text{ (trong lớp)}} + \underbrace{q_1(\mu_1 - \mu_T)^2 + q_2(\mu_2 - \mu_T)^2}_{\sigma_b^2 \text{ (giữa hai lớp)}}$$

    **Bước 2 – đổi bài toán.** $\sigma_T^2$ cố định, nên

    $$\arg\min_t \sigma_w^2(t) = \arg\max_t \sigma_b^2(t)$$

    **Bước 3 – rút gọn $\sigma_b^2$.** Từ Bước 0: $\mu_1 - \mu_T = \mu_1 - q_1\mu_1 - q_2\mu_2 = q_2(\mu_1 - \mu_2)$, tương tự $\mu_2 - \mu_T = -q_1(\mu_1 - \mu_2)$. Thay vào:

    $$\sigma_b^2 = q_1 q_2^2(\mu_1 - \mu_2)^2 + q_2 q_1^2(\mu_1 - \mu_2)^2 = q_1 q_2 (q_1 + q_2)(\mu_1 - \mu_2)^2 = q_1 q_2 (\mu_1 - \mu_2)^2$$

    Công thức này giải thích trực quan của Otsu: $\sigma_b^2$ lớn khi **hai lớp cách xa nhau** ($|\mu_1 - \mu_2|$ lớn) **và đều có nhiều pixel** ($q_1 q_2$ lớn nhất khi $q_1 = q_2 = 1/2$). Ngưỡng ở thung lũng giữa hai đỉnh thỏa cả hai điều đó.

    **Bước 4 – công thức tính nhanh $O(L)$.** Đặt $m(t) = \sum_{i<t} iP(i)$ (tổng tích lũy), khi đó $\mu_1 = m / q_1$, $\mu_2 = (\mu_T - m)/q_2$:

    $$\sigma_b^2 = q_1 q_2\left(\frac{m}{q_1} - \frac{\mu_T - m}{q_2}\right)^2 = \frac{\big(m q_2 - (\mu_T - m) q_1\big)^2}{q_1 q_2} = \frac{\big(\mu_T\,q_1 - m\big)^2}{q_1(1 - q_1)}$$

    (dùng $q_1 + q_2 = 1$ ở bước cuối). Chỉ cần hai mảng tổng tích lũy $q_1(t)$ và $m(t)$ là tính được $\sigma_b^2$ cho mọi $t$ cùng lúc. $\blacksquare$

    **Ví dụ tính tay** ($L = 4$): $P = (0.3,\ 0.2,\ 0.1,\ 0.4)$, nên $\mu_T = 0.2 + 0.2 + 1.2 = 1.6$ và $\sigma_T^2 = (0.2 + 0.4 + 3.6) - 1.6^2 = 1.64$.

    | $t$ | $C_1$ | $q_1$ | $m$ | $\sigma_b^2 = (1.6\,q_1 - m)^2 / (q_1(1-q_1))$ |
    |---|---|---|---|---|
    | 1 | {0} | 0.3 | 0 | $0.48^2/0.21 \approx 1.097$ |
    | 2 | {0, 1} | 0.5 | 0.2 | $0.6^2/0.25 = 1.44$ |
    | 3 | {0, 1, 2} | 0.6 | 0.4 | $0.56^2/0.24 \approx 1.307$ |

    Chọn $t = 2$. Kiểm tra lại bằng định nghĩa: $\mu_1 = 0.4$, $\sigma_1^2 = 0.24$, $\mu_2 = 2.8$, $\sigma_2^2 = 0.16$, nên $\sigma_w^2 = 0.5 \cdot 0.24 + 0.5 \cdot 0.16 = 0.2 = 1.64 - 1.44$ ✓.

    **Code NumPy** (cho cùng ngưỡng với OpenCV):

    ```python
    P = hist.ravel() / hist.sum()
    i = np.arange(256)
    q1 = np.cumsum(P)                 # q1[t]: lớp 1 gồm các mức 0..t
    m = np.cumsum(i * P)
    muT = m[-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        sb = (muT * q1 - m) ** 2 / (q1 * (1 - q1))
    t = np.nanargmax(sb)              # = giá trị ret của cv.threshold(..., THRESH_OTSU)
    ```

    Lưu ý chỉ số: `cumsum` tại vị trí $t$ gồm cả mức $t$, nên `t` ở đây là mức lớn nhất của lớp 1 – đúng với `ret` của OpenCV (pixel `> ret` thành `maxval`). Theo quy ước $C_1 = \{0..t-1\}$ ở trên thì đó là $t = \text{ret} + 1$. Mình đã chạy trên histogram hai đỉnh mô phỏng: cả ba cách (min $\sigma_w^2$, max $\sigma_b^2$, OpenCV) cho cùng một ngưỡng.

    **Liên hệ:** cực tiểu $\sigma_w^2$ chính là cực tiểu tổng bình phương khoảng cách tới tâm lớp, nên Otsu = **k-means với k = 2 trên trục mức xám**, giải chính xác bằng cách thử hết $L$ ngưỡng (trong 1D, phân cụm tối ưu luôn là một ngưỡng). Khi histogram chỉ có một đỉnh, $\sigma_b^2(t)$ gần như phẳng nên ngưỡng tìm được không còn ý nghĩa rõ ràng.
    :::

