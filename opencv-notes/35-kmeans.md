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
