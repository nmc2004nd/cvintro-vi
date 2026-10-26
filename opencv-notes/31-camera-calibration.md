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
- **Thông số nội (intrinsic)** - riêng của camera, chỉ cần tính một lần:

    $$K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

    - $f_x, f_y$: tiêu cự (đơn vị pixel), $(c_x, c_y)$: tâm quang học
- **Thông số ngoại (extrinsic)**: vector xoay `rvec` và tịnh tiến `tvec`, biến đổi từ hệ tọa độ thế giới sang hệ tọa độ camera, ==khác nhau với mỗi ảnh==
- **Chuẩn bị:**
    - In bàn cờ (chessboard), chụp ==ít nhất 10 ảnh== ở nhiều góc và vị trí khác nhau
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
