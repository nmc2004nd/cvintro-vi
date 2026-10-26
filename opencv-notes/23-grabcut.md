---
title: 23. GrabCut
lesson: lesson42_semantic_segmentation
after:
draft: true
---
- Thuật toán ==tách tiền cảnh (foreground) với rất ít tương tác==: người dùng chỉ cần vẽ một khung chữ nhật quanh vật thể, có thể sửa thêm bằng vài nét vẽ
- Do Carsten Rother, Vladimir Kolmogorov, Andrew Blake (Microsoft Research) đề xuất năm 2004
- Cơ chế:
    - Mọi thứ ngoài khung chữ nhật → ==nền chắc chắn==; trong khung → chưa biết
    - Dùng **Gaussian Mixture Model (GMM)** mô hình hóa phân bố màu của tiền cảnh và nền
    - Xây đồ thị: mỗi pixel là một nút, thêm hai nút đặc biệt **Source** (tiền cảnh) và **Sink** (nền)
        - Cạnh pixel - Source/Sink: trọng số = xác suất pixel thuộc tiền cảnh/nền (theo GMM)
        - Cạnh pixel - pixel: trọng số lớn nếu hai pixel giống màu → khó bị cắt
    - Dùng thuật toán **min-cut** cắt đồ thị với tổng trọng số nhỏ nhất → pixel nối với Source là tiền cảnh
    - Lặp lại (cập nhật GMM, cắt lại) đến khi hội tụ
- Hàm: `mask, bgdModel, fgdModel = cv.grabCut(img, mask, rect, bgdModel, fgdModel, iterCount, mode)`

| Tham số | Ý nghĩa |
|---|---|
| `img` | Ảnh màu 8-bit 3 kênh |
| `mask` | Ảnh 1 kênh `uint8`, vừa là đầu vào vừa là đầu ra, giá trị theo bảng dưới |
| `rect` | Khung `(x, y, w, h)` chứa vật thể, chỉ dùng với `GC_INIT_WITH_RECT` |
| `bgdModel`, `fgdModel` | Mảng `np.zeros((1, 65), np.float64)` cho thuật toán dùng nội bộ |
| `iterCount` | Số vòng lặp |
| `mode` | `cv.GC_INIT_WITH_RECT` (dùng khung) hoặc `cv.GC_INIT_WITH_MASK` (dùng mask đã vẽ) |

| Giá trị mask | Hằng số | Ý nghĩa |
|---|---|---|
| 0 | `cv.GC_BGD` | Nền chắc chắn |
| 1 | `cv.GC_FGD` | Tiền cảnh chắc chắn |
| 2 | `cv.GC_PR_BGD` | Có lẽ là nền |
| 3 | `cv.GC_PR_FGD` | Có lẽ là tiền cảnh |

```python
mask = np.zeros(img.shape[:2], np.uint8)
bgdModel = np.zeros((1, 65), np.float64)
fgdModel = np.zeros((1, 65), np.float64)

rect = (40, 10, 250, 230)
cv.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv.GC_INIT_WITH_RECT)

# 0 và 2 là nền, 1 và 3 là tiền cảnh
mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
img_fg = img * mask2[:, :, np.newaxis]
```

![](img/opencv-notes/23-grabcut-1.png)

- **Sửa kết quả bằng nét vẽ**: chỗ nào bị sai thì tô trắng (chắc chắn tiền cảnh) hoặc đen (chắc chắn nền) rồi chạy lại với `GC_INIT_WITH_MASK`

    ```python
    # newmask: ảnh người dùng vẽ, trắng = tiền cảnh, đen = nền
    mask[newmask == 0] = 0
    mask[newmask == 255] = 1
    mask, bgdModel, fgdModel = cv.grabCut(img, mask, None, bgdModel, fgdModel, 5, cv.GC_INIT_WITH_MASK)
    ```

- ==Hạn chế:== vật thể và nền có màu giống nhau (ví dụ chân con chó và cỏ trong hình trên) thì dễ bị cắt nhầm → cần thêm nét vẽ sửa
- ==Ứng dụng:==
    - ==Xóa phông, tách người/vật khỏi ảnh==
    - ==Tạo nhanh mask nhãn cho dữ liệu huấn luyện phân đoạn==
