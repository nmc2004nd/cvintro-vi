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
