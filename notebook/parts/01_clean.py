# %% [markdown]
# ## 1. Làm sạch dữ liệu
# Quy tắc cố định để slide, báo cáo và notebook cùng số liệu:
# 1. Đọc CSV bằng `utf-8-sig` (file có BOM).
# 2. Bảng lương `df_sal`: giữ lương `ConvertedCompYearly` (USD) trong khoảng 1.000–500.000 USD và chỉ người "I am a developer by profession".
# 3. Cột chọn nhiều đáp án tách theo dấu `;`; tỷ lệ tính trên số người có trả lời cột đó.
# 4. Nước chỉ vào so sánh khi có đủ 30 dòng lương; vai trò (`DevType`) cần đủ 200 dòng lương, bỏ nhóm "Other".
# 5. Kinh nghiệm dùng cột `WorkExp`, chia 5 nhóm (0–2, 3–5, 6–10, 11–20, 21+ năm).

# %%
import pycountry

COUNTRY_ALIASES = (
    Label("Iran, Islamic Republic of...", "IRN"), Label("Turkey", "TUR"), Label("Hong Kong (S.A.R.)", "HKG"),
    Label("Republic of Korea", "KOR"), Label("Venezuela, Bolivarian Republic of...", "VEN"),
    Label("Kosovo", "XKX"), Label("Swaziland", "SWZ"), Label("Palestine", "PSE"),
    Label("Congo, Republic of the...", "COG"), Label("Democratic Republic of the Congo", "COD"),
    Label("Micronesia, Federated States of...", "FSM"), Label("Libyan Arab Jamahiriya", "LBY"),
    Label("Cape Verde", "CPV"),
)
COUNTRY_SHORT = (
    Label("United States of America", "United States"),
    Label("United Kingdom of Great Britain and Northern Ireland", "United Kingdom"),
    Label("Republic of Korea", "South Korea"), Label("Viet Nam", "Vietnam"),
    Label("Russian Federation", "Russia"), Label("Democratic Republic of the Congo", "DR Congo"),
    Label("Libyan Arab Jamahiriya", "Libya"), Label("Hong Kong (S.A.R.)", "Hong Kong"),
    Label("United Republic of Tanzania", "Tanzania"), Label("Syrian Arab Republic", "Syria"),
)
ROLE_SHORT = (
    Label("Developer, full-stack", "Full-stack"), Label("Developer, back-end", "Back-end"),
    Label("Architect, software or solutions", "Architect"),
    Label("Developer, desktop or enterprise applications", "Desktop/enterprise"),
    Label("Developer, front-end", "Front-end"), Label("Developer, mobile", "Mobile"),
    Label("Developer, embedded applications or devices", "Embedded"),
    Label("Engineering manager", "Engineering manager"), Label("DevOps engineer or professional", "DevOps"),
    Label("Data engineer", "Data engineer"), Label("AI/ML engineer", "AI/ML engineer"),
    Label("Data scientist", "Data scientist"),
)
VALUE_SHORT = (
    Label("Bash/Shell (all shells)", "Bash/Shell"), Label("Amazon Web Services (AWS)", "AWS"),
    Label("Visual Basic (.Net)", "VB.NET"), Label("Microsoft SQL Server", "SQL Server"),
)
VIETNAM = "Viet Nam"
OTHER_ROLE_PREFIX = "Other"
NO_ISO = "Nomadic"
AI_DAILY = "Yes, I use AI tools daily"
MULTI_SEP = ";"


def short_country(name: str) -> str:
    """Rút gọn tên nước để hiển thị trên biểu đồ."""
    mapped = label_map(COUNTRY_SHORT).get(name)
    return mapped if mapped else name.split(",")[0].replace("...", "").strip()


def short_role(name: str) -> str:
    """Rút gọn tên vai trò để hiển thị trên biểu đồ."""
    return label_map(ROLE_SHORT).get(name, name)


def country_to_iso3(name: str):
    """Đổi tên nước trong khảo sát sang mã ISO-3; trả về None nếu không phải nước."""
    alias = label_map(COUNTRY_ALIASES).get(name)
    if alias or name == NO_ISO:
        return alias
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        return None


# %%
def fetch_results() -> Path:
    """Tìm file results.csv ở local, chưa có thì tải từ GitHub."""
    path = PATHS.data / "results.csv"
    if not path.exists():
        urllib.request.urlretrieve(Cfg.results_url, path)
    return path


def load_all() -> pd.DataFrame:
    """Đọc toàn bộ người trả lời, chỉ giữ các cột dùng trong phân tích."""
    return pd.read_csv(fetch_results(), encoding="utf-8-sig", usecols=list(Col.RAW), low_memory=False)


def build_sal(df_all: pd.DataFrame) -> pd.DataFrame:
    """Dựng bảng lương theo quy tắc lọc: lập trình viên chuyên nghiệp, lương hợp lệ."""
    keep = df_all[Col.SAL_RAW].between(Cfg.sal_min, Cfg.sal_max) & (df_all[Col.MAIN] == Cfg.pro_branch)
    sal = df_all.loc[keep].rename(columns={Col.SAL_RAW: Col.SAL}).copy()
    iso_by_name = {name: country_to_iso3(name) for name in sal[Col.COUNTRY].dropna().unique()}
    sal[Col.ISO3] = sal[Col.COUNTRY].map(iso_by_name)
    sal[Col.EXPBIN] = pd.cut(sal[Col.WORKEXP], bins=list(Cfg.exp_edges), labels=list(Cfg.exp_labels))
    sal[Col.ROLE] = sal[Col.DEVTYPE].map(short_role)
    return sal


def explode_multi(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Tách cột chọn nhiều đáp án thành bảng dạng dài (ResponseId, value)."""
    answered = df[[Col.ID, col]].dropna()
    longer = answered.assign(**{Col.VALUE: answered[col].str.split(MULTI_SEP)}).explode(Col.VALUE)
    longer[Col.VALUE] = longer[Col.VALUE].replace(label_map(VALUE_SHORT))
    return longer[[Col.ID, Col.VALUE]].reset_index(drop=True)


def share_answered(df: pd.DataFrame, col: str):
    """Trả về (tỷ lệ % theo từng đáp án, số người có trả lời) cho cột chọn nhiều đáp án."""
    answered = int(df[col].notna().sum())
    counts = explode_multi(df, col)[Col.VALUE].value_counts()
    return counts / answered * 100, answered


def bootstrap_median_ci(values: np.ndarray, seed: int = Cfg.seed):
    """Khoảng tin cậy bootstrap của median."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(values), size=(Cfg.boot_n, len(values)))
    medians = np.median(values[idx], axis=1)
    tail = (100 - Cfg.ci_level) / 2
    return np.percentile(medians, tail), np.percentile(medians, 100 - tail)


def median_table(df: pd.DataFrame, by: str, value: str = Col.SAL, with_ci: bool = True) -> pd.DataFrame:
    """Bảng n, median và khoảng tin cậy của một biến số theo nhóm."""
    rows = []
    for key, grp in df.groupby(by, observed=True):
        vals = grp[value].dropna().to_numpy()
        lo, hi = bootstrap_median_ci(vals) if with_ci and len(vals) > 1 else (np.nan, np.nan)
        rows.append({by: key, "n": len(vals), "median": float(np.median(vals)), "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


# %%
df_all = load_all()
df_sal = build_sal(df_all)
roles = [r for r, k in df_sal[Col.ROLE].value_counts().items() if k >= Cfg.min_role_n and not r.startswith(OTHER_ROLE_PREFIX)]
country_n = df_sal[Col.COUNTRY].value_counts()
countries = country_n[country_n >= Cfg.min_country_n].index.tolist()
print(f"Tổng số người trả lời: {fmt_int(len(df_all))} | Bảng lương df_sal: {fmt_int(len(df_sal))} dòng")
print(f"Số nước đủ {Cfg.min_country_n} dòng lương: {len(countries)} | Số vai trò đủ {Cfg.min_role_n} dòng: {len(roles)}")
print(f"Việt Nam có {int(country_n.get(VIETNAM, 0))} dòng lương")
missing_iso = sorted(set(df_sal.loc[df_sal[Col.ISO3].isna(), Col.COUNTRY].dropna()))
print("Nước chưa có mã ISO-3 (bị loại khỏi bản đồ):", missing_iso)

# %%
# Mức độ thiếu dữ liệu của các cột dùng trong phân tích
fill = (df_all.notna().mean() * 100).round(1).rename("Tỷ lệ có trả lời (%)").to_frame()
fill.index.name = "Cột"
export_table(fill.reset_index(), "t_fill")
display(fill)
