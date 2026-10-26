---
title: 27. Feature Matching + Homography
lesson: lesson25_stitching_mosaicking
after:
draft: true
---
- Mục tiêu: ==tìm một vật thể đã biết trong ảnh khác==, kể cả khi bị xoay, co giãn, nhìn nghiêng
- Homography H (ma trận 3x3, 8 bậc tự do) ánh xạ điểm trên ==một mặt phẳng== giữa hai ảnh:

    $$s \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = H \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

- ==Cần tối thiểu 4 cặp điểm đúng== để tính H
- Các bước:
    - **B1**: Tìm keypoint + descriptor ở ảnh vật thể và ảnh cảnh (SIFT, ORB)
    - **B2**: So khớp + ratio test → các cặp tốt `good`
    - **B3**: Nếu đủ cặp (ví dụ `MIN_MATCH_COUNT = 10`) thì tính H bằng `cv.findHomography` với RANSAC
    - **B4**: Biến đổi 4 góc ảnh vật thể bằng `cv.perspectiveTransform` → khung vật thể trong ảnh cảnh
- Hàm: `M, mask = cv.findHomography(srcPoints, dstPoints, method, ransacReprojThreshold)`
    - `srcPoints`, `dstPoints`: `float32` shape (N, 1, 2)
    - `method`: `0` (bình phương tối thiểu, dùng mọi điểm), ==`cv.RANSAC`==, `cv.LMEDS`, `cv.RHO`
    - `ransacReprojThreshold`: sai số chiếu lại tối đa (pixel) để coi là inlier, thường 3-5
    - `mask`: mảng 0/1, ==1 = inlier==
- RANSAC: lặp nhiều lần {chọn ngẫu nhiên 4 cặp → tính H → đếm số cặp khớp với H}, giữ H có nhiều inlier nhất → ==bền vững với các cặp so khớp sai==

```python
MIN_MATCH_COUNT = 10

sift = cv.SIFT_create()
kp1, des1 = sift.detectAndCompute(img1, None)     # img1: ảnh vật thể
kp2, des2 = sift.detectAndCompute(img2, None)     # img2: ảnh cảnh

flann = cv.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
matches = flann.knnMatch(des1, des2, k=2)
good = [m for m, n in matches if m.distance < 0.7 * n.distance]

if len(good) > MIN_MATCH_COUNT:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
    matchesMask = mask.ravel().tolist()

    h, w = img1.shape
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv.perspectiveTransform(pts, M)          # 4 góc vật thể trong ảnh cảnh
    img2 = cv.polylines(img2, [np.int32(dst)], True, 255, 3, cv.LINE_AA)
else:
    matchesMask = None

draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None,
                   matchesMask=matchesMask, flags=2)      # chỉ vẽ inlier
img3 = cv.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)
```

![](img/opencv-notes/27-homography-1.png)

- Phân biệt các hàm:
    - `cv.getPerspectiveTransform(4 điểm, 4 điểm)`: đúng 4 cặp, không lọc nhiễu
    - `cv.findHomography(N điểm, N điểm, cv.RANSAC)`: N ≥ 4 cặp, có lọc outlier
    - `cv.perspectiveTransform(points, M)`: biến đổi **điểm**
    - `cv.warpPerspective(img, M, dsize)`: biến đổi **cả ảnh**
- ==Ứng dụng:==
    - ==Ghép ảnh panorama: tính H giữa hai ảnh rồi `warpPerspective` một ảnh sang hệ tọa độ ảnh kia==
    - ==Nhận diện và định vị bìa sách, biển báo, poster==
    - ==Thực tế tăng cường (AR) trên mặt phẳng==
