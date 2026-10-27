---
title: 35. K-Means Clustering
lesson: lesson19_clustering
after: k-means on real color data
draft: true
---
- K-Means chia dữ liệu thành K cụm:
    - **B1**: chọn ngẫu nhiên K tâm cụm
    - **B2**: gán mỗi điểm vào tâm gần nhất
    - **B3**: tính lại tâm = trung bình các điểm trong cụm
    - Lặp B2-B3 đến khi tâm không đổi (hoặc đạt điều kiện dừng)
    - Mục tiêu: cực tiểu tổng bình phương khoảng cách từ điểm tới tâm cụm của nó (compactness)

        :::proof vì sao k-means luôn dừng và vì sao tâm = trung bình
        Hàm mục tiêu (chính là `compactness`), với $c(i)$ là cụm của điểm $\mathbf{x}_i$ và $\boldsymbol{\mu}_j$ là các tâm:

        $$J = \sum_{i=1}^{N}\big\|\mathbf{x}_i - \boldsymbol{\mu}_{c(i)}\big\|^2$$

        **Bổ đề – trung bình là điểm gần nhất (theo bình phương) với một nhóm điểm.** Với nhóm $S$ có $n$ điểm, trung bình $\bar{\mathbf{x}}$, và một điểm $\mathbf{m}$ bất kỳ:

        $$\sum_{i \in S}\|\mathbf{x}_i - \mathbf{m}\|^2 = \sum_{i \in S}\|(\mathbf{x}_i - \bar{\mathbf{x}}) + (\bar{\mathbf{x}} - \mathbf{m})\|^2 = \sum_{i \in S}\|\mathbf{x}_i - \bar{\mathbf{x}}\|^2 + n\|\bar{\mathbf{x}} - \mathbf{m}\|^2$$

        (số hạng chéo $2(\bar{\mathbf{x}} - \mathbf{m})^T\sum_{i\in S}(\mathbf{x}_i - \bar{\mathbf{x}})$ bằng 0 vì tổng độ lệch so với trung bình bằng 0). Vế phải nhỏ nhất khi và chỉ khi $\mathbf{m} = \bar{\mathbf{x}}$. $\blacksquare$

        **Định lý – $J$ không bao giờ tăng, và thuật toán dừng sau hữu hạn bước.**

        - **B2 (gán điểm)**: tâm cố định, mỗi điểm chuyển sang tâm gần nhất, nên số hạng của từng điểm không tăng → $J$ không tăng.
        - **B3 (cập nhật tâm)**: nhãn cố định, $J$ tách thành tổng theo từng cụm, và theo bổ đề mỗi cụm đạt nhỏ nhất khi tâm là trung bình → $J$ không tăng.

        $J \ge 0$ và không tăng qua mỗi vòng. Hơn nữa chỉ có hữu hạn cách chia $N$ điểm thành $K$ nhóm (nhiều nhất $K^N$), và mỗi cách chia xác định duy nhất các tâm. Nếu $J$ giảm ngặt thì không thể quay lại một cách chia cũ, nên sau hữu hạn bước các nhãn ngừng thay đổi. $\blacksquare$

        **Nhưng chỉ là cực tiểu địa phương.** Phép chứng minh chỉ nói $J$ giảm, không nói đạt cực tiểu toàn cục (bài toán tổng quát là NP-khó). Kết quả phụ thuộc khởi tạo – đó là lý do có tham số `attempts` (chạy nhiều lần, giữ $J$ nhỏ nhất) và `KMEANS_PP_CENTERS` (k-means++ chọn tâm ban đầu xa nhau, có đảm bảo kỳ vọng $J$ chỉ kém tối ưu cỡ $O(\log K)$ lần).

        **Vì sao phải `float32` và chuẩn hóa đặc trưng.** $J$ dùng khoảng cách Euclid, nên đặc trưng có thang đo lớn (ví dụ chiều cao tính bằng cm cạnh cân nặng tính bằng tấn) sẽ lấn át hoàn toàn đặc trưng còn lại.
        :::

- Hàm: `compactness, labels, centers = cv.kmeans(data, K, bestLabels, criteria, attempts, flags)`

| Tham số | Ý nghĩa |
|---|---|
| `data` | ==`np.float32`, mỗi hàng là một điểm== (shape (N, số đặc trưng)) |
| `K` | Số cụm |
| `bestLabels` | Nhãn khởi tạo, thường `None` |
| `criteria` | `(type, max_iter, epsilon)`: `cv.TERM_CRITERIA_EPS` (dừng khi tâm dịch < epsilon), `cv.TERM_CRITERIA_MAX_ITER` (dừng sau max_iter vòng), hoặc cộng cả hai |
| `attempts` | Số lần chạy với khởi tạo khác nhau, trả về lần có compactness nhỏ nhất |
| `flags` | `cv.KMEANS_RANDOM_CENTERS` hoặc `cv.KMEANS_PP_CENTERS` (k-means++, khởi tạo tốt hơn) |

| Kết quả | Ý nghĩa |
|---|---|
| `compactness` | Tổng bình phương khoảng cách tới tâm cụm |
| `labels` | Nhãn cụm (0, 1, ...) của từng điểm, shape (N, 1) |
| `centers` | Tọa độ các tâm cụm, shape (K, số đặc trưng) |

- **Dữ liệu 1 đặc trưng** (ví dụ chiều cao): `data` shape (N, 1)
- **Nhiều đặc trưng** (ví dụ chiều cao + cân nặng): `data` shape (N, 2), chia điểm theo nhãn: `A = Z[labels.ravel() == 0]`

    ```python
    Z = np.float32(np.vstack((X, Y)))                    # (N, 2)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv.kmeans(Z, 2, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)

    A = Z[label.ravel() == 0]
    B = Z[label.ravel() == 1]
    ```

- ==**Lượng tử hóa màu (Color Quantization)**==: giảm số màu trong ảnh xuống K màu
    - Mỗi pixel là một điểm 3 đặc trưng (B, G, R) → `reshape((-1, 3))`
    - Sau khi phân cụm, thay mỗi pixel bằng màu của tâm cụm

    ```python
    Z = np.float32(img.reshape((-1, 3)))
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 8
    ret, label, center = cv.kmeans(Z, K, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)

    center = np.uint8(center)
    res = center[label.flatten()]                        # tra màu tâm cho từng pixel
    res2 = res.reshape(img.shape)
    ```

![](img/opencv-notes/35-kmeans-1.png)

- ==Lưu ý:==
    - ==Phải chọn K trước==; K-Means giả định cụm có dạng tròn, kích thước gần nhau → kém với cụm không lồi (xem DBSCAN trong bài)
    - Kết quả phụ thuộc khởi tạo → dùng `attempts > 1` hoặc `KMEANS_PP_CENTERS`
- ==Ứng dụng:==
    - ==Giảm số màu để nén ảnh, tạo hiệu ứng poster==
    - ==Phân đoạn ảnh theo màu==
    - ==Tạo "từ điển hình ảnh" (bag of visual words) từ các descriptor==
