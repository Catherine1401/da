"""Bộ công cụ dựng báo cáo docx: các khối nội dung, hàm vẽ khối, mục lục có trường TOC thật và số trang."""
import re
from dataclasses import dataclass, field, replace
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Twips

from data import FigNote, aspect, load_note

PAGE_W, PAGE_H = 21.0, 29.7
MARGIN_LEFT_CM, MARGIN_RIGHT_CM, MARGIN_TOP_CM, MARGIN_BOTTOM_CM = 3.0, 2.0, 2.0, 2.0
HEADER_CM = 1.25
TEXT_W_CM = PAGE_W - MARGIN_LEFT_CM - MARGIN_RIGHT_CM
FIG_W_CM = 15.5
TEMPLATE = Path(__file__).resolve().parent / "assets" / "template.docx"
BULLET_NUM_ID = "2"
NO_NUM_ID = "0"
BULLET_TAB_TWIPS = 210
BULLET_LINE_TWIPS = "264"
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


def set_num(paragraph, num_id: str) -> None:
    """Gắn đoạn vào danh sách đánh số của mẫu (num_id '0' là tắt đánh số kế thừa từ kiểu)."""
    num = OxmlElement("w:numPr")
    for tag, value in (("w:ilvl", "0"), ("w:numId", num_id)):
        child = OxmlElement(tag)
        child.set(qn("w:val"), value)
        num.append(child)
    paragraph._p.get_or_add_pPr().append(num)


def new_document() -> Document:
    """Mở mẫu báo cáo (kiểu chữ, danh sách và trang bìa của trường), đặt lề và số trang ở đầu trang căn giữa."""
    doc = Document(str(TEMPLATE))
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(PAGE_W), Cm(PAGE_H)
    section.orientation = WD_ORIENT.PORTRAIT
    section.left_margin, section.right_margin = Cm(MARGIN_LEFT_CM), Cm(MARGIN_RIGHT_CM)
    section.top_margin, section.bottom_margin = Cm(MARGIN_TOP_CM), Cm(MARGIN_BOTTOM_CM)
    section.header_distance = Cm(HEADER_CM)
    header = section.header.paragraphs[0]
    header.style, header.alignment = doc.styles["Header"], WD_ALIGN_PARAGRAPH.CENTER
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
    """Thêm danh sách gạch ngang đầu dòng bằng danh sách của mẫu, giãn dòng như mẫu."""
    for item in block.items:
        para = doc.add_paragraph(item)
        set_num(para, BULLET_NUM_ID)
        para.paragraph_format.tab_stops.add_tab_stop(Twips(BULLET_TAB_TWIPS))
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:line"), BULLET_LINE_TWIPS)
        spacing.set(qn("w:lineRule"), "auto")
        para._p.get_or_add_pPr().append(spacing)


def caption_text(kind: str, label: str, title: str) -> str:
    """Chú thích kiểu mẫu: 'Hình 3.1: tiêu đề.'"""
    end = "" if title.endswith((".", "?", "!")) else "."
    return f"{REF_LABEL[kind]} {label}: {title}{end}"


def add_caption(doc: Document, text: str) -> None:
    """Thêm chú thích hình hoặc bảng theo kiểu Caption của mẫu (nghiêng, căn giữa)."""
    doc.add_paragraph(text, style="Caption")


def add_figure(doc: Document, note: FigNote, label: str) -> str:
    """Thêm ảnh biểu đồ (đã cắt tiêu đề) và chú thích bên dưới; trả về chú thích."""
    doc.add_picture(str(note.cropped), width=Cm(FIG_W_CM))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.keep_with_next = True
    text = caption_text("fig", label, note.title)
    add_caption(doc, text)
    return text


def fill_cell(cell, text: str, bold: bool) -> None:
    """Ghi chữ vào ô bảng theo kiểu table của mẫu; ô tiêu đề in đậm căn giữa."""
    cell.text = ""
    para = cell.paragraphs[0]
    para.style = cell.part.document.styles["table"]
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


def add_title(doc: Document, text: str, new_page: bool = False, plain: bool = False) -> None:
    """Tiêu đề trang phần đầu in hoa theo kiểu section của mẫu; plain là chữ đậm căn giữa (như MỤC LỤC); new_page để sang trang."""
    para = doc.add_paragraph(style=None if plain else "section")
    para.paragraph_format.page_break_before = new_page
    if plain:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.add_run(text.upper()).bold = plain or None


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


def add_heading(doc: Document, block: Head, new_page: bool) -> None:
    """Tiêu đề chương có số theo kiểu Heading của mẫu (số ghi sẵn trong chữ nên tắt đánh số tự động); chương không số dùng kiểu section."""
    if block.level == 1 and not chapter_number(block):
        para = doc.add_paragraph(head_text(block), style="section")
    else:
        para = doc.add_heading(head_text(block), level=block.level)
        set_num(para, NO_NUM_ID)
    para.paragraph_format.page_break_before = new_page


def render_blocks(doc: Document, blocks: list) -> None:
    """Vẽ các khối vào tài liệu với số hình và bảng theo chương; ngắt trang trước tiêu đề được đặt vào chính tiêu đề."""
    labels, pending_break = caption_labels(blocks), False
    for idx, block in enumerate(blocks):
        if pending_break and not isinstance(block, Head):
            add_page_break(doc)
        if isinstance(block, Head):
            add_heading(doc, block, pending_break)
        elif isinstance(block, Para):
            add_para(doc, block)
        elif isinstance(block, Bullets):
            add_bullets(doc, block)
        elif isinstance(block, Fig):
            add_figure(doc, load_note(block.code), labels[idx])
        elif isinstance(block, Tab):
            add_table(doc, block, labels[idx])
        pending_break = isinstance(block, Break)
