"""Dựng báo cáo docx từ ảnh, chú giải và bảng số do notebook sinh ra; dựng 2 lượt để mục lục có số trang."""
import subprocess
import sys
import tempfile
from pathlib import Path

from docx.shared import Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data import ROOT, SummaryData, fmt_int, fmt_num, load_note, load_summary
from docx_kit import (Break, Bullets, Fig, Head, Para, Tab, add_page_break, add_toc, heading_entries, new_document,
                      render_blocks, resolve_refs)
from report_ch12 import chapters_1_2
from report_ch3 import chapter3
from report_ch4 import chapter4
from report_ch56 import chapters_5_6
from report_common import pct, usd

OUT_DOCX = ROOT / "deliverables" / "report.docx"
MIN_PAGES = 30
TITLE = "Phân tích xu hướng công nghệ và mức lương lập trình viên"
SUBTITLE = "Qua khảo sát Stack Overflow Developer Survey 2025"
COURSE = "Học phần CSE702060 – Trực quan hóa dữ liệu · Phenikaa School of Computing"
LECTURER = "Giảng viên: Nguyễn Ngọc Giang"
TEAM = "Nhóm 8"
MEMBERS = ("Lê Đức Duy – 23010772", "Vũ Viết Huy – 23010699", "Lê Mạnh Hùng – 23010123", "Nguyễn Bá Huy – 23010806")
DATE_TEXT = "Tháng 10 năm 2026"
MATCH_PREFIX = 40
ABSTRACT_TITLE = "Tóm tắt báo cáo"
TOC_TITLE = "Mục lục"
FIG_LIST_TITLE = "Danh mục hình"
TAB_LIST_TITLE = "Danh mục bảng"


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


def caption_entries(blocks: list) -> tuple:
    """Danh sách chú thích hình và bảng theo thứ tự (để lập danh mục)."""
    figs, tabs = [], []
    for block in blocks:
        if isinstance(block, Fig):
            figs.append(f"Hình {len(figs) + 1}. {load_note(block.code).title}")
        elif isinstance(block, Tab):
            tabs.append(f"Bảng {len(tabs) + 1}. {block.caption}")
    return figs, tabs


def add_cover(doc) -> None:
    """Trang bìa."""
    for _ in range(5):
        doc.add_paragraph()
    for text, size, bold in ((TITLE, 26, True), (SUBTITLE, 16, False), ("", 0, False), (COURSE, 12, False), (LECTURER, 12, False), (TEAM, 14, True)):
        para = doc.add_paragraph()
        run = para.add_run(text)
        run.bold = bold
        if size:
            run.font.size = Pt(size)
    for member in MEMBERS:
        doc.add_paragraph(member)
    doc.add_paragraph()
    doc.add_paragraph(DATE_TEXT)
    add_page_break(doc)


def build(pages: dict) -> object:
    """Dựng tài liệu; pages ánh xạ tên mục hoặc chú thích tới số trang (lượt 1 để trống)."""
    s = load_summary()
    blocks = body_blocks(s)
    figs, tabs = caption_entries(blocks)
    doc = new_document()
    doc.core_properties.title, doc.core_properties.author = TITLE, TEAM
    add_cover(doc)
    add_toc(doc, [(text, level, pages.get(text, "")) for text, level in heading_entries(blocks)], TOC_TITLE)
    add_page_break(doc)
    add_toc(doc, [(text, 1, pages.get(text, "")) for text in figs], FIG_LIST_TITLE)
    doc.add_paragraph()
    add_toc(doc, [(text, 1, pages.get(text, "")) for text in tabs], TAB_LIST_TITLE)
    add_page_break(doc)
    render_blocks(doc, blocks, {"fig": 0, "tab": 0})
    return doc, [text for text, _ in heading_entries(blocks)] + figs + tabs


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
        first, entries = build({})
        draft = tmp_dir / "draft.docx"
        first.save(draft)
        pages = locate(entries, pdf_pages(to_pdf(draft, tmp_dir)))
        final, _ = build(pages)
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
