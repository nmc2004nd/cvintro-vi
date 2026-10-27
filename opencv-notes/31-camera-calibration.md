---
title: 31. Camera Calibration
lesson: lesson27_camera_calibration
after:
draft: true
---
- Camera giá rẻ làm ảnh bị ==méo (distortion)==; hiệu chỉnh camera tìm ra các thông số để sửa méo và để đo đạc 3D
- **Hai loại méo:**
    - ==Méo xuyên tâm (radial)==: đường thẳng bị cong, càng xa tâm ảnh càng cong (méo thùng - barrel, méo gối - pincushion)

        $$x_{distorted} = x (1 + k_1 r^2 + k_2 r^4 + k_3 r^6)$$

        $$y_{distorted} = y (1 + k_1 r^2 + k_2 r^4 + k_3 r^6)$$

    - ==Méo tiếp tuyến (tangential)==: thấu kính không song song với cảm biến → một phần ảnh trông gần hơn

        $$x_{distorted} = x + [2 p_1 x y + p_2 (r^2 + 2 x^2)]$$

        $$y_{distorted} = y + [p_1 (r^2 + 2 y^2) + 2 p_2 x y]$$

    - ==Hệ số méo theo thứ tự OpenCV: $(k_1, k_2, p_1, p_2, k_3)$==

        :::proof vì sao méo xuyên tâm chỉ có lũy thừa chẵn, và mô hình đầy đủ của OpenCV
        **Khẳng định:** với thấu kính đối xứng quanh trục quang học, méo xuyên tâm có dạng $\mathbf{x}_d = \mathbf{x}\,L(r)$ với $L$ chỉ chứa lũy thừa **chẵn** của $r$.

        **Lập luận.** Đối xứng quay có hai hệ quả:

        1. Điểm bị đẩy dọc theo **bán kính** (không lệch sang ngang), nên $\mathbf{x}_d$ cùng hướng với $\mathbf{x}$: $\mathbf{x}_d = \mathbf{x}\,L(r)$, với $L$ chỉ phụ thuộc khoảng cách $r = \sqrt{x^2 + y^2}$ tới tâm.
        2. $L$ phải là hàm **trơn** của tọa độ $(x, y)$ tại tâm. Mà $r = \sqrt{x^2 + y^2}$ không khả vi tại gốc, còn $r^2 = x^2 + y^2$ là đa thức. Một hàm trơn, đối xứng quay của $(x, y)$ thì viết được thành hàm trơn của $r^2$. Khai triển Taylor theo $r^2$:

        $$L(r) = 1 + k_1 r^2 + k_2 r^4 + k_3 r^6 + \dots$$

        Số hạng hằng bằng 1 vì tại tâm không có méo. Cắt ở bậc 6 là đủ cho hầu hết ống kính; ống kính mắt cá cần mô hình khác (`cv.fisheye`). $\blacksquare$

        - $k_1 < 0$: điểm xa tâm bị **kéo vào** → méo thùng (barrel), đường thẳng phình ra ngoài.
        - $k_1 > 0$: điểm xa tâm bị **đẩy ra** → méo gối (pincushion).

        **Méo tiếp tuyến** (công thức của Brown–Conrady) là hạng tử bậc thấp nhất mô tả thấu kính bị lệch tâm/nghiêng; đây là mô hình thực nghiệm, không suy ra được từ một nguyên lý đối xứng như phần xuyên tâm.

        **Mô hình đầy đủ trong OpenCV** cộng cả hai lên tọa độ chuẩn hóa $(x, y) = (X/Z, Y/Z)$, rồi mới nhân $K$:

        $$x_d = x(1 + k_1r^2 + k_2r^4 + k_3r^6) + 2p_1xy + p_2(r^2 + 2x^2)$$

        $$y_d = y(1 + k_1r^2 + k_2r^4 + k_3r^6) + p_1(r^2 + 2y^2) + 2p_2xy$$

        $$u = f_x x_d + c_x, \qquad v = f_y y_d + c_y$$

        Mình đã kiểm tra: tự tính theo ba dòng trên cho kết quả trùng với `cv.projectPoints` (5 hệ số méo bất kỳ).
        :::

- **Thông số nội (intrinsic)** - riêng của camera, chỉ cần tính một lần:

    $$K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

    - $f_x, f_y$: tiêu cự (đơn vị pixel), $(c_x, c_y)$: tâm quang học

    :::proof từ camera lỗ kim tới ma trận K
    **Bước 1 – tam giác đồng dạng.** Đặt tâm quang học ở gốc, trục $Z$ nhìn về phía trước, mặt phẳng ảnh cách tâm một khoảng $f$ (tiêu cự, đơn vị mm). Tia nối điểm 3D $(X, Y, Z)$ với tâm cắt mặt phẳng ảnh tại $(x, y)$. Hai tam giác vuông có chung đỉnh ở tâm nên đồng dạng:

    $$\frac{x}{f} = \frac{X}{Z}, \quad \frac{y}{f} = \frac{Y}{Z} \;\Rightarrow\; x = f\frac{X}{Z}, \quad y = f\frac{Y}{Z}$$

    Chia cho $Z$ là lý do vật xa trông nhỏ hơn. Tọa độ $x_n = X/Z$, $y_n = Y/Z$ gọi là **tọa độ chuẩn hóa** (camera có $f = 1$).

    **Bước 2 – đổi từ mm sang pixel.** Cảm biến có pixel kích thước $p_x \times p_y$ mm, gốc ảnh ở góc trên trái thay vì ở tâm quang học $(c_x, c_y)$:

    $$u = \frac{f}{p_x}\,x_n + c_x = f_x\,x_n + c_x, \qquad v = f_y\,y_n + c_y$$

    Vì vậy $f_x = f/p_x$, $f_y = f/p_y$ có **đơn vị pixel**, và $f_x \ne f_y$ khi pixel không vuông.

    **Bước 3 – viết dạng ma trận** bằng tọa độ đồng nhất (chia cho thành phần thứ ba ở cuối):

    $$\begin{bmatrix} u \\ v \\ 1 \end{bmatrix} \sim \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}\begin{bmatrix} X \\ Y \\ Z \end{bmatrix} = \begin{bmatrix} f_xX + c_xZ \\ f_yY + c_yZ \\ Z \end{bmatrix} \;\to\; \Big(f_x\frac{X}{Z} + c_x,\ f_y\frac{Y}{Z} + c_y\Big) \qquad \blacksquare$$

    Cộng thêm thông số ngoại: điểm trong hệ thế giới $X_w$ được đưa về hệ camera bằng $X = RX_w + \mathbf{t}$ (`rvec`, `tvec`), nên toàn bộ phép chiếu là $\mathbf{x} \sim K[R \mid \mathbf{t}]X_w$. Méo ống kính được áp lên $(x_n, y_n)$ **trước khi** nhân $K$ (xem mục dưới).
    :::

- **Thông số ngoại (extrinsic)**: vector xoay `rvec` và tịnh tiến `tvec`, biến đổi từ hệ tọa độ thế giới sang hệ tọa độ camera, ==khác nhau với mỗi ảnh==
- **Chuẩn bị:**
    - In bàn cờ (chessboard), chụp ==ít nhất 10 ảnh== ở nhiều góc và vị trí khác nhau

        :::proof phương pháp Zhang – vì sao ảnh một mặt phẳng ở nhiều góc lại tìm được K
        Đây là thuật toán mà `calibrateCamera` dùng để khởi tạo (Zhang, 2000).

        **Bước 1 – mỗi ảnh bàn cờ cho một homography.** Bàn cờ nằm trên mặt phẳng $Z_w = 0$, nên với $R = [\mathbf{r}_1\ \mathbf{r}_2\ \mathbf{r}_3]$:

        $$\mathbf{x} \sim K[\mathbf{r}_1\ \mathbf{r}_2\ \mathbf{r}_3\ \mathbf{t}]\begin{bmatrix} X \\ Y \\ 0 \\ 1 \end{bmatrix} = K[\mathbf{r}_1\ \mathbf{r}_2\ \mathbf{t}]\begin{bmatrix} X \\ Y \\ 1 \end{bmatrix}$$

        Tức $H = [\mathbf{h}_1\ \mathbf{h}_2\ \mathbf{h}_3] = \lambda K[\mathbf{r}_1\ \mathbf{r}_2\ \mathbf{t}]$, tính được từ các góc bàn cờ (xem ghi chú Homography).

        **Bước 2 – hai ràng buộc từ tính chất của phép xoay.** Từ đó $\mathbf{r}_1 = \frac{1}{\lambda}K^{-1}\mathbf{h}_1$, $\mathbf{r}_2 = \frac{1}{\lambda}K^{-1}\mathbf{h}_2$. Các cột của ma trận xoay **vuông góc và có độ dài bằng nhau**:

        $$\mathbf{r}_1^T\mathbf{r}_2 = 0 \;\Rightarrow\; \mathbf{h}_1^T B\,\mathbf{h}_2 = 0$$

        $$\mathbf{r}_1^T\mathbf{r}_1 = \mathbf{r}_2^T\mathbf{r}_2 \;\Rightarrow\; \mathbf{h}_1^T B\,\mathbf{h}_1 = \mathbf{h}_2^T B\,\mathbf{h}_2$$

        với $B = K^{-T}K^{-1}$ (vì $\mathbf{r}_i^T\mathbf{r}_j = \frac{1}{\lambda^2}\mathbf{h}_i^T K^{-T}K^{-1}\mathbf{h}_j$, hệ số $\frac{1}{\lambda^2}$ ở hai vế triệt tiêu).

        **Bước 3 – đếm ẩn.** $B$ đối xứng 3x3 → 6 phần tử, xác định sai khác hệ số → 5 ẩn (ứng với 5 thông số $f_x, f_y, c_x, c_y$, skew). Hai ràng buộc ở Bước 2 **tuyến tính** theo các phần tử của $B$. Mỗi ảnh cho 2 phương trình, nên cần **ít nhất 3 ảnh** ở các hướng khác nhau (2 ảnh nếu giả sử skew = 0). Giải hệ tuyến tính ra $B$, rồi tách $K$ bằng phân tích Cholesky ($B = K^{-T}K^{-1}$).

        **Vì sao ảnh phải nghiêng nhiều góc khác nhau.** Nếu hai ảnh chỉ khác nhau một phép tịnh tiến song song với mặt bàn cờ, chúng cho cùng một cặp phương trình – không có thông tin mới. Ảnh chụp thẳng góc cũng yếu vì không ràng buộc được tiêu cự với khoảng cách.

        **Bước 4 – tinh chỉnh.** Nghiệm tuyến tính chỉ là khởi tạo; sau đó OpenCV cực tiểu **sai số chiếu lại** (Levenberg–Marquardt) theo cả $K$, hệ số méo và $(R, \mathbf{t})$ của từng ảnh:

        $$\min \sum_{\text{ảnh } i}\sum_{\text{góc } j}\big\|\mathbf{x}_{ij} - \pi(K, \text{dist}, R_i, \mathbf{t}_i, X_j)\big\|^2$$

        Giá trị `ret` trả về là $\sqrt{\text{tổng trên} / \text{số điểm}}$ (RMS, đơn vị pixel). Khuyến nghị 10+ ảnh vì có nhiều ẩn hơn (5 hệ số méo + 6 thông số ngoại cho mỗi ảnh) và để trung bình hóa sai số phát hiện góc. Trong hình minh họa ở dưới: dữ liệu mô phỏng với $f_x = 600$, $k_1 = -0.35$ cho ra lại $f_x \approx 600.1$, $k_1 \approx -0.36$, RMS ≈ 0.1 pixel.
        :::

    - **Object points**: tọa độ 3D các góc trong bàn cờ. Bàn cờ phẳng nên đặt Z = 0, mỗi ô dài 1 đơn vị: (0,0,0), (1,0,0), ..., (6,5,0)
    - **Image points**: tọa độ 2D các góc đó trong ảnh, tìm bằng `cv.findChessboardCorners`
    - ==`patternSize` là số **góc trong** (cols, rows)==, không phải số ô: bàn cờ 8x8 ô có 7x7 góc trong
    - Có thể dùng lưới hình tròn với `cv.findCirclesGrid()`, cần ít ảnh hơn
- **Tìm góc:**

    ```python
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    cols, rows = 7, 6                                        # số góc trong

    objp = np.zeros((cols * rows, 3), np.float32)
    objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)  # (0,0,0), (1,0,0), ...

    objpoints, imgpoints = [], []                            # điểm 3D thật, điểm 2D trên ảnh
    for fname in glob.glob("*.jpg"):
        img = cv.imread(fname)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        ret, corners = cv.findChessboardCorners(gray, (cols, rows), None)
        if ret:
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            cv.drawChessboardCorners(img, (cols, rows), corners2, ret)
    ```

- **Hiệu chỉnh:**

    ```python
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    ```

    - `ret`: sai số chiếu lại RMS (pixel), ==càng gần 0 càng tốt, thường < 1==
    - `mtx`: ma trận K; `dist`: hệ số méo; `rvecs`, `tvecs`: tư thế bàn cờ trong từng ảnh
    - `gray.shape[::-1]` = (w, h)
- **Sửa méo:**
    - Tinh chỉnh ma trận camera: `newK, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), alpha, (w, h))`
        - ==`alpha = 0`: cắt hết vùng đen, có thể mất pixel ở rìa==
        - ==`alpha = 1`: giữ mọi pixel gốc, xuất hiện vùng đen ở rìa==
        - `roi`: vùng hợp lệ để cắt ảnh
    - Cách 1: `cv.undistort`

    ```python
    dst = cv.undistort(img, mtx, dist, None, newK)
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    ```

    - Cách 2: tính bảng ánh xạ một lần, dùng lại cho nhiều frame video → nhanh hơn

    ```python
    mapx, mapy = cv.initUndistortRectifyMap(mtx, dist, None, newK, (w, h), cv.CV_32FC1)
    dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
    ```

![](img/opencv-notes/31-camera-calibration-1.png)

- Hình trên: 12 ảnh bàn cờ mô phỏng với méo thùng $k_1 = -0.35$ và $f_x = 600$; `calibrateCamera` ước lượng lại được $k_1 \approx -0.36$, $f_x \approx 600.1$, RMS ≈ 0.1 pixel
- **Sai số chiếu lại (re-projection error)**: chiếu ngược object points bằng thông số vừa tìm, so với image points

    ```python
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        # tổng bình phương sai số / số điểm = sai số bình phương trung bình của ảnh i
        mean_error += cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2SQR) / len(imgpoints2)
    print("total error:", mean_error / len(objpoints))
    ```

- ==Lưu kết quả để dùng lại==: `np.savez("calib.npz", mtx=mtx, dist=dist)`
