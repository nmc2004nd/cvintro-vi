---
title: 29. Optical Flow
lesson: lesson21_optical_flow
after:
draft: true
---
| Hàm | Loại | Kết quả |
|---|---|---|
| `cv.calcOpticalFlowPyrLK()` | Thưa (sparse), Lucas-Kanade | Vị trí mới của một tập điểm |
| `cv.calcOpticalFlowFarneback()` | Dày (dense), Gunnar Farneback | Vector chuyển động $(u, v)$ cho **mọi** pixel |

- Optical flow: ==chuyển động biểu kiến của các pixel giữa hai frame liên tiếp==, là trường vector 2D
- Giả thiết:
    - ==Độ sáng không đổi== khi pixel di chuyển (brightness constancy)
    - ==Chuyển động nhỏ== giữa hai frame
    - Các pixel lân cận chuyển động giống nhau
- Phương trình optical flow:
    - $I(x, y, t) = I(x + dx, y + dy, t + dt)$, khai triển Taylor →

        $$I_x u + I_y v + I_t = 0$$

        :::proof phương trình optical flow và bài toán khẩu độ
        **Bước 1 – Taylor bậc nhất** (dịch nhỏ):

        $$I(x + dx, y + dy, t + dt) \approx I(x, y, t) + I_x\,dx + I_y\,dy + I_t\,dt$$

        **Bước 2 – dùng giả thiết độ sáng không đổi**, vế trái bằng $I(x, y, t)$, nên

        $$I_x\,dx + I_y\,dy + I_t\,dt = 0$$

        **Bước 3 – chia cho $dt$** và đặt $u = dx/dt$, $v = dy/dt$ (với hai frame liên tiếp, $dt = 1$ frame và $I_t$ = hiệu hai frame):

        $$I_x u + I_y v + I_t = 0 \iff \nabla I \cdot (u, v) = -I_t \qquad \blacksquare$$

        **Bài toán khẩu độ (aperture problem) – chính xác thì biết được gì?** Phương trình $\nabla I \cdot \mathbf{d} = -I_t$ là một **đường thẳng** trong mặt phẳng $(u, v)$. Nếu $\mathbf{d}$ là một nghiệm thì $\mathbf{d} + c\,\mathbf{d}_\perp$ (với $\mathbf{d}_\perp \perp \nabla I$) cũng là nghiệm, vì $\nabla I \cdot \mathbf{d}_\perp = 0$. Chỉ xác định được **thành phần theo hướng gradient**:

        $$\mathbf{d} \cdot \frac{\nabla I}{|\nabla I|} = \frac{-I_t}{|\nabla I|} \quad \text{(normal flow)}$$

        Thành phần dọc theo cạnh hoàn toàn không đo được. Ví dụ quen thuộc: nhìn một vạch thẳng dài di chuyển qua một lỗ nhỏ, ta chỉ thấy nó chuyển động vuông góc với chính nó, bất kể nó thực ra đi chéo.

        **Khi nào Taylor bậc nhất đúng:** khi chuyển động nhỏ hơn khoảng cách mà ảnh còn gần tuyến tính – cỡ dưới 1 pixel với ảnh nhiều chi tiết. Đó là giả thiết "chuyển động nhỏ" ở trên, và là lý do cần kim tự tháp.
        :::


    - $I_x, I_y$: gradient không gian, $I_t$: gradient theo thời gian, $(u, v)$: vector chuyển động cần tìm
    - ==Một phương trình, hai ẩn → không giải được tại một pixel đơn lẻ== (aperture problem)
- ==**Lucas-Kanade**==
    - Giả sử cả vùng 3x3 quanh điểm chuyển động như nhau → 9 phương trình, 2 ẩn → giải bằng bình phương tối thiểu:

        $$\begin{bmatrix} u \\ v \end{bmatrix} = \begin{bmatrix} \sum I_x^2 & \sum I_x I_y \\ \sum I_x I_y & \sum I_y^2 \end{bmatrix}^{-1} \begin{bmatrix} -\sum I_x I_t \\ -\sum I_y I_t \end{bmatrix}$$

        :::proof nghiệm Lucas–Kanade từ bình phương tối thiểu
        **Bước 1 – xếp $n$ phương trình** (một cho mỗi pixel $q_i$ trong cửa sổ) thành $A\mathbf{d} = \mathbf{b}$:

        $$A = \begin{bmatrix} I_x(q_1) & I_y(q_1) \\ \vdots & \vdots \\ I_x(q_n) & I_y(q_n) \end{bmatrix}, \quad \mathbf{d} = \begin{bmatrix} u \\ v \end{bmatrix}, \quad \mathbf{b} = -\begin{bmatrix} I_t(q_1) \\ \vdots \\ I_t(q_n) \end{bmatrix}$$

        **Bước 2 – cực tiểu sai số bình phương** $S(u, v) = \sum_i (I_{x,i}u + I_{y,i}v + I_{t,i})^2$. Tại cực tiểu, đạo hàm riêng bằng 0:

        $$\frac{\partial S}{\partial u} = 2\sum_i I_{x,i}(I_{x,i}u + I_{y,i}v + I_{t,i}) = 0, \qquad \frac{\partial S}{\partial v} = 2\sum_i I_{y,i}(I_{x,i}u + I_{y,i}v + I_{t,i}) = 0$$

        **Bước 3 – sắp xếp lại** thành hệ 2x2 (phương trình chuẩn $A^TA\mathbf{d} = A^T\mathbf{b}$):

        $$\begin{bmatrix} \sum I_x^2 & \sum I_xI_y \\ \sum I_xI_y & \sum I_y^2 \end{bmatrix}\begin{bmatrix} u \\ v \end{bmatrix} = \begin{bmatrix} -\sum I_xI_t \\ -\sum I_yI_t \end{bmatrix}$$

        Nhân hai vế với nghịch đảo ra đúng công thức trên. $S$ là hàm bậc hai lồi (vì $A^TA$ nửa xác định dương), nên điểm dừng này là cực tiểu toàn cục. $\blacksquare$

        **Khi nào giải được – nối với Harris.** $A^TA$ chính là ma trận $M$ của Harris (với cửa sổ đều). Nó khả nghịch khi $\lambda_{\min} > 0$, và nghiệm ổn định khi $\lambda_{\min}$ đủ lớn so với nhiễu:

        - Vùng phẳng: $\lambda_1 \approx \lambda_2 \approx 0$ → gần suy biến, nghiệm là nhiễu.
        - Cạnh: hạng 1 → đúng bài toán khẩu độ, chỉ giải được thành phần vuông góc với cạnh.
        - Góc: hai trị riêng lớn → giải tốt.

        **Kiểm chứng số:** dịch một ảnh đã làm mờ đi $(0.4, -0.3)$ pixel, giải hệ trên cửa sổ 15x15 cho $(0.434, -0.349)$. Sai số đến từ xấp xỉ Taylor bậc nhất; `calcOpticalFlowPyrLK` **lặp** bước này (dịch ảnh theo ước lượng hiện tại rồi giải tiếp phần dư) đến khi thỏa `criteria`, nên hội tụ về giá trị đúng.

        **Vì sao kim tự tháp xử lý được chuyển động lớn.** Ở tầng $L$, ảnh thu nhỏ $2^L$ lần nên chuyển động $d$ pixel chỉ còn $d / 2^L$ – đủ nhỏ để Taylor đúng. Ước lượng ở tầng thô được nhân 2 làm điểm xuất phát cho tầng mịn hơn, tầng mịn chỉ phải sửa phần dư nhỏ. Với `maxLevel=2`, chuyển động tối đa xử lý được tăng khoảng $2^2 = 4$ lần.
        :::


    - Ma trận nghịch đảo giống ma trận M của Harris → ==giải tốt nhất tại các góc== → chọn điểm bằng `goodFeaturesToTrack`
    - Chuyển động lớn → dùng ==kim tự tháp ảnh==: ở tầng nhỏ, chuyển động lớn trở thành nhỏ
    - Hàm: `p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)`
        - `p0`: điểm cần theo dõi, `float32` shape (N, 1, 2)
        - `p1`: vị trí mới
        - `st`: 1 nếu tìm thấy điểm, 0 nếu mất
        - `winSize`: kích thước cửa sổ, `maxLevel`: số tầng kim tự tháp

    ```python
    feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
    lk_params = dict(winSize=(15, 15), maxLevel=2,
                     criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

    ret, old_frame = cap.read()
    old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)
    p0 = cv.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

        good_new = p1[st == 1]                     # chỉ giữ điểm còn theo dõi được
        good_old = p0[st == 1]
        for new, old in zip(good_new, good_old):
            a, b = new.ravel()
            c, d = old.ravel()
            cv.line(frame, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)

        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1, 1, 2)
    ```

    - Điểm mất dần theo thời gian → tài liệu khuyên ==định kỳ tìm lại điểm mới== (sample `lk_track.py` còn kiểm tra ngược để loại điểm sai)
- ==**Dense Optical Flow - Farneback**==
    - Tính flow cho mọi pixel, kết quả shape (H, W, 2)
    - `flow = cv.calcOpticalFlowFarneback(prev, next, None, pyr_scale, levels, winsize, iterations, poly_n, poly_sigma, flags)`
        - Tham số hay dùng: `0.5, 3, 15, 3, 5, 1.2, 0`
    - Trực quan hóa bằng HSV: ==Hue = hướng, Value = độ lớn==

    ```python
    flow = cv.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv.cartToPolar(flow[..., 0], flow[..., 1])

    hsv = np.zeros_like(frame)
    hsv[..., 0] = ang * 180 / np.pi / 2            # radian → 0-179 của OpenCV
    hsv[..., 1] = 255
    hsv[..., 2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)
    bgr = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    ```

![](img/opencv-notes/29-optical-flow-1.png)

- ==Ứng dụng:==
    - ==Theo dõi điểm, ổn định video (video stabilization)==
    - ==Phát hiện vật chuyển động, ước lượng hướng di chuyển==
    - ==Nội suy frame, nén video==
