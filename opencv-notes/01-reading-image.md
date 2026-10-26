---
title: 1. Reading image
lesson: lesson01_images_as_arrays
after:
---
- Đọc ảnh bằng `cv2.imread(path, flag)` :
    - ==path== : Đường dẫn đến ảnh cần đọc
    - ==flag :== Kiểu đọc ảnh
        - ==`cv2.IMREAD_COLOR`== - (default) - 1 - Đọc ảnh màu BGR
        - ==`cv2.IMREAD_GRAYSCALE`== - 0 - Đọc ảnh xám
        - ==`CV2.IMREAD_UNCHANGE`== - -1 - Đọc ảnh gốc giữ cả kênh alpha nếu có
- Lưu ảnh bằng `cv2.imwwrite(name, img)`
- Hiển thị ảnh bằng:` cv2.imshow(name_window, img)`
- Chờ phím `cv2.waitKey(d)` :
    - d = 0 - Chờ đến khi nào người dùng nhập phím
    - d - mili giây
    - d = x → FPS = $\frac{1000}{d}$
