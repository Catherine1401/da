# %% [markdown]
# # Phân tích xu hướng công nghệ và mức lương lập trình viên
# **Nguồn dữ liệu:** Stack Overflow Developer Survey 2025 (49.191 phản hồi, 172 cột).
# **Môn học:** CSE702060 – Trực quan hóa dữ liệu, Nhóm 8.
#
# **Đối tượng và mục tiêu:** sau khi xem sản phẩm, sinh viên và lập trình viên mới ở Việt Nam sẽ hiểu
# công nghệ nào đang được dùng và ngưỡng mộ, mức lương phụ thuộc vào yếu tố nào, từ đó chọn công nghệ học và đặt kỳ vọng lương hợp lý.
#
# **Cách chạy:** chọn *Run All*. Notebook tự tìm `data/results.csv`, nếu chưa có sẽ tự tải về từ GitHub của Stack Overflow.
# Ảnh biểu đồ và bảng số được lưu vào thư mục `out/` để dùng lại cho slide và báo cáo.
#
# **Cấu trúc:** (1) cấu hình và hàm dùng chung, (2) làm sạch dữ liệu, (3) hồ sơ người trả lời (Q1),
# (4) xu hướng công nghệ (Q2–Q4), (5) lương (Q5–Q7), (6) so sánh vai trò (Q8), (7) hồi quy kiểm chứng thông điệp (Q6),
# (8) AI và kỹ năng tương lai (Q9), (9) tóm tắt.

# %%
# Thư viện dùng chung
import json
import re
import textwrap
import warnings
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from IPython.display import Image, Markdown, display

warnings.filterwarnings("ignore")


# %%
@dataclass(frozen=True)
class Cfg:
    """Hằng số cấu hình dùng chung cho toàn notebook."""
    results_url: str = "https://github.com/StackExchange/Survey/raw/refs/heads/main/packages/archive/2025/results.csv"
    pro_branch: str = "I am a developer by profession"
    sal_min: int = 1_000
    sal_max: int = 500_000
    min_country_n: int = 30
    min_role_n: int = 200
    min_cell_n: int = 30
    exp_edges: tuple = (0, 2, 5, 10, 20, 200)
    exp_labels: tuple = ("0–2", "3–5", "6–10", "11–20", "21+")
    boot_n: int = 1000
    ci_level: float = 95.0
    seed: int = 42
    top_lang: int = 15
    fig_w: float = 8.0
    fig_h: float = 4.5
    dpi: int = 200
    px_w: int = 1600
    px_h: int = 900


@dataclass(frozen=True)
class Pal:
    """Bảng màu Okabe-Ito an toàn cho người mù màu."""
    accent: str = "#0072B2"
    accent2: str = "#D55E00"
    neutral: str = "#999999"
    light: str = "#D9D9D9"
    cat: tuple = ("#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000")


class Col:
    """Tên cột dùng trong dữ liệu gốc và các cột dẫn xuất."""
    ID = "ResponseId"
    MAIN = "MainBranch"
    AGE = "Age"
    COUNTRY = "Country"
    DEVTYPE = "DevType"
    WORKEXP = "WorkExp"
    SAL_RAW = "ConvertedCompYearly"
    AI = "AISelect"
    REMOTE = "RemoteWork"
    JOBSAT = "JobSat"
    LANG_HAVE = "LanguageHaveWorkedWith"
    LANG_WANT = "LanguageWantToWorkWith"
    LANG_ADM = "LanguageAdmired"
    DB_HAVE = "DatabaseHaveWorkedWith"
    PLAT_HAVE = "PlatformHaveWorkedWith"
    WEB_HAVE = "WebframeHaveWorkedWith"
    AIOPEN = "AIOpen"
    SAL = "salary_usd"
    ISO3 = "iso3"
    EXPBIN = "exp_bin"
    ROLE = "role"
    VALUE = "value"
    RAW = (ID, MAIN, AGE, COUNTRY, DEVTYPE, WORKEXP, SAL_RAW, AI, REMOTE, JOBSAT, LANG_HAVE, LANG_WANT,
           LANG_ADM, DB_HAVE, PLAT_HAVE, WEB_HAVE, AIOPEN)


@dataclass(frozen=True)
class Label:
    """Cặp nhãn gốc và nhãn rút gọn dùng trên biểu đồ."""
    raw: str
    short: str


@dataclass
class Note:
    """Chú giải của một biểu đồ, dùng lại cho slide và báo cáo."""
    code: str
    title: str
    observation: str
    insight: str
    footer: str
    n: int


@dataclass(frozen=True)
class Paths:
    """Các thư mục dữ liệu và kết quả."""
    root: Path
    data: Path
    figs: Path
    tables: Path

    @staticmethod
    def discover() -> "Paths":
        here = Path.cwd().resolve()
        candidates = [here, here.parent, here.parent.parent]
        root = next((c for c in candidates if (c / "data" / "results.csv").exists()), here)
        paths = Paths(root, root / "data", root / "out" / "figs", root / "out" / "tables")
        for folder in (paths.data, paths.figs, paths.tables):
            folder.mkdir(parents=True, exist_ok=True)
        return paths


PATHS = Paths.discover()
TITLE_WRAP = 66
FOOT_WRAP = 150
TITLE_SIZE = 13
FOOT_SIZE = 6.5
THOUSAND_SEP = "."
HALF_EPS = 1e-9
MINUS_SIGN = "−"
DECIMAL_SEP = ","


# %%
def fmt_int(value) -> str:
    """Định dạng số nguyên kiểu Việt Nam (dấu chấm phân tách hàng nghìn)."""
    return f"{value + HALF_EPS:,.0f}".replace(",", THOUSAND_SEP)


def fmt_num(value, digits: int = 1) -> str:
    """Định dạng số thập phân kiểu Việt Nam."""
    text = f"{value:,.{digits}f}"
    return text.replace(",", "_").replace(".", DECIMAL_SEP).replace("_", THOUSAND_SEP).replace("-", MINUS_SIGN)


def fmt_pct(value, digits: int = 1) -> str:
    """Định dạng phần trăm kiểu Việt Nam."""
    return fmt_num(value, digits) + "%"


def label_map(labels) -> dict:
    """Chuyển danh sách Label thành từ điển tra cứu."""
    return {label.raw: label.short for label in labels}


def source_line(n: int, filters: str) -> str:
    """Dòng chú thích chân biểu đồ: nguồn, bộ lọc, cỡ mẫu."""
    return f"Nguồn: Stack Overflow Developer Survey 2025. {filters} n = {fmt_int(n)}."


def thousands_axis(ax, axis: str = "x") -> None:
    """Hiển thị số trên trục kiểu Việt Nam (dấu chấm hàng nghìn)."""
    formatter = FuncFormatter(lambda value, _: fmt_int(value))
    (ax.xaxis if axis == "x" else ax.yaxis).set_major_formatter(formatter)


def apply_style() -> None:
    """Thiết lập kiểu chung cho mọi biểu đồ matplotlib."""
    plt.rcParams.update({
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "grid.color": "#E5E5E5", "axes.axisbelow": True, "font.size": 9, "figure.facecolor": "white",
    })


apply_style()


# %%
TOP_MARGIN = 0.80
BOTTOM_MARGIN = 0.15
RIGHT_MARGIN = 0.97


def decorate_fig(fig, note: Note, left: float = 0.18) -> None:
    """Gắn tiêu đề nêu phát hiện, chú thích chân và lề cho một figure matplotlib."""
    fig.suptitle(textwrap.fill(note.title, TITLE_WRAP), x=0.01, ha="left", fontsize=TITLE_SIZE, fontweight="bold")
    fig.text(0.01, 0.012, textwrap.fill(note.footer, FOOT_WRAP), fontsize=FOOT_SIZE, color="#555555", va="bottom")
    fig.subplots_adjust(top=TOP_MARGIN, bottom=BOTTOM_MARGIN, left=left, right=RIGHT_MARGIN)


def new_fig(note: Note, nrows: int = 1, ncols: int = 1, left: float = 0.18, **kwargs):
    """Tạo khung biểu đồ 1600×900 px có tiêu đề nêu phát hiện và chú thích chân."""
    fig, axes = plt.subplots(nrows, ncols, figsize=(Cfg.fig_w, Cfg.fig_h), dpi=Cfg.dpi, **kwargs)
    decorate_fig(fig, note, left)
    return fig, axes


def style_plotly(fig: go.Figure, note: Note) -> go.Figure:
    """Gắn tiêu đề, chú thích chân và kích thước chuẩn cho biểu đồ plotly."""
    fig.update_layout(
        title={"text": "<b>" + textwrap.fill(note.title, TITLE_WRAP).replace("\n", "<br>") + "</b>",
               "x": 0.01, "xanchor": "left", "font": {"size": 22}},
        width=Cfg.px_w, height=Cfg.px_h, paper_bgcolor="white", plot_bgcolor="white",
        margin={"l": 40, "r": 40, "t": 130, "b": 90}, separators=",.",
    )
    fig.add_annotation(text=textwrap.fill(note.footer, FOOT_WRAP).replace("\n", "<br>"), x=0.0, y=-0.08,
                       xref="paper", yref="paper", showarrow=False, xanchor="left", align="left", font={"size": 12, "color": "#555555"})
    return fig


def export_table(table: pd.DataFrame, code: str) -> None:
    """Lưu bảng số của biểu đồ để báo cáo dùng lại."""
    table.to_csv(PATHS.tables / f"{code}.csv", index=False, encoding="utf-8-sig")


BAR_HEIGHT = 0.7
PCT_PAD = 0.4


def annotate_bars_h(ax, values, texts) -> None:
    """Ghi nhãn giá trị ở cuối mỗi cột ngang."""
    for idx, (val, text) in enumerate(zip(values, texts)):
        ax.text(val + PCT_PAD, idx, text, va="center", fontsize=8)


def finish(fig, note: Note) -> None:
    """Lưu ảnh PNG và chú giải JSON, rồi hiển thị biểu đồ kèm nhận xét."""
    path = PATHS.figs / f"{note.code}.png"
    if isinstance(fig, go.Figure):
        fig.write_image(path, width=Cfg.px_w, height=Cfg.px_h)
    else:
        fig.savefig(path, dpi=Cfg.dpi)
        plt.close(fig)
    (PATHS.tables / f"{note.code}_note.json").write_text(json.dumps(asdict(note), ensure_ascii=False, indent=1), encoding="utf-8")
    display(Image(filename=path, width=800))
    display(Markdown(f"**Nhận xét.** {note.observation}\n\n**Insight.** {note.insight}"))
