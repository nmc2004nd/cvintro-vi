---
title: 40. Face Detection - Haar Cascade
lesson: lesson40_object_detection_sliding_windows
after:
draft: true
---
- ==Lưu ý phiên bản==: `cv.CascadeClassifier` có trong OpenCV 4.x. Bản `opencv-python` 5.0 không còn → dùng OpenCV 4.x, hoặc bộ phát hiện mặt bằng DNN `cv.FaceDetectorYN` (YuNet, có cả trong 4.x và 5.0), chính xác hơn nhiều
- Thuật toán Viola-Jones (2001): ==phát hiện đối tượng bằng cửa sổ trượt + cascade các bộ phân loại==
- **Đặc trưng Haar**: hiệu tổng pixel giữa vùng trắng và vùng đen của các mẫu hình chữ nhật (cạnh, đường, tâm)
    - Ví dụ: vùng mắt tối hơn vùng má, sống mũi sáng hơn hai bên mắt
    - Cửa sổ 24x24 có hơn 160.000 đặc trưng
- **Ảnh tích phân (integral image)**: ==tổng pixel của mọi hình chữ nhật chỉ cần 4 phép truy cập== → tính đặc trưng Haar rất nhanh
- **AdaBoost**: chọn ra vài nghìn đặc trưng tốt nhất trong 160.000 (bài báo: khoảng 6000), mỗi đặc trưng là một bộ phân loại yếu, ghép lại thành bộ phân loại mạnh
- ==**Cascade**==: chia các đặc trưng thành nhiều tầng (bài báo: 38 tầng)
    - Tầng đầu chỉ vài đặc trưng, loại ngay phần lớn cửa sổ không phải mặt
    - ==Cửa sổ chỉ là mặt nếu vượt qua tất cả các tầng==
    - Trung bình mỗi cửa sổ chỉ cần tính khoảng 10 đặc trưng → chạy thời gian thực
- OpenCV có sẵn các file XML đã huấn luyện (mặt chính diện, mắt, nụ cười, toàn thân, biển số Nga...) trong thư mục `cv.data.haarcascades`
- Hàm: `objects = classifier.detectMultiScale(gray, scaleFactor, minNeighbors, minSize)`
    - `scaleFactor`: mỗi lần thu nhỏ ảnh bao nhiêu để quét ở nhiều tỷ lệ (1.1 = giảm 10%); nhỏ → chính xác hơn nhưng chậm hơn
    - `minNeighbors`: ==số khung chồng lấp tối thiểu để giữ một phát hiện; lớn → ít phát hiện sai nhưng dễ sót==
    - `minSize`, `maxSize`: giới hạn kích thước đối tượng
    - Trả về danh sách `(x, y, w, h)`

```python
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")
eyes_cascade = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_eye.xml")

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = cv.equalizeHist(gray)                      # chuẩn hóa ánh sáng

faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(60, 60))
for (x, y, w, h) in faces:
    cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    roi_gray = gray[y:y + h, x:x + w]              # chỉ tìm mắt bên trong mặt
    eyes = eyes_cascade.detectMultiScale(roi_gray)
    for (ex, ey, ew, eh) in eyes:
        cv.rectangle(img, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 0), 2)
```

![](img/opencv-notes/40-face-detection-1.png)

- Hình trên: `minNeighbors=5` cho 4 vùng, trong đó có 1 vùng nhận nhầm (khung đỏ ở tay); tăng lên `minNeighbors=10` chỉ còn đúng 3 khuôn mặt
- ==Hạn chế:==
    - ==Chỉ tốt với mặt chính diện==, nghiêng nhiều hoặc bị che thì sót
    - Nhạy với ánh sáng, nhiều phát hiện sai trên nền phức tạp
    - Hiện nay nên dùng bộ phát hiện dựa trên deep learning (`cv.FaceDetectorYN`, các mô hình trong module `cv.dnn`)
- Có thể tự huấn luyện cascade bằng công cụ `opencv_traincascade` (đã ngừng phát triển, chỉ còn ở nhánh OpenCV 3.4)
- ==Ứng dụng:== ==phát hiện mặt trên camera giá rẻ, thiết bị nhúng; bước đầu của nhận diện khuôn mặt==
