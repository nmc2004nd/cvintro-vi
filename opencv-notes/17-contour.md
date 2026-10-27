---
title: 17. Contour
lesson: lesson04_floodfill_connected_components
after:
---
### 17.1 Intro Contour

| Tên hàm OpenCV | Mục tiêu trong pipeline | Tham số cấu hình trọng tâm |
|---|---|---|
| `cv.findContours()` | Trích xuất thông tin: quét ma trận pixel nhị phân để gom cụm tọa độ hình học. | `image`,` mode`,` method`. |
| `cv.drawContours()` | Trực quan hóa đồ họa: vẽ các đường viền từ dạng dữ liệu số lên màn hình. | `target_img`,` contours_list`,` contourIdx`,` color`,` thickness`. |

- Contour là đường cong khép kín nối tất cả các điểm liên tục dọc theo ranh giới của một hình khối có cùng màu sắc hoặc cùng cường độ sáng
- ==Quy tắc khi tìm kiếm contour==
    - ==Luôn sử dụng ảnh nhị phân (Binary Image) → trước khi tìm kiếm contour cần áp dụng tách ngưỡng (`Thresholding`) hoặc phát hiện cạnh` Canny`==
    - ==Tìm vật thể trắng trên nền đen==
    - ==Từ OpenCV 3.2 `cv2.findContours()` không còn sửa ảnh đầu vào; với bản cũ hơn nên truyền bản sao `thresh.copy()` để không làm hỏng ảnh gốc==

```python
# 2. Chuyển ảnh màu sang ảnh xám (Grayscale)
imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

# 3. Chuyển ảnh xám sang ảnh nhị phân (Thresholding)
ret, thresh = cv.threshold(imgray, 127, 255, cv.THRESH_BINARY)

# 4. Trích xuất đường viền bằng hàm cv.findContours()
contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
```

- `cv2.findContours( image, mode, method)`
- `contours, hierarchy = cv.findContours(...)`
    - contours : list các đường viền tìm được. Mỗi đường viền là một mảng Numpy lưu trữ tập hợp các tọa độ (x, y)
    - hierachy: Ma trận phân cấp chứa thông tin về mối quan hệ cha-con, trong-ngoài của các đường viền
- Vẽ đường viền lên ảnh:

    ![](img/opencv-notes/17-contour-1.png)

    - `cv2.drawContours(image, contours, contourIdx, color, thickness)`

    ```python
    # Kịch bản A: Vẽ toàn bộ các đường viền tìm được (truyền contourIdx = -1)
    # Tham số: (ảnh nền, danh sách contours, contourIdx, màu sắc BGR, độ dày nét)
    cv.drawContours(im, contours, -1, (0, 255, 0), 3)

    # Kịch bản B: Chỉ vẽ duy nhất đường viền thứ 4 trong danh sách (truyền index = 3)
    cv.drawContours(im, contours, 3, (0, 255, 0), 3)

    # Kịch bản C: Trích xuất đường viền ra biến riêng rồi vẽ
    cnt = contours[4]
    cv.drawContours(im, [cnt], 0, (0, 255, 0), 3)
    ```

- Phương pháp xấp xỉ đường viền (Contour Approximation Method)
    - tham số `method` quyết định số lượng tọa độ mà máy tính sẽ lưu vào RAM

    | Phương pháp | Cơ chế | Hệ quả |
    |---|---|---|
    | `cv.CHAIN_APPROX_NONE` | Lưu trữ toàn bộ các điểm tọa độ nằm trên đường ranh giới. | Tạo ra một mảng dữ liệu lớn. Ví dụ, để biểu diễn một hình chữ nhật, nó có thể lưu tới hàng trăm điểm xếp dọc theo 4 cạnh. |
    | `cv.CHAIN_APPROX_SIMPLE` | Loại bỏ các điểm tọa độ dư thừa bị trùng lặp hướng tuyến tính và nén đường viền lại. | Tiết kiệm bộ nhớ đáng kể. Với hình chữ nhật, một cạnh thẳng chỉ cần xác định bởi điểm đầu và điểm cuối, nên kết quả có thể chỉ còn 4 điểm góc. |

### 17.2 Feature Contour

| Tên hàm OpenCV | Giá trị đặc trưng trích xuất | Ý nghĩa ứng dụng trong AI/CV |
|---|---|---|
| `cv.moments()` | Dictionary các giá trị moment (`m00`,` m10`,` m01`, ...). | Tính toán trọng tâm hình học của vật thể. |
| `cv.contourArea()` | Diện tích vùng khép kín, tính theo số lượng pixel. | Lọc bỏ các vật thể quá nhỏ như nhiễu, hoặc quá lớn. |
| `cv.arcLength()` | Chu vi đường viền. | Dùng làm tham số chuẩn hóa, tính độ tròn vật thể. |
| `cv.approxPolyDP()` | Mảng các đỉnh đa giác đơn giản hóa. | Nhận diện hình khối cơ bản như tam giác, hình vuông, hình tròn. |
| `cv.convexHull()` | Các đỉnh của bao lồi bên ngoài. | Xử lý nhận diện cử chỉ bàn tay, ngón tay. |
| `cv.boundingRect()` | Tọa độ chữ nhật thẳng `(x, y, w, h)`. | Khoanh vùng ROI (Region of Interest) để cắt ảnh vật thể. |
| `cv.minAreaRect()` | Cấu trúc chữ nhật xoay tối ưu diện tích. | Nhận diện hướng nghiêng của biển số xe, văn bản. |

- Moment ảnh và trọng tâm
    - `cv2.moments()`

    ```python
    ret, thresh = cv.threshold(img, 127, 255, 0)
    contours, hierarchy = cv.findContours(thresh, 1, 2)

    cnt = contours[0]
    M = cv.moments(cnt)
    ```

    - Trích xuất tọa độ trọng tâm (Centroid) $C_x, C_y$ của vật thể theo công thức:
        - $$C_x = \frac{M_{10}}{M_{00}}, C_y = \frac{M_{01}}{M_{00}}$$

        ```python
        # Tính toán tọa độ trọng tâm, ép kiểu về số nguyên để vẽ lên lưới pixel
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        ```

        - Cẩn thận `M['m00'] = 0` (contour suy biến, diện tích bằng 0) sẽ gây lỗi chia cho 0 → nên kiểm tra trước

        :::proof trọng tâm từ mô-men và công thức diện tích của contour
        **1. Mô-men của vùng nhị phân.** Định nghĩa $M_{pq} = \sum_{x, y} x^p y^q\, I(x, y)$. Với ảnh nhị phân ($I = 1$ trong vùng $R$, 0 ngoài vùng):

        $$M_{00} = \sum_{(x,y) \in R} 1 = |R| \;\text{(diện tích)}, \qquad M_{10} = \sum_{(x,y) \in R} x, \qquad M_{01} = \sum_{(x,y) \in R} y$$

        Nên $C_x = \frac{M_{10}}{M_{00}} = \frac{1}{|R|}\sum_R x$ chính là **trung bình tọa độ x** của các pixel trong vùng, tương tự $C_y$. Với ảnh xám, $I$ đóng vai trò trọng số: pixel càng sáng kéo trọng tâm càng nhiều. $\blacksquare$

        **2. Khi gọi `cv.moments(cnt)` trên contour, OpenCV không đếm pixel** mà tính trên đa giác nối các đỉnh contour, bằng định lý Green. Với diện tích:

        $$A = \iint_R 1\,dx\,dy = \frac12 \oint_{\partial R} (x\,dy - y\,dx)$$

        (kiểm tra: theo Green, $\oint (P\,dx + Q\,dy) = \iint (\partial_x Q - \partial_y P)$; với $P = -y/2$, $Q = x/2$ thì vế phải là $\iint (\frac12 + \frac12) = A$). Trên đa giác các đỉnh $(x_k, y_k)$, tích phân trên mỗi cạnh tính được chính xác, cho **công thức dây giày (shoelace)**:

        $$A = \frac12 \left|\sum_{k} (x_k\,y_{k+1} - x_{k+1}\,y_k)\right|$$

        **Hệ quả thực tế:** đa giác đi qua *tâm* các pixel biên, nên bỏ mất nửa pixel ở mỗi phía. Mình đã kiểm tra: hình vuông trắng 10x10 pixel cho `contourArea = 81` (= 9 x 9) và `moments(cnt)['m00'] = 81`, trong khi `moments(img, binaryImage=True)['m00'] = 100`. Cần số pixel chính xác thì dùng `cv.countNonZero` hoặc mô-men của ảnh.

        **3. Vì sao $M_{00} = 0$ được.** Contour suy biến (một đường thẳng, một điểm) có diện tích đa giác bằng 0, nên $C_x = M_{10}/M_{00}$ không xác định – đúng như cảnh báo ở trên.
        :::


- Diện tích và chu vi đường viền
    - Diện tích contour - `cv2.contourArea()`
        - `area = cv.contourArea(cnt)`
    - Chu vi contour/ độ dài cung - `cv2.arcLength()`
        - `perimeter = cv.arcLength(cnt, True)`
        - True: Đường cong khép kín
        - False: Đường cong hở
- Phép xấp xỉ đa giác đường viền

    ![](img/opencv-notes/17-contour-2.png)

    - `cv2.approxPolyDP(cnt, epsilon, closed)`
    - Phép này giúp biến đổi một đường cong ngoằn ngoèo có nhiều đỉnh thành khối hình học có ít đỉnh hơn
    - `epsilon` : Khoảng cách tối đa cho phép đường viền gốc đến đường viền xấp xỉ
        - $\epsilon$ quá lớn → Hình xấp xỉ bị thô và mất nhiều chi tiết
        - $\epsilon$ quá nhỏ → Hình xấp xỉ bám quá sát ảnh gốc, không nén được số đỉnh

        :::proof thuật toán Douglas–Peucker và ý nghĩa chính xác của epsilon
        `approxPolyDP` dùng thuật toán **Douglas–Peucker** (đệ quy):

        1. Nối điểm đầu $A$ và điểm cuối $B$ của đoạn đường cong bằng một đoạn thẳng.
        2. Tìm điểm $P$ trên đường cong **xa đoạn $AB$ nhất**, khoảng cách $d_{\max}$.
        3. Nếu $d_{\max} \le \varepsilon$: thay cả đoạn cong bằng đoạn $AB$. Nếu không: giữ $P$ làm đỉnh, đệ quy cho hai đoạn $A \to P$ và $P \to B$.

        **Khoảng cách từ điểm tới đường thẳng.** Diện tích tam giác $ABP$ bằng nửa độ lớn tích có hướng, và cũng bằng $\frac12 \cdot \text{đáy} \cdot \text{chiều cao}$:

        $$\frac12\big|(B - A) \times (P - A)\big| = \frac12\,|AB|\,d \;\Rightarrow\; d = \frac{|(x_B - x_A)(y_P - y_A) - (y_B - y_A)(x_P - x_A)|}{\sqrt{(x_B - x_A)^2 + (y_B - y_A)^2}}$$

        **Khẳng định:** mọi điểm của contour gốc cách đa giác xấp xỉ không quá $\varepsilon$.

        **Chứng minh (quy nạp theo số lần đệ quy).** Một đoạn chỉ được thay bằng đường thẳng ở bước 3 khi $d_{\max} \le \varepsilon$, tức *mọi* điểm của đoạn cong đó cách đường thẳng $AB$ không quá $\varepsilon$. Mọi điểm gốc cuối cùng đều thuộc đúng một đoạn như vậy (vì đệ quy chỉ dừng khi điều kiện này đúng, hoặc khi đoạn chỉ còn 2 điểm – lúc đó khoảng cách bằng 0). $\blacksquare$

        Đây là lý do $\varepsilon$ được đặt theo **tỉ lệ chu vi** (`0.01`–`0.05 * arcLength`): sai số cho phép tỉ lệ với kích thước vật, nên cùng một hệ số cho kết quả giống nhau dù vật to hay nhỏ trong ảnh.
        :::


    ```python
    # Ví dụ trong tài liệu: epsilon = 10% chu vi (thực tế hay dùng 1-5% để giữ hình dạng tốt hơn)
    epsilon = 0.1 * cv.arcLength(cnt, True)
    approx = cv.approxPolyDP(cnt, epsilon, True)  # Đối số 3: đường cong khép kín
    ```

- Bao lồi (Convex Hull)
    - `cv2.convexHull()`
    - Quét qua tất cả các điểm lõm của đường cong và tự động căng phẳng hoặc bọc lồi nó lại

    ![](img/opencv-notes/17-contour-3.png)

    - `hull = cv.convexHull(points[, hull[, clockwise[, returnPoints]]])`
        - `points`: Tập hợp đường viền` cnt `truyền vào
        - `clockwise`: Cờ định hướng. Nếu` True`, các đỉnh bao lồi được sắp theo chiều kim đồng hồ,` False` thì ngược chiều kim đồng hồ
        - `returnPoints` :
            - Mặc định là True → Trả về tọa độ các đỉnh bao lồi.
            - False trả về chỉ số index của các điểm đó trong mảng cnt.
            - Đặt False nếu muốn tính toán convexity defects
    - Thông thường dùng:

    ```python
    # Cách dùng phổ biến để lấy tọa độ vẽ bao lồi
    hull = cv.convexHull(cnt)
    ```

    - Kiểm tra tính lồi - `cv2.isContourConvex()` :
        - `is_convex = cv.isContourConvex(cnt)`
- Bounding Rectangle
    - Hình chữ nhật bao thẳng đứng - `cv2.boundingRect`
        - Hình chữ nhật thẳng theo lưới tọa độ không quan tâm đến góc xoay của vật thể
        - **Diện tích hộp này thường lớn hơn diện tích thực tế của vật thể**

        ```python
        x, y, w, h = cv.boundingRect(cnt)
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Vẽ hộp màu xanh lá
        ```

    - Hộp bao chữ nhật xoay quanh có diện tích tối thiểu - `cv2.minAreaRect`
        - Ôm sát vật thể bằng cách xoay theo góc nghiêng của vật thể
        - Hàm trả về Box2D: `((cx, cy), (width, height), angle)` - tâm, kích thước và góc xoay
        - Để vẽ hộp này cần phải chuyển cấu trúc trên thành 4 đỉnh tọa độ thông qua hàm `cv2.boxPoints`

        ```python
        rect = cv.minAreaRect(cnt)
        box = cv.boxPoints(rect)     # Lấy 4 đỉnh tọa độ
        box = np.intp(box)           # Chuyển tọa độ sang số nguyên để vẽ
        cv.drawContours(img, [box], 0, (0, 0, 255), 2)  # Vẽ hộp xoay màu đỏ
        ```

- Đường tròn, elip và đường thẳng khớp tối ưu
    - Đường tròn ngoại tiếp tối thiểu

        ![](img/opencv-notes/17-contour-4.png)

        - Tìm đường tròn có diện tích nhỏ nhất có thể bao bọc trọn vẹn vật thể
        - `cv2.minEnclosingCircle(cnt)`

        ```python
        (x, y), radius = cv.minEnclosingCircle(cnt)
        center = (int(x), int(y))
        radius = int(radius)
        cv.circle(img, center, radius, (0, 255, 0), 2)
        ```

    - Khớp khung hình elip

        ![](img/opencv-notes/17-contour-5.png)

        - `cv2.fitEllipse(cnt)`

        ```python
        ellipse = cv.fitEllipse(cnt)
        cv.ellipse(img, ellipse, (0, 255, 0), 2)
        ```

    - Khớp đường thẳng tối ưu

        ![](img/opencv-notes/17-contour-6.png)

        - Dựa vào bình phương tối thiểu để fit line

        ```python
        [vx, vy, x, y] = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01).flatten()
        print(f"Đường thẳng khớp contour: vx={vx}, vy={vy}, x={x}, y={y}")
        # (vx, vy): vector chỉ phương, (x, y): một điểm trên đường thẳng
        # X = vx * t + x
        # Y = vy * t + y
        # lefty: giải pt tại X = 0, righty: giải pt tại X = img.shape[1] - 1 (cột cuối cùng)
        lefty = float((-x * vy / vx) + y)
        righty = float(((img.shape[1] - 1 - x) * vy / vx) + y)
        cv2.line(img, (img.shape[1] - 1, int(righty)), (0, int(lefty)), (0, 255, 0), 2)
        ```

### 17.3 Properties Contour

| Thuộc tính / hàm | Bản chất toán học | Bài toán ứng dụng thực tế |
|---|---|---|
| `Aspect Ratio` | W/H của hộp bao thẳng đứng. | Phân biệt xe máy, thường có hộp bao hẹp và tỷ lệ đứng, với xe ô tô, thường có hộp rộng và tỷ lệ ngang. |
| `Extent` | Diện tích thực / diện tích hộp bao thẳng đứng. | Đánh giá mức độ lấp đầy của vật thể trong ROI. |
| `Solidity` | Diện tích thực / diện tích bao lồi. | Phân loại hình dáng, phát hiện vật thể bị méo mó, khuyết tật hoặc có kết cấu lồi lõm. |
| `Equivalent Diameter` | Đường kính hình tròn có cùng diện tích với contour. | Chuẩn hóa kích thước vật thể về một đại lượng đường kính dễ so sánh. |
| `cv.minMaxLoc()` | Lọc điểm cực trị độ sáng qua `mask`. | Tìm điểm phản xạ chói sáng nhất trên bề mặt sản phẩm để kiểm thử chất lượng lỗi. |
| `cv.mean()` | Trung bình cộng cường độ pixel qua `mask`. | Nhận diện màu sắc của một quả trái cây trên băng chuyền để phân loại độ chín. |
| `Extreme Points` | Các điểm có x hoặc y nhỏ nhất/lớn nhất trên contour. | Xác định kích thước biên ngoài cùng hoặc điểm mốc để căn chỉnh vật thể. |

- **Shape Properties**
    - **Tỷ lệ khung hình (Aspect Ratio)**
        - $$\text{Aspect Ratio} = \frac{\text{Width}}{\text{Height}}$$

        ```python
        x, y, w, h = cv.boundingRect(cnt)
        aspect_ratio = float(w) / h
        ```

    - **Độ phủ / mức độ mở rộng (Extent)**
        - Tỷ số giữa diện tích của đường viền và diện tích của hình chữ nhật bao (bounding rect)
        - Thể hiện mức độ lấp đầy của vật thể trong khung hình chữ nhật bao quanh nó
        - $$\text{Extent} = \frac{\text{Contour Area}}{\text{Bounding Rect Area}}$$

        ```python
        area = cv.contourArea(cnt)
        x, y, w, h = cv.boundingRect(cnt)
        rect_area = w * h

        extent = float(area) / rect_area
        ```

        :::proof vì sao Extent, Solidity nằm trong (0, 1] và công thức đường kính tương đương
        **Extent ≤ 1.** Hình chữ nhật bao là hình chữ nhật thẳng nhỏ nhất *chứa* contour, nên vùng contour $R \subseteq$ hình chữ nhật, suy ra $\text{Area}(R) \le w \cdot h$. Dấu bằng chỉ khi vật chính là hình chữ nhật thẳng. Ví dụ: hình tròn có Extent $= \frac{\pi r^2}{(2r)^2} = \frac{\pi}{4} \approx 0.785$; tam giác vuông nửa hình chữ nhật có Extent $= 0.5$.

        **Solidity ≤ 1, và = 1 khi và chỉ khi vật lồi.** Bao lồi là tập lồi nhỏ nhất chứa $R$, nên $R \subseteq \text{Hull}(R)$ và $\text{Area}(R) \le \text{Area}(\text{Hull})$. Nếu $R$ lồi thì chính $R$ là tập lồi chứa $R$, nên $\text{Hull}(R) = R$ và Solidity = 1. Ngược lại nếu $R$ không lồi thì phần "lõm" $\text{Hull} \setminus R$ có diện tích dương, nên Solidity < 1. $\blacksquare$ (Do `contourArea` tính trên đa giác qua tâm pixel, contour lồi thực tế cho giá trị rất gần 1 chứ không phải luôn đúng bằng 1.)

        **Đường kính tương đương.** Đặt diện tích hình tròn đường kính $d$ bằng diện tích vật:

        $$\pi\left(\frac{d}{2}\right)^2 = \text{Area} \iff \frac{\pi d^2}{4} = \text{Area} \iff d = \sqrt{\frac{4 \cdot \text{Area}}{\pi}}$$

        **Bất biến:** Aspect Ratio, Extent, Solidity là tỉ số của hai đại lượng cùng đơn vị nên **không đổi khi phóng to/thu nhỏ** vật (cả tử và mẫu cùng nhân $s$ hoặc $s^2$). Solidity còn không đổi khi xoay; Extent và Aspect Ratio thì có đổi khi xoay vì hình chữ nhật bao luôn thẳng theo trục.
        :::


    - **Độ đặc/ độ rắn (Solidity)**
        - Tỷ số giữa diện tích của đường viền vật thể và diện tích bao lồi (Convex Hull)
        - Thuộc tính phản ánh độ lồi lõm của cấu trúc hiện tại
        - Một đa giác lồi thuần túy sẽ có `Solidity = 1`
        - $$\text{Solidity} = \frac{\text{Contour Area}}{\text{Convex Hull Area}}$$

        ```python
        area = cv.contourArea(cnt)
        hull = cv.convexHull(cnt)
        hull_area = cv.contourArea(hull)

        solidity = float(area) / hull_area
        ```

    - **Đường kính tương đương (Equivalent Diameter)**
        - Là đường kính của một hình tròn lý tưởng có diện tích bằng chính xác diện tích của đường viền vật thể
        - $$\text{Equivalent Diameter} = \sqrt{\frac{4 \times \text{Area}}{\pi}}$$

        ```python
        area = cv.contourArea(cnt)
        equi_diameter = np.sqrt(4 * area / np.pi)
        ```

    - **Hướng và trục hình học (Orientation)**
        - Hướng là góc nghiêng trục chính của vật thể, lấy từ elip khớp với contour

        ```python
        # Trả về tọa độ tâm (x, y), độ dài hai trục (đường kính, không phải bán trục) và góc nghiêng (angle)
        (x, y), (MA, ma), angle = cv.fitEllipse(cnt)
        ```

- **Trích xuất pixel và thống kê giá trị pixel trong vùng ROI**
    - **Mask và tọa độ điểm pixel thành phần**
        - Dùng khi cần cô lập vùng không gian chứa vật thể và trích xuất danh sách tất cả các tọa độ pixel cấu thành nên vật

        ```python
        # Tạo một mặt nạ đen hoàn toàn có cùng kích thước với ảnh xám nguồn
        mask = np.zeros(imgray.shape, np.uint8)

        # Vẽ tô đặc (-1) đường viền vật thể bằng màu trắng (255) lên mặt nạ đen
        cv.drawContours(mask, [cnt], 0, 255, -1)

        # CÁCH 1: Trích xuất danh sách pixel bằng hàm NumPy : y,x
        pixelpoints_numpy = np.transpose(np.nonzero(mask))

        # CÁCH 2: Trích xuất danh sách pixel bằng hàm OpenCV: x, y
        pixelpoints_opencv = cv.findNonZero(mask)
        ```

    - **Tìm giá trị cực trị và vị trí của chúng**
        - `min_val, max_val, min_loc, max_loc = cv.minMaxLoc(imgray, mask=mask)`
    - **Cường độ sáng / màu sắc trung bình**

        ```python
        # Hàm luôn trả về tuple 4 phần tử; với ảnh BGR là (B, G, R, 0)
        mean_val = cv.mean(im, mask=mask)
        ```

- **Điểm cực trị của vật thể (Extreme Points)**

    ```python
    # Điểm ngoài cùng bên trái (tọa độ X nhỏ nhất)
    leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])

    # Điểm ngoài cùng bên phải (tọa độ X lớn nhất)
    rightmost = tuple(cnt[cnt[:, :, 0].argmax()][0])

    # Điểm cao nhất trên cùng (tọa độ Y nhỏ nhất)
    topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])

    # Điểm thấp nhất dưới cùng (tọa độ Y lớn nhất)
    bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])
    ```

### 17.4 Function Contour

| Tên hàm OpenCV | Bản chất đại lượng trả về | Bài toán ứng dụng thực tế |
|---|---|---|
| `cv.convexityDefects()` | Ma trận chỉ số 4 cột của các vết lõm hình học. | Nhận diện cử chỉ tay: đếm số lượng khe khuyết lồi để suy ra số lượng ngón tay đang xòe ra. |
| `cv.pointPolygonTest()` | Khoảng cách hình học có dấu (+, −, 0). | Camera an ninh hoặc geofencing: kiểm tra xem tọa độ của người hoặc phương tiện có đang xâm nhập vào vùng đa giác cấm hay không. |
| `cv.matchShapes()` | Điểm số sai biệt dựa trên Hu-Moments. | Nhận diện ký tự quang học sơ khai (OCR): so khớp hình dáng của chữ cái hoặc con số với bảng mẫu. |

- **Điểm khuyết lồi (Convexity Defects)**

    ![](img/opencv-notes/17-contour-7.png)

    - Bất kì đoạn nào của vật thể bị lõm sâu vào trong so với đường ConvexHull được coi là một điểm khuyết lồi
    - Để tính các điểm khuyết lồi:
        - Dùng hàm `cv2.convexityDefects()`
        - Hàm này yêu cầu index của các điểm thay vì tọa độ → bao lồi phải tính bằng `cv2.convexHull(cnt, returnPoints=False)`
    - `cv2.convexityDefects()` trả về:
        - **Start Point**: Chỉ số của điểm ranh giới nơi vết lõm bắt đầu
        - **End Point**: Chỉ số của điểm ranh giới nơi vết lõm kết thúc
        - **Farthest Point**: Chỉ số của điểm nằm sâu nhất trong vết lõm, tức là có khoảng cách xa nhất tới đường bao lồi
        - **Farthest Distance**: Khoảng cách từ điểm sâu nhất đó tới đường bao lồi, lưu dạng số nguyên nhân 256 → khoảng cách thật = `d / 256`

    ```python
    # B1: Tìm bao lồi của contour
    # returnPoints=False để trả về index của các điểm của contour
    hull = cv2.convexHull(cnt, returnPoints=False)

    # B2: Tìm các điểm khuyết lồi của contour
    defects = cv2.convexityDefects(cnt, hull)
    print(defects.shape) # 5 1 4

    # B3: Vẽ contour và các điểm khuyết lồi
    for i in range(defects.shape[0]):
        # s: index của điểm bắt đầu của đoạn thẳng
        # e: index của điểm kết thúc của đoạn thẳng
        # f: index của điểm khuyết lồi
        # d: khoảng cách từ điểm khuyết lồi đến đoạn thẳng nối 2 điểm bắt đầu và kết thúc
        s, e, f, d = defects[i, 0]

        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        # Vẽ cạnh bao lồi đi qua vết lõm
        cv2.line(img, start, end, [0, 255, 0], 2)
        # Vẽ các điểm khuyết lồi
        cv2.circle(img, far, 5, [0, 0, 255], -1)
    ```

- **Kiểm tra điểm trong đa giác (Point Polygon Test)**
    - Hàm `cv2.pointPolygonTest(cnt, point, measureDist)` : dùng để tính khoảng cách ngắn nhất từ 1 điểm tọa độ tới đường viền đa giác
    - `measureDist = True`: trả về khoảng cách có dấu;` False`: chỉ trả về +1, -1, 0 (nhanh hơn)
    - Dương: điểm nằm bên trong đường viền
    - Âm: điểm nằm ngoài đường viền
    - 0: điểm nằm ngay trên đường viền

    ```python
    # Ví dụ tính khoảng cách có dấu từ điểm (50, 50) tới đường viền cnt
    distance = cv.pointPolygonTest(cnt, (50, 50), measureDist=True)
    ```

- **So khớp hình dáng**
    - `cv2.matchShapes(cnt1, cnt2, method, parameter)`
    - Score càng gần 0 thì hai hình càng giống nhau

    ```python
    # Phép toán so sánh hai đường viền
    similarity_score = cv.matchShapes(cnt1, cnt2, method=cv.CONTOURS_MATCH_I1, parameter=0.0)
    print(similarity_score)
    ```

### 17.5 Hierarchy Contour

| Chế độ (Mode) | Số lượng tầng Phân cấp | Thu thập chi tiết lỗ bên trong? | Ưu tiên ứng dụng thực tế |
|---|---|---|---|
| `cv.RETR_LIST` | Đúng 1 tầng (Phẳng) | **Có** (Nhưng coi như ngang hàng biên ngoài). | Đếm tổng số lượng, xử lý hình khối độc lập, tối ưu tốc độ. |
| `cv.RETR_EXTERNAL` | Đúng 1 tầng (Rìa ngoài) | **Không** (Bỏ qua hoàn toàn chi tiết bên trong). | Trích xuất khuôn hình/bóng của vật thể, tách nền nhanh. |
| `cv.RETR_CCOMP` | Đúng 2 tầng (Biên & Lỗ) | **Có** (Phân tách rõ ràng biên và lỗ thủng). | Xử lý các vật thể có lỗ đục (như nhận diện các con ốc vít, long đền). |
| `cv.RETR_TREE` | Vô số tầng (Mạng lưới cây) | **Có** (Lập gia phả chi tiết từ ngoài vào trong). | Phân tích cấu trúc lồng nhau phức tạp, quét mã vạch, mã QR. |

- Thông thường dùng hàm `cv2.findContours()` để phát hiện các vật thể độc lập. Tuy nhiên trong thực tế gặp nhiều trường hợp các hình khối nằm lồng vào bên trong nhau
    - **Đường viền Cha (Parent Contour)**: Đường bao bọc phía ngoài
    - **Đường viền Con (Child Contour)**: Đường nằm trọn vẹn ở phía bên trong
    - **Cùng cấp bậc (Same Hierarchy Level)**: Các đường viền nằm độc lập ở cùng một tầng không gian
- $$\text{Hierarchy Array} = \begin{bmatrix} \text{Next}, & \text{Previous}, & \text{First_Child}, & \text{Parent} \end{bmatrix}$$
    - `Next` **(Đường viền tiếp theo):** Chỉ số (index) của đường viền tiếp theo **nằm cùng một cấp bậc** phân cấp với đường viền hiện tại.
    - `Previous` **(Đường viền trước đó):** Chỉ số của đường viền nằm ngay trước nó **trên cùng một cấp bậc**.
    - `First_Child` **(Con đầu lòng):** Chỉ số của đường viền con **đầu tiên** nằm lồng bên trong nó (nếu có nhiều con, chỉ lấy đứa đầu tiên).
    - `Parent` **(Đường viền cha):** Chỉ số của đường viền cha trực tiếp bao bọc lấy nó ở tầng ngay phía trên.
    - **Quy ước:** Nếu tại vị trí nào đó không tồn tại đường viền thỏa mãn (không có cha, không có con, hoặc không có anh em cùng cấp ở trước/sau), OpenCV sẽ gán giá trị `-1`.
- **Contour Retrieval Modes**
    - `cv2.RETR_LIST`
        - **Luật xử lý:** Đây là chế độ đơn giản nhất. Nó thu thập **tuyệt đối tất cả mọi đường viền** nhưng **không thiết lập bất kỳ mối quan hệ cha-con nào**. Cha và con hoàn toàn bình đẳng và bị ép nằm chung ở một cấp phân cấp duy nhất.
        - **Hệ quả ma trận:** Giá trị cột số 3 (`First_Child`) và cột số 4 (`Parent`) luôn luôn bằng` -1`.
        - **Ứng dụng:** Hãy luôn chọn `cv.RETR_LIST` nếu ứng dụng của bạn chỉ cần đếm số lượng vật thể hoặc tính diện tích mà không quan tâm chúng có lồng nhau hay không, vì chế độ này chạy rất nhanh và tiết kiệm tài nguyên.
    - `cv2.RETR_EXTERNAL`
        - **Luật xử lý:** Chế độ này **chỉ thu thập các đường viền nằm ở rìa ngoài cùng**, loại bỏ sạch sẽ tất cả các đường viền con nằm lồng bên trong. (Có thể hiểu vui là luật này chỉ quan tâm đến vị trưởng tộc cao nhất trong gia đình).
        - **Hệ quả ma trận:** Chỉ trả về các đường viền ở tầng ngoài cùng; đường viền con không được trả về nên `First_Child` và `Parent` luôn bằng `-1`.
        - **Ứng dụng:** Cực kỳ hữu ích khi bạn muốn cắt lấy biên dạng tổng thể của một vật thể phức tạp và muốn loại bỏ các chi tiết đục lỗ, hoa văn rỗng ở bên trong vật thể đó
    - `cv2.RETR_CCOMP`
        - **Luật xử lý:** Thu thập tất cả các đường viền nhưng ép cấu trúc về dạng **phân cấp đúng 2 tầng cố định**:
            - **Tầng 1 (Hierarchy-1):** Chứa các đường biên ngoài cùng của vật thể.
            - **Tầng 2 (Hierarchy-2):** Chứa đường biên của các lỗ thủng (holes) nằm bên trong vật thể đó.
            - *Nếu bên trong lỗ thủng lại chứa một vật thể con khác?* Vật thể con đó sẽ tự động được đưa ngược lên xếp ở Tầng 1, và lỗ thủng của nó lại nằm ở Tầng 2.
    - `cv2.RETR_TREE`
        - **Luật xử lý:** Đây là chế độ toàn diện và hoàn hảo nhất. Nó thiết lập một **cây phả hệ đầy đủ nhiều tầng bậc**, ghi nhận chính xác tuyệt đối mối quan hệ từ ông bà, cha mẹ, con cái, cháu chắt lồng ghép sâu bao nhiêu tầng tùy ý vào bên trong.
        - **Ứng dụng:** Sử dụng khi cần phân tích các cấu trúc đồ họa phức tạp đan xen lồng nhau, như nhận diện cấu trúc các linh kiện trên bo mạch điện tử hoặc phân tích văn bản nhiều lớp ký tự
