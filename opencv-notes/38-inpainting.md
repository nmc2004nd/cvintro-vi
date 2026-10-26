---
title: 38. Image Inpainting
lesson: lesson14_nonlinear_filters
after:
draft: true
---
- Inpainting: ==khôi phục vùng ảnh bị hỏng hoặc bị xóa== bằng thông tin từ các pixel xung quanh (vết xước, vết bẩn, chữ chèn lên ảnh)
- Cần hai đầu vào:
    - Ảnh hỏng
    - ==Mask 8-bit 1 kênh, pixel khác 0 là vùng cần vá==, cùng kích thước ảnh
- Hàm: `dst = cv.inpaint(src, inpaintMask, inpaintRadius, flags)`
    - `inpaintRadius`: bán kính vùng lân cận dùng để vá mỗi điểm (thường 3)
    - `flags`: một trong hai thuật toán:

| Flag | Thuật toán | Cơ chế |
|---|---|---|
| `cv.INPAINT_TELEA` | Fast Marching Method (Alexandru Telea, 2004) | Vá dần từ biên vùng hỏng vào trong; mỗi pixel = trung bình có trọng số của các pixel đã biết lân cận, ưu tiên pixel gần, gần hướng pháp tuyến biên và nằm trên đường viền |
| `cv.INPAINT_NS` | Navier-Stokes (Bertalmio et al., 2001) | Dựa trên phương trình động lực học chất lỏng: kéo dài các đường đẳng sáng (isophote) từ vùng đã biết vào vùng hỏng, giữ liên tục gradient |

```python
img = cv.imread("messi_2.jpg")
mask = cv.imread("mask2.png", cv.IMREAD_GRAYSCALE)   # trắng = vùng cần vá

dst_telea = cv.inpaint(img, mask, 3, cv.INPAINT_TELEA)
dst_ns = cv.inpaint(img, mask, 3, cv.INPAINT_NS)
```

![](img/opencv-notes/38-inpainting-1.png)

- Cách tạo mask:
    - Vẽ tay bằng chuột (dùng `setMouseCallback`) lên ảnh đen cùng kích thước
    - Threshold nếu vùng hỏng có màu đặc trưng (ví dụ vết trắng)
    - ==Nên dilate mask một chút== để phủ cả viền của vùng hỏng, nếu không viền sẽ bị kéo vào ảnh vá
- ==Hạn chế:== chỉ tốt với ==vùng hỏng mảnh, nhỏ== (nét chữ, vết xước). Vùng lớn có kết cấu phức tạp sẽ bị mờ, bệt → cần phương pháp dựa trên patch hoặc deep learning
- ==Ứng dụng:==
    - ==Phục chế ảnh cũ bị xước==
    - ==Xóa chữ, ngày tháng in trên ảnh==
    - ==Xóa vật thể nhỏ khỏi ảnh==
