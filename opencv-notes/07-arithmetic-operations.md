---
title: 7. Arithmetic Operations
lesson: lesson02_image_arithmetic
after:
---
- Cộng ảnh
    - Dùng `cv2.add` nếu value mới lớn hơn 255 sẽ bão hòa về 255
    - Dùng `x+y` nếu value mới lớn hơn 255 thì sẽ tràn số `(x + y) % 256`

    ```python
    x = np.uint8([[250]])
    y = np.uint8([[10]])
    # [] not image scalar: [[]]: image 1 pixel, 1 channel, uint8

    print("Cộng bằng OpenCV:", cv2.add(x, y))
    # Kết quả sẽ là 255 (bão hòa)
    print("Cộng bằng NumPy:", x + y)
    # Kết quả sẽ là 4 (tràn số) : 260 mod 256 = 4
    ```

- Trừ ảnh
    - Dùng `cv2.subtract` nếu value mới nhỏ hơn 0 thì sẽ bão hòa về 0
    - Dùng`x-y` nếu value mới nhỏ hơn 0 thì sẽ tràn số `(x - y) % 256`

    ```python
    x = np.uint8([[50]])
    y = np.uint8([[100]])

    print("Trừ bằng OpenCV:", cv2.subtract(x, y))
    # Kết quả sẽ là 0 (bão hòa)
    print("Trừ bằng NumPy:", x - y)
    # Kết quả sẽ là 206 (tràn số)  : 50 - 100 mod 256 = 206
    ```

- Nhân ảnh
    - Dùng `cv2.multiply` nếu value mới lớn hơn 255 thì sẽ bão hòa về 255
    - Dùng `x*y` nếu value mới lớn hơn 255 thì sẽ tràn số `(x * y) % 256`

    ```python
    print("Nhân bằng OpenCV:", cv2.multiply(x, y))
    # Kết quả sẽ là 255 (bão hòa)
    print("Nhân bằng NumPy:", x * y)
    # Kết quả sẽ là 136 (tràn số): 50 * 100 = 5000, 5000 mod 256 = 136
    ```

- Trộn hai ảnh với nhau
    - $g(x) = (1 - \alpha) f_0(x) + \alpha f_1(x)$

        :::proof trộn ảnh không bị tràn số
        **Khẳng định:** nếu $0 \le \alpha \le 1$ và $f_0(x), f_1(x) \in [0, 255]$ thì $g(x) \in [\min(f_0, f_1), \max(f_0, f_1)] \subseteq [0, 255]$.

        **Chứng minh.** Đặt $a = \min(f_0(x), f_1(x))$, $b = \max(f_0(x), f_1(x))$. Vì $1 - \alpha \ge 0$ và $\alpha \ge 0$:

        $$g(x) = (1-\alpha) f_0(x) + \alpha f_1(x) \ge (1-\alpha)a + \alpha a = a$$

        $$g(x) \le (1-\alpha) b + \alpha b = b$$

        Vậy $g$ luôn nằm giữa hai giá trị gốc (đây là một *tổ hợp lồi*), không thể vượt 255 hay xuống dưới 0. $\blacksquare$

        - Hai hệ số có tổng $(1 - \alpha) + \alpha = 1$ là điều kiện then chốt. Với `addWeighted(img1, alpha, img2, beta, gamma)`, nếu `alpha + beta > 1` hoặc `gamma != 0` thì kết quả có thể vượt 255 và bị OpenCV bão hòa (kẹp về 255).
        - Độ sáng trung bình cũng trộn tuyến tính: $\overline{g} = (1-\alpha)\overline{f_0} + \alpha\overline{f_1}$ (lấy trung bình hai vế, phép trung bình là tuyến tính).
        - Hiệu ứng fade: cho $\alpha$ tăng đều từ 0 đến 1 theo thời gian, ảnh đi thẳng từ $f_0$ ($\alpha = 0$) sang $f_1$ ($\alpha = 1$).
        :::

    - Dùng hàm `cv2.addWeighted(img1, alpha, img2, beta, gamma)` = `img1*alpha + img2*beta + gamma`, để ra công thức trên thì` beta = 1 - alpha`
    - Hai ảnh `img1` và `img2` phải cùng kích thước và cùng số kênh
    - Dùng hàm `cv2.resize(img, (W, H))` - chú ý thứ tự (W, H) khác với `img.shape` là (H, W, D)
    - Có thể tạo hiệu ứng `Fade in Fade out` bằng cách đổi `alpha từ 0-1`
- Phép toán Bitwise cần ==mask==

| Hàm | Ý nghĩa |
|---|---|
| `cv.bitwise_and()` | Giữ lại vùng pixel thỏa mask hoặc vùng chung giữa hai ảnh. |
| `cv.bitwise_or()` | Gộp vùng pixel từ hai ảnh. |
| `cv.bitwise_not()` | Đảo ngược giá trị pixel hoặc mask. |
| `cv.bitwise_xor()` | Giữ vùng khác nhau giữa hai ảnh hoặc hai mask. |

- Ứng dụng
    1. Trích xuất một vùng ảnh bất kỳ.
    2. Làm việc với ROI không phải hình chữ nhật.
    3. Tạo mask cho vật thể có hình dạng phức tạp.
    4. Chèn logo hoặc đối tượng vào ảnh nền mà không làm biến đổi màu sắc.
- Phân tích ý tưởng chèn logo bằng mask:
    - Chuẩn bị ảnh logo
    - Chuẩn bị vùng ROI trong ảnh có kích thước bằng kích thước ảnh logo
    - Mục tiêu là:
        - Vùng ROI: nền giữ nguyên và vùng logo bị mask thành đen - inv_mask
        - Vùng Logo: nền bị mask thành đen và logo giữ nguyên - mask
        - Sau đó dùng `add` hai vùng với nhau sẽ thu được vùng mới có nền ảnh gốc và logo là logo cần chèn
    - Chuẩn bị mask: chuyển ảnh logo sang `grayscale` và dùng `threshold` để tách ngưỡng
    - Inv_mask được chuẩn bị bằng `bitwise_not(mask)`
    - Sau khi bitwise hai vùng xong ta thế vùng mới vào ảnh gốc là xong
