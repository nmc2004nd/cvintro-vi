"""Thêm mục lục sổ xuống vào thanh điều hướng và sửa nút "tiếp" của trang trắc nghiệm.

- Mọi trang (trừ index.html) có nút "Các bài" trên thanh điều hướng: danh sách tất cả bài học
  theo từng phần (lấy từ index.html), kèm link trắc nghiệm nếu có.
- Trang bài học có thêm nút "Trong bài này": các mục (h2) của bài.
- Trang trắc nghiệm Bài N: nút "tiếp" dẫn sang lý thuyết Bài N+1 (thay vì trắc nghiệm Bài N+1).

Chạy lại bao nhiêu lần cũng được (phần chèn nằm giữa marker <!-- site-toc:begin/end -->).
build_opencv_notes.py gọi add_toc() cho opencv-notes.html, nên chạy script đó trước hoặc sau đều được.

    python3 tools/build_nav.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = ROOT / "lessons"
QUIZZES_DIR = ROOT / "quizzes"

TOC_RE = re.compile(r"[ \t]*<!-- site-toc:begin -->.*?<!-- site-toc:end -->\n", re.S)
NAV_LINKS = '<ul class="nav-links">\n'

SCRIPT = """<script>
document.addEventListener('click', function (e) {
    document.querySelectorAll('.site-toc[open]').forEach(function (d) {
        if (!d.contains(e.target) || e.target.closest('.site-toc-panel a')) d.removeAttribute('open');
    });
});
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') document.querySelectorAll('.site-toc[open]').forEach(function (d) { d.removeAttribute('open'); });
});
document.querySelectorAll('.site-toc').forEach(function (d) {
    d.addEventListener('toggle', function () {
        if (!d.open) return;
        document.querySelectorAll('.site-toc[open]').forEach(function (o) { if (o !== d) o.removeAttribute('open'); });
        var cur = d.querySelector('.current');
        if (cur) cur.scrollIntoView({block: 'center'});
    });
});
</script>"""


def load_parts():
    """[(tên phần, [(file lesson, tiêu đề)])] theo thứ tự trong index.html."""
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    parts = []
    for m in re.finditer(r"<h2>(Phần[^<]*)</h2>(.*?)</ul>", page, re.S):
        lessons = re.findall(r'href="lessons/([^"]+)\.html" class="lesson-link"><span class="lesson-title">(.*?)</span>', m.group(2))
        parts.append((m.group(1), lessons))
    return parts


def lesson_number(stem):
    return int(re.match(r"lesson(\d+)", stem).group(1))


def quiz_stem(n):
    stem = f"quiz{n:02d}"
    return stem if (QUIZZES_DIR / f"{stem}.html").exists() else None


def strip_tags(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).replace("¶", "").strip()


def lesson_sections(page):
    items = []
    for m in re.finditer(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', page, re.S):
        items.append(f'<li><a href="#{m.group(1)}">{html.escape(strip_tags(m.group(2)))}</a></li>')
    return items


def build_toc(parts, prefix, current=None, page=None):
    """prefix: "" cho trang ở gốc, "../" cho lessons/ và quizzes/. current: stem lesson/quiz đang xem."""
    rows = []
    for title, lessons in parts:
        rows.append(f'<li class="site-toc-part">{title}</li>')
        for stem, lesson_title in lessons:
            n = lesson_number(stem)
            quiz = quiz_stem(n)
            cls = ' class="current"' if current in (stem, quiz) else ""
            quiz_link = (f' <a class="site-toc-quiz" href="{prefix}quizzes/{quiz}.html" title="Trắc nghiệm Bài {n}">TN</a>'
                         if quiz else "")
            rows.append(f'<li{cls}><a href="{prefix}lessons/{stem}.html">{lesson_title}</a>{quiz_link}</li>')
    rows.append(f'<li class="site-toc-part"><a href="{prefix}opencv-notes.html">Ghi chú OpenCV</a> &middot; '
                f'<a href="{prefix}references.html">Tài liệu tham khảo</a></li>')

    items = [
        '<li><details class="site-toc">'
        '<summary>&#9776; Các bài</summary>'
        '<div class="site-toc-panel"><ul>\n' + "\n".join(rows) + '\n</ul></div></details></li>'
    ]
    if page is not None:
        sections = lesson_sections(page)
        if sections:
            items.append(
                '<li><details class="site-toc">'
                '<summary>&sect; Trong bài này</summary>'
                '<div class="site-toc-panel"><ul>\n' + "\n".join(sections) + '\n</ul></div></details></li>'
            )
    return "                <!-- site-toc:begin -->\n" + "\n".join(items) + "\n" + SCRIPT + "\n<!-- site-toc:end -->\n"


def add_toc(page, parts, prefix, current=None, with_sections=False):
    page = TOC_RE.sub("", page)
    pos = page.index(NAV_LINKS) + len(NAV_LINKS)
    toc = build_toc(parts, prefix, current, page if with_sections else None)
    return page[:pos] + toc + page[pos:]


def fix_quiz_next(page, n, parts):
    titles = {stem: t for _, lessons in parts for stem, t in lessons}
    nxt = next((s for s in titles if lesson_number(s) == n + 1), None)
    if nxt is None:
        return page
    link = (f'<div class="lesson-nav-next"><a href="../lessons/{nxt}.html">'
            f'Lý thuyết {titles[nxt]} &rarr;</a></div>')
    return re.sub(r'<div class="lesson-nav-next">.*?</div>', lambda _: link, page, count=1)


def write(path, old, new):
    if new != old:
        path.write_text(new, encoding="utf-8")
        print("cập nhật", path.relative_to(ROOT))


def main():
    parts = load_parts()
    for path in sorted(LESSONS_DIR.glob("*.html")):
        page = path.read_text(encoding="utf-8")
        write(path, page, add_toc(page, parts, "../", path.stem, with_sections=True))
    for path in sorted(QUIZZES_DIR.glob("quiz*.html")):
        page = path.read_text(encoding="utf-8")
        n = int(path.stem[4:])
        write(path, page, fix_quiz_next(add_toc(page, parts, "../", path.stem), n, parts))
    for name in ("references.html", "opencv-notes.html"):
        path = ROOT / name
        page = path.read_text(encoding="utf-8")
        write(path, page, add_toc(page, parts, ""))


if __name__ == "__main__":
    main()
