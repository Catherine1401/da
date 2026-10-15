"""Phần đầu báo cáo theo mẫu: điền trang bìa có sẵn trong mẫu, bảng không chú thích, đánh số trang La Mã và Ả Rập."""
from copy import deepcopy
from dataclasses import dataclass

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from docx_kit import add_grid, add_title


@dataclass(frozen=True)
class Member:
    """Một thành viên nhóm."""
    name: str
    sid: str
    phone: str
    role: str


@dataclass(frozen=True)
class Cover:
    """Nội dung trang bìa."""
    university: str
    school: str
    kind: str
    subject: str
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


def fill_token(root, token: str, value: str) -> None:
    """Thay placeholder {token} trong các đoạn chữ của trang bìa mẫu."""
    for text in root.iter(qn("w:t")):
        if f"{{{token}}}" in text.text:
            text.text = text.text.replace(f"{{{token}}}", value)


def fill_members(cover_tbl, members: tuple) -> None:
    """Nhân dòng thành viên của bảng lồng trên bìa mẫu: 'Họ tên - Mã sinh viên', cột lớp để trống."""
    token = next(t for t in cover_tbl.iter(qn("w:t")) if "{member}" in t.text)
    row = next(token.iterancestors(qn("w:tr")))
    for member in members:
        clone = deepcopy(row)
        fill_token(clone, "member", f"{member.name} - {member.sid}")
        fill_token(clone, "klass", "")
        row.addprevious(clone)
    row.getparent().remove(row)


def trim_spacers(cover_tbl, count: int) -> None:
    """Bỏ count đoạn trống ngay trước dòng nơi và thời gian để bìa vẫn nằm gọn một trang khi nội dung dài hơn mẫu."""
    cell = cover_tbl.find(qn("w:tr")).find(qn("w:tc"))
    spacers = [p for p in cell.findall(qn("w:p")) if not "".join(t.text for t in p.iter(qn("w:t")))]
    for para in spacers[len(spacers) - count:] if count > 0 else []:
        cell.remove(para)


def add_cover(doc: Document, cover: Cover) -> None:
    """Điền trang bìa có sẵn trong mẫu (khung, logo, đường kẻ giữ nguyên) bằng nội dung của báo cáo."""
    template_members, title_extra_lines = 2, 1
    cover_tbl = doc.element.body.find(qn("w:tbl"))
    fill_members(cover_tbl, cover.members)
    trim_spacers(cover_tbl, len(cover.members) - template_members + title_extra_lines)
    values = {"university": cover.university, "school": cover.school, "kind": cover.kind, "subject": cover.subject,
              "title": " ".join(cover.title_lines), "lecturer": cover.lecturer, "course": cover.course, "place_date": cover.place_date}
    for token, value in values.items():
        fill_token(cover_tbl, token, value)


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


def finish_sections(doc: Document) -> None:
    """Bìa không số trang (khung có sẵn trong mẫu); phần đầu đánh số La Mã từ ii; nội dung đánh số Ả Rập từ 1."""
    cover, front, body = doc.sections
    cover.different_first_page_header_footer = True
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
