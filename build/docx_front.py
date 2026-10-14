"""Phần đầu báo cáo theo mẫu: trang bìa có khung và logo, bảng không chú thích, đánh số trang La Mã và Ả Rập."""
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from docx_kit import add_grid, add_title


@dataclass(frozen=True)
class Member:
    """Một thành viên nhóm."""
    name: str
    sid: str


@dataclass(frozen=True)
class Cover:
    """Nội dung trang bìa."""
    university: str
    school: str
    kind: str
    title_lines: tuple
    lecturer: str
    members: tuple
    course: str
    place_date: str


@dataclass(frozen=True)
class Grid:
    """Bảng không đánh số ở phần đầu: tiêu đề trang (có thể rỗng), dòng tiêu đề, các dòng và độ rộng tương đối."""
    title: str
    header: list
    rows: list
    widths: list


def cover_line(doc: Document, text: str, size: float, before: float = 0) -> None:
    """Một dòng in đậm căn giữa trên trang bìa."""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before, para.paragraph_format.space_after = Pt(before), Pt(0)
    run = para.add_run(text)
    run.bold, run.font.size = True, Pt(size)


def info_line(doc: Document, label: str, value: str, extra: str = "", before: float = 0) -> None:
    """Một dòng thông tin trên bìa: nhãn đậm, giá trị và cột phụ thẳng hàng bằng điểm dừng tab."""
    indent_cm, value_cm, extra_cm, size_pt, after_pt = 2.25, 5.5, 9.95, 14, 6
    para = doc.add_paragraph()
    fmt = para.paragraph_format
    fmt.left_indent, fmt.space_before, fmt.space_after = Cm(indent_cm), Pt(before), Pt(after_pt)
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for stop in (value_cm, extra_cm):
        fmt.tab_stops.add_tab_stop(Cm(indent_cm + stop))
    head = para.add_run(label)
    head.bold, head.font.size = True, Pt(size_pt)
    para.add_run(f"\t{value}" + (f"\t{extra}" if extra else "")).font.size = Pt(size_pt)


def add_cover(doc: Document, cover: Cover) -> None:
    """Trang bìa theo mẫu: trường, logo, loại bài, tên đề tài, thông tin nhóm, nơi và thời gian."""
    title_pt, info_pt, logo_cm, school_before, logo_before, kind_before, info_before, date_before = 16, 14, 6.9, 14, 18, 30, 60, 110
    logo = Path(__file__).resolve().parent / "assets" / "logo.jpg"
    cover_line(doc, cover.university, title_pt, school_before)
    cover_line(doc, cover.school, title_pt)
    doc.add_picture(str(logo), width=Cm(logo_cm))
    pic = doc.paragraphs[-1]
    pic.alignment, pic.paragraph_format.space_before = WD_ALIGN_PARAGRAPH.CENTER, Pt(logo_before)
    cover_line(doc, cover.kind, title_pt, kind_before)
    for line in cover.title_lines:
        cover_line(doc, line, title_pt)
    info_line(doc, "Giảng viên hướng dẫn:", cover.lecturer, before=info_before)
    for idx, member in enumerate(cover.members):
        info_line(doc, "Sinh viên thực hiện:" if idx == 0 else "", member.name, member.sid)
    info_line(doc, "Lớp tín chỉ:", cover.course)
    cover_line(doc, cover.place_date, info_pt, date_before)


def add_front_grid(doc: Document, grid: Grid, new_page: bool = False) -> None:
    """Tiêu đề trang (nếu có) và bảng không chú thích, kèm một dòng trống sau bảng."""
    if grid.title:
        add_title(doc, grid.title, new_page)
    add_grid(doc, grid.header, grid.rows, grid.widths)
    doc.add_paragraph()


def set_page_numbers(section, fmt: str, start: int) -> None:
    """Đặt kiểu số trang (decimal, lowerRoman) và số bắt đầu cho một section."""
    num = OxmlElement("w:pgNumType")
    num.set(qn("w:fmt"), fmt)
    num.set(qn("w:start"), str(start))
    section._sectPr.find(qn("w:cols")).addprevious(num)


def set_cover_border(section) -> None:
    """Khung viền đôi (dày ngoài, mảnh trong) quanh trang bìa."""
    style, size, space = "thickThinSmallGap", "24", "24"
    borders = OxmlElement("w:pgBorders")
    borders.set(qn("w:offsetFrom"), "text")
    for side in ("top", "left", "bottom", "right"):
        edge = OxmlElement(f"w:{side}")
        for key, value in (("val", style), ("sz", size), ("space", space), ("color", "auto")):
            edge.set(qn(f"w:{key}"), value)
        borders.append(edge)
    section._sectPr.find(qn("w:pgMar")).addnext(borders)


def finish_sections(doc: Document) -> None:
    """Bìa không số trang và có khung; phần đầu đánh số La Mã từ ii; nội dung đánh số Ả Rập từ 1."""
    cover, front, body = doc.sections
    cover.different_first_page_header_footer = True
    set_cover_border(cover)
    set_page_numbers(front, "lowerRoman", 2)
    set_page_numbers(body, "decimal", 1)


def to_roman(number: int) -> str:
    """Số La Mã chữ thường (dùng cho số trang phần đầu)."""
    table = ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"))
    out = ""
    for value, mark in table:
        while number >= value:
            out, number = out + mark, number - value
    return out
