---
title: 3. Drawing
lesson: 
after:
---
- Tham số chung
    - `img`
    - `color` - BGR
    - `thickness `- độ đày - (-1) tô full không gian trong
    - `lineType`:` cv2.Line_AA` kiểu răng cưa
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
        - axes (d1, d2) đọ dài hai trục
        - angle: góc xoay
        - startAngle: góc bắt đầu cung
        - endAngle: góc kết thúc cung
        - Muốn vẽ 1 hình ellipse full thì 0-360
- Polylines
    - `cv.polylines(img, [pts], True, color)`
    - `pts = np.array([[10, 5], [20, 30], [70, 20], [50, 10]], np.int32)`
    - `pts = pts.reshape((-1, 1, 2))` size theo yêu cầu của OpenCV và vị trí pixel là các số nguyên
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
