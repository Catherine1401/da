"""Phần dùng chung của các chương báo cáo: đọc bảng số, hướng dẫn đọc biểu đồ, sinh khối cho một biểu đồ."""
from dataclasses import dataclass

import pandas as pd

from data import TABLES, fmt_int, fmt_num, load_note
from docx_kit import Fig, Para

@dataclass(frozen=True)
class Label:
    """Cặp nhãn gốc và nhãn rút gọn."""
    raw: str
    short: str


BRANCH_SHORT = (
    Label("I am a developer by profession", "lập trình viên chuyên nghiệp"),
    Label("I am not primarily a developer, but I write code sometimes as part of my work/studies", "viết code thỉnh thoảng"),
    Label("I am learning to code", "đang học code"),
    Label("I code primarily as a hobby", "code như sở thích"),
    Label("I used to be a developer by profession, but no longer am", "từng là lập trình viên"),
    Label("I work with developers or my work supports developers but am not a developer by profession", "làm việc cùng lập trình viên"),
)


def short_branch(raw: str) -> str:
    """Rút gọn tên nhóm MainBranch."""
    return {label.raw: label.short for label in BRANCH_SHORT}.get(raw, raw)


HOWTO = {
    "bar_short": "Biểu đồ cột như ở hình trước: chiều dài cột tỷ lệ với giá trị, số ghi ở cuối mỗi cột.",
    "bar": "Biểu đồ cột (bar chart) so sánh giá trị giữa các nhóm; chiều dài cột tỷ lệ với giá trị nên dễ so sánh và xếp hạng. Biểu đồ không thể hiện xu hướng theo thời gian hay phân bố bên trong mỗi nhóm.",
    "treemap": "Treemap biểu diễn quan hệ phần và tổng thể trong cấu trúc phân cấp (nhóm công nghệ rồi tới từng công nghệ); diện tích mỗi ô tỷ lệ với số người dùng, màu phân biệt nhóm. Treemap không phù hợp để đọc số chính xác, vì vậy số người dùng được ghi ngay trong ô.",
    "small": "Các biểu đồ cột nhỏ lặp lại (small multiples) đặt cạnh nhau cùng một thang để so sánh nhiều nhóm mà không làm một biểu đồ quá tải. Mỗi ô con là một nhóm công nghệ với cùng cách đọc như biểu đồ cột.",
    "scatter": "Biểu đồ phân tán (scatter plot) cho thấy quan hệ giữa hai biến số; mỗi điểm là một ngôn ngữ lập trình. Hai đường nét đứt là median của từng trục, chia mặt phẳng thành bốn góc phần tư để nhận ra nhóm phổ biến và nhóm được ngưỡng mộ.",
    "diverging": "Biểu đồ cột phân kỳ đặt giá trị 0 ở giữa: cột sang phải (xanh) là mức muốn dùng cao hơn mức đang dùng, cột sang trái (cam) là thấp hơn. Chiều dài cột thể hiện độ lớn chênh lệch tính bằng điểm phần trăm.",
    "network": "Biểu đồ mạng (node-link) gồm các nút là ngôn ngữ và các cạnh là cặp ngôn ngữ thường được dùng chung. Kích thước nút tỷ lệ với số người dùng, độ dày cạnh tỷ lệ với chỉ số lift, màu là cụm cộng đồng do thuật toán phát hiện. Vị trí nút chỉ phục vụ quan sát, không có ý nghĩa đo lường.",
    "sankey": "Biểu đồ Sankey thể hiện luồng giữa hai tập nút: bên trái là ngôn ngữ người trả lời đang dùng, bên phải là ngôn ngữ họ muốn dùng; độ dày dải tỷ lệ với số người. Biểu đồ không dùng để đọc số chính xác nên các tỷ lệ cụ thể được nêu trong phần nhận xét.",
    "hist": "Histogram cho thấy phân bố của một biến số; trục ngang chia thành các khoảng, chiều cao cột là số người trong khoảng đó. Trục ngang dùng thang log vì lương trải rộng trên nhiều bậc độ lớn; hai vạch đứng đánh dấu median và mean.",
    "ridge": "Biểu đồ ridgeline xếp chồng nhẹ các đường mật độ (KDE) của nhiều nhóm trên cùng một trục để so sánh hình dạng phân bố: vị trí đỉnh cho biết mức lương điển hình, độ rộng cho biết mức phân tán. Vạch cam là median của từng vai trò.",
    "line": "Biểu đồ đường nối median lương theo từng nhóm kinh nghiệm theo thứ tự tăng dần; vùng tô nhạt là khoảng tin cậy 95% bằng bootstrap, số dưới mỗi điểm là cỡ mẫu.",
    "ci": "Biểu đồ cột ngang kèm thanh sai số: chiều dài cột là median lương, thanh sai số là khoảng tin cậy bootstrap 95%. Khi hai thanh sai số chồng lấn thì chênh lệch giữa hai nhóm kém chắc chắn.",
    "heat": "Heatmap biểu diễn ma trận hai chiều (ngôn ngữ × vai trò) bằng màu: ô càng đậm thì median lương càng cao, số trong ô là median tính bằng nghìn USD. Ô thiếu dữ liệu (ít hơn 30 người) được để trống thay vì tô màu.",
    "r2": "Biểu đồ cột so sánh R² của các mô hình hồi quy: R² là phần trăm biến thiên của log(lương) được mô hình giải thích. Mô hình càng nhiều biến thì R² càng không giảm, nên điều cần xem là phần R² tăng thêm khi bổ sung từng nhóm biến.",
    "coef": "Biểu đồ hệ số hồi quy: mỗi chấm là chênh lệch lương ước lượng (quy ra phần trăm) đi cùng việc dùng một ngôn ngữ so với không dùng, đã kiểm soát quốc gia và kinh nghiệm; thanh ngang là khoảng tin cậy 95%. Chấm xanh có khoảng tin cậy không chứa 0, chấm xám thì chưa đủ bằng chứng.",
    "choropleth": "Bản đồ choropleth tô màu mỗi nước theo median lương, một biến duy nhất với thang màu tuần tự (càng đậm càng cao). Bản đồ chỉ dùng giá trị chuẩn hóa (median) chứ không dùng số tuyệt đối, và chỉ hiển thị nước đủ 30 dòng lương.",
    "rank": "Biểu đồ xếp hạng gồm 10 nước cao nhất, Việt Nam (màu cam) và 10 nước thấp nhất; thanh sai số là khoảng tin cậy bootstrap 95% và n là số người có lương ở mỗi nước.",
    "spider": "Spider chart (radar) so sánh hồ sơ nhiều chỉ số của vài đối tượng trên các trục xuất phát từ tâm. Để tránh các nhược điểm đã biết (thứ tự trục ảnh hưởng hình dạng, diện tích phóng đại chênh lệch), biểu đồ chỉ có 4 trục, 3 vai trò, mỗi trục được chia cho giá trị cao nhất để bắt đầu từ 0 và dải giá trị thật ghi cạnh tên trục.",
    "dot": "Biểu đồ chấm (dot plot) hiển thị giá trị thật của từng chỉ số cho mọi vai trò, sắp theo lương; ba chấm màu là ba vai trò đã so sánh trong spider chart, dùng khi cần đọc số chính xác.",
    "cloud": "Wordcloud thể hiện tần suất từ trong văn bản: kích thước chữ tỷ lệ với số câu trả lời chứa từ đó. Wordcloud nhanh và trực quan nhưng không cho biết ngữ cảnh, nên đi kèm bảng tần suất.",
    "words": "Biểu đồ cột ngang liệt kê 20 từ khóa xuất hiện trong nhiều câu trả lời nhất; tỷ lệ là số câu trả lời chứa từ chia cho tổng số câu trả lời.",
}


def table(name: str) -> pd.DataFrame:
    """Đọc một bảng số do notebook xuất ra."""
    return pd.read_csv(TABLES / f"{name}.csv", encoding="utf-8-sig")


def pct(value, digits: int = 1) -> str:
    """Định dạng phần trăm kiểu Việt Nam."""
    return fmt_num(value, digits) + "%"


def usd(value) -> str:
    """Định dạng tiền USD kiểu Việt Nam."""
    return f"{fmt_int(value)} USD"


def join_names(names, last: str = "và") -> str:
    """Nối danh sách tên: 'A, B và C'."""
    items = list(names)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + f" {last} " + items[-1]


def figure(code: str, how: str, extra: list = None) -> list:
    """Khối đầy đủ cho một biểu đồ: cách đọc, hình, nhận xét, phần phân tích thêm và insight."""
    note = load_note(code)
    blocks = [Para(f"[[fig:{code}]] là " + HOWTO[how][0].lower() + HOWTO[how][1:], lead="Cách đọc biểu đồ."), Fig(code), Para(note.observation, lead="Nhận xét.")]
    blocks += [Para(text) for text in (extra or [])]
    blocks.append(Para(note.insight, lead="Insight."))
    return blocks
