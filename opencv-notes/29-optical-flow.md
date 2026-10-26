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

    - $I_x, I_y$: gradient không gian, $I_t$: gradient theo thời gian, $(u, v)$: vector chuyển động cần tìm
    - ==Một phương trình, hai ẩn → không giải được tại một pixel đơn lẻ== (aperture problem)
- ==**Lucas-Kanade**==
    - Giả sử cả vùng 3x3 quanh điểm chuyển động như nhau → 9 phương trình, 2 ẩn → giải bằng bình phương tối thiểu:

        $$\begin{bmatrix} u \\ v \end{bmatrix} = \begin{bmatrix} \sum I_x^2 & \sum I_x I_y \\ \sum I_x I_y & \sum I_y^2 \end{bmatrix}^{-1} \begin{bmatrix} -\sum I_x I_t \\ -\sum I_y I_t \end{bmatrix}$$

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
