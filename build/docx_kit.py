"""Bộ công cụ dựng báo cáo docx: các khối nội dung, hàm vẽ khối, mục lục có trường TOC thật và số trang."""
import re
from dataclasses import dataclass, field, replace

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from data import FigNote, aspect, load_note

PAGE_W, PAGE_H = 21.0, 29.7
MARGIN_CM = 2.5
TEXT_W_CM = PAGE_W - 2 * MARGIN_CM
FIG_W_CM = 15.5
BODY_PT = 11
CAPTION_PT = 10
SMALL_PT = 8.5
TABLE_PT = 9
SPACE_AFTER_PT = 6
LINE_SPACING = 1.15
ACCENT = RGBColor(0x00, 0x72, 0xB2)
GREY = RGBColor(0x55, 0x55, 0x55)
TOC_TAB_CM = TEXT_W_CM
HEADER_FILL = "0072B2"
BAND_FILL = "EAF2F8"


@dataclass(frozen=True)
class Head:
    """Tiêu đề mục (level 1 = chương, 2 = mục, 3 = tiểu mục)."""
    text: str
    level: int


@dataclass(frozen=True)
class Para:
    """Một đoạn văn; lead là cụm in đậm đầu đoạn (ví dụ 'Nhận xét.')."""
    text: str
    lead: str = ""
    italic: bool = False


@dataclass(frozen=True)
class Bullets:
    """Danh sách gạch đầu dòng."""
    items: list


@dataclass(frozen=True)
class Fig:
    """Một biểu đồ lấy theo mã, kèm chú thích tự sinh."""
    code: str


@dataclass(frozen=True)
class Tab:
    """Một bảng: chú thích, dòng tiêu đề, các dòng dữ liệu và độ rộng cột tương đối."""
    caption: str
    header: list
    rows: list
    widths: list = field(default_factory=list)
    key: str = ""


@dataclass(frozen=True)
class Break:
    """Ngắt trang."""


def set_cell_fill(cell, hex_fill: str) -> None:
    """Tô nền một ô bảng."""
    props = cell._tc.get_or_add_tcPr()
    shade = OxmlElement("w:shd")
    shade.set(qn("w:val"), "clear")
    shade.set(qn("w:color"), "auto")
    shade.set(qn("w:fill"), hex_fill)
    props.append(shade)


def add_field(paragraph, instruction: str) -> None:
    """Chèn một trường Word (ví dụ PAGE) vào đoạn."""
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, instruction), ("separate", None), (None, "1"), ("end", None)):
        if kind:
            element = OxmlElement("w:fldChar")
            element.set(qn("w:fldCharType"), kind)
        elif text == instruction:
            element = OxmlElement("w:instrText")
            element.set(qn("xml:space"), "preserve")
            element.text = instruction
        else:
            element = OxmlElement("w:t")
            element.text = text
        run._r.append(element)


def new_document() -> Document:
    """Tạo tài liệu A4, lề 2,5 cm, thiết lập kiểu cơ bản và chân trang có số trang."""
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(PAGE_W), Cm(PAGE_H)
    section.orientation = WD_ORIENT.PORTRAIT
    section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Cm(MARGIN_CM)
    normal = doc.styles["Normal"]
    normal.font.size = Pt(BODY_PT)
    normal.paragraph_format.space_after = Pt(SPACE_AFTER_PT)
    normal.paragraph_format.line_spacing = LINE_SPACING
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        doc.styles[name].font.color.rgb = ACCENT
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("Nhóm 8 · Phân tích xu hướng công nghệ và mức lương lập trình viên · Trang ").font.size = Pt(SMALL_PT)
    add_field(footer, "PAGE")
    return doc


def add_para(doc: Document, block: Para) -> None:
    """Thêm một đoạn văn thường."""
    para = doc.add_paragraph()
    if block.lead:
        para.add_run(block.lead + " ").bold = True
    run = para.add_run(block.text)
    run.italic = block.italic


def add_bullets(doc: Document, block: Bullets) -> None:
    """Thêm danh sách gạch đầu dòng."""
    for item in block.items:
        doc.add_paragraph(item, style="List Bullet")


def add_caption(doc: Document, text: str) -> None:
    """Thêm chú thích hình hoặc bảng (căn giữa, in nghiêng)."""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    run.italic = True
    run.font.size = Pt(CAPTION_PT)


def add_figure(doc: Document, note: FigNote, number: int) -> None:
    """Thêm ảnh biểu đồ (đã cắt tiêu đề), chú thích đánh số và dòng nguồn."""
    doc.add_picture(str(note.cropped), width=Cm(FIG_W_CM))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    add_caption(doc, f"Hình {number}. {note.title}")


def add_table(doc: Document, block: Tab, number: int) -> None:
    """Thêm bảng có dòng tiêu đề tô màu, dòng xen kẽ và chú thích phía trên."""
    add_caption(doc, f"Bảng {number}. {block.caption}")
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    table = doc.add_table(rows=1, cols=len(block.header))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    header_props = table.rows[0]._tr.get_or_add_trPr()
    header_props.append(OxmlElement("w:tblHeader"))
    for idx, text in enumerate(block.header):
        cell = table.rows[0].cells[idx]
        cell.text = ""
        run = cell.paragraphs[0].add_run(str(text))
        run.bold, run.font.size, run.font.color.rgb = True, Pt(TABLE_PT), RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_fill(cell, HEADER_FILL)
    for row_idx, row in enumerate(block.rows):
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = ""
            cells[idx].paragraphs[0].add_run(str(value)).font.size = Pt(TABLE_PT)
            if row_idx % 2 == 1:
                set_cell_fill(cells[idx], BAND_FILL)
    if block.widths:
        total = sum(block.widths)
        for row in table.rows:
            for cell, width in zip(row.cells, block.widths):
                cell.width = Cm(TEXT_W_CM * width / total)
    doc.add_paragraph()


def add_toc(doc: Document, entries: list, title: str) -> None:
    """Mục lục tĩnh gồm tên mục, dấu chấm dẫn và số trang (số trang đo từ bản PDF dựng thử)."""
    heading = doc.add_paragraph()
    heading.add_run(title).bold = True
    heading.runs[0].font.size = Pt(16)
    heading.runs[0].font.color.rgb = ACCENT
    for idx, (text, level, page) in enumerate(entries):
        para = doc.add_paragraph()
        para.paragraph_format.left_indent = Cm(0.8 * (level - 1))
        para.paragraph_format.space_after = Pt(2)
        para.paragraph_format.tab_stops.add_tab_stop(Cm(TOC_TAB_CM), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        run = para.add_run(f"{text}\t{page}")
        run.bold = level == 1
        run.font.size = Pt(BODY_PT)


def add_page_break(doc: Document) -> None:
    """Ngắt sang trang mới."""
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


REF_RE = re.compile(r"\[\[(tab|fig):(\w+)\]\]")
REF_LABEL = {"tab": "Bảng", "fig": "Hình"}


def resolve_refs(blocks: list) -> list:
    """Thay các tham chiếu [[tab:khóa]] và [[fig:mã]] trong văn bản bằng số thứ tự thật của bảng và hình."""
    numbers, tab_n, fig_n = {}, 0, 0
    for block in blocks:
        if isinstance(block, Tab):
            tab_n += 1
            numbers[("tab", block.key)] = tab_n
        elif isinstance(block, Fig):
            fig_n += 1
            numbers[("fig", block.code)] = fig_n
    sub = lambda text: REF_RE.sub(lambda m: f"{REF_LABEL[m[1]]} {numbers[(m[1], m[2])]}", text)
    out = []
    for block in blocks:
        if isinstance(block, Para):
            block = replace(block, text=sub(block.text))
        elif isinstance(block, Bullets):
            block = replace(block, items=[sub(item) for item in block.items])
        out.append(block)
    return out


def heading_entries(blocks: list) -> list:
    """Danh sách (tên, cấp) của các tiêu đề cấp 1 và 2 trong dãy khối."""
    return [(b.text, b.level) for b in blocks if isinstance(b, Head) and b.level <= 2]


def render_blocks(doc: Document, blocks: list, counters: dict) -> list:
    """Vẽ các khối vào tài liệu; trả về danh sách chú thích hình và bảng theo thứ tự (nhãn, tiêu đề)."""
    captions = []
    for block in blocks:
        if isinstance(block, Head):
            doc.add_heading(block.text, level=block.level)
        elif isinstance(block, Para):
            add_para(doc, block)
        elif isinstance(block, Bullets):
            add_bullets(doc, block)
        elif isinstance(block, Fig):
            note = load_note(block.code)
            counters["fig"] += 1
            add_figure(doc, note, counters["fig"])
            captions.append((f"Hình {counters['fig']}. {note.title}", "fig"))
        elif isinstance(block, Tab):
            counters["tab"] += 1
            add_table(doc, block, counters["tab"])
            captions.append((f"Bảng {counters['tab']}. {block.caption}", "tab"))
        elif isinstance(block, Break):
            add_page_break(doc)
    return captions
