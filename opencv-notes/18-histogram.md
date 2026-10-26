---
title: 18. Histogram
lesson: lesson03_thresholding_morphology
after: Thresholding
draft: true
---
| Hàm | Ý nghĩa | Ứng dụng |
|---|---|---|
| `cv.calcHist()` | Tính histogram 1D/2D, có thể kèm `mask` | Phân tích độ sáng, tương phản, màu sắc |
| `cv.equalizeHist()` | Cân bằng histogram toàn cục | Tăng tương phản ảnh xám |
| `cv.createCLAHE()` | Cân bằng histogram thích nghi theo từng ô | Tăng tương phản cục bộ, không làm cháy sáng |
| `cv.calcBackProject()` | Chiếu ngược histogram mẫu lên ảnh | Tách vật thể theo màu, dùng cho CamShift |

- Histogram là đồ thị phân bố cường độ của ảnh:
    - Trục x: giá trị pixel (0-255 với ảnh `uint8`)
    - Trục y: số pixel có giá trị đó
    - Histogram dồn về bên trái → ảnh tối, dồn về bên phải → ảnh sáng, dồn vào một vùng hẹp → ==tương phản thấp==
- Các thuật ngữ:
    - **BINS** (`histSize`): số khoảng chia. 256 bins = mỗi giá trị một cột, 16 bins = mỗi cột gom 16 giá trị
    - **DIMS**: số đặc trưng thu thập; ảnh xám chỉ có cường độ → 1
    - **RANGE**: khoảng giá trị cần đo, thường là `[0, 256]`
- Tính histogram bằng OpenCV:
    - `hist = cv.calcHist(images, channels, mask, histSize, ranges)`
    - ==Các tham số đều truyền dạng list `[...]`==
        - `images`: `[img]`, kiểu `uint8` hoặc `float32`
        - `channels`: `[0]` với ảnh xám; `[0]`, `[1]`, `[2]` tương ứng kênh B, G, R
        - `mask`: `None` để tính cả ảnh, hoặc mask trắng ở vùng cần tính
        - `histSize`: `[256]`
        - `ranges`: `[0, 256]`
    - Kết quả là mảng `256x1` kiểu `float32`

    ```python
    hist = cv.calcHist([img], [0], None, [256], [0, 256])

    # Histogram chỉ trong một vùng: tạo mask trắng ở vùng đó
    mask = np.zeros(img.shape[:2], np.uint8)
    mask[100:300, 100:400] = 255
    hist_mask = cv.calcHist([img], [0], mask, [256], [0, 256])
    ```

- Tính histogram bằng NumPy:
    - `hist, bins = np.histogram(img.ravel(), 256, [0, 256])` → `bins` có 257 phần tử (thêm mốc 256 ở cuối)
    - `hist = np.bincount(img.ravel(), minlength=256)` nhanh hơn `np.histogram` khoảng 10 lần
    - `cv.calcHist` vẫn nhanh nhất (khoảng 40 lần so với `np.histogram` theo tài liệu OpenCV)
- Vẽ histogram:
    - Nhanh nhất: `plt.hist(img.ravel(), 256, [0, 256])`
    - Ảnh màu: tính từng kênh rồi `plt.plot`

    ```python
    for i, col in enumerate(("b", "g", "r")):
        histr = cv.calcHist([img], [i], None, [256], [0, 256])
        plt.plot(histr, color=col)
    plt.xlim([0, 256])
    ```

- ==**Cân bằng histogram (Histogram Equalization)**==
    - Ý tưởng: kéo giãn histogram đang dồn vào một vùng hẹp ra toàn dải 0-255 → ==tăng tương phản==
    - Dùng hàm phân phối tích lũy (CDF) làm bảng tra (look-up table):

        $$h(v) = \text{round}\left(\frac{cdf(v) - cdf_{min}}{M \times N - cdf_{min}} \times (L - 1)\right)$$

        - $M \times N$: số pixel, $L = 256$

    ```python
    # Cách làm bằng NumPy
    hist, bins = np.histogram(img.flatten(), 256, [0, 256])
    cdf = hist.cumsum()
    cdf_m = np.ma.masked_equal(cdf, 0)                       # bỏ các giá trị 0
    cdf_m = (cdf_m - cdf_m.min()) * 255 / (cdf_m.max() - cdf_m.min())
    lut = np.ma.filled(cdf_m, 0).astype("uint8")
    img2 = lut[img]                                         # áp bảng tra cho từng pixel

    # Cách làm bằng OpenCV
    equ = cv.equalizeHist(img)                              # chỉ nhận ảnh xám 8-bit
    ```

    - Ảnh tối hay sáng sau khi cân bằng đều cho kết quả gần giống nhau → dùng để ==chuẩn hóa điều kiện ánh sáng== (ví dụ trước khi huấn luyện nhận diện khuôn mặt)
    - Hạn chế: với ảnh vừa có vùng rất tối vừa có vùng rất sáng, cân bằng toàn cục làm cháy chi tiết
    - Ảnh màu: ==không cân bằng riêng từng kênh B, G, R== (lệch màu) → chuyển sang YCrCb hoặc LAB, chỉ cân bằng kênh độ sáng rồi chuyển ngược lại
- ==**CLAHE (Contrast Limited Adaptive Histogram Equalization)**==
    - Chia ảnh thành các ô nhỏ (`tileGridSize`, mặc định 8x8), cân bằng histogram trong từng ô
    - Nhiễu trong ô nhỏ dễ bị khuếch đại → ==giới hạn tương phản==: bin nào vượt `clipLimit` (mặc định 40) thì phần dư được cắt và chia đều cho các bin khác
    - Nội suy song tuyến tính ở biên các ô để không lộ đường ranh giới

    ```python
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl1 = clahe.apply(img)
    ```

    ![](img/opencv-notes/18-histogram-1.png)

- **Histogram 2D**
    - Thu thập hai đặc trưng cùng lúc, thường là Hue và Saturation → histogram màu
    - Chuyển ảnh sang HSV, rồi:
        - `channels = [0, 1]`: kênh H và S
        - `histSize = [180, 256]`: 180 bins cho H, 256 bins cho S
        - `ranges = [0, 180, 0, 256]`

    ```python
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    hist = cv.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
    plt.imshow(hist, interpolation="nearest")              # trục y: H, trục x: S
    ```

    ![](img/opencv-notes/18-histogram-2.png)

- ==**Histogram Backprojection**==
    - Tạo ảnh một kênh cùng kích thước ảnh gốc, mỗi pixel là ==xác suất pixel đó thuộc vật thể== → vật thể hiện lên màu trắng
    - Các bước:
        - Tính histogram màu (H-S) của vùng mẫu chứa vật thể. Vùng mẫu nên chứa càng nhiều vật thể càng tốt
        - Chuẩn hóa histogram mẫu rồi "chiếu ngược" lên ảnh cần tìm
        - Tích chập với kernel hình đĩa để gom các điểm rời rạc
        - Phân ngưỡng để lấy mask

    ```python
    hsv_roi = cv.cvtColor(roi, cv.COLOR_BGR2HSV)
    hsv_target = cv.cvtColor(target, cv.COLOR_BGR2HSV)

    roihist = cv.calcHist([hsv_roi], [0, 1], None, [180, 256], [0, 180, 0, 256])
    cv.normalize(roihist, roihist, 0, 255, cv.NORM_MINMAX)
    dst = cv.calcBackProject([hsv_target], [0, 1], roihist, [0, 180, 0, 256], 1)

    disc = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
    cv.filter2D(dst, -1, disc, dst)

    ret, thresh = cv.threshold(dst, 50, 255, 0)
    res = cv.bitwise_and(target, target, mask=thresh)
    ```

    ![](img/opencv-notes/18-histogram-3.png)

    - ==Ứng dụng:==
        - ==Tách vật thể có màu đặc trưng (sân cỏ, da người, hoa quả)==
        - ==Là bước đầu của thuật toán theo dõi meanShift / CamShift==
