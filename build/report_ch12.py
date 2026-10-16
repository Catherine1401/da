"""Nội dung phần giới thiệu và chương 1 (dữ liệu, tiền xử lý, hồ sơ người trả lời)."""
from data import SummaryData, fmt_int
from docx_kit import Bullets, Break, Head, Para, Tab
from report_common import figure, join_names, pct, short_branch, table

VARIABLES = (
    ("MainBranch", "Mức độ gắn với nghề lập trình (lập trình viên chuyên nghiệp, đang học, sở thích…)"),
    ("Age", "Nhóm tuổi"),
    ("Country", "Nước đang sống"),
    ("DevType", "Vai trò công việc hiện tại (full-stack, back-end, architect…)"),
    ("WorkExp", "Số năm kinh nghiệm làm việc chuyên nghiệp"),
    ("ConvertedCompYearly", "Tổng thu nhập năm đã quy đổi sang USD"),
    ("AISelect", "Mức độ dùng công cụ AI trong phát triển phần mềm"),
    ("JobSat", "Mức hài lòng công việc (thang 0–10)"),
    ("LanguageHaveWorkedWith", "Ngôn ngữ lập trình đang dùng (chọn nhiều đáp án)"),
    ("LanguageWantToWorkWith", "Ngôn ngữ muốn dùng trong năm tới (chọn nhiều đáp án)"),
    ("LanguageAdmired", "Ngôn ngữ đang dùng và muốn tiếp tục dùng (được ngưỡng mộ)"),
    ("DatabaseHaveWorkedWith", "Cơ sở dữ liệu đang dùng"),
    ("PlatformHaveWorkedWith", "Cloud và nền tảng đang dùng"),
    ("WebframeHaveWorkedWith", "Web framework đang dùng"),
    ("AIOpen", "Câu hỏi mở: kỹ năng còn giá trị trong 3–5 năm tới"),
)


def chapter1(s: SummaryData) -> list:
    """Phần giới thiệu: giới thiệu bối cảnh, mục tiêu, câu hỏi và cấu trúc báo cáo."""
    return [
        Head("Giới thiệu", 1),
        Head("1. Bối cảnh", 2),
        Para("Mỗi năm, Stack Overflow thực hiện một cuộc khảo sát lớn với cộng đồng lập trình viên trên toàn thế giới về công nghệ họ sử dụng, công cụ họ yêu thích, công việc và thu nhập. "
             f"Bộ dữ liệu năm 2025 gồm {fmt_int(s.n_all)} phản hồi, trong đó {pct(s.pct_pro, 0)} là lập trình viên chuyên nghiệp. Đây là một trong những nguồn dữ liệu công khai lớn nhất về hệ sinh thái lập trình và là nguồn tham khảo quen thuộc của sinh viên, nhà tuyển dụng và các nhóm kỹ thuật."),
        Para("Với sinh viên và lập trình viên mới, hai câu hỏi thực tế nhất là nên học công nghệ nào và có thể kỳ vọng mức lương ra sao. Hai câu hỏi này thường được trả lời bằng ý kiến cá nhân hoặc các bảng xếp hạng đơn giản. "
             "Dữ liệu khảo sát cho phép trả lời có bằng chứng hơn, nhưng cần trực quan hóa cẩn thận vì dữ liệu lớn, nhiều cột chọn nhiều đáp án, lương lệch rất mạnh và mẫu không đồng đều giữa các nước."),
        Head("2. Mục tiêu và đối tượng", 2),
        Para("Bài tập lớn có ba mục tiêu: (1) mô tả xu hướng công nghệ qua ba chỉ số là đang dùng, muốn dùng và được ngưỡng mộ; (2) mô tả mức lương và các yếu tố đi cùng mức lương; (3) kiểm chứng bằng một mô hình định lượng đơn giản xem yếu tố nào giải thích lương nhiều nhất."),
        Para("Theo cách đặt mục tiêu giao tiếp của bài giảng Data Storytelling, đối tượng của sản phẩm là sinh viên và lập trình viên mới ở Việt Nam. Mục tiêu giao tiếp: sau khi xem, họ sẽ hiểu công nghệ nào đang được dùng và ngưỡng mộ, mức lương đi cùng những yếu tố nào, từ đó có thể chọn công nghệ để học và đặt kỳ vọng lương hợp lý.", italic=True),
        Head("3. Câu hỏi phân tích", 2),
        Bullets([
            "Q1. Ai là người trả lời khảo sát, và mẫu có lệch không?",
            "Q2. Công nghệ nào (ngôn ngữ, cơ sở dữ liệu, cloud, web framework) đang được dùng nhiều nhất?",
            "Q3. Công nghệ dùng nhiều có được ngưỡng mộ và muốn dùng nhiều không?",
            "Q4. Các ngôn ngữ đi cùng nhau thế nào, và người đang dùng ngôn ngữ này muốn dùng thêm ngôn ngữ nào?",
            "Q5. Phân phối lương theo vai trò và theo số năm kinh nghiệm ra sao?",
            "Q6. Công nghệ nào đi cùng mức lương cao, sau khi tách ảnh hưởng của quốc gia và kinh nghiệm?",
            "Q7. Lương khác nhau thế nào giữa các nước, và Việt Nam đứng ở đâu?",
            "Q8. Các vai trò khác nhau thế nào về lương, kinh nghiệm, mức dùng AI và mức hài lòng?",
            "Q9. Người trả lời cho rằng kỹ năng nào còn giá trị trong 3–5 năm tới?",
        ]),
        Head("4. Phạm vi và cấu trúc báo cáo", 2),
        Para("Phạm vi chỉ gồm dữ liệu khảo sát năm 2025 nên không đo được thay đổi theo thời gian; vì vậy khái niệm xu hướng được thay bằng ba chỉ số nói trên. Bài tập lớn không xây dashboard tương tác mà tập trung vào ba sản phẩm: notebook phân tích, bộ slide thuyết trình và báo cáo này."),
        Para("Báo cáo gồm phần giới thiệu, bốn chương và phần kết luận. Chương 1 mô tả dữ liệu và cách tiền xử lý. Chương 2 phân tích xu hướng công nghệ. Chương 3 phân tích mức lương, gồm cả mô hình hồi quy kiểm chứng. Chương 4 bàn về AI và kỹ năng tương lai rồi kể lại câu chuyện dữ liệu hoàn chỉnh. Phần kết luận nêu kết luận, khuyến nghị, hạn chế và hướng phát triển. Mỗi biểu đồ có ba phần: cách đọc, nhận xét và insight."),
    ]


def data_overview(s: SummaryData) -> list:
    """Mục 2.1 và 2.2: nguồn, cấu trúc và các biến được dùng."""
    fill = table("t_fill").set_index("Cột")["Tỷ lệ có trả lời (%)"]
    rows = [(name, desc, pct(fill[name], 1)) for name, desc in VARIABLES]
    return [
        Break(),
        Head("1. Dữ liệu và tiền xử lý", 1),
        Head("1.1. Nguồn dữ liệu và cấu trúc", 2),
        Para("Dữ liệu lấy từ kho lưu trữ chính thức của Stack Overflow trên GitHub, gồm hai tệp: results.csv (câu trả lời) và schema.csv (mô tả câu hỏi). "
             f"Dữ liệu được công bố công khai theo [1]. Tệp results.csv có {fmt_int(s.n_all)} dòng và 172 cột, mỗi dòng là một người trả lời với mã ResponseId không trùng lặp. Tệp schema.csv có 139 dòng mô tả câu hỏi, gồm bốn kiểu: xếp hạng (49 dòng), chọn một hoặc nhiều đáp án (48), văn bản tự do (29) và ma trận (13)."),
        Para("Các cột thuộc ba nhóm. Nhóm thông tin nhân khẩu và công việc (tuổi, nước, vai trò, kinh nghiệm, thu nhập) có dạng số hoặc phân loại. Nhóm công nghệ (ngôn ngữ, cơ sở dữ liệu, cloud, web framework…) là các cột chọn nhiều đáp án, các đáp án nối nhau bằng dấu chấm phẩy, ví dụ 'Dart;HTML/CSS;JavaScript;TypeScript'. Nhóm câu hỏi mở chứa văn bản tự do. "
             "Cột ConvertedCompYearly là lương đã được quy đổi sang USD: trong 8.780 dòng có đơn vị tiền là USD, có 6.319 dòng có cả giá trị khai báo và giá trị quy đổi, và hai giá trị bằng nhau ở cả 6.319 dòng; các tiền tệ khác (EUR, UAH…) đã được quy đổi sẵn."),
        Head("1.2. Các biến được sử dụng", 2),
        Para("Trong 172 cột, báo cáo chỉ dùng 15 biến liên quan trực tiếp tới các câu hỏi phân tích, liệt kê ở [[tab:vars]] cùng tỷ lệ người có trả lời mỗi biến."),
        Tab("Các biến được sử dụng và tỷ lệ người có trả lời", ["Biến", "Ý nghĩa", "Có trả lời"], rows, [3.2, 6.8, 1.6], "vars"),
    ]


def missing_and_rules(s: SummaryData) -> list:
    """Mục 2.3 và 2.4: dữ liệu thiếu và quy tắc làm sạch."""
    rules = [
        ("Đọc dữ liệu", "Đọc bằng mã hóa utf-8-sig vì tệp có BOM", f"{fmt_int(s.n_all)} dòng"),
        ("Người có lương", "ConvertedCompYearly có giá trị", "23.947 dòng"),
        ("Lọc ngoại lai", "Giữ lương từ 1.000 đến 500.000 USD (loại 724 dòng dưới 1.000 USD và 179 dòng trên 500.000 USD, trong đó 46 dòng trên 1 triệu USD)", "23.044 dòng (96,2%)"),
        ("Lập trình viên chuyên nghiệp", "MainBranch là 'I am a developer by profession'", f"{fmt_int(s.n_sal)} dòng"),
        ("Nước đủ mẫu", "Chỉ so sánh nước có ít nhất 30 dòng lương", f"{s.n_countries} nước"),
        ("Vai trò đủ mẫu", "Giữ vai trò có ít nhất 200 dòng lương, bỏ nhóm 'Other'", "12 vai trò"),
        ("Cột chọn nhiều đáp án", "Tách theo dấu ';'; tỷ lệ tính trên số người có trả lời cột đó", "Mẫu số thay đổi theo cột"),
        ("Tên nước", "Đổi sang mã ISO-3; 13 tên không khớp được ánh xạ thủ công, 'Nomadic' bị loại khỏi bản đồ", "177 tên nước"),
        ("Kinh nghiệm", "Dùng WorkExp, chia 5 nhóm: 0–2, 3–5, 6–10, 11–20, 21+ năm", "19.381 dòng có WorkExp"),
    ]
    return [
        Head("1.3. Dữ liệu thiếu", 2),
        Para("Dữ liệu khảo sát có nhiều ô trống vì người trả lời không bắt buộc trả lời mọi câu và nhiều câu chỉ hiện ra khi chọn đáp án trước đó. Trong 172 cột, chỉ 8 cột có tỷ lệ trả lời từ 90% trở lên, 93 cột nằm trong khoảng 50–90% và 71 cột dưới 50%. "
             "Vì vậy mỗi biểu đồ trong báo cáo ghi rõ cỡ mẫu n thực sự được dùng, và tỷ lệ phần trăm luôn tính trên số người có trả lời cột đó thay vì trên toàn bộ 49.191 người."),
        Para("Một lưu ý riêng về mức ngưỡng mộ (Admired): trong những người đang dùng ít nhất một ngôn ngữ, có khoảng 4.600 người bỏ trống cả mục 'muốn dùng'. Không có cơ sở để coi họ là 'không ngưỡng mộ', nên mẫu số của mức ngưỡng mộ là những người đang dùng công nghệ đó và có trả lời mục ngưỡng mộ."),
        Head("1.4. Quy tắc làm sạch dữ liệu", 2),
        Para("Các quy tắc ở [[tab:rules]] được cố định ngay từ đầu để notebook, slide và báo cáo dùng cùng một bộ số liệu. Ngưỡng 30 dòng cho mỗi nước và 200 dòng cho mỗi vai trò là lựa chọn của nhóm nhằm tránh kết luận từ mẫu quá nhỏ; ngưỡng lương 1.000–500.000 USD giữ lại 96,2% số dòng có lương."),
        Tab("Quy tắc làm sạch và số dòng còn lại", ["Bước", "Quy tắc", "Kết quả"], [list(r) for r in rules], [2.6, 7.2, 2.8], "rules"),
        Para("Hai điểm chất lượng dữ liệu cần ghi nhận. Thứ nhất, cột WorkExp lớn hơn YearsCode ở 3.564 trong 39.869 dòng có cả hai giá trị (khoảng 9%), mâu thuẫn về logic vì kinh nghiệm làm việc không thể dài hơn thời gian đã lập trình; nhóm giữ nguyên các dòng này và dùng WorkExp vì gắn với thu nhập hơn. "
             "Thứ hai, số liệu Việt Nam chỉ có 145 phản hồi và 31 dòng có lương, nên mọi con số về Việt Nam chỉ mang tính tham khảo."),
    ]


def methods(s: SummaryData) -> list:
    """Mục 2.5: phương pháp thống kê và trực quan hóa."""
    return [
        Head("1.5. Phương pháp", 2),
        Bullets([
            "Median thay cho mean: lương lệch phải mạnh (mean cao hơn median 17% trên bảng lương đã lọc), nên median phản ánh mức điển hình tốt hơn.",
            "Khoảng tin cậy bootstrap 95% [3]: lấy mẫu lại có hoàn lại 1.000 lần, tính median mỗi lần và lấy phân vị 2,5% và 97,5%; dùng cho các biểu đồ lương.",
            "Tỷ lệ dùng, muốn dùng, ngưỡng mộ: tỷ lệ người có trả lời cột tương ứng; ngưỡng mộ là tỷ lệ trong những người đang dùng.",
            "Hệ số tương quan hạng Spearman: đo mức liên hệ đơn điệu giữa hai biến, không giả định quan hệ tuyến tính.",
            "Lift của cặp ngôn ngữ: tỷ lệ cùng dùng chia cho tích hai tỷ lệ dùng riêng; lift lớn hơn 1 nghĩa là đi cùng nhau nhiều hơn mức ngẫu nhiên.",
            "Hồi quy OLS trên log(lương) với biến quốc gia (62 nước), log(1 + WorkExp) và 15 ngôn ngữ phổ biến nhất; khoảng tin cậy dùng sai số chuẩn bền vững HC3; kiểm định F cho nhóm biến ngôn ngữ; ước lượng bằng thư viện statsmodels [4].",
        ]),
        Para("Về trực quan hóa, nhóm tuân thủ các nguyên tắc của môn học: tiêu đề nêu phát hiện chứ không chỉ mô tả, màu xám cho phần nền và một đến hai màu nhấn, cùng một màu cho cùng một ý, ghi n và bộ lọc ở chân biểu đồ, không dùng hiệu ứng 3D, và không chỉ dùng màu để mã hóa thông tin (luôn có nhãn trực tiếp). Bảng màu Okabe-Ito [6] được chọn vì an toàn cho người mù màu. Mỗi biểu đồ là một ảnh 1600 × 900 điểm ảnh dùng chung cho notebook, slide và báo cáo."),
        Para("Cách diễn đạt trong báo cáo phân biệt phát hiện (có phạm vi và cỡ mẫu rõ) với ý kiến. Các quan hệ giữa lương, quốc gia, kinh nghiệm và ngôn ngữ được diễn đạt là 'đi cùng', không phải 'gây ra', vì dữ liệu khảo sát không có thiết kế để suy ra nhân quả."),
    ]


def profile_section(s: SummaryData) -> list:
    """Mục 2.6: hồ sơ người trả lời (Q1)."""
    branch, age, country = table("f1_1"), table("f1_2"), table("f1_3")
    age_rows = ", ".join(f"{row.Age.replace(' years old', '').replace(' years or older', '+').replace('-', '–').replace('Prefer not to say', 'không muốn nói')}: {pct(row.pct)}" for row in age.itertuples())
    top5 = join_names(f"{row.Country} ({fmt_int(row[2])})" for row in country.head(5).itertuples())
    return [
        Head("1.6. Hồ sơ người trả lời (Q1)", 2),
        Para("Trước khi phân tích, cần biết mẫu khảo sát gồm những ai, vì mọi kết luận chỉ đúng với nhóm người đã trả lời. Ba biểu đồ dưới đây cho biết mức độ gắn với nghề lập trình, độ tuổi và nơi sống."),
        *figure("f1_1", "bar", ["Tỷ lệ theo từng nhóm: " + ", ".join(f"{short_branch(r.MainBranch)} {pct(r.pct)}" for r in branch.sort_values("pct", ascending=False).itertuples()) + "."]),
        *figure("f1_2", "bar_short", [f"Phân bố đầy đủ theo nhóm tuổi (trên toàn bộ người trả lời): {age_rows}."]),
        *figure("f1_3", "bar_short", [f"Năm nước đông nhất là {top5}. Việt Nam có 145 phản hồi, bằng khoảng 2% số phản hồi của Hoa Kỳ."]),
        Para("Kết luận của phần này: mẫu khảo sát chủ yếu là lập trình viên chuyên nghiệp trong độ tuổi 25–44 ở Hoa Kỳ và châu Âu. Điều này phù hợp để rút ra bức tranh chung của người đi làm, nhưng không đại diện cho sinh viên mới học và chỉ cho phép đọc số liệu Việt Nam ở mức tham khảo."),
        Break(),
    ]


def chapters_1_2(s: SummaryData) -> list:
    """Gộp phần giới thiệu và chương 1."""
    return chapter1(s) + data_overview(s) + missing_and_rules(s) + methods(s) + profile_section(s)
