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
        - ==`cv2.IMREAD_UNCHANGED`== - -1 - Đọc ảnh gốc giữ cả kênh alpha nếu có
- Lưu ảnh bằng `cv2.imwrite(name, img)`
- Hiển thị ảnh bằng: `cv2.imshow(name_window, img)`
- Chờ phím `cv2.waitKey(d)` :
    - d = 0 - Chờ đến khi nào người dùng nhập phím
    - d > 0 - chờ tối đa d mili giây
    - Khi phát video với mỗi frame chờ d ms → FPS ≈ $\frac{1000}{d}$ (thực tế thấp hơn một chút vì còn thời gian xử lý frame)
    - `waitKey` chỉ hoạt động khi có ít nhất một cửa sổ `imshow` đang mở
