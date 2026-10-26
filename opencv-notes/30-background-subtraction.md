---
title: 30. Background Subtraction
lesson: lesson21_optical_flow
after:
draft: true
---
- Mục tiêu: từ video camera ==cố định==, tách các vật đang chuyển động (foreground) khỏi nền tĩnh
- Cách đơn giản nhất: trừ frame hiện tại cho ảnh nền trống → nhưng thường không có sẵn ảnh nền, và nền còn thay đổi (ánh sáng, lá cây rung, bóng đổ)
- OpenCV dùng ==mô hình thống kê cho từng pixel==, cập nhật liên tục theo thời gian

| Hàm | Thuật toán | Tham số chính |
|---|---|---|
| `cv.createBackgroundSubtractorMOG2()` | Mỗi pixel là hỗn hợp K phân phối Gauss, ==tự chọn số Gauss phù hợp== cho từng pixel | `history=500`, `varThreshold=16`, `detectShadows=True` |
| `cv.createBackgroundSubtractorKNN()` | K láng giềng gần nhất trên các mẫu quá khứ của pixel | `history=500`, `dist2Threshold=400`, `detectShadows=True` |
| `cv.bgsegm.createBackgroundSubtractorMOG()` | MOG gốc, số Gauss cố định | Trong `opencv-contrib-python` |
| `cv.bgsegm.createBackgroundSubtractorGMG()` | Ước lượng Bayes, cần khoảng 120 frame đầu để học nền | Trong `opencv-contrib-python` |

- `history`: số frame dùng để học nền; `varThreshold` / `dist2Threshold`: ngưỡng để coi pixel là khác nền
- ==Phát hiện bóng (`detectShadows=True`)==: pixel bóng có giá trị ==127== trong mask (vật thể = 255, nền = 0)
    - Pixel bóng: tối hơn nền nhưng cùng sắc màu → không bị tính là vật thể
    - Muốn bỏ bóng: `_, fg = cv.threshold(mask, 200, 255, cv.THRESH_BINARY)`
    - Không cần bóng thì đặt `detectShadows=False` cho nhanh hơn

```python
backSub = cv.createBackgroundSubtractorMOG2()          # hoặc createBackgroundSubtractorKNN()
cap = cv.VideoCapture("vtest.avi")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    fgMask = backSub.apply(frame)                     # vừa cập nhật mô hình vừa trả về mask
    # learningRate: -1 tự động, 0 không học nữa, 1 học lại từ đầu theo frame hiện tại
    # fgMask = backSub.apply(frame, learningRate=-1)
```

- `backSub.getBackgroundImage()`: ảnh nền mà mô hình đang ước lượng

![](img/opencv-notes/30-background-subtraction-1.png)

- Hậu xử lý thường dùng:
    - Bỏ bóng bằng threshold
    - Opening để xóa nhiễu nhỏ, closing để lấp lỗ trong vật thể
    - `findContours` + lọc theo diện tích → khung bao từng vật thể
- ==Hạn chế:==
    - ==Camera phải đứng yên==; camera rung hoặc di chuyển → cả ảnh thành foreground
    - Vật đứng yên lâu sẽ dần bị học thành nền
- ==Ứng dụng:==
    - ==Camera giám sát: phát hiện người, xe chuyển động==
    - ==Đếm phương tiện, đếm người qua cửa==
