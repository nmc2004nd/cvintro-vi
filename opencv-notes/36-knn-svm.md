---
title: 36. kNN và SVM
lesson: lesson30_projection
after: A projection for classification
draft: true
---
- ==Lưu ý phiên bản==: module `cv.ml` có trong OpenCV 4.x. Bản `opencv-python` 5.0 không còn `cv.ml` → dùng OpenCV 4.x hoặc scikit-learn (`KNeighborsClassifier`, `SVC`)
- Quy ước dữ liệu của `cv.ml`:
    - ==Dữ liệu huấn luyện: `np.float32`, mỗi hàng một mẫu== → truyền cờ `cv.ml.ROW_SAMPLE`
    - Nhãn: `np.float32` hoặc `np.int32`, shape (N, 1)
- ==**k-Nearest Neighbour (kNN)**==
    - Không có bước học thật sự: lưu lại toàn bộ dữ liệu
    - Phân loại điểm mới: tìm k điểm gần nhất, ==lớp nào chiếm đa số thì gán lớp đó==

        :::proof vì sao kNN với k lẻ không hòa (2 lớp) và trọng số theo khoảng cách
        **k lẻ không hòa với 2 lớp.** Nếu hai lớp có $a$ và $b$ phiếu thì $a + b = k$. Hòa nghĩa là $a = b$, tức $k = 2a$ chẵn. Vậy $k$ lẻ thì không thể hòa. $\blacksquare$ Với 3 lớp trở lên, $k$ lẻ **không** đủ (ví dụ $k = 3$ với ba lớp mỗi lớp 1 phiếu) – khi đó cần quy tắc phá hòa, thường là chọn lớp có điểm gần nhất.

        **Trọng số theo khoảng cách** (ví dụ $w_i = 1/d_i$): lớp được chọn là lớp có tổng $w_i$ lớn nhất. Điểm nằm gần điểm mới quyết định nhiều hơn, nên kết quả ít nhạy với việc chọn $k$ hơn.

        **Vì sao kNN cần chuẩn hóa đặc trưng** – giống k-means: khoảng cách Euclid $\sqrt{\sum_j (x_j - x'_j)^2}$ bị chi phối bởi đặc trưng có thang đo lớn nhất.
        :::

    - k nhỏ → nhạy với nhiễu; k lớn → biên quyết định mượt hơn nhưng có thể lấn sang lớp khác; thường chọn k lẻ để tránh hòa
    - Có thể đặt trọng số theo khoảng cách (điểm gần quan trọng hơn)

    ```python
    knn = cv.ml.KNearest_create()
    knn.train(trainData, cv.ml.ROW_SAMPLE, responses)
    ret, results, neighbours, dist = knn.findNearest(newcomer, k=3)
    # results: nhãn dự đoán; neighbours: nhãn của k láng giềng; dist: khoảng cách tới chúng
    ```

    - **Ví dụ nhận dạng chữ số viết tay (OCR)** trong tài liệu:
        - Ảnh `digits.png` gồm 5000 chữ số, mỗi chữ số 20x20 → làm phẳng thành vector 400 chiều
        - 2500 mẫu huấn luyện, 2500 mẫu kiểm tra, k = 5 → ==độ chính xác khoảng 91%==

    ```python
    gray = cv.cvtColor(cv.imread("digits.png"), cv.COLOR_BGR2GRAY)
    cells = [np.hsplit(row, 100) for row in np.vsplit(gray, 50)]   # 50 hàng x 100 cột ô 20x20
    x = np.array(cells)                                           # (50, 100, 20, 20)

    train = x[:, :50].reshape(-1, 400).astype(np.float32)         # (2500, 400)
    test = x[:, 50:100].reshape(-1, 400).astype(np.float32)
    k = np.arange(10)
    train_labels = np.repeat(k, 250)[:, np.newaxis]
    test_labels = train_labels.copy()

    knn = cv.ml.KNearest_create()
    knn.train(train, cv.ml.ROW_SAMPLE, train_labels)
    ret, result, neighbours, dist = knn.findNearest(test, k=5)
    accuracy = np.count_nonzero(result == test_labels) * 100.0 / result.size
    ```

    - ==Nhược điểm==: lưu toàn bộ dữ liệu, dự đoán phải so với mọi mẫu → chậm và tốn bộ nhớ khi dữ liệu lớn
- ==**Support Vector Machine (SVM)**==
    - Tìm siêu phẳng phân chia hai lớp với ==lề (margin) lớn nhất==

        :::proof độ rộng lề 2/‖w‖, vai trò của C và kernel RBF
        **1. Khoảng cách từ điểm tới siêu phẳng.** Siêu phẳng $\mathbf{w}^T\mathbf{x} + b = 0$ có pháp tuyến $\mathbf{w}$. Lấy $\mathbf{x}_0$ trên siêu phẳng; khoảng cách từ $\mathbf{x}$ là độ dài hình chiếu của $\mathbf{x} - \mathbf{x}_0$ lên $\mathbf{w}/\|\mathbf{w}\|$:

        $$\text{dist} = \frac{|\mathbf{w}^T(\mathbf{x} - \mathbf{x}_0)|}{\|\mathbf{w}\|} = \frac{|\mathbf{w}^T\mathbf{x} + b|}{\|\mathbf{w}\|}$$

        (vì $\mathbf{w}^T\mathbf{x}_0 = -b$).

        **2. Độ rộng lề = $2/\|\mathbf{w}\|$.** Nhân $\mathbf{w}, b$ với cùng một hằng số không đổi siêu phẳng, nên có thể chọn thang đo sao cho các điểm gần nhất thỏa $|\mathbf{w}^T\mathbf{x} + b| = 1$. Với nhãn $y_i \in \{-1, +1\}$, mọi điểm được phân loại đúng với lề khi $y_i(\mathbf{w}^T\mathbf{x}_i + b) \ge 1$. Hai đường biên của lề là $\mathbf{w}^T\mathbf{x} + b = \pm1$, mỗi đường cách siêu phẳng $\frac{1}{\|\mathbf{w}\|}$ (theo mục 1), nên lề rộng $\frac{2}{\|\mathbf{w}\|}$. Cực đại lề tương đương bài toán lồi:

        $$\min_{\mathbf{w}, b}\ \frac12\|\mathbf{w}\|^2 \quad \text{với } y_i(\mathbf{w}^T\mathbf{x}_i + b) \ge 1\ \ \forall i$$

        **3. Vì sao chỉ support vector quyết định.** Theo điều kiện tối ưu (KKT) của bài toán trên, nghiệm có dạng $\mathbf{w} = \sum_i \alpha_i y_i \mathbf{x}_i$ với $\alpha_i \ge 0$, và $\alpha_i > 0$ **chỉ** với các điểm nằm đúng trên biên lề ($y_i(\mathbf{w}^T\mathbf{x}_i + b) = 1$). Xóa một điểm nằm ngoài lề thì $\alpha_i = 0$ vẫn thỏa mọi điều kiện, nghiệm không đổi. Đó là các *support vector* trong hình minh họa.

        **4. Tham số C (lề mềm).** Khi dữ liệu không tách được, cho phép vi phạm $\xi_i \ge 0$:

        $$\min\ \frac12\|\mathbf{w}\|^2 + C\sum_i\xi_i \quad \text{với } y_i(\mathbf{w}^T\mathbf{x}_i + b) \ge 1 - \xi_i$$

        $C$ là giá của mỗi đơn vị vi phạm. $C$ lớn → vi phạm rất đắt → bộ giải chấp nhận $\|\mathbf{w}\|$ lớn (lề hẹp) để phân loại đúng hết, dễ khớp cả nhiễu. $C$ nhỏ → ưu tiên $\|\mathbf{w}\|$ nhỏ (lề rộng), chấp nhận vài điểm sai. Đó chính là mô tả `C` trong ghi chú.

        **5. Kernel trick.** Trong bài toán đối ngẫu, dữ liệu chỉ xuất hiện qua tích vô hướng $\mathbf{x}_i^T\mathbf{x}_j$, và hàm quyết định là $\sum_i\alpha_iy_i\,\mathbf{x}_i^T\mathbf{x} + b$. Thay tích vô hướng bằng $K(\mathbf{x}_i, \mathbf{x}) = \phi(\mathbf{x}_i)^T\phi(\mathbf{x})$ là làm SVM tuyến tính trong không gian đặc trưng $\phi$, mà không cần tính $\phi$ tường minh. RBF:

        $$K(\mathbf{x}, \mathbf{x}') = e^{-\gamma\|\mathbf{x} - \mathbf{x}'\|^2}$$

        Hàm quyết định thành tổng các "quả chuông" Gauss đặt tại các support vector, độ rộng cỡ $1/\sqrt{\gamma}$. **$\gamma$ lớn → chuông hẹp → biên uốn sát từng điểm**; $\gamma$ nhỏ → chuông rộng → biên mượt. Đúng như mô tả tham số `gamma` ở dưới.
        :::

    - Chỉ các điểm nằm sát biên (==support vectors==) quyết định siêu phẳng → sau khi học không cần giữ toàn bộ dữ liệu
    - Dữ liệu không tách được bằng đường thẳng → **kernel trick**: ánh xạ ngầm sang không gian nhiều chiều hơn (RBF, đa thức)
    - Tham số:
        - `C`: ==C lớn → phạt nặng điểm bị phân loại sai, lề hẹp, dễ overfit; C nhỏ → lề rộng, chấp nhận vài điểm sai==
        - `gamma` (RBF): gamma lớn → biên quyết định uốn lượn sát từng điểm

    ```python
    svm = cv.ml.SVM_create()
    svm.setType(cv.ml.SVM_C_SVC)
    svm.setKernel(cv.ml.SVM_RBF)                   # hoặc cv.ml.SVM_LINEAR
    svm.setC(10.0)
    svm.setGamma(0.001)
    svm.train(trainData, cv.ml.ROW_SAMPLE, responses)

    result = svm.predict(testData)[1]
    sv = svm.getSupportVectors()
    svm.save("svm_data.dat")                       # tải lại: cv.ml.SVM_load("svm_data.dat")
    ```

    - `svm.trainAuto(...)` tự tìm C, gamma tốt nhất bằng cross-validation
    - **Ví dụ OCR với SVM** trong tài liệu: chỉnh nghiêng chữ số bằng moment (deskew), tính đặc trưng ==HOG== (histogram hướng gradient, 64 chiều), huấn luyện SVM tuyến tính → ==độ chính xác khoảng 94%==

![](img/opencv-notes/36-knn-svm-1.png)

- Hình trên: hai lớp điểm 2D. kNN cho biên quyết định gồ ghề theo từng điểm; SVM RBF cho biên mượt, chỉ phụ thuộc vào các support vector (vòng đen)
- ==Ứng dụng:==
    - ==Phân loại đặc trưng thủ công (HOG, histogram màu) trước thời deep learning: HOG + SVM phát hiện người đi bộ==
    - ==kNN dùng cho tìm kiếm ảnh tương tự theo vector đặc trưng==
