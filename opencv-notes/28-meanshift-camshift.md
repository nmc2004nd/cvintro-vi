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

        :::proof dịch về trọng tâm = leo dốc theo mật độ
        **1. Một bước meanShift tính gì.** Với ảnh xác suất $P(x, y)$ (backprojection) và cửa sổ $W$, trọng tâm có trọng số là

        $$\mathbf{c} = \Big(\frac{M_{10}}{M_{00}},\ \frac{M_{01}}{M_{00}}\Big), \qquad M_{pq} = \sum_{(x,y) \in W} x^p y^q P(x, y)$$

        – đúng công thức trọng tâm từ mô-men (xem ghi chú Contour), với $P$ đóng vai trò khối lượng.

        **2. Vì sao đi về phía mật độ cao nhất – mean shift là leo dốc.** Ước lượng mật độ bằng kernel: $f(\mathbf{x}) = \sum_i w_i\,k\big(\|\mathbf{x} - \mathbf{x}_i\|^2/h^2\big)$, với $w_i = P(\mathbf{x}_i)$ và $k$ là "profile" giảm dần. Đặt $g = -k'$. Lấy gradient (đạo hàm hàm hợp):

        $$\nabla f(\mathbf{x}) = \frac{2}{h^2}\sum_i w_i\,g_i\,(\mathbf{x}_i - \mathbf{x}) = \frac{2}{h^2}\Big(\sum_i w_i g_i\Big)\Big[\underbrace{\frac{\sum_i w_i g_i\,\mathbf{x}_i}{\sum_i w_i g_i} - \mathbf{x}}_{\text{vector mean shift}}\Big]$$

        với $g_i = g(\|\mathbf{x} - \mathbf{x}_i\|^2/h^2) \ge 0$. Hệ số đứng trước dấu ngoặc dương, nên **vector mean shift luôn cùng hướng với $\nabla f$**: mỗi bước đi lên dốc của mật độ. $\blacksquare$

        Với kernel Epanechnikov $k(r) = 1 - r$ (khi $r \le 1$), ta có $g = 1$ trong cửa sổ và 0 ngoài cửa sổ, nên số hạng đầu trong ngoặc chính là **trọng tâm có trọng số của các điểm trong cửa sổ** – đúng bước "dịch tâm cửa sổ về trọng tâm" ở trên.

        **3. Hội tụ.** Bước mean shift tự điều chỉnh độ dài: xa đỉnh (dốc lớn) thì bước dài, gần đỉnh (gradient → 0) thì bước ngắn dần, và tại đỉnh trọng tâm trùng tâm cửa sổ nên dừng. Comaniciu & Meer (2002) chứng minh $f$ tăng đơn điệu qua các bước nên dãy hội tụ tới một cực đại địa phương. Hệ quả: meanShift chỉ tìm được đỉnh **gần cửa sổ ban đầu nhất**; vật di chuyển quá xa giữa hai frame (ra ngoài cửa sổ) sẽ bị mất dấu.
        :::

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

        :::proof công thức s = 2√(M00/256) và hướng của elip
        **1. Kích thước cửa sổ.** Backprojection có giá trị 0–255, với 255 ≈ "chắc chắn là vật". $M_{00} = \sum P$ nên $\frac{M_{00}}{256} \approx$ **số pixel tương đương có xác suất đầy** – tức diện tích vật $A$ tính bằng pixel (chia 256 vì đó là số mức của ảnh 8 bit). Hình vuông có diện tích $A$ có cạnh $\sqrt{A}$, nên

        $$s = 2\sqrt{\frac{M_{00}}{256}} \approx 2\sqrt{A}$$

        là cửa sổ có cạnh **gấp đôi kích thước vật**. Hệ số 2 là lựa chọn của Bradski (1998), không phải kết quả chứng minh: cửa sổ lớn hơn vật để vẫn bao được vật khi nó di chuyển hoặc to ra ở frame sau, nhưng không quá lớn để tránh lẫn nền. Vật to lên → $M_{00}$ tăng → cửa sổ tự to ra, và ngược lại.

        **2. Hướng của elip từ mô-men bậc hai.** Ma trận hiệp phương sai của phân bố $P$ trong cửa sổ:

        $$C = \frac{1}{M_{00}}\begin{bmatrix} \mu_{20} & \mu_{11} \\ \mu_{11} & \mu_{02} \end{bmatrix}$$

        ($\mu_{pq}$: mô-men trung tâm). Trục chính của elip là vector riêng ứng với trị riêng lớn. Tìm góc $\theta$ sao cho hệ trục xoay $\theta$ làm $C$ **chéo hóa**: phần tử ngoài đường chéo của $R^TCR$ bằng 0. Với hai trục mới $\mathbf{e}_1 = (\cos\theta, \sin\theta)$, $\mathbf{e}_2 = (-\sin\theta, \cos\theta)$:

        $$\mathbf{e}_1^T C\,\mathbf{e}_2 \propto -\sin\theta\cos\theta\,\mu_{20} + (\cos^2\theta - \sin^2\theta)\,\mu_{11} + \sin\theta\cos\theta\,\mu_{02} = 0$$

        Dùng $\cos^2\theta - \sin^2\theta = \cos2\theta$ và $\sin\theta\cos\theta = \frac12\sin2\theta$:

        $$\mu_{11}\cos2\theta = \tfrac12(\mu_{20} - \mu_{02})\sin2\theta \;\Rightarrow\; \theta = \frac12\operatorname{atan2}\big(2\mu_{11},\ \mu_{20} - \mu_{02}\big) \qquad \blacksquare$$

        Dùng `atan2` để chọn đúng nghiệm ứng với trục **dài** (phương trình $\tan 2\theta = \dots$ có hai nghiệm cách nhau 90°, ứng với hai trục). Đây cũng là công thức hướng của đốm trong Bài 5–6 của khóa học. Độ dài hai trục tỉ lệ với căn bậc hai của hai trị riêng của $C$.
        :::

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
