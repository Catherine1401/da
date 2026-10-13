"""Nội dung chương 4: mức lương (Q5, Q6, Q7, Q8)."""
import numpy as np
import pandas as pd

from data import SummaryData, fmt_int, fmt_num
from docx_kit import Break, Head, Para, Tab
from report_common import figure, join_names, pct, table, usd

TOP_LIST = 3
RANK_TABLE = 10
MEXICO = "Mexico"
SINGAPORE = "Singapore"
REGION_COUNTRIES = ("Singapore", "Malaysia", "Philippines", "Indonesia", "Thailand", "India", "Pakistan", "Bangladesh", "Sri Lanka", "Japan", "China", "Egypt", "Kenya", "Nigeria")
MIN_SIG_LIST = 6


def with_ties(df: pd.DataFrame, column: str, label: str, count: int) -> str:
    """Danh sách top (nhãn, giá trị) và ghi rõ các hàng hòa giá trị ở hạng cuối."""
    ranked = df.sort_values(column, ascending=False)
    cut = ranked[column].iloc[count - 1]
    top = ranked[ranked[column] >= cut]
    text = join_names(f"{getattr(r, label)} ({usd(getattr(r, column))})" for r in top.itertuples())
    return text + (f" (có hòa hạng ở mức {usd(cut)})" if len(top) > count else "")


def ci(lo, hi) -> str:
    """Khoảng tin cậy dạng 'thấp–cao' kiểu Việt Nam."""
    return f"{fmt_int(lo)}–{fmt_int(hi)}"


def intro(s: SummaryData) -> list:
    """Mở đầu chương 4."""
    return [
        Head("4. Mức lương", 1),
        Para(f"Chương này dùng bảng {fmt_int(s.n_sal)} lập trình viên chuyên nghiệp có lương hợp lệ (1.000–500.000 USD). Lương là tổng thu nhập năm đã quy đổi sang USD danh nghĩa, chưa điều chỉnh sức mua. "
             "Do lương lệch phải mạnh, báo cáo dùng median và khoảng tin cậy bootstrap 95% thay cho mean. Chương gồm bốn phần: phân phối lương theo vai trò và kinh nghiệm (Q5), công nghệ đi cùng lương và hồi quy kiểm chứng (Q6), lương theo nước (Q7) và so sánh vai trò (Q8)."),
        Para("Giả thuyết cần kiểm chứng ở Q6 là quốc gia và kinh nghiệm đi cùng chênh lệch lương nhiều hơn ngôn ngữ lập trình. Giả thuyết này có lý do: ngôn ngữ phổ biến ở các nước lương cao sẽ trông như 'trả lương cao' chỉ vì người dùng sống ở nước có mặt bằng lương cao. "
             "Vì vậy các biểu đồ mô tả ở Q6 được bổ sung bằng một mô hình hồi quy có kiểm soát quốc gia và kinh nghiệm."),
    ]


def q5_section(s: SummaryData) -> list:
    """Mục 4.1: Q5 – phân phối lương."""
    stats = table("f5_1").set_index("stat").usd
    roles, exp = table("f5_2").sort_values("median", ascending=False), table("f5_3")
    top = with_ties(roles, "median", "role", TOP_LIST)
    low = join_names(f"{r.role} ({usd(r.median)})" for r in roles.tail(TOP_LIST).itertuples())
    role_rows = [(r.role, fmt_int(r.n), fmt_int(r.median)) for r in roles.itertuples()]
    exp_rows = [(str(r.exp_bin), fmt_int(r.n), fmt_int(r.median), ci(r.lo, r.hi)) for r in exp.itertuples()]
    return [
        Head("4.1. Phân phối lương theo vai trò và kinh nghiệm (Q5)", 2),
        *figure("f5_1", "hist", [f"Các mốc phân vị: phân vị 25% là {usd(stats['q1'])}, median {usd(stats['median'])}, phân vị 75% là {usd(stats['q3'])}; mean là {usd(stats['mean'])}.",
                                   f"Phần đuôi bên phải kéo dài tới 500.000 USD nhưng chiếm tỷ lệ nhỏ; một nửa số người có lương nằm trong khoảng từ {usd(stats['q1'])} đến {usd(stats['q3'])}."]),
        *figure("f5_2", "ridge", [f"Ba vai trò có median cao nhất: {top}. Ba vai trò thấp nhất: {low}.", "Chi tiết median và cỡ mẫu từng vai trò ở [[tab:roles]]."]),
        Tab("Median lương và cỡ mẫu theo vai trò", ["Vai trò", "n", "Median (USD)"], role_rows, [4.5, 2, 3], "roles"),
        *figure("f5_3", "line", [f"[[tab:exp]] cho thấy median lương tăng qua cả năm nhóm kinh nghiệm: " + ", ".join(f"{r.exp_bin} năm {usd(r.median)}" for r in exp.itertuples()) + ".",
                                   "Mức tăng lớn nhất xảy ra từ nhóm 3–5 năm lên nhóm 6–10 năm, sau đó tăng chậm dần; khoảng tin cậy hẹp ở mọi nhóm do cỡ mẫu lớn (từ 1.471 đến 6.027 người)."]),
        Tab("Median lương theo nhóm năm kinh nghiệm (WorkExp)", ["Kinh nghiệm", "n", "Median (USD)", "Khoảng tin cậy 95%"], exp_rows, [2.5, 2, 3, 4], "exp"),
    ]


def q6_descriptive() -> list:
    """Mục 4.2 (phần mô tả): median lương theo ngôn ngữ và heatmap."""
    langs = table("f6_1").sort_values("median", ascending=False)
    high = join_names(f"{r.lang} ({usd(r.median)}, n = {fmt_int(r.n)})" for r in langs.head(TOP_LIST).itertuples())
    heat = table("f6_2").set_index("lang")
    stacked = heat.stack()
    best_cells = stacked[stacked == stacked.max()].index
    worst_cell = heat.stack().idxmin()
    role_means = heat.mean().sort_values(ascending=False)
    return [
        Head("4.2. Công nghệ nào đi cùng mức lương cao (Q6)", 2),
        *figure("f6_1", "ci", [f"Ba ngôn ngữ có median cao nhất: {high}. PHP có median thấp nhất ({usd(langs.iloc[-1]['median'])}).",
                                 "Các ngôn ngữ ở giữa (từ Python đến SQL) có median rất gần nhau và khoảng tin cậy chồng lấn, nên thứ tự giữa chúng không đáng tin cậy."]),
        *figure("f6_2", "heat", [f"Ô cao nhất là {join_names(f'{a} × {b}' for a, b in best_cells)} ({usd(stacked.max())}), ô thấp nhất là {worst_cell[0]} × {worst_cell[1]} ({usd(heat.stack().min())}). "
                                   f"Theo vai trò, median trung bình trên 10 ngôn ngữ cao nhất ở {role_means.index[0]} ({usd(role_means.iloc[0])}) và thấp nhất ở {role_means.index[-1]} ({usd(role_means.iloc[-1])})."]),
    ]


def q6_regression() -> list:
    """Mục 4.2 (phần hồi quy): R² các mô hình và hệ số ngôn ngữ."""
    r2 = table("f6_3")
    steps = [None, None, None, r2.r2.iloc[3] - r2.r2.iloc[2], r2.r2.iloc[4] - r2.r2.iloc[3]]
    r2_rows = [(r.model, pct(r.r2 * 100), "–" if steps[i] is None else f"+{fmt_num(steps[i] * 100)} điểm %") for i, r in enumerate(r2.itertuples())]
    coef = table("f6_4").sort_values("pct", ascending=False)
    medians = table("f7_1")["median"]
    country_ratio = medians.max() / medians.min()
    sig = coef[(coef.lo > 0) | (coef.hi < 0)]
    pos = ", ".join(f"{r.lang} +{fmt_num(r.pct)}%" for r in sig[sig.pct > 0].itertuples())
    neg = ", ".join(f"{r.lang} {fmt_num(r.pct)}%" for r in sig[sig.pct < 0].itertuples())
    return [
        Para("Phương pháp kiểm chứng. Mô hình hồi quy OLS có biến phụ thuộc là log(lương), nên hệ số của biến nhị phân đọc được như phần trăm chênh lệch lương. Biến giải thích gồm quốc gia (62 nước), kinh nghiệm dưới dạng log(1 + WorkExp) và 15 biến nhị phân cho 15 ngôn ngữ phổ biến nhất (1 nếu người đó dùng). "
             "Ta so sánh R² của các mô hình xây dựng dần: R² cho biết phần biến thiên của log(lương) được mô hình giải thích, và phần R² tăng thêm khi thêm một nhóm biến cho biết nhóm biến đó giải thích được bao nhiêu điều mà các nhóm trước chưa giải thích."),
        *figure("f6_3", "r2", ["Phần R² tăng thêm khi bổ sung từng nhóm biến được nêu ở [[tab:r2]]."]),
        Tab("R² của các mô hình hồi quy log(lương) và phần tăng thêm", ["Mô hình", "R²", "Tăng thêm"], r2_rows, [6, 2, 3], "r2"),
        Para("Kiểm định F cho nhóm 15 biến ngôn ngữ cho giá trị p rất nhỏ (cỡ 3 × 10⁻¹⁹⁵). Điều này nghĩa là ngôn ngữ có đóng góp khác không một cách có ý nghĩa thống kê, nhưng với hơn 17 nghìn quan sát thì ngay cả đóng góp nhỏ cũng có ý nghĩa thống kê; điều quan trọng cho kết luận thực tế là độ lớn của đóng góp, chỉ 2,6 điểm phần trăm R², so với 44,9% của quốc gia và 7,3 điểm phần trăm tăng thêm của kinh nghiệm."),
        *figure("f6_4", "coef", [f"Ngôn ngữ có hệ số dương có ý nghĩa: {pos}. Ngôn ngữ có hệ số âm có ý nghĩa: {neg}.",
                                   "Dữ liệu khảo sát không có cột về loại công việc hay quy mô công ty, nên không giải thích được vì sao một số ngôn ngữ có hệ số dương và một số có hệ số âm; đây là hướng cần nghiên cứu thêm."]),
        Para(f"Kết luận kiểm chứng: dữ liệu ủng hộ giả thuyết. Biết người đó sống ở nước nào đã giải thích {pct(r2.r2.iloc[2] * 100, 0)} biến thiên log(lương), thêm kinh nghiệm lên {pct(r2.r2.iloc[3] * 100, 0)}, còn thêm 15 ngôn ngữ chỉ tăng thêm {fmt_num(steps[4] * 100)} điểm phần trăm. Khi đã cố định nước và kinh nghiệm, chênh lệch lương đi cùng việc dùng từng ngôn ngữ nằm trong khoảng từ {fmt_num(coef.pct.min(), 0)}% đến +{fmt_num(coef.pct.max(), 0)}%; để so sánh, median thô của nước cao nhất gấp khoảng {fmt_num(country_ratio)} lần nước thấp nhất ([[tab:ends]]), tuy hai đại lượng này tính khác nhau nên chỉ so sánh tham khảo. Phép so sánh có cơ sở hơn là R²: quốc gia giải thích {pct(r2.r2.iloc[2] * 100)} biến thiên log(lương), còn 15 ngôn ngữ chỉ thêm {fmt_num(steps[4] * 100)} điểm phần trăm."),
    ]


def country_tables() -> tuple:
    """Bảng 10 nước cao nhất, thấp nhất và các nước trong khu vực."""
    full = table("f7_1").sort_values("median", ascending=False).reset_index(drop=True)
    rows = lambda df: [(r.name, fmt_int(r.n), fmt_int(r.median), ci(r.lo, r.hi)) for r in df.itertuples()]
    ends = pd.concat([full.head(RANK_TABLE), full.tail(RANK_TABLE)])
    region = full[full["name"].isin(REGION_COUNTRIES + ("Vietnam",))]
    return full, rows(ends), rows(region)


def q7_section(s: SummaryData) -> list:
    """Mục 4.3: Q7 – lương theo nước."""
    full, end_rows, region_rows = country_tables()
    by_name = full.set_index("name")["median"]
    header = ["Quốc gia", "n", "Median (USD)", "Khoảng tin cậy 95%"]
    return [
        Head("4.3. Lương theo nước và vị trí của Việt Nam (Q7)", 2),
        *figure("f7_1", "choropleth", [f"Nước có median cao nhất là {s.top_country} ({usd(s.top_country_median)}), thấp nhất là {s.low_country} ({usd(s.low_country_median)}); chênh lệch {fmt_num(s.top_country_median / s.low_country_median)} lần. "
                                         f"Phần lớn các nước Bắc Mỹ, Tây Âu và Úc có màu đậm (ngoại lệ trong Bắc Mỹ: Mexico, {usd(by_name[MEXICO])}); Nam Á và châu Phi có màu nhạt, còn Singapore ({usd(by_name[SINGAPORE])}) là ngoại lệ của Đông Nam Á."]),
        *figure("f7_2", "rank", [f"[[tab:region]] so sánh Việt Nam với một số nước chọn trong khu vực. Việt Nam xếp thứ {s.vn_rank}/{s.n_countries} với median {usd(s.vn_median)} từ {s.vn_n} người. Khoảng tin cậy rộng nên thứ hạng không chắc chắn, nhưng Việt Nam nằm gần nhóm các nước đang phát triển ở châu Á và châu Phi trong dữ liệu này."]),
        Tab("10 nước có median cao nhất và 10 nước thấp nhất", header, end_rows, [3.5, 1.8, 3, 4], "ends"),
        Tab("Việt Nam và một số nước chọn để so sánh (đủ 30 dòng lương)", header, region_rows, [3.5, 1.8, 3, 4], "region"),
        Para("Cần nhấn mạnh hai giới hạn khi đọc số liệu Việt Nam. Thứ nhất, lương tính bằng USD danh nghĩa theo tỷ giá quy đổi, chưa điều chỉnh sức mua, nên không phản ánh mức sống thực. Thứ hai, chỉ 31 người Việt Nam có lương hợp lệ, và người tham gia khảo sát của Stack Overflow có thể không đại diện cho toàn bộ lập trình viên Việt Nam."),
    ]


def q8_section() -> list:
    """Mục 4.4: Q8 – so sánh vai trò."""
    prof = table("f8_1").sort_values("median_sal", ascending=False)
    rows = [(r.role, fmt_int(r.n), fmt_int(r.median_sal), fmt_num(r.median_exp, 0), pct(r.ai_daily, 0), fmt_num(r.mean_sat)) for r in prof.itertuples()]
    return [
        Head("4.4. So sánh các vai trò (Q8)", 2),
        *figure("f8_1", "spider", ["Ba vai trò được chọn vì tương phản: Engineering manager (lương cao nhất), AI/ML engineer (dùng AI hằng ngày nhiều nhất) và Embedded (dùng AI hằng ngày ít nhất). "
                                     "Trong ba vai trò này, Engineering manager vượt trội ở lương và kinh nghiệm, AI/ML engineer vượt ở mức dùng AI nhưng ít kinh nghiệm hơn, còn Embedded thấp ở cả mức dùng AI và hài lòng (Architect còn có kinh nghiệm cao hơn, 18 năm, nhưng không thuộc ba vai trò được chọn)."]),
        *figure("f8_2", "dot", ["[[tab:profile]] liệt kê số liệu đầy đủ của 12 vai trò."]),
        Tab("Hồ sơ 12 vai trò: lương, kinh nghiệm, dùng AI hằng ngày và hài lòng công việc", ["Vai trò", "n", "Median lương (USD)", "Kinh nghiệm (năm)", "Dùng AI hằng ngày", "Hài lòng (0–10)"], rows, [3.6, 1.4, 2.4, 2, 1.8, 1.8], "profile"),
        Para("Mức hài lòng công việc trung bình gần như không khác biệt giữa các vai trò (7,0–7,5 trên thang 10), nên bốn chỉ số đưa vào spider thực chất chỉ có ba chỉ số phân biệt được vai trò. Mức dùng AI hằng ngày gần như không liên hệ với lương giữa các vai trò (hệ số Spearman 0,08): vai trò dùng AI nhiều không phải là vai trò lương cao."),
    ]


def summary_section(s: SummaryData) -> list:
    """Mục 4.5: tóm tắt chương."""
    return [
        Head("4.5. Tóm tắt chương", 2),
        Para(f"Median lương của lập trình viên chuyên nghiệp trong mẫu là {usd(s.median_pay)} (mean {usd(s.mean_pay)}). Lương tăng đều theo kinh nghiệm, từ {usd(s.median_0_2)} ở nhóm 0–2 năm lên {usd(s.median_21)} ở nhóm 21+ năm. "
             f"Quốc gia là yếu tố gắn với chênh lệch lớn nhất: {fmt_num(s.top_country_median / s.low_country_median)} lần giữa nước cao nhất và thấp nhất. Hồi quy cho thấy quốc gia giải thích {pct(s.r2_country * 100, 0)} biến thiên log(lương), thêm kinh nghiệm lên {pct(s.r2_country_exp * 100, 0)}, thêm 15 ngôn ngữ chỉ cộng {fmt_num((s.r2_full - s.r2_country_exp) * 100)} điểm phần trăm."),
        Break(),
    ]


def chapter4(s: SummaryData) -> list:
    """Gộp chương 4."""
    return intro(s) + q5_section(s) + q6_descriptive() + q6_regression() + q7_section(s) + q8_section() + summary_section(s)
