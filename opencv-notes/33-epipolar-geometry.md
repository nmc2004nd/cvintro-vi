---
title: 33. Epipolar Geometry
lesson: lesson28_epipolar_geometry
after:
draft: true
---
- Một ảnh mất thông tin độ sâu: mọi điểm trên tia OX đều chiếu về cùng một pixel. Có ảnh thứ hai thì các điểm đó chiếu thành ==một đường thẳng== trên ảnh thứ hai
- Các khái niệm:
    - **Epiline**: đường trên ảnh 2 chứa mọi vị trí có thể của điểm tương ứng với x ở ảnh 1 → ==tìm điểm tương ứng chỉ cần dò dọc epiline (bài toán 1D)==
    - **Epipolar plane**: mặt phẳng chứa X và tâm hai camera
    - **Epipole**: giao của đường nối hai tâm camera với mặt phẳng ảnh; mọi epiline đều đi qua epipole (có thể nằm ngoài ảnh)
- **Ma trận cơ bản (Fundamental Matrix) F** và **ma trận thiết yếu (Essential Matrix) E**:
    - Ràng buộc epipolar: ==$x'^T F x = 0$== với x, x' là cặp điểm tương ứng (tọa độ pixel)

        :::proof suy ra E = [t]×R, F = K'^{-T}EK^{-1} và epiline
        **Thiết lập.** Camera 1 ở gốc tọa độ. Điểm 3D có tọa độ $X$ trong hệ camera 1 và $X' = RX + \mathbf{t}$ trong hệ camera 2. Tọa độ ảnh chuẩn hóa: $\hat{\mathbf{x}} \sim X$, $\hat{\mathbf{x}}' \sim X'$ (tức $\hat{\mathbf{x}} = K^{-1}\mathbf{x}$).

        **Bước 1 – ba vector đồng phẳng.** Trong hệ camera 2: tâm camera 2 ở gốc, tâm camera 1 ở $\mathbf{t}$, điểm 3D ở $X'$. Ba điểm này (và gốc) tạo thành **mặt phẳng epipolar**. Các vector $X'$, $\mathbf{t}$, và $X' - \mathbf{t} = RX$ cùng nằm trong mặt phẳng đó, nên $X'$ vuông góc với pháp tuyến $\mathbf{t} \times RX$:

        $$X'^T(\mathbf{t} \times RX) = 0$$

        **Bước 2 – viết tích có hướng thành ma trận.** $\mathbf{t} \times \mathbf{a} = [\mathbf{t}]_\times\mathbf{a}$ với

        $$[\mathbf{t}]_\times = \begin{bmatrix} 0 & -t_z & t_y \\ t_z & 0 & -t_x \\ -t_y & t_x & 0 \end{bmatrix}$$

        (kiểm tra từng thành phần của tích có hướng). Thay vào Bước 1:

        $$X'^T\,\underbrace{[\mathbf{t}]_\times R}_{E}\,X = 0$$

        Phương trình đồng nhất nên chia hai vế cho độ sâu: $\hat{\mathbf{x}}'^T E\,\hat{\mathbf{x}} = 0$. $\blacksquare$

        **Bước 3 – sang tọa độ pixel.** Thay $\hat{\mathbf{x}} = K^{-1}\mathbf{x}$, $\hat{\mathbf{x}}' = K'^{-1}\mathbf{x}'$:

        $$\mathbf{x}'^T\,\underbrace{K'^{-T}EK^{-1}}_{F}\,\mathbf{x} = 0 \qquad \blacksquare$$

        **Hạng 2.** $[\mathbf{t}]_\times\mathbf{t} = \mathbf{t} \times \mathbf{t} = 0$ nên $[\mathbf{t}]_\times$ có nhân khác 0, hạng 2. Nhân với ma trận khả nghịch không làm tăng hạng, nên $E$, $F$ đều hạng 2, $\det F = 0$.

        **Bậc tự do.** $F$ có 9 số, trừ 1 (sai khác hệ số), trừ 1 (ràng buộc $\det F = 0$) → **7**. Mỗi cặp điểm cho **một** phương trình tuyến tính $\mathbf{x}'^TF\mathbf{x} = 0$ theo 9 phần tử của $F$. Thuật toán 8 điểm dùng 8 phương trình để giải tuyến tính (bỏ qua ràng buộc det), sau đó ép hạng 2 bằng SVD (đặt giá trị kỳ dị nhỏ nhất bằng 0). $E$ chỉ có 5 bậc tự do (3 cho xoay, 2 cho hướng của $\mathbf{t}$ – độ dài của $\mathbf{t}$ không xác định được từ ảnh).

        **Epiline.** Một đường thẳng $ax + by + c = 0$ viết bằng tọa độ đồng nhất là $\mathbf{l}^T\mathbf{x} = 0$ với $\mathbf{l} = (a, b, c)$. Cố định $\mathbf{x}$, đặt $\mathbf{l}' = F\mathbf{x}$; ràng buộc epipolar thành $\mathbf{x}'^T\mathbf{l}' = 0$: mọi điểm tương ứng $\mathbf{x}'$ nằm trên đường thẳng $\mathbf{l}' = F\mathbf{x}$. Tương tự, chuyển vị ràng buộc cho $\mathbf{x}^T(F^T\mathbf{x}') = 0$, nên $\mathbf{l} = F^T\mathbf{x}'$. Để vẽ, tính hai đầu mút tại $x = 0$ và $x = W$: $y = -(c + ax)/b$.

        **Epipole.** Epipole $\mathbf{e}$ trên ảnh 1 thỏa $F\mathbf{e} = 0$ (vector trong nhân của $F$). Khi đó mọi epiline $\mathbf{l} = F^T\mathbf{x}'$ đều đi qua $\mathbf{e}$ vì $\mathbf{e}^T F^T\mathbf{x}' = (F\mathbf{e})^T\mathbf{x}' = 0$ – đúng như "mọi epiline đều đi qua epipole".

        **Kiểm chứng số:** hai camera mô phỏng ($K \ne K'$, có xoay và tịnh tiến), 10 điểm 3D ngẫu nhiên: $\max|\mathbf{x}'^TF\mathbf{x}| = 2 \times 10^{-16}$ và hạng của $F$ bằng 2.
        :::

    - E chứa phép xoay và tịnh tiến giữa hai camera, dùng tọa độ đã chuẩn hóa; F = E + thông số nội: $F = K'^{-T} E K^{-1}$
    - F là ma trận 3x3, hạng 2, 7 bậc tự do
    - Epiline trên ảnh 2 ứng với x: $l' = F x$; trên ảnh 1 ứng với x': $l = F^T x'$
    - ==Cần tối thiểu 8 cặp điểm== (thuật toán 8 điểm), nên dùng RANSAC/LMedS để chống outlier
- Hàm:
    - `F, mask = cv.findFundamentalMat(pts1, pts2, method)`: `method` = `cv.FM_8POINT`, `cv.FM_LMEDS`, `cv.FM_RANSAC`; `mask` = 1 với inlier
    - `lines = cv.computeCorrespondEpilines(points, whichImage, F)`
        - `whichImage = 1`: điểm thuộc ảnh 1 → trả về epiline trên ảnh 2
        - `whichImage = 2`: điểm thuộc ảnh 2 → trả về epiline trên ảnh 1
        - Mỗi đường là (a, b, c) với $ax + by + c = 0$

```python
sift = cv.SIFT_create()
kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

flann = cv.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
matches = flann.knnMatch(des1, des2, k=2)

pts1, pts2 = [], []
for m, n in matches:
    if m.distance < 0.8 * n.distance:
        pts2.append(kp2[m.trainIdx].pt)
        pts1.append(kp1[m.queryIdx].pt)

pts1, pts2 = np.int32(pts1), np.int32(pts2)
F, mask = cv.findFundamentalMat(pts1, pts2, cv.FM_LMEDS)
pts1 = pts1[mask.ravel() == 1]                         # chỉ giữ inlier
pts2 = pts2[mask.ravel() == 1]

def drawlines(img1, img2, lines, pts1, pts2):
    """Vẽ epiline lên img1, chấm điểm tương ứng lên cả hai ảnh."""
    r, c = img1.shape
    img1 = cv.cvtColor(img1, cv.COLOR_GRAY2BGR)
    img2 = cv.cvtColor(img2, cv.COLOR_GRAY2BGR)
    for r_, pt1, pt2 in zip(lines, pts1, pts2):
        color = tuple(np.random.randint(0, 255, 3).tolist())
        x0, y0 = map(int, [0, -r_[2] / r_[1]])          # giao với cạnh trái (x = 0)
        x1, y1 = map(int, [c, -(r_[2] + r_[0] * c) / r_[1]])  # giao với cạnh phải
        img1 = cv.line(img1, (x0, y0), (x1, y1), color, 1)
        img1 = cv.circle(img1, tuple(map(int, pt1)), 5, color, -1)
        img2 = cv.circle(img2, tuple(map(int, pt2)), 5, color, -1)
    return img1, img2

# epiline trên ảnh trái ứng với điểm ở ảnh phải
lines1 = cv.computeCorrespondEpilines(pts2.reshape(-1, 1, 2), 2, F).reshape(-1, 3)
img5, img6 = drawlines(img1, img2, lines1, pts1, pts2)

# epiline trên ảnh phải ứng với điểm ở ảnh trái
lines2 = cv.computeCorrespondEpilines(pts1.reshape(-1, 1, 2), 1, F).reshape(-1, 3)
img3, img4 = drawlines(img2, img1, lines2, pts2, pts1)
```

![](img/opencv-notes/33-epipolar-geometry-1.png)

- Nếu camera thứ hai chỉ dịch ngang so với camera thứ nhất thì các epiline song song và nằm ngang (trường hợp stereo đã rectify). Trong hình trên các epiline không song song mà hội tụ về một epipole nằm ngoài khung ảnh
- ==Kết quả F rất nhạy với chất lượng điểm==: điểm sai, ít điểm, hoặc mọi điểm nằm trên cùng một mặt phẳng → F sai
- Khi đã biết thông số nội K: dùng `cv.findEssentialMat` rồi `cv.recoverPose` để lấy R, t giữa hai camera (bước đầu của Structure from Motion)
- ==Ứng dụng:==
    - ==Thu hẹp vùng tìm điểm tương ứng trong stereo matching==
    - ==Chỉnh ảnh song song (rectification) trước khi tính độ sâu==
    - ==Khôi phục chuyển động camera trong SfM, Visual Odometry==
