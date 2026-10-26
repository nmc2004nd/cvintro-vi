---
title: 6. Core Operations
lesson: lesson01_images_as_arrays
after:
---
==Các hàm OpenCV nhận tọa độ điểm theo (x, y) - (col, row), còn truy cập mảng NumPy là img[y, x] - [row, col]==

==OpenCV đọc ảnh theo BGR, còn matplotlib (plt) hiển thị theo RGB==

- Truy cập và thay đổi giá trị pixel
    - Đọc: `px = img[row, col]`
    - Ghi: `img[row, col] = [255, 255, 255]`
- Truy cập vào thuộc tính ảnh
    - Kích thước ảnh:
        - `img.shape - HxWxD` - Row-Column
    - Tổng số phần tử (H × W × số kênh):
        - `img.size`
    - Kiểu dữ liệu
        - `img.dtype`
- Vùng quan tâm ROI
    - `img[y1:y2, x1:x2]`
- Tách màu và gộp kênh
    - Tách kênh: `b, g, r = cv.split(img)`
    - Gộp kênh: `img = cv.merge((b, g, r))`
    - `cv.split()` khá tốn thời gian, nên dùng indexing của NumPy nếu được, ví dụ `b = img[:, :, 0]`
- Tạo viền cho ảnh: Border

    ![](img/opencv-notes/06-core-operations-1.png)

    - `dst = cv.copyMakeBorder(src, top, bottom, left, right, borderType, value)`
    - borderType:

        | Type | Cách lặp | Ví dụ |
        |---|---|---|
        | `cv.BORDER_CONSTANT` | Tạo viền màu cố định | `iiiiii \| abcdefgh \| iiiiiii` |
        | `cv.BORDER_REFLECT` | Phản chiếu ảnh ở biên | `fedcba \| abcdefgh \| hgfedcb` |
        | `cv.BORDER_REFLECT_101` (mặc định của các hàm lọc) | Phản chiếu nhưng không lặp lại pixel biên | `gfedcb \| abcdefgh \| gfedcba` |
        | `cv.BORDER_REPLICATE` | Lặp pixel ở biên | `aaaaaa \| abcdefgh \| hhhhhhh` |
        | `cv.BORDER_WRAP` | Lấy phần đối diện bù vào | `cdefgh \| abcdefgh \| abcdefg` |
