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
MARGIN_LEFT_CM, MARGIN_RIGHT_CM, MARGIN_TOP_CM, MARGIN_BOTTOM_CM = 3.0, 2.0, 2.0, 2.0
HEADER_CM = 1.2
TEXT_W_CM = PAGE_W - MARGIN_LEFT_CM - MARGIN_RIGHT_CM
FIG_W_CM = 15.5
FONT = "Times New Roman"
BODY_PT = 13
CAPTION_PT = 12
SPACE_AFTER_PT = 6
HEADING_AFTER_PT = (12, 6, 6)
LINE_SPACING = 1.1
TABLE_SPACING = 1.0
BLACK = RGBColor(0x00, 0x00, 0x00)
TOC_TAB_CM = TEXT_W_CM
TOC_INDENT_CM = 0.75
BULLET_INDENT_CM = 0.75
BULLET_MARK = "-"
CHAPTER_PREFIX = "CHƯƠNG"
FRONT_CHAPTER = "0"
APPENDIX_CHAPTER = "PL"


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


def set_font(font, size: float = BODY_PT) -> None:
    """Đặt font Times New Roman (cả chữ Latin và Đông Á), cỡ chữ và màu đen, bỏ font theo theme."""
    font.name, font.size, font.color.rgb = FONT, Pt(size), BLACK
    fonts = font.element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        fonts.attrib.pop(qn(attr), None)
    for attr in ("w:eastAsia", "w:cs"):
        fonts.set(qn(attr), FONT)


def style_document(doc: Document) -> None:
    """Định dạng kiểu Normal và Heading 1–3 theo mẫu báo cáo."""
    normal = doc.styles["Normal"]
    set_font(normal.font)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.space_before, normal.paragraph_format.space_after = Pt(0), Pt(SPACE_AFTER_PT)
    normal.paragraph_format.line_spacing = LINE_SPACING
    for level, after in enumerate(HEADING_AFTER_PT, start=1):
        style = doc.styles[f"Heading {level}"]
        set_font(style.font)
        style.font.bold, style.font.italic = True, level == 3
        fmt = style.paragraph_format
        fmt.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT
        fmt.space_before, fmt.space_after, fmt.line_spacing = Pt(0), Pt(after), TABLE_SPACING


def new_document() -> Document:
    """Tạo tài liệu A4 với lề, kiểu chữ và số trang ở đầu trang căn giữa theo mẫu."""
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(PAGE_W), Cm(PAGE_H)
    section.orientation = WD_ORIENT.PORTRAIT
    section.left_margin, section.right_margin = Cm(MARGIN_LEFT_CM), Cm(MARGIN_RIGHT_CM)
    section.top_margin, section.bottom_margin = Cm(MARGIN_TOP_CM), Cm(MARGIN_BOTTOM_CM)
    section.header_distance = Cm(HEADER_CM)
    style_document(doc)
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(header, "PAGE")
    return doc


def add_para(doc: Document, block: Para) -> None:
    """Thêm một đoạn văn thường."""
    para = doc.add_paragraph()
    if block.lead:
        para.add_run(block.lead + " ").bold = True
    run = para.add_run(block.text)
    run.italic = block.italic


def add_bullets(doc: Document, block: Bullets) -> None:
    """Thêm danh sách gạch ngang đầu dòng thụt treo như mẫu."""
    for item in block.items:
        para = doc.add_paragraph(f"{BULLET_MARK}\t{item}")
        fmt = para.paragraph_format
        fmt.left_indent, fmt.first_line_indent = Cm(BULLET_INDENT_CM), Cm(-BULLET_INDENT_CM)
        fmt.tab_stops.add_tab_stop(Cm(BULLET_INDENT_CM))


def caption_text(kind: str, label: str, title: str) -> str:
    """Chú thích kiểu mẫu: 'Hình 3.1: tiêu đề.'"""
    end = "" if title.endswith((".", "?", "!")) else "."
    return f"{REF_LABEL[kind]} {label}: {title}{end}"


def add_caption(doc: Document, text: str) -> None:
    """Thêm chú thích hình hoặc bảng (căn giữa, chữ thường cỡ 12)."""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.add_run(text).font.size = Pt(CAPTION_PT)


def add_figure(doc: Document, note: FigNote, label: str) -> str:
    """Thêm ảnh biểu đồ (đã cắt tiêu đề) và chú thích bên dưới; trả về chú thích."""
    doc.add_picture(str(note.cropped), width=Cm(FIG_W_CM))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    text = caption_text("fig", label, note.title)
    add_caption(doc, text)
    return text


def fill_cell(cell, text: str, bold: bool) -> None:
    """Ghi chữ vào ô bảng với giãn dòng đơn, không cách đoạn."""
    cell.text = ""
    para = cell.paragraphs[0]
    para.paragraph_format.space_after, para.paragraph_format.line_spacing = Pt(0), TABLE_SPACING
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER if bold else WD_ALIGN_PARAGRAPH.LEFT
    para.add_run(str(text)).bold = bold


def add_grid(doc: Document, header: list, rows: list, widths: list) -> None:
    """Bảng viền đơn: dòng tiêu đề in đậm căn giữa, lặp lại khi sang trang."""
    table = doc.add_table(rows=1, cols=len(header))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    for cell, text in zip(table.rows[0].cells, header):
        fill_cell(cell, text, True)
    for row in rows:
        for cell, value in zip(table.add_row().cells, row):
            fill_cell(cell, value, False)
    if widths:
        total = sum(widths)
        table.autofit = False
        for column, width in zip(table.columns, widths):
            column.width = Cm(TEXT_W_CM * width / total)
        for row in table.rows:
            for cell, width in zip(row.cells, widths):
                cell.width = Cm(TEXT_W_CM * width / total)


def add_table(doc: Document, block: Tab, label: str) -> str:
    """Thêm chú thích phía trên và bảng; trả về chú thích."""
    text = caption_text("tab", label, block.caption)
    add_caption(doc, text)
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    add_grid(doc, block.header, block.rows, block.widths)
    doc.add_paragraph()
    return text


def add_title(doc: Document, text: str, new_page: bool = False) -> None:
    """Tiêu đề trang phần đầu (in hoa, đậm, căn giữa), không vào kiểu Heading; new_page để bắt đầu trang mới."""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.page_break_before = new_page
    para.paragraph_format.space_after = Pt(HEADING_AFTER_PT[0])
    para.add_run(text.upper()).bold = True


def add_toc(doc: Document, entries: list, title: str, new_page: bool = False) -> None:
    """Mục lục tĩnh: tên mục, dấu chấm dẫn và số trang; mục cấp 1 in đậm, cấp 3 thụt vào."""
    add_title(doc, title, new_page)
    for text, level, page in entries:
        para = doc.add_paragraph()
        fmt = para.paragraph_format
        fmt.left_indent = Cm(TOC_INDENT_CM * max(level - 2, 0))
        fmt.space_after, fmt.line_spacing, para.alignment = Pt(0), TABLE_SPACING, WD_ALIGN_PARAGRAPH.LEFT
        fmt.tab_stops.add_tab_stop(Cm(TOC_TAB_CM), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        para.add_run(f"{text}\t{page}").bold = level == 1


def add_page_break(doc: Document) -> None:
    """Ngắt sang trang mới."""
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


REF_RE = re.compile(r"\[\[(tab|fig):(\w+)\]\]")
REF_LABEL = {"tab": "Bảng", "fig": "Hình"}


def chapter_number(block: Head) -> str:
    """Số chương của tiêu đề cấp 1 dạng 'n. Tên'; rỗng nếu tiêu đề không đánh số."""
    token = block.text.split()[0].rstrip(".")
    return token if block.level == 1 and token.isdigit() else ""


def head_text(block: Head) -> str:
    """Chữ hiển thị của tiêu đề: cấp 1 in hoa, chương có tiền tố 'CHƯƠNG'."""
    if block.level != 1:
        return block.text
    return (f"{CHAPTER_PREFIX} {block.text}" if chapter_number(block) else block.text).upper()


def caption_labels(blocks: list) -> dict:
    """Số hình/bảng theo chương ('3.1') cho từng vị trí khối; trước chương 1 là 0, sau chương cuối là PL."""
    labels, counts, chapter = {}, {}, FRONT_CHAPTER
    for idx, block in enumerate(blocks):
        if isinstance(block, Head) and block.level == 1:
            chapter = chapter_number(block) or (APPENDIX_CHAPTER if chapter != FRONT_CHAPTER else chapter)
        kind = "fig" if isinstance(block, Fig) else "tab" if isinstance(block, Tab) else ""
        if kind:
            counts[(kind, chapter)] = counts.get((kind, chapter), 0) + 1
            labels[idx] = f"{chapter}.{counts[(kind, chapter)]}"
    return labels


def resolve_refs(blocks: list) -> list:
    """Thay các tham chiếu [[tab:khóa]] và [[fig:mã]] trong văn bản bằng số hình và bảng theo chương."""
    numbers = {}
    for idx, label in caption_labels(blocks).items():
        block = blocks[idx]
        numbers[("fig", block.code) if isinstance(block, Fig) else ("tab", block.key)] = label
    sub = lambda text: REF_RE.sub(lambda m: f"{REF_LABEL[m[1]]} {numbers[(m[1], m[2])]}", text)
    out = []
    for block in blocks:
        if isinstance(block, Para):
            block = replace(block, text=sub(block.text))
        elif isinstance(block, Bullets):
            block = replace(block, items=[sub(item) for item in block.items])
        out.append(block)
    return out


def caption_entries(blocks: list) -> tuple:
    """Danh sách chú thích hình và bảng theo thứ tự (để lập danh mục)."""
    figs, tabs = [], []
    for idx, label in caption_labels(blocks).items():
        block = blocks[idx]
        if isinstance(block, Fig):
            figs.append(caption_text("fig", label, load_note(block.code).title))
        else:
            tabs.append(caption_text("tab", label, block.caption))
    return figs, tabs


def heading_entries(blocks: list) -> list:
    """Danh sách (chữ hiển thị, cấp) của các tiêu đề cấp 1 và 2 trong dãy khối."""
    return [(head_text(b), b.level) for b in blocks if isinstance(b, Head) and b.level <= 2]


def render_blocks(doc: Document, blocks: list) -> None:
    """Vẽ các khối vào tài liệu với số hình và bảng theo chương; ngắt trang trước tiêu đề được đặt vào chính tiêu đề."""
    labels, pending_break = caption_labels(blocks), False
    for idx, block in enumerate(blocks):
        if pending_break and not isinstance(block, Head):
            add_page_break(doc)
        if isinstance(block, Head):
            heading = doc.add_heading(head_text(block), level=block.level)
            heading.paragraph_format.page_break_before = pending_break
        elif isinstance(block, Para):
            add_para(doc, block)
        elif isinstance(block, Bullets):
            add_bullets(doc, block)
        elif isinstance(block, Fig):
            add_figure(doc, load_note(block.code), labels[idx])
        elif isinstance(block, Tab):
            add_table(doc, block, labels[idx])
        pending_break = isinstance(block, Break)
