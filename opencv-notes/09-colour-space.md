---
title: 9. Colour Space
lesson: lesson18_color_spaces
after:
---
- OpenCV cung cấp hơn 150 phương thức chuyển đổi không gian màu khác nhau.
    - BGR to Gray
    - BGR to RGB - cho hiển thị ảnh bằng matplotlib
    - BGR to HSV
- Hàm dùng để chuyển đổi:
    - `dst = cv2.cvtColor(src, code)`

    ```python
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    ```

- Không gian màu HSV
    - Dùng kiểu dữ liệu `uint8`

    ![](img/opencv-notes/09-colour-space-1.jpg)

    | Kênh | Ý nghĩa | Dải giá trị trong OpenCV |
    |---|---|---|
    | H | Hue - tông màu | 0-179: H = độ / 2 (0-360°) để vừa kiểu uint8 |
    | S | Saturation - độ bão hòa màu | 0-255 |
    | V | Value - độ sáng | 0-255 |

- Tách lọc vật thể theo màu
    - Dùng hàm `cv2.inRange(img_hsv, lower, upper)` để tạo mask nhị phân
        - Nếu giá trị pixel trong khoảng từ `lower` đến `upper` thì ghim thành 255 còn lại ghim về 0
        - Xác định `lower` và `upper` dùng `trackbar` để tuning
    - Dùng phép `bitwise_and(img, img, mask = mask)`
- Thông thường:
    - `Lower`:` H-10, 100, 100`
    - `Upper`:` H+10, 255, 255`
- Nếu muốn mask nhiều màu thì tạo mask tổng hợp bằng `bitwise_or` của các mask lẻ
    - Màu đỏ nằm ở cả hai đầu dải H (gần 0 và gần 179) nên thường phải tạo 2 mask rồi `bitwise_or`
