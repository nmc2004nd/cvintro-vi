---
title: 3. Drawing
lesson: 
after:
---
- Tham số chung
    - `img`
    - `color` - BGR
    - `thickness` - độ dày - (-1) tô kín bên trong hình
    - `lineType`:` cv2.LINE_AA` - nét khử răng cưa (anti-aliased), nét mịn hơn
- Line
    - `cv.line(img, pts1, pts2, color, thickness)`
        - pts1 : (x, y) - điểm đầu
        - pts2: (x, y) - điểm cuối
- Rectangle
    - `cv.rectangle(img, pts1, pts2, color, thickness)`
        - pts1 : (x, y) - top left
        - pts2: (x, y) - bottom right
- Circle
    - `cv.circle(img, pts1, radius, color, thickness)`
        - pts1 (x, y) - center (cx, cy)
- Ellipse
    - `cv.ellipse(img, center, axes, angle, startAngle, endAngle, color, thickness)`
        - center: (x, y)
        - axes: (a, b) - độ dài hai **bán trục** (nửa trục lớn, nửa trục nhỏ)
        - angle: góc xoay
        - startAngle: góc bắt đầu cung
        - endAngle: góc kết thúc cung
        - Muốn vẽ 1 hình ellipse full thì 0-360
- Polylines
    - `cv.polylines(img, [pts], isClosed, color)` - `isClosed = True` thì nối điểm cuối về điểm đầu
    - `pts = np.array([[10, 5], [20, 30], [70, 20], [50, 10]], np.int32)`
    - `pts = pts.reshape((-1, 1, 2))` shape (số điểm, 1, 2) theo yêu cầu của OpenCV, tọa độ phải là số nguyên `int32`
- Vẽ chữ
    - `font = cv.FONT_HERSHEY_SIMPLEX`

    ```python
    cv.putText(
        img,
        "OpenCV",
        (10, 500), # position of bottom left of text
        font,
        4,
        (255, 255, 255),
        2,
        cv.LINE_AA,
    )
    ```
