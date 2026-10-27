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

        :::proof tái tạo chính xác từ kim tự tháp Laplace
        **Khẳng định:** từ các tầng $L_0, L_1, \dots, L_{n-1}$ và tầng Gauss nhỏ nhất $G_n$, ta khôi phục **chính xác** ảnh gốc $G_0$:

        $$G_i = L_i + \text{pyrUp}(G_{i+1}), \quad i = n-1, \dots, 0$$

        **Chứng minh.** Chỉ là chuyển vế định nghĩa $L_i = G_i - \text{pyrUp}(G_{i+1})$. Bắt đầu từ $G_n$ đã lưu, tính được $G_{n-1}$, rồi $G_{n-2}$, ..., cuối cùng $G_0$. Ghép lại (dạng "lồng nhau"):

        $$G_0 = L_0 + \text{pyrUp}\Big(L_1 + \text{pyrUp}\big(L_2 + \dots + \text{pyrUp}(G_n)\big)\Big) \qquad \blacksquare$$

        Điểm quan trọng: phép chứng minh **không cần** `pyrUp` là nghịch đảo của `pyrDown` (thực tế không phải). Thông tin bị mất khi thu nhỏ đã được cất sẵn trong $L_i$. Mình đã kiểm tra với 3 tầng trên ảnh `float32`: sai số tái tạo $6 \times 10^{-8}$ (chỉ là làm tròn số thực). Với ảnh `uint8` phải tính $L_i$ bằng kiểu có dấu (`float32` hoặc `int16`) vì $L_i$ có giá trị âm.

        **Tổng dung lượng:** mỗi tầng có $1/4$ số pixel của tầng trước:

        $$1 + \frac14 + \frac1{16} + \dots < \frac{1}{1 - 1/4} = \frac43$$

        Cả kim tự tháp chỉ tốn thêm chưa tới 33% so với ảnh gốc.

        **Vì sao phải lọc Gauss trước khi bỏ hàng/cột.** Bỏ một nửa số mẫu thì tần số cao nhất biểu diễn được giảm từ $\pi$ xuống $\pi/2$ (rad/pixel). Thành phần nào cao hơn $\pi/2$ sẽ "gập" lại thành tần số thấp giả (**aliasing** – răng cưa, vân moiré). Kernel của `pyrDown` là $\frac{1}{16}[1, 4, 6, 4, 1]$ theo mỗi chiều, và

        $$\tfrac{1}{16}[1, 4, 6, 4, 1] = \tfrac14[1, 2, 1] * \tfrac14[1, 2, 1]$$

        Đáp ứng tần số của $\frac14[1, 2, 1]$ là $\frac14(2 + e^{i\omega} + e^{-i\omega}) = \frac{1 + \cos\omega}{2} = \cos^2\frac{\omega}{2}$, nên kernel 5 điểm có đáp ứng $H(\omega) = \cos^4\frac{\omega}{2}$: bằng 1 ở $\omega = 0$ (giữ độ sáng), bằng 0 ở $\omega = \pi$, và $H(\pi/2) = 1/4$ – các tần số sẽ bị gập đã bị dập phần lớn.

        **Vì sao `pyrUp` nhân kernel với 4.** `pyrUp` chèn số 0 vào giữa các pixel (gấp đôi mỗi chiều), nên 3/4 số pixel bằng 0 và độ sáng trung bình giảm 4 lần. Kernel làm mờ có tổng 1 giữ nguyên trung bình, nên phải nhân 4 để trả lại độ sáng cũ.
        :::

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

            :::proof vì sao ghép theo từng tầng thì không lộ vết cắt
            Phần này là giải thích (theo Burt & Adelson, 1983) chứ không phải chứng minh chặt.

            - Ghép mỗi tầng $L_i$ bằng mặt nạ $M_i$ (mặt nạ đã thu nhỏ theo kim tự tháp Gauss): $L_i^{AB} = M_i L_i^A + (1 - M_i) L_i^B$. Mặt nạ ở tầng $i$ bị làm mờ ở tỉ lệ $2^i$, nên **vùng chuyển tiếp rộng khoảng $2^i$ pixel** (tính theo ảnh gốc).
            - Tầng $i$ chủ yếu chứa chi tiết có kích thước cỡ $2^i$ pixel. Vậy mỗi dải tần được trộn qua một vùng chuyển tiếp **vừa với kích thước của chính nó**:
                - Tần số thấp (màu nền, độ sáng chung) trộn qua vùng rộng → không có bậc sáng tối đột ngột.
                - Tần số cao (vân, chi tiết nhỏ) trộn qua vùng hẹp → không bị bóng ma hai lớp chồng lên nhau.
            - Ghép thẳng bằng `hstack` tương đương dùng vùng chuyển tiếp rộng 0 cho mọi tần số → vết cắt lộ rõ. Ngược lại, trộn tuyến tính toàn ảnh với một vùng chuyển tiếp rộng cố định thì chi tiết nhỏ ở vùng đó thành hai lớp chồng mờ.

            Tái tạo từ các tầng đã ghép dùng đúng công thức $G_i = L_i + \text{pyrUp}(G_{i+1})$ đã chứng minh ở trên.
            :::

        - **Khôi phục ảnh** bằng cách bắt đầu từ tầng Gaussian nhỏ nhất đã ghép, sau đó lặp lại:
            1. `pyrUp()`
            2. cộng với Laplacian đã ghép ở tầng tương ứng.
        - Lặp cho đến khi trở về kích thước ban đầu để thu được ảnh blend mượt, không xuất hiện đường nối rõ như khi ghép trực tiếp.
        - Lý do vết nối mượt: mỗi dải tần số được trộn ở đúng tỷ lệ của nó. Thành phần tần số thấp (màu sắc, độ sáng ở tầng Gaussian nhỏ nhất) được trộn trên một vùng chuyển tiếp rộng, còn chi tiết tần số cao (các tầng Laplacian lớn) được trộn trên vùng hẹp nên vẫn sắc nét
