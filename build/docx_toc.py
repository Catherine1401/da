"""Mục lục và danh mục động: trường TOC của Word có sẵn kết quả, mỗi dòng là liên kết tới bookmark của tiêu đề hoặc chú thích."""
import zlib

from docx import Document
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Twips

from docx_kit import add_title

TOC_TAB_TWIPS = 9061
FIG_ID, TAB_ID = "F", "T"
FIG_PREFIX, TAB_PREFIX = "Hình", "Bảng"
LINKED_STYLES = ("Heading 1", "Heading 2", "section", "Caption")


def anchor_name(text: str) -> str:
    """Tên bookmark ổn định suy ra từ chữ của mục (cùng chữ thì cùng tên ở mọi lượt dựng)."""
    return f"_Toc{zlib.crc32(' '.join(text.split()).encode('utf-8'))}"


def field_char(kind: str):
    """Một run chứa dấu trường (begin, separate, end)."""
    run = OxmlElement("w:r")
    char = OxmlElement("w:fldChar")
    char.set(qn("w:fldCharType"), kind)
    run.append(char)
    return run


def instr_run(instruction: str):
    """Một run chứa mã lệnh của trường."""
    run = OxmlElement("w:r")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {instruction} "
    run.append(instr)
    return run


def text_run(text: str, tab: bool = False):
    """Một run chữ thường, hoặc một dấu tab."""
    run = OxmlElement("w:r")
    child = OxmlElement("w:tab" if tab else "w:t")
    if not tab:
        child.set(qn("xml:space"), "preserve")
        child.text = text
    run.append(child)
    return run


def link(text: str, page: str):
    """Liên kết nội bộ tới bookmark của mục: chữ, tab dẫn chấm và số trang."""
    hyper = OxmlElement("w:hyperlink")
    hyper.set(qn("w:anchor"), anchor_name(text))
    hyper.set(qn("w:history"), "1")
    for run in (text_run(text), text_run("", tab=True), text_run(page)):
        hyper.append(run)
    return hyper


def add_toc(doc: Document, entries: list, title: str, new_page: bool = False, tc_id: str = "") -> None:
    """Trường TOC có sẵn kết quả: mục lục theo cấp tiêu đề, hoặc danh mục theo trường TC mã tc_id (kiểu table of figures)."""
    add_title(doc, title, new_page, plain=not tc_id)
    instruction = f"TOC \\f {tc_id} \\h \\z" if tc_id else 'TOC \\o "1-2" \\h \\z'
    paras = []
    for text, level, page in entries:
        para = doc.add_paragraph(style="table of figures" if tc_id else f"toc {level}")
        para.paragraph_format.tab_stops.add_tab_stop(Twips(TOC_TAB_TWIPS), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        para._p.append(link(text, page))
        paras.append(para)
    for run in (field_char("begin"), instr_run(instruction), field_char("separate")):
        paras[0]._p.hyperlink_lst[0].addprevious(run)
    paras[-1]._p.append(field_char("end"))


def add_tc(paragraph, text: str) -> None:
    """Trường TC ẩn trong chú thích để Word gom vào danh mục hình hoặc bảng khi cập nhật."""
    tc_id = FIG_ID if text.startswith(FIG_PREFIX) else TAB_ID
    quoted = text.replace('"', '\\"')
    for run in (field_char("begin"), instr_run(f'TC "{quoted}" \\f {tc_id} \\l 1'), field_char("end")):
        paragraph._p.append(run)


def link_targets(doc: Document, entries: list) -> None:
    """Gắn bookmark cho tiêu đề và chú thích có trong mục lục hoặc danh mục; chú thích có thêm trường TC."""
    wanted = {" ".join(text.split()) for text in entries}
    for number, para in enumerate(p for p in doc.paragraphs if p.style.name in LINKED_STYLES):
        text = " ".join(para.text.split())
        if text not in wanted:
            continue
        start, end = OxmlElement("w:bookmarkStart"), OxmlElement("w:bookmarkEnd")
        start.set(qn("w:id"), str(number))
        start.set(qn("w:name"), anchor_name(text))
        end.set(qn("w:id"), str(number))
        para._p.get_or_add_pPr().addnext(start)
        para._p.append(end)
        if para.style.name == "Caption":
            add_tc(para, text)
