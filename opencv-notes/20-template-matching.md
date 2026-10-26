---
title: 20. Template Matching
lesson: lesson10_convolution
after:
draft: true
---
- Tìm vị trí của một ảnh mẫu nhỏ (template) trong ảnh lớn
- Cơ chế: ==trượt template trên ảnh giống tích chập 2D==, tại mỗi vị trí tính một điểm so khớp giữa template và vùng ảnh bên dưới
- Hàm: `res = cv.matchTemplate(image, templ, method)`
    - Ảnh kích thước W x H, template w x h → `res` có kích thước ==(W - w + 1) x (H - h + 1)==
    - Mỗi pixel `res[y, x]` là điểm so khớp khi góc trên trái của template đặt tại (x, y)
- Tìm vị trí tốt nhất bằng `cv.minMaxLoc(res)` → `min_val, max_val, min_loc, max_loc`
- Các phương pháp so khớp ($T$: template, $I$: ảnh):

| Method | Công thức | Vị trí tốt nhất |
|---|---|---|
| `cv.TM_SQDIFF` | $\sum (T - I)^2$ | **min** |
| `cv.TM_SQDIFF_NORMED` | SQDIFF chuẩn hóa về [0, 1] | **min** |
| `cv.TM_CCORR` | $\sum T \cdot I$ | max |
| `cv.TM_CCORR_NORMED` | CCORR chuẩn hóa | max |
| `cv.TM_CCOEFF` | $\sum T' \cdot I'$ với $T', I'$ đã trừ trung bình | max |
| `cv.TM_CCOEFF_NORMED` | CCOEFF chuẩn hóa về [-1, 1] | max |

- ==Với `TM_SQDIFF` và `TM_SQDIFF_NORMED` phải lấy `min_loc`==, các phương pháp còn lại lấy `max_loc`
- `TM_CCORR` không trừ trung bình nên dễ bị vùng sáng đánh lừa → kết quả kém nhất
- ==Thường dùng `TM_CCOEFF_NORMED`==: chịu được thay đổi độ sáng, ngưỡng dễ chọn (gần 1 là giống)

```python
img = cv.imread("scene.jpg", cv.IMREAD_GRAYSCALE)
template = cv.imread("template.jpg", cv.IMREAD_GRAYSCALE)
h, w = template.shape                                     # chú ý: shape là (h, w)

res = cv.matchTemplate(img, template, cv.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

top_left = max_loc                                       # (x, y)
bottom_right = (top_left[0] + w, top_left[1] + h)
cv.rectangle(img, top_left, bottom_right, 255, 2)
```

![](img/opencv-notes/20-template-matching-1.png)

- **Tìm nhiều đối tượng cùng lúc**
    - `minMaxLoc` chỉ trả về một vị trí → dùng ngưỡng để lấy mọi vị trí có điểm cao

    ```python
    res = cv.matchTemplate(img_gray, template, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= 0.8)                            # trả về (các y, các x)
    for pt in zip(*loc[::-1]):                            # đảo lại thành (x, y)
        cv.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    ```

    - Một vật thể thường cho nhiều điểm sát nhau vượt ngưỡng → cần gộp lại (non-maximum suppression)
- ==Hạn chế:==
    - ==Không bất biến với xoay và thay đổi tỷ lệ==: template phải cùng kích thước và hướng với vật thể trong ảnh
    - Muốn tìm ở nhiều tỷ lệ → chạy trên kim tự tháp ảnh; muốn bền vững hơn → dùng đặc trưng (SIFT, ORB) + homography
- ==Ứng dụng:==
    - ==Tìm logo, biểu tượng, nút bấm trên ảnh chụp màn hình==
    - ==Kiểm tra linh kiện ở vị trí cố định trên băng chuyền==
