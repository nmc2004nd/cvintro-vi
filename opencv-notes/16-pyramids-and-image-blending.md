---
title: 16. Pyramids and Image Blending
lesson: lesson13_laplacian_pyramids
after:
---
| Tên hàm OpenCV | Bản chất phép toán | Tác động lên lưới pixel |
|---|---|---|
| `cv.pyrDown(src)` | Lọc Gaussian → bỏ các hàng/cột xen kẽ. | Thu nhỏ: giảm chiều rộng và chiều cao đi một nửa, tức còn 1/4 diện tích. |
| `cv.pyrUp(src)` | Chèn thêm hàng/cột toàn 0 → lọc Gaussian để nội suy. | Phóng to: nhân đôi chiều rộng và chiều cao, tức tăng 4 lần diện tích. Ảnh bị mờ nhẹ. |

- Vấn đề là nếu chỉ làm việc với ảnh có kích thước cố định thì trong bài toán nhận diện vật thể qua camera mà không thể biết được vật cần nhận diện xuất hiện với kích thước như thế nào
- Giải pháp:
    - Dùng Pyramids tạo ra tập hợp các ảnh giống nhau có độ phân giải giảm dần, xếp chồng lên nhau
    - Ảnh gốc có độ phân giải cao nhất nằm ở đáy
    - Ảnh nhỏ nhất nằm ở đỉnh
- Có hai loại Pyramids:
    - ==Gaussian Pyramid==
    - ==Laplacian Pyramid==
- ==**Gaussian Pyramid**==
    - Mỗi tầng được tạo từ tầng ngay dưới nó (lớn hơn) bằng cách lọc Gaussian rồi bỏ xen kẽ hàng và cột
    - Ban đầu MxN → $\frac{M}{2} \times \frac{N}{2}$
    - `cv.pyrDown()`: Thu nhỏ ảnh xuống một tầng, giảm 4 lần diện tích.
    - `cv.pyrUp()`: Phóng to ảnh lên một tầng, tăng 4 lần diện tích.
    - Lưu ý do khi DownSample thì các chi tiết có tần số cao có thể biến mất vĩnh viễn và phép phóng to chỉ là phép nội suy làm mờ ảnh
- ==**Laplacian Pyramid**==
    - Công thức xây dựng một tầng của Laplacian:
        - $L_i = G_i - \text{pyrUp}(G_{i+1})$
    - Ý nghĩa
        - $G_i$ tầng còn giữ được phần nào các chi tiết có tần số cao
        - $G_{i+1}$ là downSample của $G_i$ và đã mất đi vĩnh viễn các chi tiết có tần số cao
        - $\text{pyrUp}(G_{i+1})$ là nội suy làm mờ ảnh ngược lại về $G'_i$ đã không còn các chi tiết tần số cao
        - $L_i$ là hiệu giữa $G_i$ và $G'_i$ giữ lại các chi tiết có tần số cao khi DownSample bị mất
- ==**Image Blending**==
    - Vấn đề nếu ghép ảnh trực tiếp bằng hàm `np.hstack` thì ranh giới vết cắt sẽ bị gãy đột ngột tạo cảm giác rất giả và lộ vết cắt

    ![](img/opencv-notes/16-pyramids-and-image-blending-1.png)

    - Ý tưởng là:

        ![](img/opencv-notes/16-pyramids-and-image-blending-2.png)

        - Gaussian Pyramid lưu **thành phần tần số thấp** (ảnh ngày càng mờ sau mỗi lần Downsample).
        - Laplacian Pyramid lưu **các chi tiết/tần số cao bị mất** khi Downsample.
        - Tính Gaussian Pyramid và Laplacian Pyramid cho **cả hai ảnh**.
        - Ghép (blend) các tầng **Laplacian** của hai ảnh (ví dụ: nửa trái từ ảnh A, nửa phải từ ảnh B) và ghép cả tầng Gaussian nhỏ nhất.
        - **Khôi phục ảnh** bằng cách bắt đầu từ tầng Gaussian nhỏ nhất đã ghép, sau đó lặp lại:
            1. `pyrUp()`
            2. cộng với Laplacian đã ghép ở tầng tương ứng.
        - Lặp cho đến khi trở về kích thước ban đầu để thu được ảnh blend mượt, không xuất hiện đường nối rõ như khi ghép trực tiếp.
        - Lý do vết nối mượt: mỗi dải tần số được trộn ở đúng tỷ lệ của nó. Thành phần tần số thấp (màu sắc, độ sáng ở tầng Gaussian nhỏ nhất) được trộn trên một vùng chuyển tiếp rộng, còn chi tiết tần số cao (các tầng Laplacian lớn) được trộn trên vùng hẹp nên vẫn sắc nét
