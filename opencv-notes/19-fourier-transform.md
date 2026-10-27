---
title: 19. Fourier Transform
lesson: lesson15_fourier_frequency_filtering
after:
draft: true
---
| Hàm | Ý nghĩa |
|---|---|
| `np.fft.fft2()` / `np.fft.ifft2()` | Biến đổi Fourier 2D thuận / ngược của NumPy, trả về số phức |
| `np.fft.fftshift()` / `np.fft.ifftshift()` | Đưa thành phần tần số 0 (DC) vào giữa phổ / trả về góc trên trái |
| `cv.dft()` / `cv.idft()` | Biến đổi Fourier của OpenCV, nhanh hơn NumPy, kết quả 2 kênh (thực, ảo) |
| `cv.magnitude()` | Độ lớn $\sqrt{Re^2 + Im^2}$ |
| `cv.getOptimalDFTSize()` | Kích thước tối ưu để DFT chạy nhanh |

- Ảnh có thể xem là tín hiệu lấy mẫu theo hai chiều → DFT 2D cho biết ảnh gồm những ==tần số== nào
    - Biên, nhiễu: pixel thay đổi đột ngột → ==tần số cao==
    - Vùng phẳng, mảng màu: thay đổi chậm → ==tần số thấp==
    - FFT (Fast Fourier Transform) là thuật toán nhanh để tính DFT

    :::proof DFT, dịch phổ về giữa và định lý tích chập
    **Định nghĩa DFT 2D** của ảnh $f$ kích thước $M \times N$:

    $$F(u, v) = \sum_{x=0}^{M-1}\sum_{y=0}^{N-1} f(x, y)\, e^{-2\pi i\left(\frac{ux}{M} + \frac{vy}{N}\right)}$$

    Mỗi $F(u, v)$ là một số phức $= |F|e^{i\phi}$: **độ lớn** $|F| = \sqrt{\text{Re}^2 + \text{Im}^2}$ cho biết sóng tần số $(u, v)$ mạnh đến đâu, **pha** $\phi$ cho biết sóng đó lệch vị trí ra sao.

    **1. Vì sao phải lấy log khi hiển thị.** Thay $u = v = 0$: $F(0, 0) = \sum f(x, y)$ = tổng mọi pixel (thành phần DC). Ảnh 512x512 trung bình 128 cho $F(0,0) \approx 3.4 \times 10^7$, trong khi các tần số cao thường chỉ cỡ $10^2$–$10^4$. Hiển thị tuyến tính thì chỉ thấy một chấm sáng ở DC; log nén dải này lại. (Dùng `np.log(1 + |F|)` để tránh $\log 0$.)

    **2. `fftshift` = nhân ảnh với $(-1)^{x+y}$.** Vì $e^{i\pi} = -1$:

    $$(-1)^{x+y} = e^{i\pi(x+y)} = e^{2\pi i\left(\frac{(M/2)x}{M} + \frac{(N/2)y}{N}\right)}$$

    Nhân $f$ với hàm mũ này rồi lấy DFT, số mũ cộng vào số mũ trong định nghĩa, cho $F(u - M/2,\ v - N/2)$: phổ bị dịch đi nửa kích thước, đưa DC từ góc vào giữa (với $M, N$ chẵn). Vì DFT tuần hoàn chu kỳ $M, N$, dịch nửa chu kỳ chính là hoán đổi bốn góc phần tư – đúng những gì `fftshift` làm.

    **3. Định lý tích chập – lý do lọc trong miền tần số được.** Chứng minh cho 1D (2D làm y hệt theo từng chiều), với tích chập vòng $(f \circledast g)[n] = \sum_m f[m]\,g[(n - m) \bmod N]$:

    $$\mathcal{F}\{f \circledast g\}[k] = \sum_n \sum_m f[m]\,g[n - m]\,e^{-2\pi i kn/N} = \sum_m f[m]\,e^{-2\pi i km/N} \sum_n g[n - m]\,e^{-2\pi i k(n-m)/N}$$

    (tách $e^{-2\pi i kn/N} = e^{-2\pi i km/N} \cdot e^{-2\pi i k(n-m)/N}$). Tổng bên trong chạy qua mọi $n$, nên $n' = n - m$ cũng chạy qua đủ một chu kỳ, và bằng $G[k]$. Vậy

    $$\mathcal{F}\{f \circledast g\} = F \cdot G \qquad \blacksquare$$

    Tích chập (tốn $O(N^2)$ với kernel lớn) trở thành **phép nhân từng phần tử** trong miền tần số, cộng hai lần FFT $O(N\log N)$. Đặt một vùng của phổ về 0 (như HPF ở dưới) chính là nhân với mặt nạ $G \in \{0, 1\}$, tương đương tích chập ảnh với $g = \mathcal{F}^{-1}\{G\}$.

    **4. Vì sao mặt nạ chữ nhật gây gợn sóng (ringing).** Biến đổi ngược của một hình chữ nhật là hàm sinc $\frac{\sin x}{x}$, có nhiều vòng dao động. Lọc bằng mặt nạ chữ nhật = tích chập ảnh với sinc, nên quanh mỗi cạnh xuất hiện các vân lặp lại. Dùng mặt nạ Gauss (biến đổi của Gauss vẫn là Gauss, không dao động) thì hết gợn.
    :::

- **Fourier bằng NumPy**
    - `f = np.fft.fft2(img)`: kết quả phức, thành phần DC nằm ở góc trên trái
    - `fshift = np.fft.fftshift(f)`: dịch DC vào giữa ảnh phổ, dễ quan sát
    - Phổ biên độ: `20 * np.log(np.abs(fshift))`, lấy log vì giá trị chênh nhau rất lớn

    ```python
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift))
    ```

    - ==Lọc thông cao (HPF)==: xóa vùng tần số thấp ở giữa phổ rồi biến đổi ngược

    ```python
    rows, cols = img.shape
    crow, ccol = rows // 2, cols // 2
    fshift[crow - 30:crow + 31, ccol - 30:ccol + 31] = 0     # bỏ tần số thấp
    f_ishift = np.fft.ifftshift(fshift)                      # trả DC về góc
    img_back = np.real(np.fft.ifft2(f_ishift))               # lấy phần thực
    ```

    - Kết quả HPF giữ lại biên → ==HPF là một bộ phát hiện biên==
- **Fourier bằng OpenCV**
    - Ảnh đầu vào phải chuyển sang `np.float32`
    - `flags=cv.DFT_COMPLEX_OUTPUT` → kết quả có 2 kênh: phần thực `[:, :, 0]` và phần ảo `[:, :, 1]`

    ```python
    dft = cv.dft(np.float32(img), flags=cv.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude_spectrum = 20 * np.log(cv.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))
    ```

    - Có thể dùng `cv.cartToPolar()` để lấy cả độ lớn và pha cùng lúc
    - ==Lọc thông thấp (LPF)==: tạo mask giữ vùng giữa (tần số thấp), xóa phần còn lại → ảnh bị làm mờ

    ```python
    mask = np.zeros((rows, cols, 2), np.uint8)               # 2 kênh giống dft
    mask[crow - 30:crow + 30, ccol - 30:ccol + 30] = 1

    fshift = dft_shift * mask
    img_back = cv.idft(np.fft.ifftshift(fshift))
    img_back = cv.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    ```

    ![](img/opencv-notes/19-fourier-transform-1.png)

    - ==Mask hình chữ nhật cắt đột ngột gây hiện tượng gợn sóng (ringing effect)== quanh biên → nên dùng mask Gauss để chuyển tiếp mượt
- **Tối ưu tốc độ**
    - DFT nhanh nhất khi kích thước là lũy thừa của 2, hoặc tích của các thừa số 2, 3, 5
    - `cv.getOptimalDFTSize(n)` trả về kích thước tối ưu ≥ n, sau đó đệm thêm số 0 bằng `cv.copyMakeBorder`
    - Theo tài liệu OpenCV: ảnh 342x548 đệm lên 360x576 thì DFT nhanh hơn khoảng 4 lần; `cv.dft` nhanh hơn `np.fft.fft2` khoảng 3 lần

    ```python
    nrows = cv.getOptimalDFTSize(rows)
    ncols = cv.getOptimalDFTSize(cols)
    nimg = cv.copyMakeBorder(img, 0, nrows - rows, 0, ncols - cols, cv.BORDER_CONSTANT, value=0)
    ```

- **Vì sao Laplacian là HPF, lọc trung bình là LPF?**
    - Lấy FFT của chính kernel rồi xem phổ:
        - Kernel trung bình, Gauss: phổ sáng ở giữa → chỉ cho tần số thấp đi qua → LPF
        - Laplacian: phổ tối ở giữa, sáng ở rìa → HPF
        - Sobel x: chặn tần số theo trục x thấp, cho qua tần số cao theo x → tìm cạnh dọc
    - ==Ứng dụng:==
        - ==Hiểu và thiết kế bộ lọc trong miền tần số==
        - ==Tích chập kernel lớn nhanh hơn bằng nhân trong miền tần số== (định lý tích chập)
        - ==Khử nhiễu có chu kỳ (sọc, lưới) bằng cách xóa các đỉnh tương ứng trong phổ==
