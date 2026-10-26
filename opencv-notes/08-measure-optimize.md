---
title: 8. Measure Optimize
lesson: 
after:
---
Đo thời gian thực hiện code bằng hàm `cv2.getTickCount()` và `cv2.getTickFrequency()`

- `e1 = cv2.getTickCount()`
- `e2 = cv2.getTickCount()`
- `time_seconds = (e2 - e1) / cv2.getTickFrequency`
Nên dung các hàm của Opencv vì nó tối ưu riêng cho dữ liệu ảnh
