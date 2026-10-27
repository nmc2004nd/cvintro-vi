---
title: 27. Feature Matching + Homography
lesson: lesson25_stitching_mosaicking
after:
draft: true
---
- Mục tiêu: ==tìm một vật thể đã biết trong ảnh khác==, kể cả khi bị xoay, co giãn, nhìn nghiêng
- Homography H (ma trận 3x3, 8 bậc tự do) ánh xạ điểm trên ==một mặt phẳng== giữa hai ảnh:

    $$s \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = H \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$

    :::proof vì sao H có 8 bậc tự do, cần 4 điểm, và khi nào homography đúng
    **1. Vì sao có hệ số $s$.** Khai triển $s\,(x', y', 1)^T = H(x, y, 1)^T$ với $H = [h_{ij}]$; hàng thứ ba cho $s = h_{31}x + h_{32}y + h_{33}$. Chia hai hàng đầu cho $s$:

    $$x' = \frac{h_{11}x + h_{12}y + h_{13}}{h_{31}x + h_{32}y + h_{33}}, \qquad y' = \frac{h_{21}x + h_{22}y + h_{23}}{h_{31}x + h_{32}y + h_{33}}$$

    Mẫu số thay đổi theo vị trí là thứ tạo ra hiệu ứng **phối cảnh** (vật xa nhỏ lại). Khi $h_{31} = h_{32} = 0$ thì quay về phép affine.

    **2. 8 bậc tự do.** Nhân $H$ với bất kỳ $c \ne 0$, cả tử và mẫu cùng nhân $c$, nên $(x', y')$ không đổi. $H$ có 9 số nhưng chỉ xác định **sai khác một hệ số**: 9 − 1 = 8 bậc tự do (thường cố định $h_{33} = 1$).

    **3. Mỗi cặp điểm cho 2 phương trình tuyến tính → cần 4 cặp.** Nhân chéo mẫu số:

    $$h_{11}x + h_{12}y + h_{13} - x'(h_{31}x + h_{32}y + h_{33}) = 0$$

    $$h_{21}x + h_{22}y + h_{23} - y'(h_{31}x + h_{32}y + h_{33}) = 0$$

    Hai phương trình này **tuyến tính** theo 9 ẩn $h_{ij}$. Bốn cặp điểm cho 8 phương trình, đúng bằng 8 bậc tự do. Với điều kiện không có 3 điểm nào thẳng hàng, hệ có nghiệm duy nhất (sai khác hệ số). Nhiều hơn 4 cặp thì giải bình phương tối thiểu: xếp thành $A\mathbf{h} = 0$ và lấy $\mathbf{h}$ là vector kỳ dị ứng với giá trị kỳ dị nhỏ nhất của $A$ (thuật toán **DLT**). Mình đã kiểm tra: DLT trên 4 góc khôi phục đúng $H$ ban đầu, trùng với `cv.getPerspectiveTransform`.

    **4. Vì sao chỉ đúng với mặt phẳng.** Hai camera $P = K[I \mid 0]$ và $P' = K'[R \mid \mathbf{t}]$; điểm 3D $X$ nằm trên mặt phẳng $\mathbf{n}^T X = d$. Khi đó $\frac{\mathbf{n}^T X}{d} = 1$, nên

    $$X' = RX + \mathbf{t} = RX + \mathbf{t}\,\frac{\mathbf{n}^T X}{d} = \Big(R + \frac{\mathbf{t}\,\mathbf{n}^T}{d}\Big)X$$

    Ảnh của $X$ là $\mathbf{x} \sim KX$ và $\mathbf{x}' \sim K'X'$, nên

    $$\mathbf{x}' \sim K'\Big(R + \frac{\mathbf{t}\,\mathbf{n}^T}{d}\Big)K^{-1}\,\mathbf{x} = H\mathbf{x}$$

    Ma trận này **chỉ phụ thuộc vào mặt phẳng** $(\mathbf{n}, d)$. Điểm không nằm trên mặt phẳng đó thì không thỏa – vì vậy homography chỉ khớp vật phẳng (sách, bìa đĩa, mặt tường). Trường hợp đặc biệt $\mathbf{t} = 0$ (camera chỉ xoay, như khi chụp ảnh toàn cảnh) cho $H = K'RK^{-1}$, đúng với **mọi** điểm bất kể độ sâu.
    :::


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

    :::proof cần lặp RANSAC bao nhiêu lần
    Gọi $w$ là tỉ lệ cặp đúng (inlier), $s = 4$ là số cặp mỗi lần lấy mẫu, $p$ là xác suất mong muốn (ví dụ 0.99) để **ít nhất một** lần lấy mẫu toàn inlier.

    - Một lần lấy mẫu toàn inlier: xác suất $w^s$ (coi các lần chọn độc lập).
    - Một lần lấy mẫu có ít nhất một outlier: $1 - w^s$.
    - Cả $N$ lần đều có outlier: $(1 - w^s)^N$.

    Cần $(1 - w^s)^N \le 1 - p$. Lấy log hai vế (log của số trong $(0,1)$ là số âm, nên đổi chiều bất đẳng thức khi chia):

    $$N \ge \frac{\log(1 - p)}{\log(1 - w^s)}$$

    **Ví dụ:** $w = 0.5$, $s = 4$, $p = 0.99$: $w^4 = 0.0625$, $N \ge \frac{\ln 0.01}{\ln 0.9375} = \frac{-4.605}{-0.0645} \approx 71.4$ → **72 lần**. Nếu tính fundamental matrix với $s = 8$ thì $w^8 \approx 0.0039$, cần khoảng **1177 lần** – mỗi điểm thêm vào mẫu làm số lần lặp tăng theo hàm mũ. Đó là lý do luôn dùng **mẫu nhỏ nhất có thể**.

    OpenCV ước lượng lại $w$ theo số inlier tốt nhất đã tìm được và giảm $N$ dần trong khi chạy (tham số `confidence`, mặc định 0.995; `maxIters`, mặc định 2000).
    :::


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
