---
title: 26. Feature Matching
lesson: lesson20_feature_detection_matching
after:
draft: true
---
| Matcher | Cách làm | Khi nào dùng |
|---|---|---|
| `cv.BFMatcher` | Brute-Force: so mỗi descriptor với **mọi** descriptor bên kia | Ít descriptor, cần kết quả chính xác |
| `cv.FlannBasedMatcher` | Tìm láng giềng gần đúng bằng cây (KD-tree, LSH) | Nhiều descriptor (hàng nghìn trở lên), cần nhanh |

- **Brute-Force Matcher**: `bf = cv.BFMatcher(normType, crossCheck)`
    - `normType`: cách đo khoảng cách
        - ==SIFT, SURF (số thực) → `cv.NORM_L2`== (mặc định)
        - ==ORB, BRIEF, BRISK (nhị phân) → `cv.NORM_HAMMING`==; ORB với `WTA_K` = 3 hoặc 4 → `cv.NORM_HAMMING2`
    - `crossCheck=True`: chỉ giữ cặp (i, j) nếu j là gần nhất của i **và** i là gần nhất của j → kết quả nhất quán hơn
- Hai cách so khớp:
    - `matches = bf.match(des1, des2)`: mỗi descriptor lấy 1 cặp tốt nhất
    - `matches = bf.knnMatch(des1, des2, k=2)`: mỗi descriptor lấy k cặp tốt nhất → dùng cho ratio test
- Kết quả là các đối tượng `DMatch`:
    - `distance`: khoảng cách giữa hai descriptor, ==càng nhỏ càng tốt==
    - `queryIdx`: chỉ số descriptor trong ảnh 1 (query) → `kp1[m.queryIdx].pt`
    - `trainIdx`: chỉ số descriptor trong ảnh 2 (train) → `kp2[m.trainIdx].pt`
    - `imgIdx`: chỉ số ảnh train (khi so với nhiều ảnh)
- **ORB + Brute-Force**

    ```python
    orb = cv.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda m: m.distance)   # tốt nhất lên đầu

    img3 = cv.drawMatches(img1, kp1, img2, kp2, matches[:30], None,
                          flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    ```

- ==**Ratio test của Lowe**==
    - Với mỗi descriptor lấy 2 láng giềng gần nhất m, n
    - ==Chỉ nhận m nếu `m.distance < 0.7 * n.distance` (0.7 - 0.8)==: cặp tốt nhất phải tốt hơn hẳn cặp thứ hai. Nếu hai cặp gần bằng nhau thì đặc trưng không phân biệt được (ví dụ cửa sổ lặp lại) → loại
    - Không dùng chung với `crossCheck=True`

    ```python
    sift = cv.SIFT_create()
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    bf = cv.BFMatcher()                                   # NORM_L2
    matches = bf.knnMatch(des1, des2, k=2)
    good = [[m] for m, n in matches if m.distance < 0.75 * n.distance]

    # drawMatchesKnn nhận list các list
    img3 = cv.drawMatchesKnn(img1, kp1, img2, kp2, good, None,
                             flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    ```

- **FLANN Matcher** (Fast Library for Approximate Nearest Neighbors)
    - Cần hai dict tham số:
        - `index_params`: thuật toán dựng chỉ mục
            - SIFT/SURF: `dict(algorithm=1, trees=5)` (`FLANN_INDEX_KDTREE = 1`)
            - ORB: `dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)` (`FLANN_INDEX_LSH = 6`)
        - `search_params`: `dict(checks=50)` - số lần duyệt cây, ==càng lớn càng chính xác nhưng chậm hơn==

    ```python
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(des1, des2, k=2)
    good = [m for m, n in matches if m.distance < 0.7 * n.distance]
    ```

    - Với LSH (ORB), `knnMatch` có thể trả về ít hơn 2 cặp cho một descriptor → kiểm tra `len(pair) == 2` trước khi tách `m, n`

![](img/opencv-notes/26-feature-matching-1.png)

- ==Sau khi so khớp vẫn còn cặp sai (outlier)== → dùng RANSAC khi ước lượng homography / ma trận cơ bản để loại (xem phần Homography)
