---
title: 13. Morphological Transform
lesson: lesson03_thresholding_morphology
after:
---
- Các phép hình thái học: ==Erosion, dilation, opening, closing, morphological gradient, top hat, black hat.==
- Tổng quan:

| Phép toán | Công thức | Hàm OpenCV | Ứng dụng |
|---|---|---|---|
| Erosion | Bào mòn vùng trắng | `cv.erode()` | Xóa nhiễu trắng nhỏ, tách vật thể dính nhau. |
| Dilation | Giãn nở vùng trắng | `cv.dilate()` | Nối nét đứt, làm dày vật thể. |
| Opening | Erosion rồi Dilation | `cv.MORPH_OPEN` | Xóa nhiễu trắng nhỏ. |
| Closing | Dilation rồi Erosion | `cv.MORPH_CLOSE` | Lấp lỗ đen nhỏ. |
| Gradient | Dilation(A)−Erosion(A) | `cv.MORPH_GRADIENT` | Trích biên vật thể. |
| Top Hat | A−Opening(A) | `cv.MORPH_TOPHAT` | Trích chi tiết sáng nhỏ. |
| Black Hat | Closing(A)−A | `cv.MORPH_BLACKHAT` | Trích chi tiết tối nhỏ. |

- Yêu cầu hai thành phần đầu vào:
    - Ảnh đầu vào: ==Thường là ảnh nhị phân, vật thể tiền cảnh màu trắng và nền màu đen== (cũng áp dụng được cho ảnh xám)
    - Structuring kernel: Kernel áp dụng trên ảnh
- Quy ước xử lý:
    - ==Vật thể cần xử lý nên là màu trắng 255 hoặc 1==
    - ==Nền nên là màu đen==
- Chuẩn bị kernel
    - `kernel = np.ones((5, 5), np.uint8)`
    - `kernel = cv.getStructuringElement(shape, ksize)`
    - Các shape phổ biến:

        | Shape | Ý nghĩa | Cách chọn |
        |---|---|---|
        | `cv2.MORPH_RECT` | Kernel hình chữ nhật | Vật thể dạng khối, cạnh vuông |
        | `cv2.MORPH_ELLIPSE` | Kernel hình ellip hoặc hình tròn | Vật thể tròn, oval, lỗ tròn |
        | `cv2.MORPH_CROSS` | Kernel hình chữ thập | Khi muốn tác động theo hướng ngang dọc hơn là chéo |

- ==**Erosion - Phép bào mòn ảnh**==

    ![](img/opencv-notes/13-morphological-transform-1.png)

    ![](img/opencv-notes/13-morphological-transform-2.png)

    ```python
    kernel = np.ones((5, 5), np.uint8)
    erosion = cv.erode(img, kernel, iterations=1)
    ```

    - Thu hẹp vùng trắng trong ảnh
    - Cơ chế:
        - Kernel trượt qua từng vị trí trên ảnh
        - ==Pixel trung tâm giữ giá trị trắng nếu toàn bộ vùng dưới kernel đều là màu trắng==
        - ==Nếu có ít nhất một giá trị trong vùng kernel là đen, pixel trung tâm bị gán về đen==
    - Kết quả:
        - Vật thể trắng bị nhỏ lại
        - Biên vật thể bị bào mòn
        - Nhiễu trắng có thể bị loại bỏ
    - ==Ứng dụng:==
        - ==Xóa nhiễu trắng nhỏ==
        - ==Tách hai vật thể trắng đang dính sát nhau==
        - ==Làm mỏng vùng tiền cảnh==
- ==**Dilation - Phép giãn nở ảnh**==

    ![](img/opencv-notes/13-morphological-transform-3.png)

    ![](img/opencv-notes/13-morphological-transform-4.png)

    - `dilation = cv.dilate(src, kernel, iterations=1)`
    - Mở rộng vùng trắng trong ảnh
    - Cơ chế:
        - Kernel trượt qua từng vị trí trên ảnh
        - ==Pixel trung tâm được gán trắng nếu có ít nhất một pixel trong vùng kernel là trắng==
    - Kết quả:
        - Vật thể trắng lớn hơn
        - Biên vật thể dày hơn
        - Các khe hở hoặc đứt gãy nhỏ có thể được nối lại
    - ==Ứng dụng:==
        - ==Nối các vết đứt nhỏ==
        - ==Làm dày đường nét==
        - ==Khôi phục kích thước vật thể sau erosion==
- ==**Opening - Phép toán mở**==

    ![](img/opencv-notes/13-morphological-transform-5.png)

    ![](img/opencv-notes/13-morphological-transform-6.png)

    - **Opening là erosion trước, sau đó dilation**
    - $\text{Opening}(A)=\text{Dilation}(\text{Erosion}(A))$
    - `opening = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)`
    - ==Ý nghĩa:==
        - ==Erosion xóa nhiễu trắng nhỏ==
        - ==Dilation khôi phục lại kích thước tương đối của vật thể chính==
    - ==Ứng dụng:==
        - ==Loại bỏ nhiễu trắng nhỏ xung quanh vật thể==
        - ==Làm sạch ảnh nhị phân sau threshold==
- ==**Closing - Phép toán đóng**==

    ![](img/opencv-notes/13-morphological-transform-7.png)

    ![](img/opencv-notes/13-morphological-transform-8.png)

    - **Closing là dilation trước, sau đó erosion**
    - $\text{Closing}(A)=\text{Erosion}(\text{Dilation}(A))$
    - `closing = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)`
    - ==Ý nghĩa:==
        - ==Dilation lấp khe hở nhỏ hoặc lỗ đen nhỏ==
        - ==Erosion đưa vật thể về kích thước hợp lý hơn==
    - ==Ứng dụng:==
        - ==Lấp lỗ đen bên trong vật thể==
        - ==Nối các vùng trắng với nhau==
        - ==Xóa nhiễu đen nhỏ trên vật thể trắng==
- ==**Morphological Gradient**==

    ![](img/opencv-notes/13-morphological-transform-9.png)

    - **Morphological Gradient là hiệu giữa ảnh dilation và ảnh erosion**
    - $\text{Gradient}(A)=\text{Dilation}(A)-\text{Erosion}(A)$
    - `gradient = cv.morphologyEx(img, cv.MORPH_GRADIENT, kernel)`
    - ==Kết quả:==
        - ==Thường là đường viền của vật thể==
    - ==Ứng dụng:==
        - ==Trích biên ngoài của vật thể==
        - ==Làm nổi bật outline (đường viền) trong ảnh nhị phân==
- ==**Top Hat**==

    ![](img/opencv-notes/13-morphological-transform-10.png)

    - Làm việc với ảnh grayscale
    - ==Làm nổi bật part sáng trên nền tối==
    - **Top Hat là hiệu giữa ảnh gốc và ảnh sau opening**
    - $\text{TopHat}(A)=A-\text{Opening}(A)$

        ```python
        kernel_9x9 = np.ones((9, 9), np.uint8)
        tophat = cv.morphologyEx(img, cv.MORPH_TOPHAT, kernel_9x9)
        ```

    - ==Ứng dụng:==
        - ==Trích các chi tiết sáng nhỏ hơn kernel (opening xóa các chi tiết sáng nhỏ nên lấy ảnh gốc trừ đi sẽ còn lại đúng các chi tiết đó)==
        - ==Phát hiện đốm sáng trên nền có độ sáng không đồng đều==
        - ==Tăng cường chi tiết sáng nhỏ trên ảnh==
- ==**Black Hat**==

    ![](img/opencv-notes/13-morphological-transform-11.png)

    - Làm việc với ảnh grayscale
    - ==Làm nổi bật part tối trên nền sáng==
    - **Black Hat là hiệu giữa ảnh sau closing và ảnh gốc**
    - $\text{BlackHat}(A)=\text{Closing}(A)-A$
    - `blackhat = cv.morphologyEx(img, cv.MORPH_BLACKHAT, kernel)`
    - ==Ứng dụng:==
        - ==Trích các chi tiết tối nhỏ (closing lấp các lỗ đen nhỏ nên trừ đi ảnh gốc sẽ còn lại đúng các lỗ đó)==
        - ==Phát hiện vết nứt, lỗ thủng hoặc vùng tối trên nền vật thể sáng==
        - ==Làm nổi bật chi tiết tối trên nền không đồng đều==
