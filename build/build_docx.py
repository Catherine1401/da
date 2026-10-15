"""Dựng báo cáo docx từ ảnh, chú giải và bảng số do notebook sinh ra; dựng 2 lượt để mục lục có số trang."""
import subprocess
import sys
import tempfile
from pathlib import Path

from docx.enum.section import WD_SECTION

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data import ROOT, SummaryData, fmt_int, fmt_num, load_summary
from docx_front import Cover, Member, add_cover, add_front_grid, finish_sections, to_roman
from docx_kit import (Break, Bullets, Head, Para, add_toc, caption_entries, heading_entries, new_document,
                      render_blocks, resolve_refs)
from report_ch12 import chapters_1_2
from report_ch3 import chapter3
from report_ch4 import chapter4
from report_ch56 import chapters_5_6
from report_front import member_grid, task_grids, term_grid
from report_common import pct, usd

OUT_DOCX = ROOT / "deliverables" / "report.docx"
MIN_PAGES = 30
TITLE = "Phân tích xu hướng công nghệ và mức lương lập trình viên"
SUBTITLE = "Qua khảo sát Stack Overflow Developer Survey 2025"
TEAM = "Nhóm 8"
MATCH_PREFIX = 40
ABSTRACT_TITLE = "Tóm tắt báo cáo"
TOC_TITLE = "Mục lục"
FIG_LIST_TITLE = "Danh mục hình"
TAB_LIST_TITLE = "Danh mục bảng"
MEMBER_TITLE = "Danh sách thành viên"
TASK_TITLE = "Phân công nhiệm vụ"
TERM_TITLE = "Danh sách thuật ngữ"


def abstract_blocks(s: SummaryData) -> list:
    """Trang tóm tắt báo cáo."""
    return [
        Head(ABSTRACT_TITLE, 1),
        Para(f"Báo cáo phân tích khảo sát Stack Overflow Developer Survey 2025 ({fmt_int(s.n_all)} phản hồi) để trả lời hai câu hỏi của sinh viên và lập trình viên mới ở Việt Nam: nên học công nghệ nào và có thể kỳ vọng mức lương ra sao. Dữ liệu được làm sạch theo các quy tắc cố định; bảng lương gồm {fmt_int(s.n_sal)} lập trình viên chuyên nghiệp có lương hợp lệ."),
        Bullets([
            f"Công nghệ: {', '.join(s.top_langs)} là ba ngôn ngữ dùng nhiều nhất; mức dùng và mức ngưỡng mộ gần như không liên hệ (Spearman 0,12); một số ngôn ngữ thường được dùng chung thành cụm.",
            f"Lương: median {usd(s.median_pay)}, lệch phải (mean {usd(s.mean_pay)}); tăng từ {usd(s.median_0_2)} (0–2 năm kinh nghiệm) lên {usd(s.median_21)} (21+ năm).",
            f"Kiểm chứng: quốc gia giải thích {pct(s.r2_country * 100, 0)} biến thiên log(lương), thêm kinh nghiệm lên {pct(s.r2_country_exp * 100, 0)}, thêm 15 ngôn ngữ chỉ cộng {fmt_num((s.r2_full - s.r2_country_exp) * 100)} điểm phần trăm.",
            f"Việt Nam: median {usd(s.vn_median)}, xếp thứ {s.vn_rank}/{s.n_countries} nước đủ mẫu; chỉ {s.vn_n} dòng lương nên mang tính tham khảo.",
            f"AI: {pct(s.ai_daily_pct, 0)} người trả lời dùng AI hằng ngày; cụm 'problem solving' xuất hiện trong {pct(s.problem_solving_pct)} câu trả lời về kỹ năng còn giá trị.",
        ]),
        Para(s.message, lead="Thông điệp chính."),
        Para("Từ khóa: trực quan hóa dữ liệu, Stack Overflow Developer Survey, xu hướng công nghệ, mức lương, hồi quy, data storytelling.", italic=True),
        Break(),
    ]


def body_blocks(s: SummaryData) -> list:
    """Toàn bộ nội dung chính theo thứ tự báo cáo, đã thay tham chiếu bảng và hình."""
    return resolve_refs(abstract_blocks(s) + chapters_1_2(s) + chapter3(s) + chapter4(s) + chapters_5_6(s))


def cover_info() -> Cover:
    """Thông tin trang bìa theo mẫu của trường."""
    leader, member = "Nhóm trưởng", "Thành viên"
    members = (Member("Vũ Viết Huy", "23010699", "0346530705", leader), Member("Lê Đức Duy", "23010772", "0326091105", member),
               Member("Lê Mạnh Hùng", "23010123", "0981015261", member), Member("Nguyễn Bá Huy", "23010806", "0858083524", member))
    return Cover("ĐẠI HỌC PHENIKAA", "TRƯỜNG CÔNG NGHỆ THÔNG TIN PHENIKAA", "BÀI TẬP LỚN", "TRỰC QUAN HÓA DỮ LIỆU", (TITLE.upper(), SUBTITLE.upper()),
                 "TS. Nguyễn Ngọc Giang", members, "Trực quan hoá dữ liệu-1-1-26(N01)", "Hà Nội, tháng 10 năm 2026")


def add_front(doc, cover: Cover, toc: list, figs: list, tabs: list, pages: dict) -> None:
    """Các trang đầu theo thứ tự mẫu: thành viên và phân công, mục lục, danh mục bảng, danh mục hình, thuật ngữ."""
    add_front_grid(doc, member_grid(cover.members, MEMBER_TITLE))
    for grid in task_grids(cover.members, TASK_TITLE):
        add_front_grid(doc, grid)
    add_toc(doc, toc, TOC_TITLE, new_page=True)
    for title, items in ((TAB_LIST_TITLE, tabs), (FIG_LIST_TITLE, figs)):
        add_toc(doc, [(text, 2, pages.get(text, "")) for text in items], title, new_page=True, figures=True)
    add_front_grid(doc, term_grid(TERM_TITLE), new_page=True)


def build(pages: dict) -> object:
    """Dựng tài liệu; pages ánh xạ chữ của mục hoặc chú thích tới số trang hiển thị (lượt 1 để trống)."""
    s = load_summary()
    blocks = body_blocks(s)
    figs, tabs = caption_entries(blocks)
    cover = cover_info()
    front = [title.upper() for title in (MEMBER_TITLE, TASK_TITLE, TAB_LIST_TITLE, FIG_LIST_TITLE, TERM_TITLE)]
    heads = [(text, 1) for text in front] + heading_entries(blocks)
    doc = new_document()
    doc.core_properties.title, doc.core_properties.author = TITLE, TEAM
    add_cover(doc, cover)
    doc.add_section(WD_SECTION.NEW_PAGE)
    add_front(doc, cover, [(text, level, pages.get(text, "")) for text, level in heads], figs, tabs, pages)
    doc.add_section(WD_SECTION.NEW_PAGE)
    render_blocks(doc, blocks)
    finish_sections(doc)
    return doc, [text for text, _ in heads] + figs + tabs, head_of_body(blocks)


def head_of_body(blocks: list) -> str:
    """Chữ của tiêu đề đầu tiên phần nội dung (trang Ả Rập số 1)."""
    return heading_entries(blocks)[0][0]


def display_pages(found: dict, first_body: int) -> dict:
    """Đổi trang vật lý sang số hiển thị: La Mã trước phần nội dung, Ả Rập từ 1 trong nội dung."""
    return {key: (str(page - first_body + 1) if page >= first_body else to_roman(page)) for key, page in found.items()}


def to_pdf(docx_path: Path, out_dir: Path) -> Path:
    """Chuyển docx sang PDF bằng LibreOffice để đếm trang."""
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(docx_path)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_dir / f"{docx_path.stem}.pdf"


def pdf_pages(pdf: Path) -> list:
    """Văn bản từng trang của PDF (dòng đã chuẩn hóa khoảng trắng)."""
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], check=True, capture_output=True, text=True).stdout
    pages = text.split("\f")[:-1] if text.endswith("\f") else text.split("\f")
    return [[" ".join(line.split()) for line in page.splitlines() if line.strip()] for page in pages]


def locate(entries: list, pages: list) -> dict:
    """Tìm trang chứa từng mục: dòng bằng đúng tên mục (hoặc bắt đầu bằng tiền tố dài), lấy lần xuất hiện cuối."""
    found = {}
    for entry in entries:
        key = " ".join(entry.split())
        for number, lines in enumerate(pages, start=1):
            hit = any(line == key or (len(key) > MATCH_PREFIX and line.startswith(key[:MATCH_PREFIX])) for line in lines)
            if hit:
                found[entry] = number
    return found


def main() -> None:
    """Dựng 2 lượt, kiểm tra số trang tối thiểu và lưu báo cáo."""
    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        first, entries, body_head = build({})
        draft = tmp_dir / "draft.docx"
        first.save(draft)
        found = locate(entries + [body_head], pdf_pages(to_pdf(draft, tmp_dir)))
        pages = display_pages(found, found[body_head])
        final, _, _ = build(pages)
        final.save(OUT_DOCX)
        total = len(pdf_pages(to_pdf(OUT_DOCX, tmp_dir)))
    missing = [e for e in entries if e not in pages]
    print(f"Đã lưu {OUT_DOCX}: {total} trang (tối thiểu {MIN_PAGES}); mục không tìm thấy số trang: {len(missing)}")
    for text in missing[:10]:
        print("  thiếu:", text)
    if total < MIN_PAGES:
        raise SystemExit(f"Chưa đủ {MIN_PAGES} trang")


if __name__ == "__main__":
    main()
