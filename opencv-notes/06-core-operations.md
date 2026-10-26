---
title: 6. Core Operations
lesson: lesson01_images_as_arrays
after:
---
==Nguyên tắc là OpenCV truy cập theo (x, y) - (col, row) khác với Numpy là (y, x) - (row, col)==

==OpenCV đọc ảnh theo BGR khác matplot.plt đọc theo kiểu RGB==

- Truy cập và thay đổi giá trị pixel
    - `px = img[row, col]`
- Truy cập vào thuộc tính ảnh
    - Kích thước ảnh:
        - `img.shape - HxWxD` - Row-Column
    - Tổng số phần tử:
        - `img.size`
    - Kiểu dữ liệu
        - `img.dtype`
- Vùng quan tâm ROI
    - `img[y1:y2, x1:x2]`
- Tách màu và gộp kênh
    - Tách kênh: `b, g, r = cv.split(img)`
    - Gộp kênh: `img = cv.merge((b, g, r))`
    - Nên dùng hàm của openCV nếu có thể và hạn chế tách kênh theo .split và nên truy cập theo indexing
- Tạo viền cho ảnh: Border

    ![](img/opencv-notes/06-core-operations-1.png)

    - `dst = cv.copyMakeBorder(src, top, bottom, left, right, borderType, value)`
    - borderType:

        | Type | Cách lặp | Ví dụ |
        |---|---|---|
        | `cv.BORDER_CONSTANT` | Tạo viền màu cố định | `iiiiii \| abcdefgh \| iiiiiii` |
        | `cv.BORDER_REFLECT` | Phản chiếu ảnh ở biên | `fedcba \| abcdefgh \| hgfedcb` |
        | `cv.BORDER_REFLECT_101 - default` | Phản chiếu ảnh ở biên trừ biên | `gfedcb \| abcdefgh \| gfedcba` |
        | `cv.BORDER_REPLICATE` | Lặp pixel ở biên | `aaaaaa \| abcdefgh \| hhhhhhh` |
        | `cv.BORDER_WRAP` | Lấy phần đối diện bù vào | `cdefgh \| abcdefgh \| abcdefg` |
