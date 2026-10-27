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

    :::proof quan hệ giữa các phương pháp và vì sao CCOEFF_NORMED bền nhất
    Ký hiệu tổng chạy trên cửa sổ đang xét; $I$ là phần ảnh dưới template.

    **1. SQDIFF = năng lượng template + năng lượng ảnh − 2·CCORR.**

    $$\sum (T - I)^2 = \sum T^2 - 2\sum T\,I + \sum I^2$$

    $\sum T^2$ không đổi theo vị trí. Nếu $\sum I^2$ cũng gần như không đổi thì min SQDIFF tương đương max CCORR. Nhưng $\sum I^2$ **lớn ở vùng sáng**, nên CCORR thuần có thể đạt cực đại ở một vùng trắng bất kỳ chứ không phải chỗ giống template – đúng lý do ghi chú nói CCORR "dễ bị vùng sáng đánh lừa".

    **2. Các bản chuẩn hóa nằm trong khoảng nào – bất đẳng thức Cauchy–Schwarz.** Coi $T$, $I$ là hai vector:

    $$\Big|\sum T\,I\Big| \le \sqrt{\sum T^2}\sqrt{\sum I^2}$$

    dấu bằng khi và chỉ khi $I = cT$. Do đó

    - `TM_CCORR_NORMED` $= \dfrac{\sum TI}{\sqrt{\sum T^2 \sum I^2}} \in [0, 1]$ với ảnh không âm; bằng 1 khi cửa sổ là template nhân với một hằng số dương – đã **bất biến với độ tương phản** (nhân hệ số) nhưng chưa bất biến với cộng thêm độ sáng.
    - `TM_SQDIFF_NORMED` $= \dfrac{\sum (T - I)^2}{\sqrt{\sum T^2 \sum I^2}}$ bằng 0 khi khớp hoàn toàn. Về lý thuyết tỉ số này có thể **lớn hơn 1** (ví dụ template sáng đặt lên vùng tối), nhưng OpenCV **kẹp kết quả về [0, 1]**. Mình đã kiểm tra: template toàn 250 trượt trên ảnh có vùng toàn 5 cho giá trị lớn nhất đúng bằng 1.0.

    **3. CCOEFF_NORMED là hệ số tương quan Pearson.** Đặt $T' = T - \overline{T}$, $I' = I - \overline{I}$ (trừ trung bình trong cửa sổ):

    $$\mathrm{CCOEFF\_NORMED} = \frac{\sum T'I'}{\sqrt{\sum T'^2 \sum I'^2}} \in [-1, 1]$$

    (Cauchy–Schwarz cho $T'$, $I'$). **Khẳng định:** kết quả không đổi khi đổi $I \to aI + b$ với $a > 0$.

    *Chứng minh.* $\overline{aI + b} = a\overline{I} + b$, nên $(aI + b) - \overline{(aI + b)} = a(I - \overline{I}) = aI'$: hằng số $b$ biến mất. Thay vào:

    $$\frac{\sum T'(aI')}{\sqrt{\sum T'^2 \sum a^2 I'^2}} = \frac{a\sum T'I'}{a\sqrt{\sum T'^2 \sum I'^2}} \qquad \blacksquare$$

    Vậy CCOEFF_NORMED bất biến với cả **thay đổi độ sáng** ($b$) lẫn **độ tương phản** ($a$), và giá trị có ý nghĩa tuyệt đối: 1 = khớp hoàn hảo, 0 = không liên quan, −1 = ngược màu. Đó là lý do ngưỡng (ví dụ 0.8) dễ chọn. Mình đã thử: cắt template từ ảnh rồi tìm trên ảnh $2I + 0.5$, kết quả cực đại 0.9999996 đúng ở vị trí cắt.

    **Lưu ý:** cả ba phương pháp đều **không** bất biến với xoay hay co giãn. Template phải gần đúng kích thước và hướng của vật trong ảnh; nếu không, dùng đặc trưng (SIFT/ORB + homography).
    :::

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
