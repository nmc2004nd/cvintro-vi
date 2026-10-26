---
title: 34. Depth Map from Stereo Images
lesson: lesson22_stereo_matching
after:
draft: true
---
- Hai camera đặt song song, cách nhau đoạn B (baseline), cùng tiêu cự f
- Một điểm 3D chiếu lên ảnh trái tại x, ảnh phải tại x' → ==disparity $d = x - x'$==
- Độ sâu:

    $$Z = \frac{B \cdot f}{d}$$

    - ==Disparity lớn → vật ở gần; disparity nhỏ → vật ở xa==
- ==Điều kiện: hai ảnh phải được chỉnh song song (rectified)==: điểm tương ứng nằm trên cùng một hàng → chỉ cần tìm theo hàng ngang
    - Chưa rectify thì dùng `cv.stereoRectify` + `cv.initUndistortRectifyMap` + `cv.remap` (cần hiệu chỉnh stereo trước)

| Hàm | Thuật toán | Đặc điểm |
|---|---|---|
| `cv.StereoBM_create()` | Block Matching: so khớp khối dọc theo hàng | Nhanh, nhiều lỗ ở vùng ít kết cấu |
| `cv.StereoSGBM_create()` | Semi-Global Block Matching: thêm ràng buộc trơn theo nhiều hướng | Chậm hơn, mịn và đầy đủ hơn |

- Tham số chính:
    - `numDisparities`: khoảng disparity cần tìm, ==phải chia hết cho 16==
    - `blockSize`: kích thước khối so khớp, ==số lẻ== (BM: 5-21, SGBM: 3-11)
    - `minDisparity`: disparity nhỏ nhất (thường 0)
    - SGBM thêm:
        - `P1`, `P2`: phạt khi disparity hai pixel kề nhau chênh 1 / chênh nhiều hơn 1; ==`P2 > P1`==. Gợi ý: `P1 = 8 * cn * blockSize²`, `P2 = 32 * cn * blockSize²` (cn = số kênh)
        - `uniquenessRatio`: loại kết quả nếu khối tốt nhất không tốt hơn hẳn khối thứ hai (5-15)
        - `speckleWindowSize`, `speckleRange`: lọc các đốm nhiễu nhỏ
- ==Đầu vào là ảnh xám 8-bit== (SGBM nhận được cả ảnh màu)
- ==Kết quả kiểu `int16`, đã nhân 16== (4 bit phần thập phân) → disparity thật = kết quả / 16; pixel không khớp được có giá trị âm

```python
imgL = cv.imread("tsukuba_l.png", cv.IMREAD_GRAYSCALE)
imgR = cv.imread("tsukuba_r.png", cv.IMREAD_GRAYSCALE)

stereo = cv.StereoBM_create(numDisparities=32, blockSize=9)
disparity = stereo.compute(imgL, imgR).astype(np.float32) / 16

sgbm = cv.StereoSGBM_create(minDisparity=0, numDisparities=32, blockSize=5,
                            P1=8 * 5 ** 2, P2=32 * 5 ** 2,
                            uniquenessRatio=10, speckleWindowSize=100, speckleRange=2)
disparity2 = sgbm.compute(imgL, imgR).astype(np.float32) / 16
```

![](img/opencv-notes/34-stereo-depth-map-1.png)

- `numDisparities` phải đủ lớn hơn disparity lớn nhất của cảnh: cặp tsukuba trong repo có disparity tới khoảng 20-30 nên dùng 32 (tài liệu OpenCV dùng 16 với cặp tsukuba gốc)
- Đổi disparity thành tọa độ 3D: `points3D = cv.reprojectImageTo3D(disparity, Q)`, với Q lấy từ `cv.stereoRectify`
- ==Hạn chế:== vùng không có kết cấu (tường trơn), vùng lặp lại, vùng bị che ở một ảnh → disparity sai hoặc trống
- ==Ứng dụng:==
    - ==Đo khoảng cách cho robot, xe tự hành==
    - ==Tách tiền cảnh theo độ sâu, làm mờ hậu cảnh (hiệu ứng chân dung)==
