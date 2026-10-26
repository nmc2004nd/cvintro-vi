---
title: 2. Reading videos
lesson: lesson01_images_as_arrays
after:
---
- Đọc video bằng `cv2.VideoCapture(source)` - source thường là 0, 1
    - `cap = cv2.VideoCapture(0)`
- Kiểm tra khởi tạo thành công không `cap.isOpened`
- Đọc tưng frame:` ret, frame = cap.read()`
    - `ret - True / False`: đọc thành công không
    - `frame`: ảnh
- Giải phóng camera và đóng window
    - `cv2.release()`
    - `cv2.destroyAllWindows()`
- Property: dùng hàm` cap.get(flag) or cap.set(flag)`
    - `cv2.CAP_RPOP_FRAME_WIDTH`
    - `cv2.CAP_PROP_FRAME_HEIGHT`
    - `cv2.CAP_PROP_FPS`
    - `cv2.CAP_PROP_POS_FRAME`
- Ghi video:
    - Định nghĩa Fourcc - Four character code: XVID/MJPG/DIVX/X264
        - `fourcc = cv2.VideoWriter_fourcc(*”XVID”)`
    - Khởi tạo class ghi:
        - `out = cv.VideoWriter(filename, fourcc, fps, frame_size)`
        - `out.write(frame)` : frame phải có size giống size đã khởi tạo, nếu không thì phải resize trước , ==size - WxH==
