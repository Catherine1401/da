"""Nội dung chương 5 (AI và câu chuyện dữ liệu), chương 6 (kết luận), tài liệu tham khảo và phụ lục."""
from data import SummaryData, fmt_int, fmt_num
from docx_kit import Break, Bullets, Head, Para, Tab
from report_common import figure, join_names, pct, table, usd

TOP_WORDS_TABLE = 15
APPX_WORDS = 30
REFERENCES = (
    "Stack Overflow (2025). Stack Overflow Developer Survey 2025: tệp results.csv và schema.csv. https://github.com/StackExchange/Survey (thư mục packages/archive/2025).",
    "Nguyễn Ngọc Giang. Học phần CSE702060 – Trực quan hóa dữ liệu: các bài giảng Cơ sở của trực quan hóa dữ liệu, Các biểu đồ cơ bản, Choropleth map, Heatmap, Ridgeline, Spider chart, WordCloud, Dữ liệu phân cấp – mạng – luồng, Kể chuyện bằng dữ liệu, Data Dashboard với Streamlit. Phenikaa School of Computing.",
    "Efron, B. (1979). Bootstrap methods: another look at the jackknife. The Annals of Statistics, 7(1), 1–26.",
    "Seabold, S., Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with Python. Proceedings of the 9th Python in Science Conference.",
    "Hagberg, A., Schult, D., Swart, P. (2008). Exploring network structure, dynamics, and function using NetworkX. Proceedings of the 7th Python in Science Conference.",
    "Okabe, M., Ito, K. (2008). Color Universal Design (CUD): how to make figures and presentations that are friendly to colorblind people.",
    "Các thư viện Python: pandas 2.3.3, numpy 2.2.6, scipy 1.15.3, matplotlib 3.10.9, seaborn 0.13.2, plotly 7.1.0, statsmodels 0.15.0, networkx 3.4.2, wordcloud 1.9.6, joypy 0.2.6, python-docx 1.2.0, python-pptx 1.0.2 (phiên bản chốt trong requirements.txt).",
)


TOOL_NAMES = ("python", "javascript", "java", "rust", "react", "sql", "typescript", "docker", "kubernetes", "aws")
SYSTEM_DESIGN_PCT = 2.1


def cloud_text(words, s: SummaryData) -> str:
    """Đoạn phân tích thêm cho wordcloud, mọi số lấy từ bảng tần suất và tóm tắt."""
    top = ", ".join(words.head(8).word)
    ai = words[words.word == "ai"]
    tools = words[words.word.isin(TOOL_NAMES)].head(1)
    tool_text = (f"Tên công cụ cụ thể xuất hiện ít hơn nhiều: từ đứng đầu trong số đó là '{tools.word.iloc[0]}' chỉ có trong {pct(tools.pct.iloc[0])} câu trả lời."
                 if len(tools) else "Không có tên công cụ nào nằm trong 200 từ xuất hiện nhiều nhất.")
    return (f"Các từ lớn nhất gồm {top}. Từ viết tắt 'ai' được giữ lại dù chỉ có hai chữ cái vì mang nghĩa riêng; nó xuất hiện trong {pct(ai.pct.iloc[0])} câu trả lời. "
            f"Kiểm tra trực tiếp trong văn bản gốc: cụm 'problem solving' (kể cả viết 'problem-solving') có trong {pct(s.problem_solving_pct)} câu trả lời, 'critical thinking' có trong {pct(s.critical_thinking_pct)} và 'system design' có trong {pct(SYSTEM_DESIGN_PCT)}. {tool_text}")


def q9_section(s: SummaryData) -> list:
    """Mục 5.1 và 5.2: AI trong công việc và Q9."""
    words = table("f9_2")
    word_rows = [(r.word, fmt_int(r.responses), pct(r.pct)) for r in words.head(TOP_WORDS_TABLE).itertuples()]
    return [
        Head("5. AI và kỹ năng còn giá trị, câu chuyện dữ liệu tổng hợp", 1),
        Head("5.1. AI trong công việc của lập trình viên", 2),
        Para(f"Trong {fmt_int(s.ai_daily_pct_n)} người trả lời câu hỏi về việc dùng công cụ AI, {pct(s.ai_daily_pct, 0)} dùng AI hằng ngày. Ở mức vai trò (Chương 4), tỷ lệ dùng AI hằng ngày từ 29% (Embedded) đến 74% (AI/ML engineer), và không liên hệ rõ với mức lương (hệ số Spearman 0,08). "
             "Nói cách khác, AI đã trở thành công cụ hằng ngày của gần một nửa số người trả lời, nhưng việc dùng AI nhiều không đi cùng mức lương cao ở cấp vai trò."),
        Head("5.2. Kỹ năng nào còn giá trị trong 3–5 năm tới (Q9)", 2),
        Para("Câu hỏi mở của khảo sát yêu cầu người trả lời nêu kỹ năng mà họ tin là còn giá trị trong 3–5 năm tới. Có 22.540 câu trả lời; mỗi từ được đếm một lần cho mỗi câu trả lời, đã bỏ từ dừng tiếng Anh, từ chung chung (như 'will', 'skills', 'need') và gộp dạng số nhiều với số ít."),
        *figure("f9_1", "cloud", [cloud_text(words, s)]),
        *figure("f9_2", "words", ["Bảng tần suất ở [[tab:words]] cho biết tỷ lệ chính xác."]),
        Tab("15 từ khóa xuất hiện nhiều nhất trong câu trả lời về kỹ năng", ["Từ khóa", "Số câu trả lời", "Tỷ lệ"], word_rows, [4, 3, 2.5], "words"),
        Para("Hạn chế của phép đếm từ: một từ đơn lẻ mất ngữ cảnh (ví dụ 'code' có thể nằm trong 'understanding code' hoặc 'writing code'), câu trả lời dài ngắn khác nhau rất xa, và người trả lời là người đang dùng Stack Overflow nên có thể thiên về nghề nghiệp kỹ thuật. Kết quả chỉ là ý kiến tự do của người trả lời, không phải dự báo thị trường."),
    ]


def story_section(s: SummaryData) -> list:
    """Mục 5.3: câu chuyện dữ liệu theo cấu trúc của bài giảng."""
    return [
        Head("5.3. Câu chuyện dữ liệu tổng hợp", 2),
        Para("Theo bài giảng Data Storytelling, câu chuyện dữ liệu gồm bối cảnh, vấn đề, phát hiện, bằng chứng và kết luận. Phần này kể lại toàn bộ phân tích theo cấu trúc đó, mỗi ý dẫn tới biểu đồ chứng minh.", italic=True),
        Para(f"Khảo sát Stack Overflow 2025 có {fmt_int(s.n_all)} phản hồi, {pct(s.pct_pro, 0)} là lập trình viên chuyên nghiệp, nhiều nhất ở Mỹ, Đức và Ấn Độ; Việt Nam chỉ có 145 phản hồi ([[fig:f1_3]]). Sinh viên và lập trình viên mới ở Việt Nam cần trả lời hai câu hỏi: học công nghệ nào, và kỳ vọng mức lương ra sao.", lead="Bối cảnh."),
        Para("Các nguồn tư vấn thường đồng nhất 'công nghệ phổ biến' với 'công nghệ nên học' và 'công nghệ trả lương cao'. Dữ liệu cho phép kiểm tra hai giả định ngầm này: phổ biến có đồng nghĩa với được ngưỡng mộ không, và ngôn ngữ có đi cùng mức lương cao hơn không.", lead="Vấn đề."),
        Bullets([
            f"{join_names(s.top_langs)} là ba ngôn ngữ dùng nhiều nhất ([[fig:f2_1]]), nhưng mức dùng và mức ngưỡng mộ gần như không liên hệ (Spearman 0,12): ngôn ngữ được ngưỡng mộ nhất trong nhóm khá phổ biến là {join_names(s.admired_langs)} ([[fig:f3_1]]).",
            "Một số ngôn ngữ thường được dùng chung và tạo thành cụm, gợi ý các ngôn ngữ có thể học cùng nhau ([[fig:f4_1]]).",
            f"Lương lệch phải: median {usd(s.median_pay)} thấp hơn mean {usd(s.mean_pay)} ([[fig:f5_1]]); lương tăng đều theo kinh nghiệm, từ {usd(s.median_0_2)} (0–2 năm) lên {usd(s.median_21)} (21+ năm) ([[fig:f5_3]]).",
            f"Quốc gia giải thích {pct(s.r2_country * 100, 0)} biến thiên log(lương), thêm kinh nghiệm lên {pct(s.r2_country_exp * 100, 0)}, thêm 15 ngôn ngữ chỉ cộng {fmt_num((s.r2_full - s.r2_country_exp) * 100)} điểm phần trăm ([[fig:f6_3]]).",
            f"Việt Nam xếp thứ {s.vn_rank}/{s.n_countries} về median lương ({usd(s.vn_median)}, n = {s.vn_n}), mẫu nhỏ nên chỉ tham khảo ([[fig:f7_2]]).",
            f"{pct(s.ai_daily_pct, 0)} người trả lời dùng AI hằng ngày, nhưng mức dùng AI không liên hệ với lương giữa các vai trò ([[fig:f8_1]]); cụm 'problem solving' có trong {pct(s.problem_solving_pct)} và 'critical thinking' có trong {pct(s.critical_thinking_pct)} câu trả lời về kỹ năng còn giá trị ([[fig:f9_1]]).",
        ]),
        Para("Mỗi phát hiện dựa trên một biểu đồ có ghi cỡ mẫu và bộ lọc; các so sánh lương đi kèm khoảng tin cậy bootstrap, và hệ số hồi quy đi kèm khoảng tin cậy 95%. Kết quả hồi quy được diễn đạt là mô tả, không phải nhân quả.", lead="Bằng chứng."),
        Para(s.message, lead="Kết luận."),
        Break(),
    ]


def chapter6(s: SummaryData) -> list:
    """Chương 6: kết luận, khuyến nghị, hạn chế, hướng phát triển."""
    return [
        Head("6. Kết luận và hạn chế", 1),
        Head("6.1. Kết luận", 2),
        Para("Đồ án đã trả lời chín câu hỏi bằng 23 biểu đồ, gồm các dạng bar, histogram, line, scatter, treemap, heatmap, ridgeline, spider, wordcloud, choropleth, network và Sankey. Ba kết luận chính: (1) công nghệ phổ biến không đồng nghĩa với được ngưỡng mộ; (2) lương lệch phải mạnh nên cần dùng median; (3) quốc gia và kinh nghiệm giải thích biến thiên của lương nhiều hơn hẳn ngôn ngữ lập trình."),
        Head("6.2. Khuyến nghị cho sinh viên và lập trình viên mới ở Việt Nam", 2),
        Bullets(list(s.recommendations)),
        Head("6.3. Hạn chế", 2),
        Bullets(list(s.limitations) + [
            "Wordcloud và bảng tần suất không xét ngữ cảnh của câu trả lời; các cụm ngôn ngữ phụ thuộc ngưỡng chọn cạnh (2% người trả lời và lift 1,5).",
            "Mức ngưỡng mộ phụ thuộc cách chọn mẫu số (người đang dùng và có trả lời mục ngưỡng mộ); chọn cách khác có thể thay đổi giá trị tuyệt đối nhưng không thay đổi thứ tự lớn.",
        ]),
        Head("6.4. Hướng phát triển", 2),
        Bullets([
            "Thêm dữ liệu khảo sát các năm trước (2024, 2023 đều có tệp results.csv trên cùng kho lưu trữ) để đo xu hướng theo thời gian thật, sau khi chuẩn hóa các cột khác nhau giữa các năm.",
            "Điều chỉnh lương theo sức mua (PPP) để so sánh công bằng hơn giữa các nước, đặc biệt khi so Việt Nam với Mỹ và châu Âu.",
            "Mở rộng mô hình hồi quy với vai trò, quy mô công ty và hình thức làm việc từ xa; thử mô hình hỗn hợp theo nước để tận dụng các nước có mẫu nhỏ.",
            "Xây dashboard tương tác (ví dụ Streamlit) để người học tự lọc theo nước, vai trò và kinh nghiệm.",
        ]),
        Break(),
    ]


def references() -> list:
    """Tài liệu tham khảo."""
    return [Head("Tài liệu tham khảo", 1), Bullets([f"[{i}] {text}" for i, text in enumerate(REFERENCES, 1)]), Break()]


def appendix() -> list:
    """Phụ lục A–D: bảng chi tiết và hướng dẫn tái lập."""
    lang = table("f3_1").sort_values("have_pct", ascending=False)
    lang_rows = [(r.value, fmt_int(r.users), pct(r.have_pct), pct(r.want_pct), pct(r.admired_pct)) for r in lang.itertuples()]
    country = table("f7_1").sort_values("median", ascending=False)
    country_rows = [(r.name, fmt_int(r.n), fmt_int(r.median), f"{fmt_int(r.lo)}–{fmt_int(r.hi)}") for r in country.itertuples()]
    coef = table("f6_4").sort_values("pct", ascending=False)
    coef_rows = [(r.lang, f"{fmt_num(r.pct)}%", f"{fmt_num(r.lo)}% đến {fmt_num(r.hi)}%") for r in coef.itertuples()]
    words = table("f9_2").head(APPX_WORDS)
    word_rows = [(i, r.word, fmt_int(r.responses), pct(r.pct)) for i, r in enumerate(words.itertuples(), 1)]
    return [
        Head("Phụ lục", 1),
        Head("Phụ lục A. Bảng đầy đủ các ngôn ngữ", 2),
        Para("[[tab:appxlang]] liệt kê số người dùng, tỷ lệ đang dùng, muốn dùng và ngưỡng mộ của 42 ngôn ngữ có đủ dữ liệu, sắp theo tỷ lệ đang dùng."),
        Tab("42 ngôn ngữ: đang dùng, muốn dùng, ngưỡng mộ", ["Ngôn ngữ", "Số người dùng", "Đang dùng", "Muốn dùng", "Ngưỡng mộ"], lang_rows, [3.2, 2.4, 2, 2, 2], "appxlang"),
        Head("Phụ lục B. Median lương theo nước", 2),
        Para("[[tab:appxcountry]] cho median lương và khoảng tin cậy bootstrap 95% của 62 nước có ít nhất 30 dòng lương hợp lệ, sắp giảm dần."),
        Tab("Median lương của 62 nước", ["Quốc gia", "n", "Median (USD)", "Khoảng tin cậy 95%"], country_rows, [3.5, 1.6, 3, 4], "appxcountry"),
        Head("Phụ lục C. Hệ số hồi quy theo ngôn ngữ", 2),
        Para("[[tab:appxcoef]] liệt kê hệ số hồi quy của 15 ngôn ngữ (phần trăm chênh lệch lương so với người không dùng, đã kiểm soát nước và kinh nghiệm)."),
        Tab("Chênh lệch lương (%) đi cùng việc dùng ngôn ngữ, đã kiểm soát nước và kinh nghiệm", ["Ngôn ngữ", "Ước lượng", "Khoảng tin cậy 95%"], coef_rows, [3, 3, 4.5], "appxcoef"),
        Head("Phụ lục D. Từ khóa trong câu trả lời về kỹ năng", 2),
        Para("[[tab:appxwords]] liệt kê 30 từ khóa xuất hiện nhiều nhất trong câu trả lời về kỹ năng."),
        Tab("30 từ khóa xuất hiện nhiều nhất", ["Hạng", "Từ khóa", "Số câu trả lời", "Tỷ lệ"], word_rows, [1.4, 3.5, 3, 2.4], "appxwords"),
        Head("Phụ lục E. Hướng dẫn tái lập kết quả", 2),
        Bullets([
            "Tạo môi trường: python -m venv .venv, kích hoạt rồi chạy pip install -r requirements.txt.",
            "Chạy notebook: python build/make_nb.py (ghép các phần trong notebook/parts thành deliverables/so2025.ipynb, chạy từ đầu; tự tải results.csv nếu chưa có trong thư mục data).",
            "Dựng slide: python build/build_pptx.py; dựng báo cáo: python build/build_docx.py (đếm trang bằng LibreOffice).",
            "Mọi số liệu trong slide và báo cáo được đọc từ thư mục out/ do notebook sinh ra, nên ba sản phẩm luôn khớp nhau.",
        ]),
    ]


def chapters_5_6(s: SummaryData) -> list:
    """Gộp chương 5, 6, tài liệu tham khảo và phụ lục."""
    return q9_section(s) + story_section(s) + chapter6(s) + references() + appendix()
