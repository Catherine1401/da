"""Đọc kết quả do notebook sinh ra (ảnh, chú giải, tóm tắt) để dựng slide và báo cáo."""
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "out" / "figs"
TABLES = ROOT / "out" / "tables"
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
CROP_DIR = ROOT / "out" / "crop"
WHITE_LEVEL = 250
GAP_ROWS = 12
TITLE_SCAN_MAX = 0.28


@dataclass(frozen=True)
class FigNote:
    """Chú giải một biểu đồ do notebook sinh ra."""
    code: str
    title: str
    observation: str
    insight: str
    footer: str
    n: int

    @property
    def image(self) -> Path:
        """Đường dẫn ảnh PNG của biểu đồ."""
        return FIGS / f"{self.code}.png"

    @property
    def cropped(self) -> Path:
        """Ảnh đã cắt phần tiêu đề (tiêu đề được đặt ở slide hoặc chú thích)."""
        return crop_title(self.image)


@dataclass(frozen=True)
class SummaryData:
    """Số liệu và thông điệp chính của đồ án (khớp với notebook)."""
    n_all: int
    n_sal: int
    pct_pro: float
    median_pay: float
    mean_pay: float
    n_countries: int
    top_country: str
    top_country_median: float
    low_country: str
    low_country_median: float
    vn_rank: int
    vn_median: float
    vn_n: int
    r2_country: float
    r2_country_exp: float
    r2_full: float
    r2_language: float
    f_pvalue: float
    median_0_2: float
    median_21: float
    top_langs: list
    admired_langs: list
    rising_langs: list
    problem_solving_pct: float
    critical_thinking_pct: float
    ai_daily_pct: float
    ai_daily_pct_n: int
    spider_roles: list
    message: str
    recommendations: list
    limitations: list


def crop_title(image: Path) -> Path:
    """Cắt khối tiêu đề ở đầu ảnh: bỏ tới hết khoảng trắng đầu tiên sau tiêu đề; không cắt nếu không tìm thấy."""
    pixels = np.asarray(Image.open(image).convert("L"))
    inked = (pixels < WHITE_LEVEL).any(axis=1)
    limit = int(len(inked) * TITLE_SCAN_MAX)
    rows = np.flatnonzero(inked[:limit])
    cut = 0
    if rows.size:
        gaps = np.diff(rows)
        found = np.flatnonzero(gaps > GAP_ROWS)
        cut = int(rows[found[0] + 1]) if found.size else 0
    CROP_DIR.mkdir(parents=True, exist_ok=True)
    target = CROP_DIR / image.name
    Image.open(image).crop((0, cut, pixels.shape[1], pixels.shape[0])).save(target)
    return target


def aspect(image: Path) -> float:
    """Tỷ lệ cao trên rộng của ảnh."""
    width, height = Image.open(image).size
    return height / width


def load_note(code: str) -> FigNote:
    """Đọc chú giải của biểu đồ theo mã."""
    data = json.loads((TABLES / f"{code}_note.json").read_text(encoding="utf-8"))
    return FigNote(**data)


def load_summary() -> SummaryData:
    """Đọc tóm tắt chung."""
    return SummaryData(**json.loads((TABLES / "summary.json").read_text(encoding="utf-8")))


def fmt_int(value) -> str:
    """Số nguyên kiểu Việt Nam (dấu chấm hàng nghìn)."""
    return f"{value + 1e-9:,.0f}".replace(",", ".")


def fmt_num(value, digits: int = 1) -> str:
    """Số thập phân kiểu Việt Nam."""
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".").replace("-", "−")


def shorten(text: str, limit: int) -> str:
    """Cắt văn bản ở ranh giới câu, không vượt quá giới hạn ký tự."""
    kept = ""
    for sentence in SENTENCE_END.split(text.strip()):
        if len(kept) + len(sentence) + 1 > limit and kept:
            break
        kept = f"{kept} {sentence}".strip()
    return kept
