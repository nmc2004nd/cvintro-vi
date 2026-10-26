---
title: 32. Pose Estimation
lesson: lesson27_camera_calibration
after:
draft: true
---
- Khi đã có thông số nội (`mtx`, `dist`) từ hiệu chỉnh camera, ta tìm được ==tư thế (pose) của vật thể so với camera==: vật xoay thế nào, nằm ở đâu
- Bài toán PnP (Perspective-n-Point): biết N điểm 3D trên vật và vị trí 2D tương ứng trong ảnh → tìm `rvec`, `tvec`
- Các hàm:

| Hàm | Ý nghĩa |
|---|---|
| `cv.solvePnP(objectPoints, imagePoints, mtx, dist)` | Tìm `rvec`, `tvec` |
| `cv.solvePnPRansac(...)` | Như trên nhưng loại outlier bằng RANSAC |
| `cv.projectPoints(points3D, rvec, tvec, mtx, dist)` | Chiếu điểm 3D lên ảnh |
| `cv.Rodrigues(rvec)` | Vector xoay (3x1) ↔ ma trận xoay (3x3) |
| `cv.drawFrameAxes(img, mtx, dist, rvec, tvec, length)` | Vẽ nhanh 3 trục tọa độ |

- `rvec` là vector xoay dạng ==Rodrigues==: hướng của vector là trục xoay, độ dài là góc xoay (radian)
- Ví dụ trong tài liệu: vẽ trục tọa độ 3D lên góc bàn cờ
    - Trục X (xanh dương), Y (xanh lá), Z (đỏ) dài 3 ô
    - ==Trục Z lấy giá trị âm== để hướng về phía camera (hệ tọa độ bàn cờ có Z hướng vào trong bàn cờ)

```python
with np.load("calib.npz") as X:
    mtx, dist = X["mtx"], X["dist"]

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((7 * 6, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1, 2)
axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]]).reshape(-1, 3)

def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel().astype("int32"))
    imgpts = imgpts.astype("int32")
    img = cv.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, corners = cv.findChessboardCorners(gray, (7, 6), None)
if ret:
    corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
    ret, rvec, tvec = cv.solvePnP(objp, corners2, mtx, dist)
    imgpts, jac = cv.projectPoints(axis, rvec, tvec, mtx, dist)   # chiếu 3 đầu trục lên ảnh
    img = draw(img, corners2, imgpts)
```

- Vẽ hình hộp: chiếu 8 đỉnh của hình lập phương rồi nối lại

    ```python
    cube = np.float32([[0, 0, 0], [0, 3, 0], [3, 3, 0], [3, 0, 0],
                       [0, 0, -3], [0, 3, -3], [3, 3, -3], [3, 0, -3]])
    imgpts, _ = cv.projectPoints(cube, rvec, tvec, mtx, dist)
    imgpts = np.int32(imgpts).reshape(-1, 2)
    img = cv.drawContours(img, [imgpts[:4]], -1, (0, 255, 0), -3)     # mặt đáy
    for i, j in zip(range(4), range(4, 8)):
        img = cv.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (255, 0, 0), 3)   # cột
    img = cv.drawContours(img, [imgpts[4:]], -1, (0, 0, 255), 3)      # mặt trên
    ```

![](img/opencv-notes/32-pose-estimation-1.png)

- Hình trái dùng `cv.drawFrameAxes`, màu theo quy ước X đỏ, Y xanh lá, Z xanh dương (khác màu trong hàm `draw` tự viết ở trên)

- ==Ứng dụng:==
    - ==Thực tế tăng cường (AR): đặt vật thể ảo đúng phối cảnh lên bàn cờ, marker ArUco==
    - ==Robot gắp vật: biết vị trí và hướng của vật so với camera==
    - ==Ước lượng hướng đầu người từ các điểm mốc khuôn mặt==
