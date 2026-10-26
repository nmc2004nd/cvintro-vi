# Nhập môn Thị giác Máy tính — Bản dịch tiếng Việt (không chính thức)

Bản dịch tiếng Việt **không chính thức** của
**[Introduction to Computer Vision — Lecture notes with working Python code](https://sbirchfield.github.io/cvintro/index.html)**
của tác giả **Stan Birchfield**.

📖 **Đọc online:** <https://nmc2004nd.github.io/cvintro-vi/>

## Nội dung

61 bài học, chia thành 4 phần:

| Phần | Chủ đề | Bài |
|---|---|---|
| 1 | Xử lý ảnh 2D cổ điển | 1–19 |
| 2 | Thị giác máy tính 3D cổ điển | 20–29 |
| 3 | Học sâu cho thị giác máy tính | 30–44 |
| 4 | Transformer và mô hình nền tảng *(bản gốc vẫn đang là bản nháp)* | 45–61 |

Cấu trúc repo:

- `index.html` — mục lục.
- `lessons/` — 61 trang bài học: phần giải thích đã dịch sang tiếng Việt; code Python, hình ảnh, ảnh động, công thức và kết quả chạy giữ nguyên như bản gốc.
- `notebooks/` — 61 notebook Jupyter đã dịch phần markdown (comment trong code giữ nguyên tiếng Anh). Chạy được trực tiếp, dữ liệu ảnh nằm trong `img/`.
- `quizzes/` — 44 bài trắc nghiệm (176 câu hỏi) đã dịch.
- `references.html` — tài liệu tham khảo (giữ nguyên trích dẫn gốc).
- `animations/`, `figures/`, `img/`, `css/` — tài nguyên sao chép từ bản gốc.

Quy ước dịch: thuật ngữ chuyên ngành ghi kèm tiếng Anh ở lần đầu xuất hiện, ví dụ "tích chập (convolution)"; tên riêng, thư viện, mô hình (OpenCV, PyTorch, ViT, DINO, SAM...) giữ nguyên.

## Đọc offline

```bash
git clone https://github.com/nmc2004nd/cvintro-vi.git
cd cvintro-vi
python3 -m http.server 3000
```

Mở <http://localhost:3000>.

## Nguồn gốc, bản quyền và giấy phép

- **Tác giả gốc:** Stan Birchfield. Toàn bộ nội dung chuyên môn, code, hình ảnh và ảnh động thuộc về tác giả.
- **Trang gốc:** <https://sbirchfield.github.io/cvintro/> — mã nguồn: <https://github.com/sbirchfield/sbirchfield.github.io>
- **Sách gốc:** Stan Birchfield, *Introduction to Computer Vision: Lecture Notes with Working Python Code*, arXiv:[2609.39627](https://arxiv.org/abs/2609.39627), phát hành theo giấy phép [**CC BY 4.0**](https://creativecommons.org/licenses/by/4.0/).
- **Thay đổi so với bản gốc:** phần văn bản (giải thích, tiêu đề, trắc nghiệm, giao diện) được dịch sang tiếng Việt; bố cục trang được điều chỉnh để chạy độc lập. Không thay đổi nội dung kỹ thuật, code hay kết quả.
- Bản dịch được phát hành theo cùng giấy phép **CC BY 4.0** (xem [LICENSE](LICENSE)).

Bản dịch được thực hiện cho mục đích học tập, phi thương mại, với lòng biết ơn tác giả đã chia sẻ tài liệu. Mọi sai sót trong bản dịch là của người dịch, không phải của tác giả. **Nếu tác giả có bất kỳ yêu cầu nào (chỉnh sửa, ghi công khác, hoặc gỡ bỏ), vui lòng mở một [Issue](https://github.com/nmc2004nd/cvintro-vi/issues) — người dịch sẽ thực hiện ngay.**

## Ghi chú OpenCV

Ngoài bản dịch, repo có thêm ghi chú cá nhân dựa trên tài liệu [OpenCV-Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html). Phần này **không** thuộc bản gốc.

- Nguồn: `opencv-notes/*.md`, mỗi file là một chủ đề. Phần đầu file khai báo `lesson` (bài học để chèn vào) và `after` (một đoạn chữ trong heading; ghi chú nằm ở cuối mục đó, để trống thì nằm trước phần Bài tập).
- Cú pháp Markdown thông thường, thêm `==chữ==` để tô đỏ nhấn mạnh và `$...$`, `$$...$$` cho công thức.
- Ảnh đặt trong `img/opencv-notes/`. Hình minh họa của các ghi chú 18-40 được tạo bằng `tools/make_opencv_note_figures.py` (cần OpenCV 4.x bản contrib, vì OpenCV 5 không còn `CascadeClassifier` và `cv.ml`).
- Ghi chú có dòng `draft: true` hiển thị nhãn "Bản nháp – chưa review" (do AI soạn theo tài liệu OpenCV). Xóa dòng đó sau khi đã đọc lại.
- Sau khi sửa, chạy `python3 tools/build_opencv_notes.py` để chèn lại vào các bài và cập nhật `opencv-notes.html` (cần `markdown` và `pygments`).

## Trích dẫn

Nếu thấy tài liệu hữu ích, vui lòng trích dẫn **bản gốc**:

```bibtex
@misc{birchfield2026cvintro,
  author        = {Birchfield, Stan},
  title         = {Introduction to Computer Vision: Lecture Notes with Working {P}ython Code},
  year          = {2026},
  eprint        = {2609.39627},
  archivePrefix = {arXiv},
  url           = {https://arxiv.org/abs/2609.39627},
}
```

## Góp ý

Phát hiện lỗi dịch hoặc câu chữ khó hiểu? Hãy mở Issue hoặc Pull Request.
