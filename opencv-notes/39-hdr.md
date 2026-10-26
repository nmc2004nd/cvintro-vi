---
title: 39. High Dynamic Range (HDR)
lesson: lesson26_image_formation
after:
draft: true
---
- Cảm biến 8-bit chỉ ghi được 256 mức sáng → cảnh có ==chênh lệch sáng tối lớn== (trong nhà nhìn ra cửa sổ) thì hoặc cháy vùng sáng, hoặc tối đen vùng tối
- HDR: chụp ==nhiều ảnh cùng khung hình với thời gian phơi sáng khác nhau==, ghép lại để giữ chi tiết cả vùng sáng lẫn vùng tối
- Hai hướng:

| Hướng | Thuật toán | Cần thời gian phơi sáng? | Kết quả |
|---|---|---|---|
| Ghép thành ảnh HDR rồi nén dải | `cv.createMergeDebevec()`, `cv.createMergeRobertson()` | Có | Ảnh HDR `float32` (độ rọi), phải tone mapping để hiển thị |
| Exposure fusion | `cv.createMergeMertens()` | ==Không== | Ảnh hiển thị được ngay, giá trị [0, 1] |

- **B1. Nạp ảnh và thời gian phơi sáng**

    ```python
    img_fn = ["img0.jpg", "img1.jpg", "img2.jpg", "img3.jpg"]
    img_list = [cv.imread(fn) for fn in img_fn]
    exposure_times = np.array([15.0, 2.5, 0.25, 0.0333], dtype=np.float32)   # giây
    ```

- **B2. Ghép thành ảnh HDR** (Debevec, Robertson)

    ```python
    merge_debevec = cv.createMergeDebevec()
    hdr_debevec = merge_debevec.process(img_list, times=exposure_times.copy())

    merge_robertson = cv.createMergeRobertson()
    hdr_robertson = merge_robertson.process(img_list, times=exposure_times.copy())
    ```

- **B3. Tone mapping**: nén ảnh HDR về [0, 1] để hiển thị

    ```python
    tonemap1 = cv.createTonemap(gamma=2.2)
    res_debevec = tonemap1.process(hdr_debevec.copy())
    ```

    - OpenCV còn có `createTonemapDrago`, `createTonemapReinhard`, `createTonemapMantiuk`
- **B4. Exposure fusion (Mertens)**: ==không cần thời gian phơi sáng, không cần tone mapping==; chọn pixel tốt ở mỗi ảnh theo độ tương phản, độ bão hòa và mức phơi sáng hợp lý

    ```python
    merge_mertens = cv.createMergeMertens()
    res_mertens = merge_mertens.process(img_list)
    ```

- **B5. Chuyển sang 8-bit để lưu**

    ```python
    res_debevec_8bit = np.clip(res_debevec * 255, 0, 255).astype("uint8")
    res_mertens_8bit = np.clip(res_mertens * 255, 0, 255).astype("uint8")
    cv.imwrite("fusion_mertens.jpg", res_mertens_8bit)
    ```

- **Ước lượng đường cong đáp ứng camera (CRF)**: ánh xạ độ rọi thật → giá trị pixel, thường phi tuyến

    ```python
    cal_debevec = cv.createCalibrateDebevec()
    crf_debevec = cal_debevec.process(img_list, times=exposure_times)
    hdr_debevec = merge_debevec.process(img_list, times=exposure_times.copy(), response=crf_debevec.copy())
    ```

![](img/opencv-notes/39-hdr-1.png)

- Hình trên là ==mô phỏng==: 4 mức phơi sáng được tạo từ một ảnh thường (không phải ảnh HDR thật), chỉ để minh họa Mertens fusion chọn vùng phơi sáng tốt từ mỗi ảnh
- ==Lưu ý:== các ảnh phải ==thẳng hàng== (dùng chân máy, hoặc căn chỉnh bằng `cv.createAlignMTB()`); vật chuyển động giữa các lần chụp gây bóng ma (ghosting)
- ==Ứng dụng:== ==chế độ HDR trên điện thoại, chụp nội thất, phong cảnh ngược sáng==
