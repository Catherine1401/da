"""Nội dung chương 3: xu hướng công nghệ (Q2, Q3, Q4)."""
import networkx as nx
import pandas as pd
from networkx.algorithms import community

from data import SummaryData, fmt_num
from docx_kit import Break, Head, Para, Tab
from report_common import figure, join_names, pct, table

TOP_TABLE = 12
POPULAR_MIN_PCT = 5.0
TOP_LIST = 5


def intro() -> list:
    """Mở đầu chương 3."""
    return [
        Head("3. Xu hướng công nghệ", 1),
        Para("Chương này trả lời ba câu hỏi: công nghệ nào đang được dùng nhiều (Q2), công nghệ nào được ngưỡng mộ và muốn dùng so với mức đang dùng (Q3), và các ngôn ngữ liên hệ với nhau thế nào (Q4). "
             "Vì dữ liệu chỉ có một năm, ba chỉ số 'đang dùng', 'muốn dùng' và 'được ngưỡng mộ' được dùng như chỉ số thay thế cho xu hướng: một ngôn ngữ có mức muốn dùng cao hơn mức đang dùng cho thấy người dùng kỳ vọng nó sẽ được dùng nhiều hơn, dù không chứng minh được mức dùng thực sự sẽ tăng."),
        Para("Tất cả tỷ lệ trong chương được tính trên số người có trả lời cột tương ứng (mẫu số ghi ở chân từng biểu đồ). Một người thường chọn nhiều công nghệ cùng lúc, nên tổng các tỷ lệ vượt 100%."),
    ]


def top_langs_text(df: pd.DataFrame, count: int) -> str:
    """Chuỗi 'tên tỷ lệ' của các ngôn ngữ đứng đầu."""
    return ", ".join(f"{row.value} {pct(row.pct)}" for row in df.head(count).itertuples())


def q2_section() -> list:
    """Mục 3.1: Q2 – công nghệ đang được dùng."""
    langs, groups, small = table("f2_1"), table("f2_2"), table("f2_3")
    leaders = groups.sort_values("users", ascending=False).groupby("group", sort=False).head(1)
    leader_text = "; ".join(f"{row.group}: {row.tech} ({int(row.users):,} người)".replace(",", ".") for row in leaders.itertuples())
    small_text = "; ".join(f"{group}: " + join_names(f"{row.value} {pct(row.pct, 0)}" for row in sub.head(3).itertuples())
                           for group, sub in small.groupby("group", sort=False))
    return [
        Head("3.1. Công nghệ nào đang được dùng nhiều nhất (Q2)", 2),
        *figure("f2_1", "bar_short", [f"Tám ngôn ngữ đứng đầu: {top_langs_text(langs, 8)}.",
                                  "Nhóm ba ngôn ngữ đầu (JavaScript, HTML/CSS, SQL) đều vượt 58%, nên ba công nghệ web và dữ liệu này có mặt ở phần lớn người trả lời. Python đứng thứ tư với 58,1%, sát nhóm đầu."]),
        *figure("f2_2", "treemap", [f"Người dùng nhiều nhất ở từng nhóm: {leader_text}.",
                                      "Diện tích mỗi ô tính theo số người dùng, vì vậy chỉ so sánh trực tiếp các ô trong cùng một nhóm; số người dùng ngoài nhóm có mẫu số khác nhau."]),
        *figure("f2_3", "small", [f"Ba công nghệ đứng đầu mỗi nhóm theo tỷ lệ: {small_text}.",
                                    "Docker đạt gần 72% trong nhóm cloud và nền tảng, PostgreSQL khoảng 57% trong nhóm cơ sở dữ liệu và Node.js khoảng 50% trong nhóm web framework."]),
    ]


def lang_summary_table() -> Tab:
    """Bảng tóm tắt đang dùng, muốn dùng, ngưỡng mộ của các ngôn ngữ phổ biến."""
    top = table("f3_1").sort_values("have_pct", ascending=False).head(TOP_TABLE)
    rows = [(row.value, pct(row.have_pct), pct(row.want_pct), pct(row.admired_pct), fmt_num(row.want_gap)) for row in top.itertuples()]
    return Tab(f"{TOP_TABLE} ngôn ngữ phổ biến nhất: đang dùng, muốn dùng, ngưỡng mộ và chênh lệch (điểm %)",
               ["Ngôn ngữ", "Đang dùng", "Muốn dùng", "Ngưỡng mộ", "Muốn − dùng"], rows, [3, 2, 2, 2, 2.4], "langs")


def q3_section() -> list:
    """Mục 3.2: Q3 – ngưỡng mộ và muốn dùng."""
    lang = table("f3_1")
    popular = lang[lang.have_pct >= POPULAR_MIN_PCT].sort_values("admired_pct", ascending=False)
    top_adm = ", ".join(f"{r.value} {pct(r.admired_pct, 0)}" for r in popular.head(TOP_LIST).itertuples())
    low_adm = ", ".join(f"{r.value} {pct(r.admired_pct, 0)}" for r in popular.tail(3).itertuples())
    gap = table("f3_2").sort_values("want_gap")
    up = ", ".join(f"{r.value} +{fmt_num(r.want_gap)}" for r in gap.tail(TOP_LIST)[::-1].itertuples())
    down = ", ".join(f"{r.value} {fmt_num(r.want_gap)}" for r in gap.head(TOP_LIST).itertuples())
    return [
        Head("3.2. Dùng nhiều có được ngưỡng mộ và muốn dùng nhiều không (Q3)", 2),
        *figure("f3_1", "scatter", [f"Trong các ngôn ngữ có ít nhất {pct(POPULAR_MIN_PCT, 0)} người dùng, mức ngưỡng mộ cao nhất là: {top_adm}; thấp nhất là: {low_adm}.",
                                      "Nhóm ở góc trên bên trái (mức dùng thấp nhưng ngưỡng mộ rất cao: Gleam, Elixir, Zig, và cả Rust với mức dùng vừa phải) khác với nhóm ở góc dưới bên phải (dùng nhiều nhưng ngưỡng mộ vừa phải, như Java và JavaScript). Dữ liệu không cho biết lý do (ví dụ ngôn ngữ mới hay phải dùng vì công việc), nên đây chỉ là hướng cần kiểm tra thêm."]),
        *figure("f3_2", "diverging", [f"Mức muốn dùng vượt mức đang dùng nhiều nhất (điểm phần trăm): {up}. Mức muốn dùng thấp hơn mức đang dùng nhiều nhất: {down}.",
                                        "Cần đọc cẩn thận: JavaScript, HTML/CSS và SQL có chênh lệch âm lớn một phần vì mức đang dùng của chúng đã rất cao (từ 59% đến 66%), nên 'muốn dùng' khó vượt mức này như các ngôn ngữ có mức dùng thấp."]),
        lang_summary_table(),
        Para("[[tab:langs]] (cột Muốn − dùng tính từ số chưa làm tròn nên có thể lệch 0,1 so với hiệu hai cột bên cạnh) cho thấy ba mức đo không đồng nhất: ngôn ngữ phổ biến nhất không phải là ngôn ngữ được ngưỡng mộ nhất, và ngôn ngữ được muốn dùng thêm nhiều nhất (Rust, Go, Zig) có mức dùng hiện tại thấp (xem [[tab:appxlang]] ở phụ lục). Với người mới học, điều này gợi ý một lộ trình hai bước: nắm vững nhóm ngôn ngữ phổ biến, rồi chọn thêm một ngôn ngữ đang được muốn dùng nhiều để mở rộng."),
    ]


def cluster_text(edges: pd.DataFrame) -> str:
    """Mô tả các cụm ngôn ngữ do thuật toán modularity tìm ra trên đồ thị đồng xuất hiện."""
    graph = nx.from_pandas_edgelist(edges, "source", "target", edge_attr="weight")
    groups = sorted((sorted(g) for g in community.greedy_modularity_communities(graph, weight="weight")), key=len, reverse=True)
    return "; ".join("{" + ", ".join(g) + "}" for g in groups)


def q4_section() -> list:
    """Mục 3.3: Q4 – mạng đồng xuất hiện và luồng đang dùng sang muốn dùng."""
    edges = table("f4_1").sort_values("weight", ascending=False)
    edge_text = "; ".join(f"{r.source}–{r.target} (lift {fmt_num(r.weight)}, cùng dùng ở {pct(r.share)} người)" for r in edges.head(TOP_LIST).itertuples())
    flows = table("f4_2").set_index("dang_dung")
    stacked = flows.stack().sort_values(ascending=False)
    flow_text = "; ".join(f"{src} → {dst} ({pct(v, 0)})" for (src, dst), v in stacked.head(TOP_LIST).items())
    return [
        Head("3.3. Các ngôn ngữ đi cùng nhau thế nào (Q4)", 2),
        *figure("f4_1", "network", [f"Năm cặp có lift cao nhất: {edge_text}.",
                                      f"Đồ thị được dựng bằng thư viện NetworkX [5]; thuật toán phát hiện cộng đồng (modularity) tách đồ thị thành các cụm: {cluster_text(edges)}. Một số cụm có thể giải thích bằng hệ sinh thái chung (ví dụ cụm C#, VB.NET, PowerShell, VBA hoặc cụm Java, Kotlin, Groovy), một số cụm khác (như Go và Ruby) dữ liệu không cho biết lý do. Các ngôn ngữ web rất phổ biến (JavaScript, HTML/CSS, SQL) không xuất hiện trong mạng vì chúng đi cùng mọi ngôn ngữ khác nên lift không cao (ví dụ JavaScript với HTML/CSS có lift 1,32, thấp hơn ngưỡng 1,5)."]),
        *figure("f4_2", "sankey", [f"Các luồng mạnh nhất (tỷ lệ người đang dùng ngôn ngữ nguồn muốn dùng ngôn ngữ đích): {flow_text}.",
                                     "Luồng giữa các ngôn ngữ web mạnh theo cả hai chiều: người làm web muốn có trọn bộ HTML/CSS, JavaScript, TypeScript và SQL. Lưu ý đây chỉ là mong muốn tại một thời điểm."]),
    ]


def summary_section(s: SummaryData) -> list:
    """Mục 3.4: tóm tắt chương."""
    return [
        Head("3.4. Tóm tắt chương", 2),
        Para(f"Ba ngôn ngữ dùng nhiều nhất là {join_names(s.top_langs)}; trong nhóm đã khá phổ biến, các ngôn ngữ được ngưỡng mộ nhất là {join_names(s.admired_langs)}. "
             "Mức dùng và mức ngưỡng mộ gần như không liên hệ (hệ số Spearman 0,12), nên ngôn ngữ đứng đầu về số người dùng không phải ngôn ngữ đứng đầu về mức ngưỡng mộ. Một số ngôn ngữ thường được dùng chung và tạo thành cụm, gợi ý các ngôn ngữ người học có thể học cùng nhau."),
        Para("Hạn chế cần nhớ: dữ liệu chỉ có năm 2025, nên 'muốn dùng' và 'ngưỡng mộ' là mong muốn tự khai báo chứ không phải sự thay đổi thật theo thời gian; mẫu lệch về Mỹ và châu Âu nên có thể khác với thị trường Việt Nam."),
        Break(),
    ]


def chapter3(s: SummaryData) -> list:
    """Gộp chương 3."""
    return intro() + q2_section() + q3_section() + q4_section() + summary_section(s)
