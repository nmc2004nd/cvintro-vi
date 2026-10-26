---
title: 5. Trackbar
lesson: 
after:
---
- Thanh trượt thay đổi giá trị của một tham số
- Ứng dụng:
    1. Điều chỉnh ngưỡng trong thresholding.
    2. Thay đổi tham số lọc ảnh.
    3. Tùy chỉnh màu sắc.
    4. Điều chỉnh kích thước cọ vẽ.
    5. Giả lập công tắc bật/tắt.
- Hàm callback được gọi khi value của trackbar (thanh trượt) thay đổi

    ```python
    def nothing(x):
        pass
    ```

- Tạo một cửa sổ để chứa trackbar
    - `cv2.namedWindow("Color Mixer")`
- Tạo các trackbar: `cv2.createTrackbar(name, window, value, count, onChange)` - giá trị ban đầu `value`, giá trị lớn nhất` count`

    ```python
    cv2.createTrackbar("R", "Color Mixer", 0, 255, nothing)
    cv2.createTrackbar("G", "Color Mixer", 0, 255, nothing)
    cv2.createTrackbar("B", "Color Mixer", 0, 255, nothing)
    ```

- Lấy giá trị từ trackbar - dùng hàm `cv2.getTrackbarPos(name, window)`

    ```python
    r = cv2.getTrackbarPos("R", "Color Mixer")
    g = cv2.getTrackbarPos("G", "Color Mixer")
    b = cv2.getTrackbarPos("B", "Color Mixer")
    ```
