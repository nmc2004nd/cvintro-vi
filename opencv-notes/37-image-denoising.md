---
title: 37. Image Denoising - Non-local Means
lesson: lesson14_nonlinear_filters
after:
draft: true
---
- Các bộ lọc đã học (Gaussian, median, bilateral) chỉ lấy trung bình ==trong vùng lân cận nhỏ== → làm mờ chi tiết
- Ý tưởng Non-local Means:
    - Nhiễu có trung bình bằng 0 → lấy trung bình nhiều lần quan sát của cùng một pixel sẽ triệt tiêu nhiễu
    - Một ảnh tĩnh không có nhiều lần quan sát, nhưng ảnh có ==nhiều mảng (patch) giống nhau ở nhiều nơi==
    - Với mỗi pixel: tìm các patch giống patch quanh nó trong một vùng tìm kiếm lớn, ==lấy trung bình có trọng số theo độ giống nhau==
    - Giữ chi tiết tốt hơn Gaussian nhưng ==chậm hơn nhiều==

| Hàm | Đầu vào |
|---|---|
| `cv.fastNlMeansDenoising()` | Một ảnh xám |
| `cv.fastNlMeansDenoisingColored()` | Một ảnh màu (chuyển sang CIELAB, khử nhiễu riêng độ sáng L và màu AB) |
| `cv.fastNlMeansDenoisingMulti()` | Nhiều frame xám liên tiếp (video) |
| `cv.fastNlMeansDenoisingColoredMulti()` | Nhiều frame màu |

- Tham số:
    - `h`: cường độ lọc; ==h lớn → khử nhiễu mạnh nhưng mất chi tiết==, h nhỏ → giữ chi tiết nhưng còn nhiễu (tài liệu dùng 10)
    - `hColor` (bản màu): như `h` cho kênh màu, thường bằng `h`
    - `templateWindowSize`: kích thước patch, số lẻ, khuyến nghị 7
    - `searchWindowSize`: kích thước vùng tìm patch, số lẻ, khuyến nghị 21

```python
img = cv.imread("die.png")
dst = cv.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
#                                     src  dst   h  hColor template search
```

- Với video (bản Multi):
    - `imgToDenoiseIndex`: chỉ số frame cần khử nhiễu trong danh sách
    - `temporalWindowSize`: số frame lân cận dùng để khử nhiễu, ==phải là số lẻ==
    - Ví dụ: 5 frame, `imgToDenoiseIndex = 2`, `temporalWindowSize = 3` → dùng frame 1, 2, 3 để khử nhiễu frame 2

```python
cap = cv.VideoCapture("vtest.avi")
img = [cap.read()[1] for i in range(5)]
gray = [np.float64(cv.cvtColor(i, cv.COLOR_BGR2GRAY)) for i in img]

# thêm nhiễu Gauss độ lệch chuẩn 10 để thử
noise = np.random.randn(*gray[1].shape) * 10
noisy = [np.uint8(np.clip(i + noise, 0, 255)) for i in gray]

dst = cv.fastNlMeansDenoisingMulti(noisy, 2, 5, None, 4, 7, 35)
#                                        idx tws dst h tmpl search
```

![](img/opencv-notes/37-image-denoising-1.png)

- ==So sánh nhanh:==
    - ==Gaussian: nhanh, mờ cả biên==
    - ==Median: tốt với nhiễu muối tiêu==
    - ==Bilateral: giữ biên, nhưng vùng phẳng có thể bị bệt==
    - ==Non-local Means: giữ chi tiết tốt nhất trong nhóm, chậm nhất==
