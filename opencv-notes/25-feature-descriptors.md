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

            :::proof vì sao DoG ≈ (k − 1)σ²·LoG
            **Bước 1 – Gauss thỏa phương trình nhiệt** $\dfrac{\partial G}{\partial \sigma} = \sigma\,\nabla^2 G$, với $G = \frac{1}{2\pi\sigma^2}e^{-r^2/(2\sigma^2)}$, $r^2 = x^2 + y^2$.

            *Vế trái* (đạo hàm tích $\sigma^{-2} \cdot e^{\dots}$):

            $$\frac{\partial G}{\partial\sigma} = G\cdot\Big(-\frac{2}{\sigma} + \frac{r^2}{\sigma^3}\Big)$$

            *Vế phải*: $\partial_x G = -\frac{x}{\sigma^2}G$, $\partial_{xx} G = \big(\frac{x^2}{\sigma^4} - \frac{1}{\sigma^2}\big)G$; cộng với $\partial_{yy}G$:

            $$\nabla^2 G = \Big(\frac{r^2}{\sigma^4} - \frac{2}{\sigma^2}\Big)G \;\Rightarrow\; \sigma\nabla^2 G = \Big(\frac{r^2}{\sigma^3} - \frac{2}{\sigma}\Big)G$$

            Hai vế bằng nhau. $\blacksquare$

            **Bước 2 – sai phân theo $\sigma$.** Xấp xỉ đạo hàm bằng hiệu hai mức tỉ lệ gần nhau:

            $$\frac{\partial G}{\partial\sigma} \approx \frac{G(x, y, k\sigma) - G(x, y, \sigma)}{k\sigma - \sigma}$$

            Kết hợp với Bước 1:

            $$G(k\sigma) - G(\sigma) \approx (k - 1)\,\sigma^2\,\nabla^2 G$$

            **Bước 3 – ý nghĩa.** Vế phải là **LoG đã chuẩn hóa tỉ lệ** $\sigma^2\nabla^2 G$ nhân với hằng số $(k - 1)$, mà hằng số này **giống nhau ở mọi tỉ lệ** (vì $k$ cố định). Hệ số $\sigma^2$ cần thiết vì đạo hàm bậc hai của ảnh đã làm mờ bằng $\sigma$ giảm cỡ $1/\sigma^2$; không nhân lại thì đốm lớn luôn có phản hồi yếu hơn đốm nhỏ và không so sánh được giữa các tỉ lệ. DoG cho sẵn sự chuẩn hóa này **miễn phí**, và chỉ cần trừ hai ảnh Gauss vốn đã có trong kim tự tháp.

            **Kiểm chứng số:** với $\sigma = 3$, $k = 1.1$ trên ảnh nhiễu đã làm mờ, DoG và LoG (`GaussianBlur` + `Laplacian`) có hệ số tương quan **0.9986**; tỉ lệ biên độ đo được 0.86 so với dự đoán $(k-1)\sigma^2 = 0.9$ (chênh do Laplace rời rạc và xấp xỉ bậc nhất). SIFT dùng $k = \sqrt2$ lớn hơn, xấp xỉ thô hơn nhưng vị trí cực trị vẫn giữ được.
            :::

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

        :::proof vì sao kiểm tra 4 pixel 1, 5, 9, 13 là đủ để loại (với n = 12)
        **Khẳng định:** nếu có một cung $n = 12$ pixel liên tiếp (trên vòng 16) đều sáng hơn $I_p + t$, thì **ít nhất 3** trong 4 pixel 1, 5, 9, 13 nằm trong cung đó.

        **Chứng minh.** Phần bù của cung là $16 - 12 = 4$ pixel liên tiếp. Bốn pixel 1, 5, 9, 13 cách nhau đúng 4 bước, nên một dãy 4 pixel liên tiếp bất kỳ chứa **đúng một** trong số chúng. Vậy phần bù chứa đúng 1 điểm kiểm tra, cung chứa đúng 3. $\blacksquare$ (Trường hợp tối hơn $I_p - t$ hoàn toàn tương tự.)

        **Hệ quả:** nếu ít hơn 3 trong 4 điểm kiểm tra cùng sáng hơn (hoặc cùng tối hơn) thì loại $p$ ngay, không cần xét 12 pixel còn lại. Phần lớn pixel trong ảnh (vùng phẳng) bị loại chỉ sau 2–4 phép so sánh.

        **Với $n = 9$ (mặc định của OpenCV)**, phần bù dài 7 pixel có thể chứa 1 hoặc 2 điểm kiểm tra, nên cung chỉ chắc chắn chứa ít nhất 2. Kiểm tra nhanh yếu hơn – đó là lý do bản gốc dùng cây quyết định học từ dữ liệu để chọn thứ tự kiểm tra.
        :::

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

        :::proof khoảng cách Hamming = popcount(a XOR b)
        Với hai chuỗi bit $a, b$: bit thứ $i$ của $a \oplus b$ bằng 1 khi và chỉ khi $a_i \ne b_i$ (bảng chân trị XOR: $0\oplus0 = 1\oplus1 = 0$, $0\oplus1 = 1\oplus0 = 1$). Nên số bit 1 của $a \oplus b$ đúng bằng số vị trí khác nhau:

        $$d_H(a, b) = \text{popcount}(a \oplus b) \qquad \blacksquare$$

        Descriptor 256 bit = 4 số 64 bit: chỉ cần 4 lệnh XOR và 4 lệnh `popcnt` của CPU, so với 128 phép trừ, 128 phép nhân, 127 phép cộng số thực của khoảng cách Euclid giữa hai descriptor SIFT. Đó là lý do khi dùng ORB/BRIEF phải chọn `cv.NORM_HAMMING` trong `BFMatcher`; dùng `NORM_L2` trên mảng byte là sai về nghĩa (nó coi mỗi byte là một số chứ không phải 8 bit).
        :::

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
