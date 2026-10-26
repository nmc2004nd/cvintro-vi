---
title: 22. Watershed
lesson: lesson04_floodfill_connected_components
after:
draft: true
---
- Bài toán: ==tách các vật thể chạm hoặc chồng lên nhau== (đồng xu dính nhau, tế bào). Threshold + contour chỉ ra một khối liền
- Ý tưởng: coi ảnh xám là bản đồ địa hình, pixel sáng là đỉnh, pixel tối là thung lũng
    - Đổ nước có màu khác nhau vào từng thung lũng (cực tiểu cục bộ)
    - Nước dâng lên, chỗ nước của hai thung lũng sắp gặp nhau thì xây "đập" → đập chính là ==đường biên phân tách==
- Watershed thuần túy bị phân mảnh quá mức (over-segmentation) do nhiễu → OpenCV dùng ==watershed theo marker==: ta tự chỉ định vùng nào chắc chắn là vật thể, vùng nào chắc chắn là nền, vùng nào chưa biết
- Quy ước mảng `markers` (kiểu `int32`):

| Giá trị | Ý nghĩa |
|---|---|
| `0` | Vùng chưa biết → watershed sẽ quyết định |
| `1` | Nền chắc chắn |
| `2, 3, ...` | Từng vật thể chắc chắn, mỗi vật một nhãn |
| `-1` | (Sau watershed) đường biên giữa các vùng |

- Các bước:
    - **B1**: Threshold Otsu để tách sơ bộ vật thể và nền
    - **B2**: Opening để xóa nhiễu trắng nhỏ
    - **B3**: Nền chắc chắn = dilate vật thể → vùng ngoài vùng giãn chắc chắn là nền
    - **B4**: Vật thể chắc chắn = ==distanceTransform== rồi lấy ngưỡng
        - `distanceTransform` gán mỗi pixel trắng giá trị = khoảng cách tới pixel đen gần nhất → ==tâm vật thể sáng nhất, chỗ hai vật chạm nhau tối hơn==
        - Lấy ngưỡng cao chỉ giữ phần lõi của từng vật → các lõi tách rời nhau
    - **B5**: Vùng chưa biết = nền chắc chắn - vật thể chắc chắn
    - **B6**: Gán nhãn lõi bằng `connectedComponents`, cộng 1 để nền thành 1, gán vùng chưa biết = 0
    - **B7**: Chạy `cv.watershed(img, markers)`, ==img phải là ảnh màu 8-bit 3 kênh==

```python
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

# B2: xóa nhiễu
kernel = np.ones((3, 3), np.uint8)
opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=2)

# B3: nền chắc chắn
sure_bg = cv.dilate(opening, kernel, iterations=3)

# B4: vật thể chắc chắn
dist_transform = cv.distanceTransform(opening, cv.DIST_L2, 5)
ret, sure_fg = cv.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

# B5: vùng chưa biết
sure_fg = np.uint8(sure_fg)
unknown = cv.subtract(sure_bg, sure_fg)

# B6: tạo marker
ret, markers = cv.connectedComponents(sure_fg)
markers = markers + 1                 # nền thành 1 thay vì 0
markers[unknown == 255] = 0           # vùng chưa biết = 0

# B7: watershed
markers = cv.watershed(img, markers)
img[markers == -1] = [255, 0, 0]      # tô đường biên
```

- Chú ý: tài liệu dùng `THRESH_BINARY_INV` vì đồng xu tối trên nền sáng; nếu vật thể sáng trên nền tối thì dùng `THRESH_BINARY`
- Ngưỡng của distance transform (0.7 x max) quyết định có tách được các vật hay không:
    - Quá cao → vật nhỏ không có lõi, bị coi là vùng chưa biết rồi nhập vào nền
    - Quá thấp → lõi của các vật dính nhau vẫn liền → không tách được

![](img/opencv-notes/22-watershed-1.png)

- Hình trên dùng ngưỡng 0.5: đủ thấp để vật nhỏ ở góc vẫn có lõi, đủ cao để 3 vật dính nhau có lõi tách rời
- ==Ứng dụng:==
    - ==Đếm và tách tế bào, hạt, đồng xu chạm nhau==
    - ==Phân đoạn tương tác: người dùng vẽ marker, thuật toán tự tìm biên== (xem sample `watershed.py` của OpenCV)
