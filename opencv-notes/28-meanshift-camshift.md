---
title: 28. Meanshift và Camshift
lesson: lesson21_optical_flow
after:
draft: true
---
| Hàm | Cửa sổ theo dõi | Trả về |
|---|---|---|
| `cv.meanShift()` | Kích thước cố định, không xoay | `(số vòng lặp, (x, y, w, h))` |
| `cv.CamShift()` | ==Tự đổi kích thước và xoay theo vật thể== | `(RotatedRect, (x, y, w, h))` |

- ==**Meanshift**==
    - Ý tưởng: cho một tập điểm (ví dụ ảnh backprojection) và một cửa sổ
        - Tính trọng tâm các điểm trong cửa sổ
        - Dịch tâm cửa sổ về trọng tâm đó
        - Lặp lại đến khi cửa sổ không dịch nữa → cửa sổ nằm ở ==vùng có mật độ điểm cao nhất==
    - Áp dụng để theo dõi vật thể trong video:
        - Frame đầu: chọn cửa sổ chứa vật thể, tính histogram Hue của vùng đó
        - Mỗi frame sau: backprojection histogram lên frame → ảnh xác suất → chạy meanShift từ cửa sổ cũ
    - Mask khi tính histogram: bỏ các pixel có S, V thấp (gần xám, gần đen) vì Hue của chúng không đáng tin
    - `term_crit`: điều kiện dừng, ví dụ tối đa 10 vòng hoặc dịch ít hơn 1 pixel

    ```python
    cap = cv.VideoCapture("video.mp4")
    ret, frame = cap.read()

    # Cửa sổ ban đầu chứa vật thể
    x, y, w, h = 300, 200, 100, 50
    track_window = (x, y, w, h)

    # Histogram Hue của vùng vật thể
    roi = frame[y:y + h, x:x + w]
    hsv_roi = cv.cvtColor(roi, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
    roi_hist = cv.calcHist([hsv_roi], [0], mask, [180], [0, 180])
    cv.normalize(roi_hist, roi_hist, 0, 255, cv.NORM_MINMAX)

    term_crit = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        dst = cv.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

        ret, track_window = cv.meanShift(dst, track_window, term_crit)
        x, y, w, h = track_window
        cv.rectangle(frame, (x, y), (x + w, y + h), 255, 2)
    ```

    - Hạn chế: ==kích thước cửa sổ cố định== → vật lại gần camera (to ra) hay đi xa (nhỏ lại) thì cửa sổ không theo kịp
- ==**Camshift (Continuously Adaptive Meanshift)**== - Gary Bradski, 1998
    - Chạy meanShift đến khi hội tụ, rồi ==cập nhật kích thước cửa sổ== theo $s = 2\sqrt{M_{00}/256}$ và tính hướng của elip khớp nhất
    - Chạy lại meanShift với cửa sổ mới, lặp đến khi đạt độ chính xác yêu cầu
    - Code giống meanShift, chỉ đổi dòng theo dõi và cách vẽ:

    ```python
    ret, track_window = cv.CamShift(dst, track_window, term_crit)
    pts = cv.boxPoints(ret)                       # ret là RotatedRect ((cx, cy), (w, h), angle)
    pts = np.intp(pts)
    frame = cv.polylines(frame, [pts], True, 255, 2)
    ```

![](img/opencv-notes/28-meanshift-camshift-1.png)

- ==Hạn chế chung:==
    - ==Chỉ dựa vào màu==: nền có màu giống vật thể → dễ trôi sang nền
    - Vật thể bị che khuất hoàn toàn hoặc di chuyển quá nhanh (ra khỏi cửa sổ cũ) → mất dấu
- ==Ứng dụng:==
    - ==Theo dõi khuôn mặt, bàn tay, quả bóng có màu nổi bật==
    - ==Theo dõi nhẹ, chạy được trên thiết bị yếu==
