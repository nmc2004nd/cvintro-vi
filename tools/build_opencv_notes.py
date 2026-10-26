"""Render các ghi chú OpenCV (opencv-notes/*.md) và chèn vào trang web.

- Mỗi file .md có phần đầu (front matter):
      title:  tiêu đề ghi chú
      lesson: tên file lesson (không có .html) để chèn vào; bỏ trống -> chỉ ở trang tổng hợp
      after:  một đoạn chữ trong heading của lesson; ghi chú được chèn ở cuối mục đó.
              Bỏ trống -> chèn ngay trước phần Bài tập (hoặc cuối bài).
      draft:  true -> gắn nhãn "Bản nháp – chưa review" (ghi chú do AI soạn, chưa được đọc lại).
              Xóa dòng này sau khi đã review.
- Kết quả:
      lessons/*.html     ô "Ghi chú OpenCV" nằm giữa hai marker <!-- opencv-note:begin/end -->
      opencv-notes.html  trang tổng hợp tất cả ghi chú

Chạy lại bao nhiêu lần cũng được: các ô cũ được xóa trước khi chèn lại.

    python3 tools/build_opencv_notes.py
"""
import html
import re
import xml.etree.ElementTree as etree
from pathlib import Path

import markdown
from markdown.inlinepatterns import InlineProcessor, SimpleTagInlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.util import AtomicString
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "opencv-notes"
LESSONS_DIR = ROOT / "lessons"
PAGE = ROOT / "opencv-notes.html"

BLOCK_RE = re.compile(r"<!-- opencv-note:begin [^>]*-->.*?<!-- opencv-note:end [^>]*-->\n", re.S)
CELL_START = '<div class="cell border-box-sizing'


# ---------- Markdown ----------

class MathProcessor(InlineProcessor):
    """Giữ nguyên $...$ / $$...$$ để MathJax xử lý (không để Markdown đụng vào \\, _, *)."""

    def handleMatch(self, m, data):
        el = etree.Element("span")
        if m.group(1):
            el.set("class", "math display")
            el.text = AtomicString("\\[" + m.group(1) + "\\]")
        else:
            el.set("class", "math")
            el.text = AtomicString("\\(" + m.group(2) + "\\)")
        return el, m.start(0), m.end(0)


class FencePreprocessor(Preprocessor):
    """Khối ```code``` ở mọi mức thụt lề (kể cả trong danh sách) -> HTML đã tô màu bằng Pygments.

    Extension fenced_code chuẩn của Python-Markdown không nhận khối code nằm trong danh sách.
    """

    FENCE = re.compile(r"^([ \t]*)```[ \t]*([\w+-]*)[ \t]*\n(.*?)^\1```[ \t]*$", re.M | re.S)

    def run(self, lines):
        text = "\n".join(lines)

        def repl(m):
            indent, lang, code = m.group(1), m.group(2), m.group(3)
            code = "\n".join(l[len(indent):] if l.startswith(indent) else l.lstrip() for l in code.split("\n"))
            lexer = get_lexer_by_name(lang) if lang else TextLexer()
            out = highlight(code.rstrip("\n") + "\n", lexer, HtmlFormatter(cssclass="highlight"))
            return indent + self.md.htmlStash.store(out)

        return self.FENCE.sub(repl, text).split("\n")


class LooseListPreprocessor(Preprocessor):
    """Chèn dòng trống trước mục danh sách thụt ra ngoài nếu mục con bên trên có dòng trống.

    Python-Markdown lồng sai mục đó vào danh sách con (ví dụ sau một công thức $$...$$ trong danh sách).
    """

    ITEM = re.compile(r"^( *)(?:[-*+]|\d+\.) ")

    def run(self, lines):
        out = []
        for line in lines:
            m = self.ITEM.match(line)
            if m and out and out[-1].strip():
                indent = len(m.group(1))
                prev_indent = len(out[-1]) - len(out[-1].lstrip())
                if prev_indent > indent:
                    # tìm ngược tới mục cùng cấp gần nhất; có dòng trống ở giữa thì cần tách
                    for prev in reversed(out):
                        pm = self.ITEM.match(prev)
                        if pm and len(pm.group(1)) <= indent:
                            break
                        if not prev.strip():
                            out.append("")
                            break
            out.append(line)
        return out


class NoteExtension(markdown.Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(FencePreprocessor(md), "note_fence", 30)
        md.preprocessors.register(LooseListPreprocessor(md), "note_loose_list", 29)
        # sau backtick (190) để code không bị coi là công thức, trước escape (180)
        md.inlinePatterns.register(MathProcessor(r"\$\$(.+?)\$\$|\$([^$\n]+?)\$", md), "math", 185)
        # ==chữ== -> chữ được tô màu nhấn mạnh
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"(==)(.+?)==", "mark"), "mark", 65)


def render(text, img_prefix):
    md = markdown.Markdown(
        extensions=["tables", NoteExtension()],
    )
    out = md.convert(text)
    return out.replace('src="img/', f'src="{img_prefix}img/')


def load_notes():
    notes = []
    for path in sorted(NOTES_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        meta, body = {}, raw
        m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
        if m:
            for line in m.group(1).splitlines():
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
            body = raw[m.end():]
        notes.append({
            "slug": path.stem,
            "title": meta.get("title", path.stem),
            "lesson": meta.get("lesson", ""),
            "after": meta.get("after", ""),
            "draft": meta.get("draft", "").lower() == "true",
            "body": body,
        })
    return notes


# ---------- Chèn vào lesson ----------

DRAFT_BADGE = '<span class="opencv-note-draft">Bản nháp – chưa review</span>'


def draft_badge(note):
    return " " + DRAFT_BADGE if note["draft"] else ""


def note_box(note):
    body = render(note["body"], "../")
    return (
        f'<!-- opencv-note:begin {note["slug"]} -->\n'
        f'<details class="opencv-note" id="opencv-note-{note["slug"]}">\n'
        f'<summary><span class="opencv-note-badge">Ghi chú OpenCV</span> {html.escape(note["title"])}{draft_badge(note)}</summary>\n'
        f'<div class="opencv-note-body">\n{body}\n'
        f'<p class="opencv-note-footer"><a href="../opencv-notes.html#{note["slug"]}">Xem tất cả ghi chú OpenCV &rarr;</a></p>\n'
        f'</div>\n</details>\n'
        f'<!-- opencv-note:end {note["slug"]} -->\n'
    )


def heading_text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).replace("¶", "").strip()


def insert_position(page, after):
    """Vị trí chèn: cuối mục có heading chứa `after`, hoặc trước phần Bài tập / cuối bài."""
    end = page.find('<div class="quiz-cta">')
    if end < 0:
        end = page.find('<div class="lesson-nav">')
    cells = [m.start() for m in re.finditer(re.escape(CELL_START), page)]

    def cell_of(pos):
        return max(c for c in cells if c <= pos)

    headings = [(m.start(), m.group(1), heading_text(m.group(2)))
                for m in re.finditer(r"<h([1-3])[^>]*>(.*?)</h\1>", page, re.S)]

    if after:
        for i, (pos, level, text) in enumerate(headings):
            if level == "2" and after.lower() in text.lower():
                for npos, nlevel, ntext in headings[i + 1:]:
                    if nlevel in ("1", "2") or "Exercises" in ntext:
                        return cell_of(npos)
                return end
        raise SystemExit(f'Không tìm thấy heading chứa "{after}"')

    for pos, level, text in headings:
        if "Exercises" in text:
            return cell_of(pos)
    return end


def inject(notes):
    by_lesson = {}
    for note in notes:
        if note["lesson"]:
            by_lesson.setdefault(note["lesson"], []).append(note)

    for path in sorted(LESSONS_DIR.glob("*.html")):
        page = path.read_text(encoding="utf-8")
        cleaned = BLOCK_RE.sub("", page)
        for note in by_lesson.pop(path.stem, []):
            pos = insert_position(cleaned, note["after"])
            cleaned = cleaned[:pos] + note_box(note) + cleaned[pos:]
        if cleaned != page:
            path.write_text(cleaned, encoding="utf-8")
            print("cập nhật", path.relative_to(ROOT))

    for lesson in by_lesson:
        raise SystemExit(f"Không có lesson {lesson}.html")


# ---------- Trang tổng hợp ----------

def lesson_title(stem):
    page = (LESSONS_DIR / f"{stem}.html").read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?) - ", page).group(1)
    return html.unescape(title)


def build_page(notes):
    toc, sections = [], []
    for note in notes:
        title = html.escape(note["title"])
        toc.append(f'<li><a href="#{note["slug"]}">{title}</a>{draft_badge(note)}</li>')
        if note["lesson"]:
            link = (f'<p class="opencv-note-lesson">Gắn với: <a href="lessons/{note["lesson"]}.html#opencv-note-{note["slug"]}">'
                    f'{html.escape(lesson_title(note["lesson"]))}</a></p>')
        else:
            link = '<p class="opencv-note-lesson">Chưa gắn với bài học nào.</p>'
        sections.append(
            f'<section class="opencv-note-section" id="{note["slug"]}">\n'
            f'<h2>{title}{draft_badge(note)}</h2>\n{link}\n<div class="opencv-note-body">\n{render(note["body"], "")}\n</div>\n</section>'
        )

    page = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ghi chú OpenCV - Nhập môn Thị giác Máy tính</title>
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="css/pygments.css">
    <script>
    window.MathJax = {{
        tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] }}
    }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <ul class="nav-links">
                <li><a href="index.html">Nhập môn Thị giác Máy tính</a></li>
                <li style="display: flex; align-items: center; color: #2c3e50;">&bull;</li>
                <li><a href="https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html">OpenCV-Python Tutorials</a></li>
            </ul>
        </div>
    </nav>
    <div class="container">
        <h1>Ghi chú OpenCV</h1>
        <p class="opencv-note-intro">Ghi chú cá nhân của người dịch, dựa trên tài liệu
        <a href="https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html">OpenCV-Python Tutorials</a>.
        Đây <strong>không</strong> phải nội dung của bản gốc; các ghi chú cũng được chèn vào cuối mục liên quan trong từng bài học.
        Ghi chú có nhãn {DRAFT_BADGE} là bản nháp do AI soạn theo tài liệu OpenCV, chưa được người dịch đọc lại.</p>
        <ul class="opencv-note-toc">
{chr(10).join(toc)}
        </ul>
{chr(10).join(sections)}
    </div>
</body>
</html>
"""
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != page:
        PAGE.write_text(page, encoding="utf-8")
        print("cập nhật", PAGE.relative_to(ROOT))


if __name__ == "__main__":
    notes = load_notes()
    inject(notes)
    build_page(notes)
