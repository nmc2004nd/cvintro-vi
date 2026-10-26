"""Chuyển file export Notion "Note OpenCV" thành các file Markdown trong opencv-notes/.

Chỉ dùng để nhập (import) lần đầu; sau đó các file .md là nguồn chính để chỉnh sửa.

    python3 tools/notion_to_md.py "<đường dẫn tới Note OpenCV ....html>"
"""
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup, NavigableString, Tag

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "opencv-notes"
IMG_DIR = ROOT / "img" / "opencv-notes"

# Mỗi mục trong Notion -> lesson gắn vào và heading (h2) trong lesson đó.
# "after" là một đoạn chữ nằm trong heading; note được chèn ngay trước heading
# kế tiếp (tức là ở cuối mục đó). Bỏ trống -> chèn trước phần Bài tập / cuối bài.
# lesson = None -> chỉ xuất hiện ở trang tổng hợp opencv-notes.html.
MAPPING = {
    1: ("lesson01_images_as_arrays", ""),
    2: ("lesson01_images_as_arrays", ""),
    3: (None, ""),
    4: (None, ""),
    5: (None, ""),
    6: ("lesson01_images_as_arrays", ""),
    7: ("lesson02_image_arithmetic", ""),
    8: (None, ""),
    9: ("lesson18_color_spaces", ""),
    10: ("lesson08_geometric_transformations", ""),
    11: ("lesson03_thresholding_morphology", "Otsu"),
    12: ("lesson11_smoothing_pyramids", ""),
    13: ("lesson03_thresholding_morphology", ""),
    14: ("lesson12_differentiation_edges", "Sobel"),
    15: ("lesson12_differentiation_edges", "Canny"),
    16: ("lesson13_laplacian_pyramids", ""),
    17: ("lesson04_floodfill_connected_components", ""),
}


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


BLOCK_TAGS = ("ul", "ol", "pre", "figure", "table", "div", "details", "p", "blockquote", "hr")


class Converter:
    def __init__(self, src_dir, slug):
        self.src_dir = src_dir
        self.slug = slug
        self.n_img = 0

    # ---- inline ----
    def inline(self, node):
        if isinstance(node, NavigableString):
            return str(node).replace("\n", " ")
        if not isinstance(node, Tag):
            return ""
        if node.name == "span" and "notion-text-equation-token" in (node.get("class") or []):
            tex = re.sub(r"\s*\n\s*", " ", node["data-notion-inline-equation"].strip())
            return "$" + tex + "$"
        inner = "".join(self.inline(c) for c in node.children)
        cls = node.get("class") or []
        if node.name == "code":
            text = node.get_text()
            return "`" + text + "`" if "`" not in text else "`` " + text + " ``"
        if node.name in ("strong", "b"):
            return wrap(inner, "**")
        if node.name in ("em", "i"):
            return wrap(inner, "*")
        if node.name == "mark":
            if any(c in cls for c in ("highlight-red", "highlight-purple", "highlight-blue")):
                return wrap(inner, "==")
            return inner
        if node.name == "a":
            return f"[{inner}]({node.get('href', '')})"
        if node.name == "br":
            return "<br>"
        return inner

    def inline_children(self, node, skip=("ul", "ol")):
        parts = []
        for c in node.children:
            if isinstance(c, Tag) and c.name in skip:
                continue
            parts.append(self.inline(c))
        text = re.sub(r"[ \t]+", " ", "".join(parts)).strip()
        text = text.replace("====", "")
        # công thức đứng một mình trên cả dòng -> công thức dạng khối
        if re.fullmatch(r"\$[^$]+\$", text) and ("\\begin" in text or "\\frac" in text):
            text = "$" + text + "$"
        return text

    # ---- block ----
    def blocks(self, node, indent=""):
        out = []
        for c in node.children:
            if isinstance(c, NavigableString):
                if c.strip():
                    out.append(indent + c.strip())
                continue
            out.extend(self.block(c, indent))
        return out

    def block(self, t, indent):
        name, cls = t.name, t.get("class") or []
        if name in ("ul", "ol"):
            lines = []
            for i, li in enumerate(t.find_all("li", recursive=False)):
                start = t.get("start")
                marker = "-" if name == "ul" else f"{int(start) if start else i + 1}."
                lines.append(f"{indent}{marker} {self.inline_children(li, skip=BLOCK_TAGS)}")
                sub = indent + " " * 4
                for child in li.children:
                    if isinstance(child, Tag) and child.name in BLOCK_TAGS and child.name not in ("ul", "ol"):
                        lines.append("")
                        lines.extend(self.block(child, sub))
                    elif isinstance(child, Tag) and child.name in ("ul", "ol"):
                        lines.extend(self.block(child, sub))
            return lines
        if name == "p":
            text = self.inline_children(t, skip=())
            return [indent + text, ""] if text else []
        if name in ("h1", "h2", "h3"):
            return [f"{indent}### {t.get_text(strip=True)}", ""]
        if name == "pre":
            code = t.get_text().rstrip("\n")
            lang = "python" if t.find(class_="language-python") else ""
            body = [indent + "```" + lang] + [indent + l if l else "" for l in code.split("\n")] + [indent + "```", ""]
            return [""] + body
        if name == "figure" and "image" in cls:
            img = t.find("img")
            src = self.src_dir / unquote(t.find("a")["href"] if t.find("a") else img["src"])
            self.n_img += 1
            dest = IMG_DIR / f"{self.slug}-{self.n_img}{src.suffix.lower()}"
            IMG_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            cap = t.find("figcaption")
            alt = cap.get_text(strip=True) if cap else ""
            return ["", f"{indent}![{alt}](img/opencv-notes/{dest.name})", ""]
        if name == "table":
            rows = t.find_all("tr")
            cells = [[self.inline_children(td, skip=()).replace("|", "\\|") for td in r.find_all(["td", "th"])] for r in rows]
            ncol = max(len(r) for r in cells)
            cells = [r + [""] * (ncol - len(r)) for r in cells]
            lines = ["", indent + "| " + " | ".join(cells[0]) + " |", indent + "|" + "---|" * ncol]
            lines += [indent + "| " + " | ".join(r) + " |" for r in cells[1:]]
            return lines + [""]
        if name == "details":
            summary = t.find("summary")
            title = summary.get_text(strip=True)
            body = t.find("div", class_="indented")
            lines = ["", f"{indent}### {title}", ""]
            if body:
                lines += self.blocks(body, indent)
            return lines
        if name == "div":
            return self.blocks(t, indent)
        if name == "hr":
            return ["", indent + "---", ""]
        if name == "blockquote":
            return [indent + "> " + self.inline_children(t, skip=()), ""]
        text = self.inline_children(t, skip=())
        return [indent + text, ""] if text else []


def wrap(text, mark):
    stripped = text.strip()
    if not stripped:
        return text
    lead = text[: len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()):]
    return f"{lead}{mark}{stripped}{mark}{trail}"


def tidy(lines):
    text = "\n".join(l.rstrip() for l in lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # gộp các danh sách liền kề (Notion tách mỗi mục thành một <ul> riêng)
    return text.strip() + "\n"


def main(src):
    src = Path(src)
    soup = BeautifulSoup(src.read_text(encoding="utf-8"), "html.parser")
    body = soup.find("div", class_="page-body")
    NOTES_DIR.mkdir(exist_ok=True)
    if IMG_DIR.exists():
        shutil.rmtree(IMG_DIR)
    for d in body.find_all("details", recursive=False):
        title = d.find("summary").get_text(strip=True)
        num = int(re.match(r"(\d+)", title).group(1))
        name = re.sub(r"^\d+\.\s*", "", title)
        slug = f"{num:02d}-{slugify(name)}"
        content = d.find("div", class_="indented")
        if content is None:
            print(slug, "trống, bỏ qua")
            continue
        conv = Converter(src.parent, slug)
        lines = conv.blocks(content)
        lesson, after = MAPPING.get(num, (None, ""))
        front = ["---", f"title: {num}. {name}", f"lesson: {lesson or ''}", f"after: {after}", "---", ""]
        (NOTES_DIR / f"{slug}.md").write_text("\n".join(front) + tidy(lines), encoding="utf-8")
        print(slug, conv.n_img, "ảnh")


if __name__ == "__main__":
    main(sys.argv[1])
