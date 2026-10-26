---
title: 4. Mouse
lesson: 
after:
---
- Hàm `dir(cv2)` dùng để kiểm tra thuộc tính của cv2 hoặc các hàm khác
- Hàm callback : hàm được gọi khi sự kiện chuột xảy ra

    ```python
    def callback_name(event, x, y, flags, param):
        pass
    ```

    - `event`: loại sư kiện chuột vừa xảy ra
    - `x, y`: tạo độ hiện tại của chuột
    - `flags`: trạng thái bổ sung
    - `param`: dữ liêu do người dùng truyền vào
- Tạo một của sổ và gọi callback khi event xảy ra

    ```python
    cv.namedWindow("Window Name")
    cv.setMouseCallback("Window Name", callback_name)
    ```

    - Tên của cửa số phải giống nhau
- Ứng dụng thực tế:
    1. Khoanh vùng đối tượng cần theo dõi.
    2. Chọn điểm mốc để cắt hoặc biến đổi ảnh.
    3. Đánh dấu dữ liệu để huấn luyện mô hình.
    4. Tạo công cụ gán nhãn segmentation.
    5. Xây dựng giao diện chọn vùng ROI.
