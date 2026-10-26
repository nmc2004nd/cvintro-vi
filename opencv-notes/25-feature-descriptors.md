---
title: 25. Feature Detectors & Descriptors - SIFT, FAST, BRIEF, ORB
lesson: lesson20_feature_detection_matching
after: SIFT
draft: true
---
- **Keypoint (detector)**: tìm điểm đặc biệt (vị trí, tỷ lệ, hướng)
- **Descriptor**: mô tả vùng quanh keypoint bằng một vector → để so khớp giữa các ảnh

| Thuật toán | Loại | Descriptor | Norm khi so khớp | Bất biến tỷ lệ / xoay | Tốc độ | Bản quyền |
|---|---|---|---|---|---|---|
| SIFT | Detector + descriptor | 128 số thực | `NORM_L2` | Có / Có | Chậm | Hết hạn 2020, có trong OpenCV chính từ 4.4 |
| SURF | Detector + descriptor | 64 số thực | `NORM_L2` | Có / Có | Nhanh hơn SIFT | Vẫn non-free (contrib) |
| FAST | Chỉ detector | - | - | Không / Không | Rất nhanh | Tự do |
| BRIEF | Chỉ descriptor | 128/256/512 bit | `NORM_HAMMING` | Không / Không | Rất nhanh | Contrib (`xfeatures2d`) |
| ORB | Detector + descriptor | 256 bit (32 byte) | `NORM_HAMMING` | Có (kim tự tháp) / Có | Nhanh | Tự do |

- Các hàm chung của mọi detector:
    - `kp = detector.detect(gray, mask)`: tìm keypoint
    - `kp, des = detector.compute(gray, kp)`: tính descriptor cho keypoint có sẵn
    - `kp, des = detector.detectAndCompute(gray, mask)`: làm cả hai
    - Mỗi `cv.KeyPoint` có: `pt` (x, y), `size` (đường kính vùng), `angle`, `response` (độ mạnh), `octave` (tầng kim tự tháp)
    - Vẽ: `cv.drawKeypoints(img, kp, None, flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)` → vẽ cả kích thước và hướng
- ==**SIFT (Scale-Invariant Feature Transform)**== - David Lowe, 2004
    - **B1. Tìm cực trị trong không gian tỷ lệ**
        - LoG với $\sigma$ khác nhau phát hiện đốm (blob) ở các kích thước khác nhau, nhưng LoG tốn kém
        - ==Xấp xỉ LoG bằng DoG (Difference of Gaussians)==: hiệu hai ảnh làm mờ với $\sigma$ và $k\sigma$, làm trên từng tầng kim tự tháp (octave)
        - Một pixel là cực trị nếu lớn/nhỏ nhất so với 8 lân cận cùng tỷ lệ và 9 + 9 lân cận ở tỷ lệ trên và dưới
        - Tham số gợi ý: 4 octave, 5 mức tỷ lệ, $\sigma = 1.6$, $k = \sqrt{2}$
    - **B2. Lọc keypoint**
        - Loại điểm tương phản thấp: ngưỡng `contrastThreshold` (mặc định 0.04)
        - Loại điểm nằm trên cạnh (DoG phản hồi mạnh ở cạnh): dùng tỷ số trị riêng giống Harris, ngưỡng `edgeThreshold` (mặc định 10)
    - **B3. Gán hướng**: histogram hướng gradient 36 bins quanh keypoint, lấy đỉnh cao nhất; đỉnh nào > 80% đỉnh cao nhất thì tạo thêm keypoint với hướng đó → ==bất biến với xoay==
    - **B4. Descriptor**: vùng 16x16 quanh keypoint chia thành 16 ô 4x4, mỗi ô một histogram 8 hướng → ==4 x 4 x 8 = 128 chiều==
    - **B5. So khớp**: láng giềng gần nhất + ratio test (xem phần Feature Matching)

    ```python
    sift = cv.SIFT_create()
    kp, des = sift.detectAndCompute(gray, None)        # des: (số keypoint, 128) float32
    img2 = cv.drawKeypoints(gray, kp, None, flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    ```

- ==**FAST (Features from Accelerated Segment Test)**== - Rosten & Drummond, 2006
    - Xét vòng tròn 16 pixel quanh pixel p (cường độ $I_p$), ngưỡng t
    - ==p là góc nếu có n pixel liên tiếp trên vòng đều sáng hơn $I_p + t$ hoặc đều tối hơn $I_p - t$==
        - Bài báo chọn n = 12; OpenCV mặc định `TYPE_9_16` (n = 9 trên vòng 16)
    - Kiểm tra nhanh: xét pixel 1, 9 rồi 5, 13 trước, loại được phần lớn điểm không phải góc
    - Bản dùng machine learning (cây quyết định ID3) để chọn thứ tự kiểm tra tối ưu
    - Non-maximum suppression: hai góc kề nhau giữ góc có tổng chênh lệch tuyệt đối với 16 pixel lớn hơn
    - Mặc định: `threshold=10`, `nonmaxSuppression=True`

    ```python
    fast = cv.FastFeatureDetector_create(threshold=40)
    kp = fast.detect(img, None)
    print(fast.getThreshold(), fast.getNonmaxSuppression(), fast.getType())
    fast.setNonmaxSuppression(False)                   # tắt NMS → nhiều điểm hơn hẳn
    ```

- ==**BRIEF (Binary Robust Independent Elementary Features)**==
    - ==Chỉ là descriptor==, cần detector khác (FAST, STAR...)
    - Làm mờ vùng ảnh, chọn $n_d$ cặp điểm (p, q): $I(p) < I(q)$ thì bit = 1, ngược lại 0 → chuỗi $n_d$ bit
    - $n_d$ = 128, 256 hoặc 512 bit; OpenCV mặc định 256 bit = 32 byte
    - So khớp bằng khoảng cách Hamming (đếm bit khác nhau, XOR + popcount) → rất nhanh
    - Không bất biến với xoay
    - Nằm trong `opencv-contrib-python`: `cv.xfeatures2d.BriefDescriptorExtractor_create()`
- ==**ORB (Oriented FAST and Rotated BRIEF)**== - Rublee et al., 2011, ==thay thế miễn phí cho SIFT/SURF==
    - Detector: FAST trên kim tự tháp ảnh (bất biến tỷ lệ) + xếp hạng bằng điểm Harris, giữ N điểm tốt nhất
    - Hướng: vector từ tâm vùng tới trọng tâm cường độ (intensity centroid) tính bằng moment
    - Descriptor: **rBRIEF** = BRIEF được xoay theo hướng keypoint (rời rạc hóa theo bước 12°) và chọn các cặp điểm ít tương quan
    - Tham số chính của `cv.ORB_create()`:
        - `nfeatures`: số keypoint tối đa (mặc định 500)
        - `scoreType`: `cv.ORB_HARRIS_SCORE` (mặc định) hoặc `cv.ORB_FAST_SCORE`
        - `WTA_K`: số điểm so sánh mỗi lần; 2 (mặc định) → dùng `NORM_HAMMING`, 3 hoặc 4 → dùng `NORM_HAMMING2`

    ```python
    orb = cv.ORB_create(nfeatures=500)
    kp, des = orb.detectAndCompute(img, None)          # des: (N, 32) uint8
    img2 = cv.drawKeypoints(img, kp, None, color=(0, 255, 0), flags=0)
    ```

    ![](img/opencv-notes/25-feature-descriptors-1.png)

- ==Chọn thuật toán:==
    - ==Cần chính xác, ảnh thay đổi tỷ lệ/góc nhìn nhiều → SIFT==
    - ==Cần nhanh, thời gian thực, thiết bị yếu → ORB==
    - ==Chỉ cần điểm để theo dõi (optical flow) → FAST hoặc Shi-Tomasi==
